import folium


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
        <h4>Locations</h4>
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