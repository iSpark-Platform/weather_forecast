# app.py - WeatherSense AI — Flask Application Main Entry
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
import threading
from datetime import datetime

from config import (
    FLASK_SECRET_KEY, DEBUG, PORT, FORECAST_DAYS,
    COASTAL_CITIES, WORLD_CITIES, SUPPORTED_LANGUAGES
)
from modules.weather_service import get_weather_for_location, get_weather_by_coords, fetch_weather
from modules.risk_calculator import assess_daily_risks, assess_coastal_risk, get_overall_region_risk
from modules.coastal_alerts import (
    assess_flood_risk_by_precipitation, assess_tsunami_risk,
    get_cyclone_risk, get_disaster_alerts_summary, generate_coastal_bulletin, TSUNAMI_ZONES
)
from modules.ai_tutor import process_question, get_greeting
from modules.map_data import fetch_map_data_india, fetch_map_data_world

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
CORS(app)

# ── In-memory cache for expensive map data ─────────────────────────────────
_map_cache = {"india": None, "world": None, "timestamp": None}
_cache_lock = threading.Lock()

CACHE_TTL = 1800  # 30 minutes


def _cache_is_fresh():
    if not _map_cache["timestamp"]:
        return False
    age = (datetime.now() - _map_cache["timestamp"]).seconds
    return age < CACHE_TTL


# ── Routes ─────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main master dashboard page."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="dashboard",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/hourly")
def hourly_page():
    """48-hour hourly weather detail view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="hourly",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/analytics")
@app.route("/charts")
def analytics_page():
    """Weather trends and interactive analytics view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="analytics",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/forecast")
def forecast_page():
    """15-day forecast view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="forecast",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/coastal")
def coastal_page():
    """Coastal alerts and risk view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="coastal",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/map")
def map_page():
    """Interactive risk map view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="map",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/tutor")
def tutor_page():
    """Multilingual AI weather tutor view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="tutor",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/survival")
