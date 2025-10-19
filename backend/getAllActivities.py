import requests
from dotenv import load_dotenv
import os
import json
import requests
from dataClasses.ActivityRoute import ActivityRoute
from datetime import datetime
import sqlite3
from dbManager import save_activities_to_db, load_activities_from_db
import heatmapController


#-------------------------
# 1. load environment variables
#-------------------------
load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
CODE = os.getenv("CODE")

#-------------------------
# 2. refresh access token
#-------------------------
def refresh_access_token():
    """Refresh the Strava access token using the refresh token."""
    url = "https://www.strava.com/oauth/token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("Error refreshing token:", pretty_print(response.text))
        return None

    tokens = response.json()
    print("Token refreshed\n")

    # Update the access token in memory
    global ACCESS_TOKEN
    ACCESS_TOKEN = tokens["access_token"]

    with open(".env", "w") as f:
        f.write(
            f"STRAVA_CLIENT_ID={CLIENT_ID}\n"
            f"STRAVA_CLIENT_SECRET={CLIENT_SECRET}\n"
            f"STRAVA_REFRESH_TOKEN={tokens['refresh_token']}\n"
            f"STRAVA_ACCESS_TOKEN={tokens['access_token']}\n"
            f"STRAVA_EXPIRES_AT={tokens['expires_at']}\n"
        )

    return tokens

def pretty_print(json_data):
    pretty_json = json.dumps(json_data, indent=4)
    print(pretty_json)

#-------------------------
# 3. get all activities
#-------------------------
def get_strava_activities():
    global ACCESS_TOKEN

    url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    page = 1
    per_page = 100
    activities = []
    #count = 0

    while True:
        
        param = {'per_page': per_page, 'page': page}
        res = requests.get(url, headers=header, params=param)

        if res.status_code == 401:
            print("Access token expired, refreshing...")
            refresh_access_token()
            header["Authorization"] = f"Bearer {ACCESS_TOKEN}"
            res = requests.get(url, headers=header)

        if res.status_code != 200:
            print("Error fetching club info:\n", pretty_print(res.json()))
            return

        data = res.json()
        if not data:
            break

        for activity in data:
            if "map" not in activity or "summary_polyline" not in activity["map"]:
                continue
            #count += 1

        activities.extend(data)
        page += 1

    print(f"Total activities fetched: {len(activities)}")
    return activities

#-------------------------
# 4. grab newest activites
# ------------------------
def get_newest_activites():
    conn = sqlite3.connect("activities.db")
    c = conn.cursor()
    c.execute("SELECT MAX(start_date) FROM activities")
    last_date = c.fetchone()[0]
    conn.close()

    after_ts = None
    if last_date:
        after_ts = int(datetime.fromisoformat(last_date).timestamp())

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    params = {'after': after_ts} if after_ts else {}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 401:
        print("Access token expired, refreshing...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        print("Error fetching activities:\n", pretty_print(res.json()))
        return

    new_activities = res.json()

    if new_activities:
        print(f"Fetched {len(new_activities)} activities from Strava")
        return new_activities
    else:
        print("No new activities found.")

def one_request():
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    params = {'per_page': 200, 'page': 1}

    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 401:
        print("Access token expired, refreshing...")
        refresh_access_token()
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
        res = requests.get(url, headers=headers, params=params)

    if res.status_code != 200:
        print("Error fetching activities:\n", pretty_print(res.json()))
        return

    activities = res.json()

    if activities:
        print(f"Fetched {len(activities)} activities from Strava")
        return activities
    else:
        print("No activities found.")

if __name__ == "__main__":
    
    #activites = get_strava_activities()
    # activites = one_request()

    # activites = get_newest_activites()

    # if activites:
    #     save_activities_to_db([{
    #         "id": activity.get("id"),
    #         "name": activity.get("name"),
    #         "start_date": activity.get("start_date"),
    #         "time_zone": activity.get("time_zone"),
    #         "activity_type": activity.get("activity_type"),
    #         "distance": activity.get("distance"),
    #         "moving_time": activity.get("moving_time"),
    #         "polyline": activity.get("map", {}).get("summary_polyline")
    #     } for activity in activites])

    dbModel = load_activities_from_db()

    routes = ActivityRoute.build_many_from_db(dbModel)

    heatmapController.build_frequency_map(routes).save("heatmaps/frequency_heatmap.html")
    heatmapController.make_heatmap(routes, output_file="heatmaps/standard_heatmap.html", show_routes=True)