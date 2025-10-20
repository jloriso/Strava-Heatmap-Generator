# Strava Heatmap Generator

A Python project that fetches your Strava activity data and generates interactive heatmaps visualizing where you've run, cycled, or exercised. The heatmaps highlight frequently visited routes and allow you to explore your activity patterns geographically.

## Features

- **Automated Data Fetching**: Pulls all your activities from Strava using the official API
- **SQLite Database**: Stores activity data locally for fast retrieval and offline use
- **Multiple Heatmap Types**:
  - **Standard Heatmap**: Weighted aggregation showing all locations you've visited
  - **Frequency Heatmap**: Groups activities by type (Run, Ride, etc.) with different colors
- **Interactive Maps**: Zoom, pan, and explore with Folium-powered Leaflet maps
- **Location Presets**: Quick navigation sidebar to jump to favorite locations

## Project Structure

```
StravaApi/
├── backend/
│   ├── dataClasses/
│   │   └── ActivityRoute.py       # Data model for activities
│   ├── buildDataBase.py            # Initial database setup
│   ├── dbManager.py                # Database operations (save/load)
│   ├── getAllActivities.py        # Strava API client
│   └── heatmapController.py       # Heatmap generation logic
├── heatmaps/                       # Generated HTML map files (gitignored)
├── data/                           # Placeholder for future data files
├── activities.db                   # SQLite database (gitignored)
├── .env                            # Environment variables (gitignored)
└── README.md
```

## Prerequisites

- Python 3.8 or higher
- A Strava account with activity data
- Git (to clone the repository)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/StravaApi.git
cd StravaApi
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install requests python-dotenv folium polyline
```

### 4. Get Strava API Credentials

1. Go to [Strava API Settings](https://www.strava.com/settings/api)
2. Create a new application (if you don't have one)
3. Note your **Client ID** and **Client Secret**
4. Set the **Authorization Callback Domain** to `localhost`

### 5. Obtain Authorization Code

Visit this URL in your browser (replace `YOUR_CLIENT_ID`):

```
https://www.strava.com/oauth/authorize?scope=read,activity:read_all,profile:read_all,read_all&client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost:8888/strava-call-back.php&approval_prompt=force

```

After authorizing, you'll be redirected to `localhost/?code=XXXXX`. Copy the `code` parameter from the URL.

### 6. Get Refresh Token

Use the authorization code to get your refresh token:

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=YOUR_AUTH_CODE \
  -d grant_type=authorization_code
```

The response will contain `access_token` and `refresh_token`.

### 7. Configure Environment Variables

Create a `.env` file in the project root:

```bash
touch .env
```

Add your credentials:

```env
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
STRAVA_ACCESS_TOKEN=your_access_token
CODE=your_auth_code
```

### 8. Create the Database

```bash
python backend/buildDataBase.py
```

### 9. Fetch Your Activities

```bash
python backend/getAllActivities.py
```

This will:
- Refresh your access token automatically
- Fetch all activities from Strava
- Store them in `activities.db`
- Generate heatmap
- When reran will check for new activites and update the heatmap accordingly

### 10. View Your Maps

Open the generated HTML files in your browser:

```bash
# On Linux/Mac
open heatmaps/standard_heatmap.html

# On Windows
start heatmaps/standard_heatmap.html
```

## Configuration Options

### Heatmap Parameters

- **precision** (default: 5): Decimal places for coordinate rounding
  - `3` ≈ 110m (city-scale)
  - `4` ≈ 11m (street-scale)
  - `5` ≈ 1.1m (fine trails)
- **radius** (default: 8): Heat blob size in pixels
- **blur** (default: 12): Smoothing intensity
- **max_zoom** (default: 12): Maximum zoom level where heat displays

### Location Presets

Add custom location shortcuts in `getAllActivities.py`:

```python
locations = {
    "USA": [38.0, -94.8, 5],
    "Chicago": [41.8, -87.8, 10],
    "Kalamazoo": [42.2, -85.6, 11],
    "World": [20.0, 0.0, 3]
}

heatmapController.build_frequency_map(routes, locations=locations, output_file="heatmaps/frequency_heatmap.html")
```

## Troubleshooting

### Import Errors

Ensure you're using the virtual environment:

```bash
source .venv/bin/activate
pip list  # Verify packages are installed
```

### API Rate Limits

Strava limits requests to 100 per 15 minutes and 1000 per day. The script handles pagination automatically but may take time for large activity counts.

### Missing Activities

Check that your `.env` file has the correct tokens and that `activity:read_all` scope was granted during authorization.

### Empty Heatmaps

Verify activities have GPS data (polylines). Indoor activities won't appear on maps.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [Strava API](https://developers.strava.com/) for activity data
- [Folium](https://python-visualization.github.io/folium/) for interactive maps
- [polyline](https://github.com/frederickjansen/polyline) for decoding Google polylines

---

**Note**: Never commit your `.env` file or `activities.db` to version control. They contain sensitive credentials and personal data.