@app.route("/lingo")
def survival_page():
    """LingoSurvive country survival simulator & micro-learning view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="survival",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


@app.route("/decoder")
@app.route("/puzzles")
def decoder_page():
    """Emergency signboard decoder and weather puzzles view."""
    city = request.args.get("city", "Mumbai")
    return render_template("index.html",
                           active_tab="decoder",
                           city=city,
                           languages=SUPPORTED_LANGUAGES,
                           coastal_cities=COASTAL_CITIES,
                           tsunami_zones=TSUNAMI_ZONES)


# ── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/weather", methods=["GET"])
def api_weather():
    """Get weather for a city by name."""
    city = request.args.get("city", "Mumbai")
    try:
        geo, weather = get_weather_for_location(city)
        if not weather:
            return jsonify({"error": f"Could not fetch weather for '{city}'"}), 404

        daily_with_risk = assess_daily_risks(weather["daily"])
        overall_risk = get_overall_region_risk(daily_with_risk)
        flood_risk = assess_flood_risk_by_precipitation(weather["daily"])

        return jsonify({
            "location":     geo,
            "current":      weather["current"],
            "daily":        daily_with_risk,
            "hourly":       weather["hourly"],
            "overall_risk": overall_risk,
            "flood_risk":   flood_risk,
            "elevation":    weather.get("elevation"),
            "timezone":     weather.get("timezone"),
            "fetched_at":   datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/weather/coords", methods=["GET"])
def api_weather_coords():
    """Get weather by latitude/longitude."""
    try:
        lat = float(request.args.get("lat", 19.076))
        lon = float(request.args.get("lon", 72.877))
        weather = get_weather_by_coords(lat, lon)
        if not weather:
            return jsonify({"error": "Could not fetch weather"}), 404

        daily_with_risk = assess_daily_risks(weather["daily"])
        return jsonify({
            "current": weather["current"],
            "daily":   daily_with_risk,
            "hourly":  weather["hourly"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/coastal", methods=["GET"])
def api_coastal():
    """Get coastal weather and risk for a specific city."""
    city_name = request.args.get("city", "Mumbai")
    city_info = next(
        (c for c in COASTAL_CITIES if c["name"].lower() == city_name.lower()),
        COASTAL_CITIES[0]
    )
    try:
        weather = fetch_weather(city_info["lat"], city_info["lon"])
        if not weather:
            return jsonify({"error": "Weather data unavailable"}), 404

        coastal_risks = assess_coastal_risk(weather, city_info)
        flood_risk = assess_flood_risk_by_precipitation(weather["daily"])
        tsunami_risk = assess_tsunami_risk(weather, city_info)
        overall_risk = get_overall_region_risk(coastal_risks)
        bulletin = generate_coastal_bulletin(city_info, weather, coastal_risks)

        # Cyclone risk from max wind in forecast
        max_wind = max((d.get("wind_speed", 0) for d in weather["daily"]), default=0)
        cyclone_risk = get_cyclone_risk(max_wind)

        # Live disaster alerts (best-effort)
        live_alerts = get_disaster_alerts_summary()

        return jsonify({
            "city":          city_info,
            "current":       weather["current"],
            "daily":         coastal_risks,
            "flood_risk":    flood_risk,
            "tsunami_risk":  tsunami_risk,
            "cyclone_risk":  cyclone_risk,
            "overall_risk":  overall_risk,
            "bulletin":      bulletin,
            "live_alerts":   live_alerts[:5],
            "fetched_at":    datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/map/india", methods=["GET"])
def api_map_india():
    """Get color-coded risk data for all Indian states."""
    with _cache_lock:
        if _map_cache["india"] and _cache_is_fresh():
            return jsonify({"states": _map_cache["india"], "cached": True})

    try:
        data = fetch_map_data_india()
        with _cache_lock:
            _map_cache["india"] = data
            _map_cache["timestamp"] = datetime.now()
        return jsonify({"states": data, "cached": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/map/world", methods=["GET"])
def api_map_world():
    """Get color-coded risk data for world cities."""
    with _cache_lock:
        if _map_cache["world"] and _cache_is_fresh():
            return jsonify({"cities": _map_cache["world"], "cached": True})

    try:
        data = fetch_map_data_world()
        with _cache_lock:
            _map_cache["world"] = data
            _map_cache["timestamp"] = datetime.now()
        return jsonify({"cities": data, "cached": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tutor", methods=["POST"])
def api_tutor():
    """Multilingual AI tutor endpoint."""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        lang = data.get("lang", "en")
        city = data.get("city", "")
        weather_context = ""

        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Get current weather context if city is provided
        if city:
            try:
                geo, weather = get_weather_for_location(city)
                if weather and weather.get("current"):
                    c = weather["current"]
                    weather_context = (
                        f"Current weather in {city}: {c.get('condition','')}, "
                        f"Temp: {c.get('temperature','')}°C, "
                        f"Wind: {c.get('wind_speed','')} km/h, "
                        f"Humidity: {c.get('humidity','')}%, "
                        f"Precipitation probability: {c.get('precip_prob','')}%"
                    )
            except Exception:
                pass

        result = process_question(question, lang=lang, weather_context=weather_context)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/tutor/greeting", methods=["GET"])
def api_tutor_greeting():
    """Get greeting in specified language."""
    lang = request.args.get("lang", "en")
    return jsonify({"greeting": get_greeting(lang), "lang": lang})


@app.route("/api/cities/coastal", methods=["GET"])
def api_coastal_cities():
    """Return list of monitored coastal cities."""
    return jsonify({"cities": COASTAL_CITIES})


@app.route("/api/languages", methods=["GET"])
def api_languages():
    """Return supported languages."""
    return jsonify({"languages": SUPPORTED_LANGUAGES})


@app.route("/api/alerts/live", methods=["GET"])
def api_live_alerts():
    """Get live disaster alerts from GDACS."""
    alerts = get_disaster_alerts_summary()
    return jsonify({"alerts": alerts, "count": len(alerts)})


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None
    print("=" * 55)
    print("   WeatherSense AI -- Starting Server")
    print("   Open http://localhost:5000 in your browser")
    print("=" * 55)
    app.run(debug=DEBUG, port=PORT, host="0.0.0.0")
