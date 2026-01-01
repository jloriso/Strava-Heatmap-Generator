function getFoliumMap() {
    return Object.values(window).find(v => v instanceof L.Map) || null;
}

function detachHeatLayers(map) {
    const store = [];

    map.eachLayer(function(layer) {
        if (layer instanceof L.HeatLayer) {
            store.push({ layer: layer, parent: map });
            map.removeLayer(layer);
        } else if (layer instanceof L.LayerGroup || layer instanceof L.FeatureGroup) {
            const toRemove = [];
            layer.eachLayer(function(child) {
                if (child instanceof L.HeatLayer) {
                    toRemove.push(child);
                }
                if (child && (child._heatmap || (child._baseLayer && child._baseLayer instanceof L.HeatLayer))) {
                    toRemove.push(child);
                }
            });
            toRemove.forEach(function(child) {
                store.push({ layer: child, parent: layer });
                layer.removeLayer(child);
            });
        }
    });

    return store;
}

function restoreHeatLayers(map, store) {
    store.forEach(function(entry) {
        const parent = entry.parent;
        if (parent && typeof parent.addLayer === 'function') {
            parent.addLayer(entry.layer);
        } else {
            map.addLayer(entry.layer);
        }
    });
}

function flyToLocation(lat, lon, zoom) {
    const map = getFoliumMap();
    if (!map) {
        console.error("Map object not found!");
        return;
    }

    const heatStore = detachHeatLayers(map);

    map.once('moveend', function() {
        restoreHeatLayers(map, heatStore);
    });

    map.flyTo([lat, lon], zoom);
}