# modules/map_data.py - GeoJSON Map Data Helper
# Provides color-coded risk data for India state and world country maps

import json
from config import COASTAL_CITIES, WORLD_CITIES
from modules.weather_service import fetch_weather
from modules.risk_calculator import compute_risk_score, score_to_risk, assess_daily_risks

from modules.india_geojson import INDIA_STATES_GEOJSON

# Indian States with approximate centroids for map markers
INDIA_STATES = [
    {"name": "Andhra Pradesh",    "lat": 15.9129, "lon": 79.7400, "coastal": True},
    {"name": "Arunachal Pradesh", "lat": 28.2180, "lon": 94.7278, "coastal": False},
    {"name": "Assam",             "lat": 26.2006, "lon": 92.9376, "coastal": False},
    {"name": "Bihar",             "lat": 25.0961, "lon": 85.3131, "coastal": False},
    {"name": "Chhattisgarh",      "lat": 21.2787, "lon": 81.8661, "coastal": False},
    {"name": "Goa",               "lat": 15.2993, "lon": 74.1240, "coastal": True},
    {"name": "Gujarat",           "lat": 22.2587, "lon": 71.1924, "coastal": True},
    {"name": "Haryana",           "lat": 29.0588, "lon": 76.0856, "coastal": False},
    {"name": "Himachal Pradesh",  "lat": 31.1048, "lon": 77.1734, "coastal": False},
    {"name": "Jharkhand",         "lat": 23.6102, "lon": 85.2799, "coastal": False},
    {"name": "Karnataka",         "lat": 15.3173, "lon": 75.7139, "coastal": True},
    {"name": "Kerala",            "lat": 10.8505, "lon": 76.2711, "coastal": True},
    {"name": "Madhya Pradesh",    "lat": 22.9734, "lon": 78.6569, "coastal": False},
    {"name": "Maharashtra",       "lat": 19.7515, "lon": 75.7139, "coastal": True},
    {"name": "Manipur",           "lat": 24.6637, "lon": 93.9063, "coastal": False},
    {"name": "Meghalaya",         "lat": 25.4670, "lon": 91.3662, "coastal": False},
    {"name": "Mizoram",           "lat": 23.1645, "lon": 92.9376, "coastal": False},
    {"name": "Nagaland",          "lat": 26.1584, "lon": 94.5624, "coastal": False},
    {"name": "Odisha",            "lat": 20.9517, "lon": 85.0985, "coastal": True},
    {"name": "Punjab",            "lat": 31.1471, "lon": 75.3412, "coastal": False},
    {"name": "Rajasthan",         "lat": 27.0238, "lon": 74.2179, "coastal": False},
    {"name": "Sikkim",            "lat": 27.5330, "lon": 88.5122, "coastal": False},
    {"name": "Tamil Nadu",        "lat": 11.1271, "lon": 78.6569, "coastal": True},
    {"name": "Telangana",         "lat": 18.1124, "lon": 79.0193, "coastal": False},
    {"name": "Tripura",           "lat": 23.9408, "lon": 91.9882, "coastal": False},
    {"name": "Uttar Pradesh",     "lat": 26.8467, "lon": 80.9462, "coastal": False},
    {"name": "Uttarakhand",       "lat": 30.0668, "lon": 79.0193, "coastal": False},
    {"name": "West Bengal",       "lat": 22.9868, "lon": 87.8550, "coastal": True},
    {"name": "Delhi",             "lat": 28.7041, "lon": 77.1025, "coastal": False},
    {"name": "Jammu & Kashmir",   "lat": 33.7782, "lon": 76.5762, "coastal": False},
    {"name": "Ladakh",            "lat": 34.1526, "lon": 77.5770, "coastal": False},
    {"name": "Andaman & Nicobar", "lat": 11.7401, "lon": 92.6586, "coastal": True},
    {"name": "Lakshadweep",       "lat": 10.5667, "lon": 72.6417, "coastal": True},
    {"name": "Puducherry",        "lat": 11.9416, "lon": 79.8083, "coastal": True},
]


import time

