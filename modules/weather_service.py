# modules/weather_service.py - Open-Meteo Weather Data Fetcher (robust version)
import requests
import requests_cache
from retry_requests import retry
from datetime import datetime, date, timedelta
import json

# Setup cached session for performance
cache_session = requests_cache.CachedSession('.cache', expire_after=1800)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL  = "https://geocoding-api.open-meteo.com/v1/search"

WMO_CODES = {
    0:   {"label": "Clear Sky",              "icon": "sunny",      "severity": 0},
    1:   {"label": "Mainly Clear",           "icon": "mostly_sunny","severity": 0},
    2:   {"label": "Partly Cloudy",          "icon": "partly_cloudy","severity": 0},
    3:   {"label": "Overcast",               "icon": "cloudy",     "severity": 1},
    45:  {"label": "Fog",                    "icon": "foggy",      "severity": 2},
    48:  {"label": "Rime Fog",               "icon": "foggy",      "severity": 2},
    51:  {"label": "Light Drizzle",          "icon": "drizzle",    "severity": 1},
    53:  {"label": "Moderate Drizzle",       "icon": "drizzle",    "severity": 2},
    55:  {"label": "Dense Drizzle",          "icon": "rain",       "severity": 2},
    61:  {"label": "Slight Rain",            "icon": "rain",       "severity": 2},
    63:  {"label": "Moderate Rain",          "icon": "rain",       "severity": 3},
    65:  {"label": "Heavy Rain",             "icon": "heavy_rain", "severity": 4},
    71:  {"label": "Slight Snowfall",        "icon": "snow",       "severity": 2},
    73:  {"label": "Moderate Snowfall",      "icon": "snow",       "severity": 3},
    75:  {"label": "Heavy Snowfall",         "icon": "heavy_snow", "severity": 4},
    77:  {"label": "Snow Grains",            "icon": "snow",       "severity": 2},
    80:  {"label": "Slight Rain Showers",    "icon": "showers",    "severity": 2},
    81:  {"label": "Moderate Rain Showers",  "icon": "showers",    "severity": 3},
    82:  {"label": "Violent Rain Showers",   "icon": "storm",      "severity": 5},
    85:  {"label": "Slight Snow Showers",    "icon": "snow",       "severity": 2},
    86:  {"label": "Heavy Snow Showers",     "icon": "heavy_snow", "severity": 4},
    95:  {"label": "Thunderstorm",           "icon": "thunder",    "severity": 5},
    96:  {"label": "Thunderstorm w/ Hail",   "icon": "thunder",    "severity": 6},
    99:  {"label": "Thunderstorm Heavy Hail","icon": "thunder",    "severity": 7},
}

WMO_ICON = {
    "sunny": '<i class="fa-solid fa-sun" style="color:#FFD700"></i>',
    "mostly_sunny": '<i class="fa-solid fa-cloud-sun" style="color:#FFD700"></i>',
    "partly_cloudy": '<i class="fa-solid fa-cloud-sun" style="color:#7dd3fc"></i>',
    "cloudy": '<i class="fa-solid fa-cloud" style="color:#cbd5e1"></i>',
    "foggy": '<i class="fa-solid fa-smog" style="color:#94a3b8"></i>',
    "drizzle": '<i class="fa-solid fa-cloud-rain" style="color:#38bdf8"></i>',
    "rain": '<i class="fa-solid fa-cloud-showers-heavy" style="color:#0284c7"></i>',
    "heavy_rain": '<i class="fa-solid fa-cloud-showers-water" style="color:#1d4ed8"></i>',
    "snow": '<i class="fa-solid fa-snowflake" style="color:#bae6fd"></i>',
    "heavy_snow": '<i class="fa-regular fa-snowflake" style="color:#e0f2fe"></i>',
    "showers": '<i class="fa-solid fa-cloud-sun-rain" style="color:#38bdf8"></i>',
    "storm": '<i class="fa-solid fa-cloud-bolt" style="color:#f59e0b"></i>',
    "thunder": '<i class="fa-solid fa-bolt-lightning" style="color:#ef4444"></i>',
}

def get_wmo(code):
    info = WMO_CODES.get(int(code) if code else 0, {"label": "Unknown", "icon": "cloudy", "severity": 0})
    return info["label"], WMO_ICON.get(info["icon"], '<i class="fa-solid fa-cloud"></i>'), info["severity"]

def safe_float(v, decimals=1):
    try:
        f = float(v)
        import math
        if math.isnan(f): return None
        return round(f, decimals)
    except:
        return None

def safe_int(v):
    try:
        import math
        f = float(v)
        if math.isnan(f): return 0
        return int(f)
    except:
        return 0

