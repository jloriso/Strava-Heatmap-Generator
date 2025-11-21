import json
import os
import requests
from dotenv import load_dotenv


CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
CODE = os.getenv("CODE")

def init_env():
    load_dotenv()
    global CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, ACCESS_TOKEN, CODE
    CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
    CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
    REFRESH_TOKEN = os.getenv("STRAVA_REFRESH_TOKEN")
    ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
    CODE = os.getenv("CODE")

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
            f"CODE={CODE}\n"
        )

    return tokens

def pretty_print(json_data):
    pretty_json = json.dumps(json_data, indent=4)
    print(pretty_json)

