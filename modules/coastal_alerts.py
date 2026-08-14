# modules/coastal_alerts.py - Coastal / Tsunami / Flood Alert Module
import requests
from datetime import datetime

# GDACS (Global Disaster Alert and Coordination System) RSS Feed
GDACS_FEED = "https://www.gdacs.org/xml/rss.xml"

# Indian coastal tsunami-prone zones
TSUNAMI_ZONES = [
    {"name": "Andaman & Nicobar Islands", "lat": 11.7401, "lon": 92.6586, "risk": "VERY HIGH"},
    {"name": "Tamil Nadu Coast",           "lat": 11.1271, "lon": 78.6569, "risk": "HIGH"},
    {"name": "Andhra Pradesh Coast",       "lat": 15.9129, "lon": 79.7400, "risk": "HIGH"},
    {"name": "Odisha Coast",               "lat": 20.9517, "lon": 85.0985, "risk": "HIGH"},
    {"name": "Kerala Coast",               "lat": 10.8505, "lon": 76.2711, "risk": "MODERATE"},
    {"name": "Maharashtra Coast",          "lat": 19.7515, "lon": 75.7139, "risk": "MODERATE"},
    {"name": "Gujarat Coast",              "lat": 22.2587, "lon": 71.1924, "risk": "MODERATE"},
    {"name": "West Bengal Coast",          "lat": 22.9868, "lon": 87.8550, "risk": "HIGH"},
    {"name": "Karnataka Coast",            "lat": 15.3173, "lon": 75.7139, "risk": "LOW"},
    {"name": "Goa Coast",                  "lat": 15.2993, "lon": 74.1240, "risk": "LOW"},
]

# Major Indian flood-prone river systems
FLOOD_ZONES = [
    {"name": "Ganga Basin",       "states": ["Bihar", "UP", "Bengal"], "risk": "VERY HIGH"},
    {"name": "Brahmaputra Basin", "states": ["Assam", "Arunachal"],    "risk": "VERY HIGH"},
    {"name": "Godavari Basin",    "states": ["AP", "Telangana"],        "risk": "HIGH"},
    {"name": "Krishna Basin",     "states": ["AP", "Telangana", "Karnataka"], "risk": "HIGH"},
    {"name": "Mahanadi Basin",    "states": ["Odisha", "Chhattisgarh"],"risk": "HIGH"},
    {"name": "Cauvery Basin",     "states": ["Tamil Nadu", "Karnataka"],"risk": "MODERATE"},
    {"name": "Narmada Basin",     "states": ["MP", "Gujarat"],         "risk": "MODERATE"},
    {"name": "Tapi Basin",        "states": ["Gujarat", "Maharashtra"],"risk": "MODERATE"},
    {"name": "Damodar Basin",     "states": ["Jharkhand", "Bengal"],   "risk": "HIGH"},
    {"name": "Sabarmati Basin",   "states": ["Gujarat"],               "risk": "LOW"},
]

# Bay of Bengal Cyclone Season Months
CYCLONE_SEASONS = {
    "Bay of Bengal": [4, 5, 10, 11, 12],     # April-May, Oct-Dec
    "Arabian Sea":   [5, 6, 9, 10, 11],       # May-Jun, Sep-Nov
}

CYCLONE_CATEGORIES = {
    "CS":    {"label": "Cyclonic Storm",        "wind_min": 63,  "color": "#FFD700"},
    "SCS":   {"label": "Severe Cyclonic Storm", "wind_min": 89,  "color": "#FF8C00"},
    "VSCS":  {"label": "Very Severe",           "wind_min": 118, "color": "#FF4500"},
    "ESCS":  {"label": "Extremely Severe",      "wind_min": 167, "color": "#FF0000"},
    "SuCS":  {"label": "Super Cyclonic Storm",  "wind_min": 222, "color": "#8B0000"},
}


def get_cyclone_risk(wind_speed_kmh, month=None):
    """Classify cyclone risk based on wind speed and current month."""
    if month is None:
        month = datetime.now().month

    # Check if in cyclone season
    bay_season = month in CYCLONE_SEASONS["Bay of Bengal"]
    ara_season = month in CYCLONE_SEASONS["Arabian Sea"]
    season_active = bay_season or ara_season

    if wind_speed_kmh >= 222:
        return {"category": "SuCS", "label": "Super Cyclonic Storm", "color": "#8B0000", "risk": "EXTREME"}
    elif wind_speed_kmh >= 167:
        return {"category": "ESCS", "label": "Extremely Severe Cyclonic Storm", "color": "#FF0000", "risk": "EXTREME"}
    elif wind_speed_kmh >= 118:
        return {"category": "VSCS", "label": "Very Severe Cyclonic Storm", "color": "#FF4500", "risk": "VERY HIGH"}
    elif wind_speed_kmh >= 89:
        return {"category": "SCS", "label": "Severe Cyclonic Storm", "color": "#FF8C00", "risk": "HIGH"}
    elif wind_speed_kmh >= 63:
        return {"category": "CS", "label": "Cyclonic Storm", "color": "#FFD700", "risk": "MODERATE"}
    elif wind_speed_kmh >= 40 and season_active:
        return {"category": "DD", "label": "Deep Depression (Season Active)", "color": "#FFA500", "risk": "WATCH"}
    else:
        return {"category": "NONE", "label": "No Cyclone", "color": "#00C853", "risk": "LOW"}


