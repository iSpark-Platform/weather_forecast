# config.py - WeatherSense AI Configuration
import os

# --- API Keys (optional — app works without them) ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Optional: for enhanced AI tutor
OPENWEATHERMAP_API_KEY = os.getenv("OWM_API_KEY", "")  # Optional

# --- Open-Meteo (Free, No Key Needed) ---
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

# --- App Settings ---
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "weathersense-ai-2026-secret")
DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
PORT = int(os.getenv("PORT", 5000))

# --- Forecast Settings ---
FORECAST_DAYS = 15

# --- Risk Thresholds ---
RISK_LEVELS = {
    "RED":    {"label": "DANGER",   "color": "#FF2D2D", "min_score": 80},
    "ORANGE": {"label": "WARNING",  "color": "#FF8C00", "min_score": 55},
    "YELLOW": {"label": "CAUTION",  "color": "#FFD700", "min_score": 30},
    "GREEN":  {"label": "SAFE",     "color": "#00C853", "min_score": 0},
}

# --- Indian Coastal Cities for Alert Monitoring ---
COASTAL_CITIES = [
    {"name": "Mumbai",      "lat": 19.0760, "lon": 72.8777, "coast": "West"},
    {"name": "Chennai",     "lat": 13.0827, "lon": 80.2707, "coast": "East"},
    {"name": "Kolkata",     "lat": 22.5726, "lon": 88.3639, "coast": "East"},
    {"name": "Visakhapatnam","lat":17.6868, "lon": 83.2185, "coast": "East"},
    {"name": "Kochi",       "lat": 9.9312,  "lon": 76.2673, "coast": "West"},
    {"name": "Goa (Panaji)","lat": 15.4909, "lon": 73.8278, "coast": "West"},
    {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "coast": "East"},
    {"name": "Mangalore",   "lat": 12.9141, "lon": 74.8560, "coast": "West"},
    {"name": "Thiruvananthapuram","lat":8.5241,"lon":76.9366,"coast":"West"},
    {"name": "Pondicherry", "lat": 11.9416, "lon": 79.8083, "coast": "East"},
    {"name": "Surat",       "lat": 21.1702, "lon": 72.8311, "coast": "West"},
    {"name": "Puri",        "lat": 19.8135, "lon": 85.8312, "coast": "East"},
    {"name": "Port Blair",  "lat": 11.6234, "lon": 92.7265, "coast": "Island"},
    {"name": "Dwarka",      "lat": 22.2394, "lon": 68.9678, "coast": "West"},
    {"name": "Rameswaram",  "lat": 9.2876,  "lon": 79.3129, "coast": "East"},
]

# --- World Major Cities ---
WORLD_CITIES = [
    {"name": "Tokyo",       "lat": 35.6762, "lon": 139.6503, "country": "Japan"},
    {"name": "New York",    "lat": 40.7128, "lon": -74.0060,  "country": "USA"},
    {"name": "London",      "lat": 51.5074, "lon": -0.1278,   "country": "UK"},
    {"name": "Paris",       "lat": 48.8566, "lon": 2.3522,    "country": "France"},
    {"name": "Dubai",       "lat": 25.2048, "lon": 55.2708,   "country": "UAE"},
    {"name": "Singapore",   "lat": 1.3521,  "lon": 103.8198,  "country": "Singapore"},
    {"name": "Sydney",      "lat": -33.8688,"lon": 151.2093,  "country": "Australia"},
    {"name": "Beijing",     "lat": 39.9042, "lon": 116.4074,  "country": "China"},
    {"name": "Moscow",      "lat": 55.7558, "lon": 37.6176,   "country": "Russia"},
    {"name": "Cairo",       "lat": 30.0444, "lon": 31.2357,   "country": "Egypt"},
    {"name": "São Paulo",   "lat": -23.5505,"lon": -46.6333,  "country": "Brazil"},
    {"name": "Dhaka",       "lat": 23.8103, "lon": 90.4125,   "country": "Bangladesh"},
    {"name": "Bangkok",     "lat": 13.7563, "lon": 100.5018,  "country": "Thailand"},
    {"name": "Jakarta",     "lat": -6.2088, "lon": 106.8456,  "country": "Indonesia"},
    {"name": "Istanbul",    "lat": 41.0082, "lon": 28.9784,   "country": "Turkey"},
]

# --- Supported Languages ---
SUPPORTED_LANGUAGES = {
    # Indian Languages
    "hi": "हिंदी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
    "bn": "বাংলা (Bengali)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)",
    "or": "ଓଡ଼ିଆ (Odia)",
    "as": "অসমীয়া (Assamese)",
    "ur": "اردو (Urdu)",
    "sa": "संस्कृत (Sanskrit)",
    # Non-Indian Languages
    "en": "English",
    "fr": "Français (French)",
    "es": "Español (Spanish)",
    "de": "Deutsch (German)",
    "ja": "日本語 (Japanese)",
    "zh-cn": "中文 (Chinese)",
    "ar": "العربية (Arabic)",
    "pt": "Português (Portuguese)",
    "ru": "Русский (Russian)",
    "ko": "한국어 (Korean)",
    "it": "Italiano (Italian)",
    "nl": "Nederlands (Dutch)",
}
