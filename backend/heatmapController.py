import folium
from folium.plugins import HeatMap
from collections import Counter
from controls import bookMarkControl
from controls import activityTypeControl

def build_activity_map(
        activities,
        locations=None,
        output_file="heatmaps/standard_heatmap.html",
        precision=6
        ):

    counts = Counter()

    for act in activities:
        coords = getattr(act, 'coordinates', None)
        if not coords:
            continue
        for lat, lon in coords:
            rounded = (round(lat, precision), round(lon, precision))
            counts[rounded] += 1


    weighted_data = [[lat, lon, weight] for (lat, lon), weight in counts.items()]
    
    m = folium.Map(
        location=[42.0707, -87.7368],
        zoom_start=10, 
        max_zoom=15,
        tiles="cartodbpositron")

    HeatMap(
        weighted_data,
        radius=8,
        blur=10,
        max_zoom=15,
        min_opacity=0.3,
        gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 0.85: 'red'}
    ).add_to(m)


    if locations:
        bookMarkControl.add_bookmark_sidebar(m, locations)

    activityTypeControl.add_activity_type_sidebar(m, ['Run', 'Ride', 'Walk'])


    print("Frequency heatmap generated and saved to", output_file)
    m.save(output_file)