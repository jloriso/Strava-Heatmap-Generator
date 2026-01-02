import folium
from folium.plugins import HeatMap
from collections import Counter, defaultdict
from controls import bookMarkControl
from controls import activityTypeControl
import json

def build_activity_map(
        activities,
        locations=None,
        output_file="heatmaps/standard_heatmap.html",
        precision=6
        ):

    counts = Counter()
    counts_by_type = defaultdict(Counter)

    for act in activities:
        coords = getattr(act, 'coordinates', None)
        if not coords:
            continue
        act_type = (getattr(act, "activity_type", "") or "").strip()
        for lat, lon in coords:
            rounded = (round(lat, precision), round(lon, precision))
            counts[rounded] += 1
            counts_by_type[act_type][rounded] += 1

    weighted_data = [[lat, lon, w] for (lat, lon), w in counts.items()]
    weighted_by_type = {
        act_type: [[lat, lon, w] for (lat, lon), w in ctr.items()]
        for act_type, ctr in counts_by_type.items()
    }

    m = folium.Map(
        location=[42.0707, -87.7368],
        zoom_start=10, 
        max_zoom=15,
        tiles="cartodbpositron")

    heat_layer = HeatMap(
        weighted_data,
        radius=8,
        blur=10,
        max_zoom=15,
        min_opacity=0.3,
        gradient={0.2: "blue", 0.4: "lime", 0.6: "orange", 0.85: "red"},
    ).add_to(m)

    payload = {
        "byType": weighted_by_type,
        "layerName": heat_layer.get_name(),
    }
    m.get_root().html.add_child(folium.Element(f"<script>window._activityHeat = {json.dumps(payload)};</script>"))


    if locations:
        bookMarkControl.add_bookmark_sidebar(m, locations)

    activityTypeControl.add_activity_type_sidebar(m, ['Run', 'Ride', 'Walk'])


    print("Frequency heatmap generated and saved to", output_file)
    m.save(output_file)