def _process_state(state, geo_lookup):
    try:
        time.sleep(0.03)
        weather = fetch_weather(state["lat"], state["lon"], forecast_days=3)
        if weather and weather.get("daily"):
            score = compute_risk_score(weather["daily"][0])
            risk = score_to_risk(score)
            today = weather["daily"][0]
            state_data = {
                "name":       state["name"],
                "lat":        state["lat"],
                "lon":        state["lon"],
                "coastal":    state["coastal"],
                "risk_score": score,
                "risk_level": risk["level"],
                "risk_label": risk["label"],
                "risk_color": risk["color"],
                "risk_emoji": risk["emoji"],
                "temp_max":   today.get("temp_max", "--"),
                "temp_min":   today.get("temp_min", "--"),
                "condition":  today.get("condition", "Unknown"),
                "icon":       today.get("icon", "❓"),
                "wind":       today.get("wind_speed", 0),
                "rain":       today.get("precipitation", 0),
                "precip_prob":today.get("precip_prob", 0),
                "description": risk["description"],
                "advisory":   risk["advisory"],
            }
            feat = None
            if state["name"] in geo_lookup:
                feat = json.loads(json.dumps(geo_lookup[state["name"]]))
                feat["properties"].update(state_data)
            return state_data, feat
    except Exception as e:
        print(f"Map data error for {state['name']}: {e}")
    
    fallback = _fallback_state(state)
    feat = None
    if state["name"] in geo_lookup:
        feat = json.loads(json.dumps(geo_lookup[state["name"]]))
        feat["properties"].update(fallback)
    return fallback, feat


def fetch_map_data_india():
    """Fetch weather risk for all Indian states in parallel and return map-ready JSON with GeoJSON features."""
    geo_lookup = {feat["properties"]["name"]: feat for feat in INDIA_STATES_GEOJSON["features"]}
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(_process_state, state, geo_lookup) for state in INDIA_STATES]
        results_tuples = [f.result() for f in futures]

    results = [r[0] for r in results_tuples if r[0]]
    geojson_features = [r[1] for r in results_tuples if r[1]]

    geojson_collection = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    
    return {
        "states": results,
        "geojson": geojson_collection
    }


def _process_world_city(city):
    try:
        weather = fetch_weather(city["lat"], city["lon"], forecast_days=3)
        if weather and weather.get("daily"):
            score = compute_risk_score(weather["daily"][0])
            risk = score_to_risk(score)
            today = weather["daily"][0]
            return {
                "name":       city["name"],
                "country":    city["country"],
                "lat":        city["lat"],
                "lon":        city["lon"],
                "risk_score": score,
                "risk_level": risk["level"],
                "risk_label": risk["label"],
                "risk_color": risk["color"],
                "risk_emoji": risk["emoji"],
                "temp_max":   today.get("temp_max", "--"),
                "temp_min":   today.get("temp_min", "--"),
                "condition":  today.get("condition", "Unknown"),
                "icon":       today.get("icon", "❓"),
                "wind":       today.get("wind_speed", 0),
                "rain":       today.get("precipitation", 0),
                "description": risk["description"],
            }
    except Exception as e:
        print(f"World map error for {city['name']}: {e}")
    return _fallback_world(city)


def fetch_map_data_world():
    """Fetch weather risk for world major cities in parallel."""
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(_process_world_city, WORLD_CITIES))
    return results


def _fallback_state(state):
    return {
        "name": state["name"], "lat": state["lat"], "lon": state["lon"],
        "coastal": state["coastal"], "risk_score": 0, "risk_level": "GREEN",
        "risk_label": "SAFE", "risk_color": "#00C853", "risk_emoji": '<i class="fa-solid fa-shield-halved" style="color:#00C853"></i>',
        "temp_max": "--", "temp_min": "--", "condition": "Unknown",
        "icon": '<i class="fa-solid fa-cloud"></i>', "wind": 0, "rain": 0, "precip_prob": 0,
        "description": "Data unavailable", "advisory": "Check local sources",
    }

def _fallback_world(city):
    return {
        "name": city["name"], "country": city["country"],
        "lat": city["lat"], "lon": city["lon"],
        "risk_score": 0, "risk_level": "GREEN", "risk_label": "SAFE",
        "risk_color": "#00C853", "risk_emoji": '<i class="fa-solid fa-shield-halved" style="color:#00C853"></i>',
        "temp_max": "--", "temp_min": "--", "condition": "Unknown",
        "icon": '<i class="fa-solid fa-cloud"></i>', "wind": 0, "rain": 0, "description": "Data unavailable",
    }
