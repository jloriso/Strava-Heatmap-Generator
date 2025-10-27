import folium

def add_activity_type_sidebar(m, activity_types):
    checkboxes = []
    for act_type in activity_types:
        checkboxes.append(f'''
        <label>
            <input type="checkbox" id="toggle-{act_type}" checked>
            {act_type}
        </label>
        ''')

    sidebar_html = f"""
    <style>
    .activity-filter {{
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 9999;
        background-color: white;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        min-width: 140px;
    }}
    .activity-filter h4 {{
        margin: 0 0 8px 0;
        font-size: 14px;
        text-align: center;
        border-bottom: 1px solid #ccc;
        padding-bottom: 6px;
    }}
    .activity-filter label {{
        display: block;
        margin: 6px 0;
        font-size: 13px;
        cursor: pointer;
        user-select: none;
    }}
    .activity-filter input[type="checkbox"] {{
        margin-right: 6px;
        cursor: pointer;
    }}
    </style>

    <div class="activity-filter">
        <h4>Activity Types</h4>
        {''.join(checkboxes)}
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(sidebar_html))