def geocode_city(city_name):
    """Convert city name to lat/lon using Open-Meteo geocoding."""
    try:
        resp = retry_session.get(GEOCODING_URL, params={
            "name": city_name, "count": 1, "language": "en", "format": "json"
        }, timeout=10)
        data = resp.json()
        if data.get("results"):
            r = data["results"][0]
            return {
                "name": r.get("name", city_name),
                "country": r.get("country", ""),
                "lat": r["latitude"],
                "lon": r["longitude"],
                "timezone": r.get("timezone", "auto"),
                "admin1": r.get("admin1", "")
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def fetch_weather(lat, lon, timezone="auto", forecast_days=15):
    """Fetch comprehensive 15-day forecast from Open-Meteo using raw requests."""
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_direction_10m,visibility,uv_index,surface_pressure,cloud_cover",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum",
            "timezone": timezone,
            "forecast_days": forecast_days,
            "wind_speed_unit": "kmh",
            "temperature_unit": "celsius",
            "precipitation_unit": "mm"
        }
        resp = retry_session.get(OPEN_METEO_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        # ── Parse Daily ──────────────────────────────────────────
        daily_raw = data.get("daily", {})
        daily_times = daily_raw.get("time", [])
        daily_list = []

        for i, dt_str in enumerate(daily_times):
            code = safe_int(daily_raw.get("weather_code", [0]*20)[i] if i < len(daily_raw.get("weather_code",[])) else 0)
            condition, icon, severity = get_wmo(code)

            # Parse sunrise/sunset (they come as ISO strings like "2026-08-05T06:12")
            sunrise_raw = daily_raw.get("sunrise", [None]*20)
            sunset_raw  = daily_raw.get("sunset",  [None]*20)
            sunrise_str = sunrise_raw[i] if i < len(sunrise_raw) else None
            sunset_str  = sunset_raw[i]  if i < len(sunset_raw)  else None

            def fmt_time(s):
                if not s: return "--:--"
                try: return s.split("T")[1][:5] if "T" in s else s[-5:]
                except: return "--:--"

            dt = datetime.strptime(dt_str, "%Y-%m-%d")

            def get_val(key, idx):
                arr = daily_raw.get(key, [])
                return arr[idx] if idx < len(arr) else None

            daily_list.append({
                "date":           dt_str,
                "day_name":       dt.strftime("%A"),
                "month_day":      dt.strftime("%b %d"),
                "weather_code":   code,
                "condition":      condition,
                "icon":           icon,
                "severity":       severity,
                "temp_max":       safe_float(get_val("temperature_2m_max", i)),
                "temp_min":       safe_float(get_val("temperature_2m_min", i)),
                "feels_like_max": safe_float(get_val("apparent_temperature_max", i)),
                "feels_like_min": safe_float(get_val("apparent_temperature_min", i)),
                "sunrise":        fmt_time(sunrise_str),
                "sunset":         fmt_time(sunset_str),
                "uv_index":       safe_float(get_val("uv_index_max", i)),
                "precipitation":  safe_float(get_val("precipitation_sum", i)),
                "precip_prob":    safe_int(get_val("precipitation_probability_max", i)),
                "wind_speed":     safe_float(get_val("wind_speed_10m_max", i)),
                "wind_direction": safe_int(get_val("wind_direction_10m_dominant", i)),
                "radiation":      safe_float(get_val("shortwave_radiation_sum", i)),
            })

        # ── Parse Hourly (next 48h) ──────────────────────────────
        hourly_raw = data.get("hourly", {})
        hourly_times = hourly_raw.get("time", [])
        hourly_list = []

        def get_h(key, idx):
            arr = hourly_raw.get(key, [])
            return arr[idx] if idx < len(arr) else None

        for i, th in enumerate(hourly_times[:48]):
            code = safe_int(get_h("weather_code", i) or 0)
            condition, icon, severity = get_wmo(code)
            vis_raw = get_h("visibility", i)
            hourly_list.append({
                "time":         th,
                "hour":         th.split("T")[1][:5] if "T" in th else th[-5:],
                "temperature":  safe_float(get_h("temperature_2m", i)),
                "humidity":     safe_int(get_h("relative_humidity_2m", i)),
                "precip_prob":  safe_int(get_h("precipitation_probability", i)),
                "precipitation":safe_float(get_h("precipitation", i), 2),
                "weather_code": code,
                "condition":    condition,
                "icon":         icon,
                "severity":     severity,
                "wind_speed":   safe_float(get_h("wind_speed_10m", i)),
                "wind_direction":safe_int(get_h("wind_direction_10m", i)),
                "visibility":   safe_float((vis_raw or 0) / 1000),
                "uv_index":     safe_float(get_h("uv_index", i)),
                "pressure":     safe_float(get_h("surface_pressure", i)),
                "cloud_cover":  safe_int(get_h("cloud_cover", i)),
            })

        current = hourly_list[0] if hourly_list else {}

        return {
            "current":   current,
            "daily":     daily_list,
            "hourly":    hourly_list,
            "lat":       data.get("latitude"),
            "lon":       data.get("longitude"),
            "timezone":  data.get("timezone"),
            "elevation": data.get("elevation"),
        }

    except Exception as e:
        print(f"Weather fetch error: {e}")
        import traceback; traceback.print_exc()
        return None


def get_weather_for_location(city_name):
    """Full pipeline: geocode + fetch weather."""
    geo = geocode_city(city_name)
    if not geo:
        return None, None
    weather = fetch_weather(geo["lat"], geo["lon"], geo.get("timezone", "auto"))
    return geo, weather


def get_weather_by_coords(lat, lon):
    """Fetch weather directly by coordinates."""
    return fetch_weather(lat, lon)