def assess_tsunami_risk(weather_data, coastal_city):
    """
    Estimate tsunami risk based on seismic zone + weather conditions.
    (Real tsunami alerts come from INCOIS/PTWC — this provides risk assessment)
    """
    zone_name = coastal_city.get("name", "")
    base_risk = "LOW"

    for zone in TSUNAMI_ZONES:
        if any(w in zone_name for w in zone["name"].split()):
            base_risk = zone["risk"]
            break

    risk_map = {
        "VERY HIGH": {"color": "#FF0000", "score": 85, "label": "Tsunami Zone — High Alert"},
        "HIGH":      {"color": "#FF4500", "score": 65, "label": "Tsunami Prone — Monitor alerts"},
        "MODERATE":  {"color": "#FF8C00", "score": 45, "label": "Moderate Tsunami Risk"},
        "LOW":       {"color": "#00C853", "score": 15, "label": "Low Tsunami Risk"},
    }
    return risk_map.get(base_risk, risk_map["LOW"])


def assess_flood_risk_by_precipitation(daily_forecast):
    """
    Calculate flood risk from 15-day cumulative precipitation.
    """
    if not daily_forecast:
        return {"risk": "LOW", "color": "#00C853", "label": "No flood risk"}

    total_rain = sum(d.get("precipitation", 0) for d in daily_forecast)
    max_daily = max((d.get("precipitation", 0) for d in daily_forecast), default=0)
    heavy_days = sum(1 for d in daily_forecast if d.get("precipitation", 0) > 50)

    if max_daily > 150 or total_rain > 500 or heavy_days >= 5:
        return {
            "risk": "EXTREME",
            "color": "#FF0000",
            "label": "Extreme Flood Risk — Evacuate low-lying areas",
            "total_rain": total_rain,
            "max_daily": max_daily,
            "heavy_days": heavy_days,
        }
    elif max_daily > 80 or total_rain > 250 or heavy_days >= 3:
        return {
            "risk": "HIGH",
            "color": "#FF4500",
            "label": "High Flood Risk — Prepare for flooding",
            "total_rain": total_rain,
            "max_daily": max_daily,
            "heavy_days": heavy_days,
        }
    elif max_daily > 40 or total_rain > 100 or heavy_days >= 1:
        return {
            "risk": "MODERATE",
            "color": "#FF8C00",
            "label": "Moderate Flood Risk — Monitor water levels",
            "total_rain": total_rain,
            "max_daily": max_daily,
            "heavy_days": heavy_days,
        }
    else:
        return {
            "risk": "LOW",
            "color": "#00C853",
            "label": "Low Flood Risk — Normal conditions",
            "total_rain": total_rain,
            "max_daily": max_daily,
            "heavy_days": heavy_days,
        }


def generate_coastal_bulletin(city_info, weather_data, risk_data):
    """Generate a text coastal safety bulletin."""
    city = city_info.get("name", "Unknown City")
    coast = city_info.get("coast", "")
    month = datetime.now().month

    bulletin_lines = [
        f"=== COASTAL WEATHER BULLETIN — {city} ({coast} Coast) ===",
        f"Issued: {datetime.now().strftime('%d %B %Y, %H:%M IST')}",
        "",
    ]

    if risk_data:
        overall_risk = risk_data[0].get("risk", {}) if risk_data else {}
        bulletin_lines.append(f"OVERALL RISK: {overall_risk.get('emoji','')}{overall_risk.get('label','N/A')}")
        bulletin_lines.append("")

    # Cyclone season warning
    if month in CYCLONE_SEASONS.get("Bay of Bengal", []) and coast == "East":
        bulletin_lines.append("WARNING: BAY OF BENGAL CYCLONE SEASON ACTIVE")
        bulletin_lines.append("   Monitor IMD and NDMA advisories.")
    elif month in CYCLONE_SEASONS.get("Arabian Sea", []) and coast == "West":
        bulletin_lines.append("WARNING: ARABIAN SEA CYCLONE SEASON ACTIVE")
        bulletin_lines.append("   Monitor IMD and NDMA advisories.")

    bulletin_lines += [
        "",
        "SAFETY GUIDELINES:",
        "• Follow local authorities and Coast Guard advisories",
        "• Keep emergency contacts handy: NDRF: 011-24363260",
        "• Fishermen: Check IMD marine forecast before venturing out",
        "• Coastal residents: Know your nearest evacuation route",
    ]

    return "\n".join(bulletin_lines)


def get_disaster_alerts_summary():
    """
    Attempt to fetch live GDACS alerts (returns empty list on failure).
    This is a best-effort function — the app works without live alerts.
    """
    try:
        resp = requests.get(GDACS_FEED, timeout=8)
        if resp.status_code == 200:
            # Simple XML parsing for cyclone/tsunami/flood items
            content = resp.text
            alerts = []
            import re
            items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
            for item in items[:10]:
                title_m = re.search(r'<title>(.*?)</title>', item)
                desc_m  = re.search(r'<description>(.*?)</description>', item)
                if title_m:
                    title = title_m.group(1)
                    if any(k in title.upper() for k in ["CYCLONE", "TSUNAMI", "FLOOD", "EARTHQUAKE"]):
                        alerts.append({
                            "title": title,
                            "description": desc_m.group(1) if desc_m else "",
                        })
            return alerts
    except Exception:
        pass
    return []
