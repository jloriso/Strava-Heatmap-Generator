import folium
from folium.plugins import HeatMap
from collections import Counter, defaultdict
from controls import bookMarkControl

def get_weighted_coordinates(activities, precision=5):
    all_coords = []
    for act in activities:
        coords = getattr(act, "coordinates", None)
        if coords is None and isinstance(act, dict):
            coords = act.get("coordinates")

        if not coords:
            continue

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

def build_frequency_map(activities, locations=None, output_file="heatmaps/standard_heatmap.html"):
    m = folium.Map(
        location=[42.0707, -87.7368],
          zoom_start=10, 
          max_zoom=15,
          tiles="cartodbpositron")

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
        bookMarkControl.add_bookmark_sidebar(m, locations)

    print("Frequency heatmap generated and saved to", output_file)
    m.save(output_file)

def group_activities_by_type(activities):
    grouped = defaultdict(list)
    for act in activities:
        if not act.coordinates:
            continue
        grouped[act.activity_type].extend(act.coordinates)
    return grouped