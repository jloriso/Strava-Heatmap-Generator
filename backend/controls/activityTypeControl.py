import folium
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "activityTypeAssets"

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

def add_activity_type_sidebar(m, activity_types):
    css = _read_text(ASSETS_DIR / "activityType.css")
    html = _read_text(ASSETS_DIR / "activityType.html")
    js = _read_text(ASSETS_DIR / "activityType.js")

    checkboxes = []
    for act_type in activity_types:
        checkboxes.append(f'''
        <label>
            <input type="checkbox" id="toggle-{act_type}" checked
                   onchange="document.dispatchEvent(new CustomEvent('activityCheckboxChanged', {{ detail: {{ type: '{act_type}', checked: this.checked }} }}))">
            {act_type}
        </label>
        ''')

    final_html = html.replace("<!--CHECKBOXES-->", ''.join(checkboxes))

    if css:
        m.get_root().header.add_child(folium.Element(f"<style>\n{css}\n</style>"))
    if js:
        m.get_root().html.add_child(folium.Element(f"<script>\n{js}\n</script>"))
    m.get_root().html.add_child(folium.Element(final_html))