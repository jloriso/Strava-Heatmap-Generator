import folium
import json
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "bookmarkAssets"

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def add_bookmark_sidebar(m, locations, mapType):
    css = _read_text(ASSETS_DIR / "bookmark.css")
    html = _read_text(ASSETS_DIR / "bookmark.html")
    js = _read_text(ASSETS_DIR / "bookmark.js")
    map_type_js = json.dumps(mapType)

    buttons_html = ""
    for name, (lat, lon, zoom) in locations.items():
        buttons_html += f'<button onclick="flyToLocation({lat}, {lon}, {zoom}, {map_type_js})">{name}</button>'

    final_html = html.replace("<!--BUTTONS-->", buttons_html)

    if css:
        m.get_root().header.add_child(folium.Element(f"<style>\n{css}\n</style>"))
    m.get_root().html.add_child(folium.Element(final_html))
    if js:
        m.get_root().html.add_child(folium.Element(f"<script>\n{js}\n</script>"))