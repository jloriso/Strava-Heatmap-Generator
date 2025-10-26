import datetime
import json
import requests
import dbManager
from environmentManager import ACCESS_TOKEN, refresh_access_token


def get_strava_activities():
    global ACCESS_TOKEN

    url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

    page = 1
    per_page = 100
    activities = []

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

        activities.extend(data)
        page += 1

    print(f"Total activities fetched: {len(activities)}")
    return activities

def get_newest_activites():
    after_ts = dbManager.get_latest_activity_date()

    if after_ts is None:
        return get_strava_activities()

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

def pretty_print(json_data):
    pretty_json = json.dumps(json_data, indent=4)
    print(pretty_json)