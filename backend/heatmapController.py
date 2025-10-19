import folium
from folium.plugins import HeatMap
from collections import Counter

def make_heatmap(routes, output_file="heatmaps/standard_heatmap.html", show_routes=False):
    all_points = [coord for route in routes for coord in route.coordinates]
    if not all_points:
        raise ValueError("No coordinates found in provided routes.")

    avg_lat = sum(lat for lat, _ in all_points) / len(all_points)
    avg_lon = sum(lon for _, lon in all_points) / len(all_points)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12, tiles="cartodbpositron")

    HeatMap(all_points, radius=6, blur=4, max_zoom=13).add_to(m)

    if show_routes:
        for route in routes:
            if route.coordinates:
                folium.PolyLine(route.coordinates, color="blue", weight=2, opacity=0.4).add_to(m)

    m.save(output_file)
    print(f"Heatmap generated and saved to {output_file}")

def get_weighted_coordinates(activities, precision=4):
    all_coords = []
    for act in activities:
        # Support ActivityRoute dataclass and dicts
        coords = getattr(act, "coordinates", None)
        if coords is None and isinstance(act, dict):
            coords = act.get("coordinates")

        if not coords:
            continue

        # Round to the desired precision before counting
        rounded = [(round(lat, precision), round(lon, precision)) for lat, lon in coords]
        all_coords.extend(rounded)

    counts = Counter(all_coords)
    return [[lat, lon, weight] for (lat, lon), weight in counts.items()]


def add_weighted_heatmap(m, activities):
    weighted_coords = get_weighted_coordinates(activities)

    HeatMap(
        data = weighted_coords,
        radius=10,
        blur=12,
        max_zoom=13,
        min_opacity=0.4,
        gradient={
            0.2: 'blue',
            0.4: 'lime',
            0.6: 'orange',
            0.8: 'red'
        }
    ).add_to(m)

def build_frequency_map(activities):
    base_map = folium.Map(location=[41.8781, -87.6298], zoom_start=12, tiles="CartoDB positron")
    add_weighted_heatmap(base_map, activities)
    folium.LayerControl().add_to(base_map)
    return base_map