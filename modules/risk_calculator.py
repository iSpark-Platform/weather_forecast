# modules/risk_calculator.py - Weather Risk Level Computation Engine
import math

def compute_risk_score(daily_data):
    """
    Compute a 0-100 risk score from daily weather data.
    Higher = more dangerous.
    """
    score = 0

    # WMO severity (0-7 scale -> 0-40 points)
    severity = daily_data.get("severity", 0)
    score += min(severity * 6, 40)

    # Precipitation (mm -> 0-20 points)
    precip = daily_data.get("precipitation", 0)
    if precip > 100:
        score += 20
    elif precip > 50:
        score += 15
    elif precip > 25:
        score += 10
    elif precip > 10:
        score += 5

    # Precipitation probability (% -> 0-10 points)
    precip_prob = daily_data.get("precip_prob", 0)
    score += int(precip_prob / 10)

    # Wind speed (km/h -> 0-20 points)
    wind = daily_data.get("wind_speed", 0)
    if wind > 120:
        score += 20   # Cyclone
    elif wind > 90:
        score += 17   # Severe storm
    elif wind > 60:
        score += 12   # Strong storm
    elif wind > 40:
        score += 7
    elif wind > 25:
        score += 3

    # UV Index (0-10 points)
    uv = daily_data.get("uv_index", 0)
    if uv > 11:
        score += 10
    elif uv > 8:
        score += 6
    elif uv > 5:
        score += 3

    return min(score, 100)


def score_to_risk(score):
    """Convert numeric score to risk level with refined UI labels."""
    if score >= 80:
        return {
            "level": "RED",
            "label": "DANGER",
            "subtitle": "Extreme Hazard",
            "color": "#FF2D2D",
            "bg": "rgba(255, 45, 45, 0.15)",
            "border": "#FF2D2D",
            "emoji": '<i class="fa-solid fa-triangle-exclamation" style="color:#FF2D2D"></i>',
            "description": "DANGER — Extreme Hazard! Stay indoors & follow emergency guidance.",
            "advisory": "Do not travel. Evacuate coastal/low-lying areas if advised."
        }
    elif score >= 55:
        return {
            "level": "ORANGE",
            "label": "WARNING",
            "subtitle": "Severe Weather",
            "color": "#FF8C00",
            "bg": "rgba(255, 140, 0, 0.15)",
            "border": "#FF8C00",
            "emoji": '<i class="fa-solid fa-circle-exclamation" style="color:#FF8C00"></i>',
            "description": "WARNING — Severe Weather! Hazardous conditions expected.",
            "advisory": "Avoid unnecessary travel. Monitor official weather alerts."
        }
    elif score >= 30:
        return {
            "level": "YELLOW",
            "label": "CAUTION",
            "subtitle": "Unsettled Conditions",
            "color": "#FFD700",
            "bg": "rgba(255, 215, 0, 0.15)",
            "border": "#FFD700",
            "emoji": '<i class="fa-solid fa-circle-info" style="color:#FFD700"></i>',
            "description": "CAUTION — Unsettled Conditions! Carry rain gear and plan carefully.",
            "advisory": "Plan travel carefully. Stay updated on local forecasts."
        }
    else:
        return {
            "level": "GREEN",
            "label": "SAFE",
            "subtitle": "Clear & Normal",
            "color": "#00C853",
            "bg": "rgba(0, 200, 83, 0.12)",
            "border": "#00C853",
            "emoji": '<i class="fa-solid fa-shield-halved" style="color:#00C853"></i>',
            "description": "SAFE — Clear & Normal weather. Enjoy favorable conditions!",
            "advisory": "Normal precautions apply. Have a great day!"
        }


def assess_daily_risks(daily_list):
    """Add risk level to each day in the forecast."""
    enriched = []
    for day in daily_list:
        score = compute_risk_score(day)
        risk = score_to_risk(score)
        enriched.append({**day, "risk_score": score, "risk": risk})
    return enriched


def assess_coastal_risk(weather_data, city_info):
    """
    Enhanced risk calculation for coastal cities,
    factoring in cyclone potential, storm surge, tsunami probability.
    """
    if not weather_data or not weather_data.get("daily"):
        return []

    daily = weather_data["daily"]
    results = []

    for day in daily:
        base_score = compute_risk_score(day)

        # Coastal amplifiers
        coastal_bonus = 0

        # High wind near coast → storm surge risk
        wind = day.get("wind_speed", 0)
        if wind > 80:
            coastal_bonus += 20   # Cyclone-level winds
        elif wind > 55:
            coastal_bonus += 12
        elif wind > 35:
            coastal_bonus += 5

        # Extreme precipitation → flash flood/coastal flood
        precip = day.get("precipitation", 0)
        if precip > 80:
            coastal_bonus += 15
        elif precip > 40:
            coastal_bonus += 8

        final_score = min(base_score + coastal_bonus, 100)
        risk = score_to_risk(final_score)

        # Determine specific alert types
        alerts = []
        if wind > 80 and precip > 50:
            alerts.append({"type": "CYCLONE", "icon": '<i class="fa-solid fa-tornado"></i>', "level": "RED"})
        elif wind > 60:
            alerts.append({"type": "STORM SURGE", "icon": '<i class="fa-solid fa-water"></i>', "level": "ORANGE"})
        if precip > 80:
            alerts.append({"type": "COASTAL FLOOD", "icon": '<i class="fa-solid fa-droplet"></i>', "level": "RED"})
        elif precip > 40:
            alerts.append({"type": "FLOOD RISK", "icon": '<i class="fa-solid fa-cloud-showers-heavy"></i>', "level": "ORANGE"})
        if day.get("severity", 0) >= 6:
            alerts.append({"type": "SEVERE STORM", "icon": '<i class="fa-solid fa-bolt-lightning"></i>', "level": "RED"})

        results.append({
            **day,
            "risk_score":    final_score,
            "risk":          risk,
            "coastal_bonus": coastal_bonus,
            "alerts":        alerts,
            "city":          city_info.get("name", ""),
            "coast":         city_info.get("coast", ""),
        })

    return results


def get_overall_region_risk(daily_risks):
    """Summarize the worst risk for the next 15 days."""
    if not daily_risks:
        return score_to_risk(0)
    max_score = max(d.get("risk_score", 0) for d in daily_risks)
    return score_to_risk(max_score)


def get_wind_direction_label(degrees):
    """Convert wind degrees to compass direction."""
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = round(degrees / 22.5) % 16
    return dirs[ix]


def get_uv_label(uv):
    if uv >= 11: return ("Extreme",  "#FF0000")
    if uv >= 8:  return ("Very High","#FF6B00")
    if uv >= 6:  return ("High",     "#FFD700")
    if uv >= 3:  return ("Moderate", "#00C853")
    return          ("Low",      "#00C853")


def get_humidity_label(h):
    if h >= 80: return "Very Humid"
    if h >= 60: return "Humid"
    if h >= 40: return "Comfortable"
    if h >= 20: return "Dry"
    return "Very Dry"
