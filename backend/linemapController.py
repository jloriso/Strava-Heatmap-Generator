from __future__ import annotations

import math
from collections import defaultdict
from statistics import median
from typing import Dict, Iterable, List, Optional, Tuple

import folium
from controls import bookMarkControl
from controls import activityTypeControl 

Coordinate = Tuple[float, float]
GridCell = Tuple[int, int]

DEFAULT_COLORS: Dict[str, str] = {
    "Run": "#fc4c02",       # Strava orange
    "TrailRun": "#ff8c00",
    "Ride": "#00b0ff",
    "VirtualRide": "#00b0ff",
    "Walk": "#8bc34a",
    "Hike": "#8bc34a",
}
DEFAULT_COLOR = "#000000"


# --------------------------------------------------------------------------
# Grid snapping / frequency scoring
# --------------------------------------------------------------------------

def _meters_per_degree(ref_lat: float) -> Tuple[float, float]:
    lat_m = 111_320.0
    lng_m = 111_320.0 * math.cos(math.radians(ref_lat))
    return lat_m, max(lng_m, 1.0)  # guard against poles


def _make_grid_fn(ref_lat: float, grid_size_m: float):
    lat_m, lng_m = _meters_per_degree(ref_lat)
    lat_step = grid_size_m / lat_m
    lng_step = grid_size_m / lng_m

    def to_cell(coord: Coordinate) -> GridCell:
        lat, lng = coord
        return (int(math.floor(lat / lat_step)), int(math.floor(lng / lng_step)))

    return to_cell


def _route_cells(coords: List[Coordinate], to_cell) -> List[GridCell]:
    """Snap coordinates to grid cells, collapsing consecutive duplicates
    (this doubles as simplification for GPS jitter)."""
    cells: List[GridCell] = []
    for c in coords:
        cell = to_cell(c)
        if not cells or cells[-1] != cell:
            cells.append(cell)
    return cells


def _segment_key(a: GridCell, b: GridCell) -> Tuple[GridCell, GridCell]:
    return (a, b) if a <= b else (b, a)


def compute_route_frequency_scores(
    routes: List["ActivityRoute"],
    grid_size_m: float = 15.0,
) -> Dict[int, float]:
    """
    Returns {route.id: frequency_score}, where frequency_score is the
    median number of distinct activities sharing each of this route's
    grid segments (min 1). Higher = more "well-worn" route.
    """
    all_coords = [c for r in routes for c in r.coordinates]
    if not all_coords:
        return {}
    ref_lat = sum(c[0] for c in all_coords) / len(all_coords)
    to_cell = _make_grid_fn(ref_lat, grid_size_m)

    segment_counts: Dict[Tuple[GridCell, GridCell], int] = defaultdict(int)
    route_segment_sets: Dict[int, List[Tuple[GridCell, GridCell]]] = {}

    for r in routes:
        if not r.coordinates:
            continue
        cells = _route_cells(r.coordinates, to_cell)
        seg_keys = {
            _segment_key(cells[i], cells[i + 1]) for i in range(len(cells) - 1)
        }
        route_segment_sets[r.id] = list(seg_keys)
        for key in seg_keys:
            segment_counts[key] += 1  # one increment per distinct route

    scores: Dict[int, float] = {}
    for route_id, seg_keys in route_segment_sets.items():
        if not seg_keys:
            scores[route_id] = 1.0
            continue
        counts = [segment_counts[k] for k in seg_keys]
        scores[route_id] = float(median(counts))

    return scores


def _normalize_scores(
    scores: Dict[int, float],
    clip_percentile: float = 0.9,
) -> Tuple[Dict[int, float], float]:
    """Map raw frequency scores to [0, 1], clipping at a percentile so a
    single mega-common route doesn't wash out the rest of the scale."""
    if not scores:
        return {}, 1.0
    values = sorted(scores.values())
    idx = min(int(len(values) * clip_percentile), len(values) - 1)
    clip_value = max(values[idx], 1.0)

    normalized = {
        rid: min(v, clip_value) / clip_value for rid, v in scores.items()
    }
    return normalized, clip_value


# --------------------------------------------------------------------------
# Map building
# --------------------------------------------------------------------------

def build_frequency_weighted_map(
    routes: Iterable["ActivityRoute"],
    output_path: str = "heatmaps/line_map.html",
    locations= None,
    tile: str = "cartodbpositron",
    color_map: Optional[Dict[str, str]] = None,
    group_by_type: bool = True,
    grid_size_m: float = 15.0,
    min_opacity: float = 0.35,
    max_opacity: float = 0.95,
    min_weight: float = 1.2,
    max_weight: float = 3.5,
    add_glow: bool = True,
    verbose: bool = True
) -> folium.Map:
    
    colors = {**DEFAULT_COLORS, **(color_map or {})}
    routes = [r for r in routes if r.coordinates]

    if not routes:
        raise ValueError("No routes with coordinates were provided.")

    if verbose:
        print(f"Scoring {len(routes)} routes for path frequency...")
    raw_scores = compute_route_frequency_scores(routes, grid_size_m=grid_size_m)
    norm_scores, clip_value = _normalize_scores(raw_scores)
    if verbose:
        print(f"Frequency clip value (routes at/above this render at max intensity): {clip_value}")

    all_coords = [c for r in routes for c in r.coordinates]
    lats = [c[0] for c in all_coords]
    lngs = [c[1] for c in all_coords]

    fmap = folium.Map(
        location=[42.0707, -87.7368],
        zoom_start=10,
        tiles=tile,
        control_scale=True,
        prefer_canvas=True,  # critical for rendering thousands of lines smoothly
    )

    layers: Dict[str, folium.FeatureGroup] = {}

    def get_layer(activity_type: str) -> folium.FeatureGroup:
        if not group_by_type:
            activity_type = "Activities"
        if activity_type not in layers:
            layers[activity_type] = folium.FeatureGroup(name=activity_type)
        return layers[activity_type]

    for i, r in enumerate(routes):
        if verbose and i and i % 500 == 0:
            print(f"  drawn {i}/{len(routes)}...")

        t = norm_scores.get(r.id, 0.0)
        opacity = min_opacity + t * (max_opacity - min_opacity)
        weight = min_weight + t * (max_weight - min_weight)
        color = colors.get(r.activity_type, DEFAULT_COLOR)
        layer = get_layer(r.activity_type or "Other")

        if add_glow:
            folium.PolyLine(
                locations=r.coordinates,
                color=color,
                weight=weight * 2.2,
                opacity=opacity * 0.25,
            ).add_to(layer)

        folium.PolyLine(
            locations=r.coordinates,
            color=color,
            weight=weight,
            opacity=opacity,
            tooltip=r.name,
        ).add_to(layer)

    # Include counts in layer labels now that we know group sizes.
    counts: Dict[str, int] = defaultdict(int)
    for r in routes:
        key = (r.activity_type or "Other") if group_by_type else "Activities"
        counts[key] += 1

    for key, layer in layers.items():
        layer.layer_name = f"{key} ({counts[key]})"
        layer.add_to(fmap)

    if group_by_type or len(layers) > 1:
        folium.LayerControl(collapsed=False).add_to(fmap)

    # sw = (min(lats), min(lngs))
    # ne = (max(lats), max(lngs))
    # fmap.fit_bounds([sw, ne])

    if locations:
        bookMarkControl.add_bookmark_sidebar(fmap, locations, mapType="linemap")

    #activityTypeControl.add_activity_type_sidebar(fmap, ['Run', 'Ride', 'Walk'])

    if verbose:
        print(f"Saving map to {output_path}...")
    fmap.save(output_path)
    return fmap