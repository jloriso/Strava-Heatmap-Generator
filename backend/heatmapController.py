import folium
from folium.plugins import HeatMap, HeatMapWithTime
from collections import Counter, defaultdict
from datetime import datetime

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

def build_frequency_map(activities, locations=None, output_file="heatmaps/frequency_heatmap.html"):
    m = folium.Map(location=[41.8, -87.8], zoom_start=10, tiles="CartoDB Positron")

    grouped = group_activities_by_type(activities)

    for act_type, coords in grouped.items():
        if not coords:
            continue

        rounded = [(round(lat, 6), round(lon, 6)) for lat, lon in coords]

        freq = Counter(rounded)
        weighted_data = [[lat, lon, count] for (lat, lon), count in freq.items()]

        layer = folium.FeatureGroup(name=f"{act_type} Heatmap", show=True)
        HeatMap(weighted_data, radius=8, blur=12, max_zoom=12).add_to(layer)
        layer.add_to(m)

    if locations:
        add_bookmark_sidebar(m, locations)

    folium.LayerControl(collapsed=False).add_to(m)

    print("Frequency heatmap generated and saved to", output_file)
    m.save(output_file)

def add_bookmark_sidebar(m, locations):
    sidebar_html = """
    <style>
    .sidebar {{
        position: absolute;
        bottom: 10px;
        left: 10px;
        z-index: 9999;
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        max-height: 70vh;
        overflow-y: auto;
    }}
    .sidebar h4 {{
        margin: 0 0 8px 0;
        font-size: 16px;
        text-align: center;
    }}
    .sidebar button {{
        display: block;
        width: 100%;
        margin: 4px 0;
        padding: 6px;
        border: none;
        background-color: #2a93d5;
        color: white;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
    }}
    .sidebar button:hover {{
        background-color: #1b6fa1;
    }}
    </style>

    <div class="sidebar">
        <h4>📍 Locations</h4>
        {}
    </div>

    <script>
    function getFoliumMap() {{
        return Object.values(window).find(v => v instanceof L.Map) || null;
    }}

    function detachHeatLayers(map) {{
        const store = [];

        map.eachLayer(function(layer) {{
            if (layer instanceof L.HeatLayer) {{
                store.push({{ layer: layer, parent: map }});
                map.removeLayer(layer);
            }} else if (layer instanceof L.LayerGroup || layer instanceof L.FeatureGroup) {{
                const toRemove = [];
                layer.eachLayer(function(child) {{
                    if (child instanceof L.HeatLayer) {{
                        toRemove.push(child);
                    }}
                    if (child && (child._heatmap || (child._baseLayer && child._baseLayer instanceof L.HeatLayer))) {{
                        toRemove.push(child);
                    }}
                }});
                toRemove.forEach(function(child) {{
                    store.push({{ layer: child, parent: layer }});
                    layer.removeLayer(child);
                }});
            }}
        }});

        return store;
    }}

    function restoreHeatLayers(map, store) {{
        store.forEach(function(entry) {{
            const parent = entry.parent;
            if (parent && typeof parent.addLayer === 'function') {{
                parent.addLayer(entry.layer);
            }} else {{
                map.addLayer(entry.layer);
            }}
        }});
    }}

    function flyToLocation(lat, lon, zoom) {{
        const map = getFoliumMap();
        if (!map) {{
            console.error("Map object not found!");
            return;
        }}

        const heatStore = detachHeatLayers(map);

        map.once('moveend', function() {{
            restoreHeatLayers(map, heatStore);
        }});

        map.flyTo([lat, lon], zoom);
    }}
    </script>
    """

    buttons_html = ""
    for name, (lat, lon, zoom) in locations.items():
        buttons_html += f'<button onclick="flyToLocation({lat}, {lon}, {zoom})">{name}</button>'

    sidebar_final = sidebar_html.format(buttons_html)
    m.get_root().html.add_child(folium.Element(sidebar_final))

def group_activities_by_type(activities):
    grouped = defaultdict(list)
    for act in activities:
        if not act.coordinates:
            continue
        grouped[act.activity_type].extend(act.coordinates)
    return grouped