function getHeatMeta() {
  return window._activityHeat || null;
}

function getHeatLayer() {
  const meta = getHeatMeta();
  if (!meta || !meta.layerName || !window[meta.layerName]) return null;
  const layer = window[meta.layerName];
  return layer instanceof L.HeatLayer ? layer : null;
}

function checkedKeys() {
  return Array.from(document.querySelectorAll('input[type=checkbox][id^="toggle-"]:checked'))
    .map(cb => cb.id.replace('toggle-', '').toLowerCase());
}

function rebuildHeatFromFilters() {
  const meta = getHeatMeta();
  const layer = getHeatLayer();
  if (!meta || !meta.byType || !layer) return;

  const selected = checkedKeys();
  const merged = [];

  Object.entries(meta.byType).forEach(([activityType, points]) => {
    const typeKey = activityType.toLowerCase();
    const matches = selected.some(key => typeKey.includes(key) || key.includes(typeKey));
    if (matches) merged.push(...points);
  });

  layer.setLatLngs(merged);
  if (typeof layer.redraw === 'function') layer.redraw();
}

document.addEventListener('activityCheckboxChanged', function (e) {
  const { type, checked } = e.detail;
  if (window._activityCheckboxNotify) window._activityCheckboxNotify(type, checked);
  rebuildHeatFromFilters();
});

function initAllActivityCheckboxes() {
  document.querySelectorAll('input[type=checkbox][id^="toggle-"]').forEach(cb => {
    if (!cb.checked) cb.checked = true;
  });
  rebuildHeatFromFilters();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAllActivityCheckboxes);
} else {
  initAllActivityCheckboxes();
}