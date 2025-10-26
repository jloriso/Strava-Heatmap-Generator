import sqlite3

def save_activities_to_db(activities, db_path="data/activities.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for act in activities:
        c.execute("""
        INSERT OR IGNORE INTO activities (athleteid, activityid, name, start_date, time_zone, activity_type, distance, moving_time, polyline, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            act["athleteid"],
            act["activityid"],
            act["name"],
            act["start_date"],
            act["time_zone"],
            act["activity_type"],
            act["distance"],
            act["moving_time"],
            act["polyline"]
        ))

    conn.commit()
    conn.close()
    print(f"Saved {len(activities)} activities to database at {db_path}")

def load_activities_from_db(db_path="data/activities.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT athleteid, activityid, name, start_date, time_zone, activity_type, distance, moving_time, polyline, last_updated FROM activities")
    rows = c.fetchall()

    conn.close()
    activities = []
    for row in rows:
        activities.append({
            "athleteid": row[0],
            "activityid": row[1],
            "name": row[2],
            "start_date": row[3],
            "time_zone": row[4],
            "activity_type": row[5],
            "distance": row[6],
            "moving_time": row[7],
            "polyline": row[8],
            "last_updated": row[9]
        })
    print(f"Loaded {len(activities)} activities from database at {db_path}")
    return activities

def get_latest_activity_date(db_path="data/activities.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM activities")
    activity_count = c.fetchone()[0]
    if activity_count == 0:
        conn.close()
        return None
    c.execute("SELECT MAX(start_date) FROM activities")
    last_date = c.fetchone()[0]
    conn.close()
    return last_date