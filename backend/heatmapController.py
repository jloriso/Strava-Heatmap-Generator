import folium
from folium.plugins import HeatMap
from collections import Counter, defaultdict
from controls import bookMarkControl
from controls import activityTypeControl

def build_frequency_map(activities, locations=None, output_file="heatmaps/standard_heatmap.html"):
    m = folium.Map(
        location=[42.0707, -87.7368],
          zoom_start=10, 
          max_zoom=15,
          tiles="cartodbpositron")

    grouped = group_activities_by_type(activities)
    activityTypeControl.add_activity_type_sidebar(m, grouped.keys())

    all_coords = []
    for act in grouped.values():
        if act:
            all_coords.extend(act)

    if all_coords:
        rounded = [(round(lat, 6), round(lon, 6)) for lat, lon in all_coords]
        freq = Counter(rounded)
        weighted_data = [[lat, lon, count] for (lat, lon), count in freq.items()]

        HeatMap(
            weighted_data, 
            radius=10, 
            blur=15, 
            max_zoom=15,
            min_opacity=0.4,
            gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 0.8: 'red'}
        ).add_to(m)

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