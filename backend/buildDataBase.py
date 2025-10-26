import sqlite3

def init_db(db_path="data/activities.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        athleteid INTEGER,
        activityid INTEGER PRIMARY KEY,
        name TEXT,
        start_date TEXT,
        time_zone TEXT,
        activity_type TEXT,
        distance REAL,
        moving_time INTEGER,
        polyline TEXT,
        last_updated TEXT
    )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

import sqlite3

def clear_activities_table(db_path="data/activities.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS activities")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()