# modules/ai_tutor.py - Multilingual Weather AI Tutor
import json
import os
import re
from deep_translator import GoogleTranslator

# Try importing Gemini (optional — works without it)
GEMINI_AVAILABLE = False
try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
except ImportError:
    pass


# ─────────────────────────────────────────────────────────────────────────────
# KNOWLEDGE BASE — Comprehensive weather Q&A in English
# ─────────────────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "tsunami": {
        "keywords": ["tsunami", "tidal wave", "seismic wave", "soo nami"],
        "answer": """**Tsunami Information:**
A tsunami is a series of large ocean waves caused by underwater earthquakes, volcanic eruptions, or landslides.

**Warning Signs:**
• Strong earthquake near the coast
• Ocean suddenly recedes (sea pulls back)
• Loud roaring sound from the ocean

**Safety Rules:**
• Move to high ground immediately (at least 30 meters above sea level)
• Do NOT go to the beach to watch — this is fatal!
• Follow official evacuation routes
• Await official all-clear before returning

**India Tsunami Alert System:** INCOIS (Indian National Centre for Ocean Information Services) issues tsunami warnings. Call: 040-23895011

**High Risk Zones in India:** Andaman & Nicobar Islands, Tamil Nadu coast, Andhra Pradesh coast"""
    },
    "cyclone": {
        "keywords": ["cyclone", "hurricane", "typhoon", "tropical storm", "storm"],
        "answer": """**Cyclone Information:**
A cyclone is a rapidly rotating storm system with low pressure at its center, bringing strong winds and heavy rain.

**Indian Cyclone Categories (IMD Scale):**
• Cyclonic Storm: 63-88 km/h winds
• Severe Cyclonic Storm: 89-117 km/h
• Very Severe: 118-167 km/h
• Extremely Severe: 168-221 km/h
• Super Cyclonic Storm: 222+ km/h

**Bay of Bengal Season:** April-May, October-December
**Arabian Sea Season:** May-June, September-November

**Before a Cyclone:**
• Stock 3-day emergency supplies
• Secure or store outdoor items
• Know your evacuation route
• Keep phone charged

**Emergency Numbers:**
• NDRF: 011-24363260
• Coast Guard: 1554
• Disaster Helpline: 1078"""
    },
    "flood": {
        "keywords": ["flood", "flooding", "inundation", "waterlogging", "flash flood", "deluge"],
        "answer": """**Flood Safety Information:**
Floods occur when water overflows onto normally dry land. India's major flood-prone regions include the Ganga, Brahmaputra, Godavari, and Krishna basins.

**Types of Floods:**
• **Flash Floods:** Sudden, occur within 6 hours of heavy rain
• **River Floods:** Gradual rise in river water levels
• **Coastal Floods:** Storm surge from cyclones
• **Urban Floods:** Poor drainage in cities

**Safety Guidelines:**
• Never walk or drive through floodwater (15cm can knock you down, 30cm can move a car)
• Move to higher ground before flooding begins
• Disconnect electrical appliances
• Keep important documents in waterproof bags
• Do NOT drink floodwater

**Warning Signs:**
• Very heavy continuous rain
• Rivers rising rapidly
• Unusual water flow in streets

**Helplines:**
• NDRF Flood Rescue: 1800-180-4188
• State Disaster Management: Check local numbers"""
    },
    "rain": {
        "keywords": ["rain", "rainfall", "monsoon", "drizzle", "precipitation", "shower", "downpour"],
        "answer": """**Rain & Monsoon Information:**

**India's Monsoon Pattern:**
• **Southwest Monsoon:** June - September (main season, brings ~75% of annual rainfall)
• **Northeast Monsoon:** October - December (Tamil Nadu, AP coasts)
• **Pre-monsoon:** April - May (thunderstorms in NE India)

**Rainfall Categories (IMD):**
• Light Rain: < 2.5 mm/hour
• Moderate Rain: 2.5 - 7.5 mm/hour
• Heavy Rain: 7.5 - 35.5 mm/hour
• Very Heavy Rain: 35.5 - 124.4 mm/hour
• Extremely Heavy Rain: > 124.4 mm/hour

**Safety During Heavy Rain:**
• Avoid low-lying areas
• Do not shelter under trees (lightning risk)
• Carry waterproof bags for electronics
• Check drainage before parking

**Average Annual Rainfall by Region:**
• Northeast India: 1000-4000+ mm (highest in the world — Cherrapunji)
• Coastal areas: 1000-3000 mm
• Central India: 700-1500 mm
• Rajasthan (desert): < 300 mm"""
    },
    "temperature": {
        "keywords": ["temperature", "hot", "cold", "heat", "degrees", "celsius", "heat wave", "cold wave", "warm", "freeze"],
        "answer": """**Temperature & Heat/Cold Waves:**

**India's Temperature Extremes:**
• Hottest recorded: 51°C at Phalodi, Rajasthan (2016)
• Coldest recorded: -45°C at Dras, Ladakh

**Heat Wave (IMD Definition):**
• Plains: Temperature ≥ 40°C and 4.5°C above normal
• Coastal: Temperature ≥ 37°C
• Hills: Temperature ≥ 30°C

**Heat Wave Safety:**
• Drink water every 30 minutes (even if not thirsty)
• Avoid outdoor activity between 12 PM - 3 PM
• Wear light-colored, loose cotton clothes
• Apply sunscreen (SPF 30+)
• Signs of heatstroke: confusion, no sweating, high temp (103°F+) — Call emergency immediately

**Cold Wave Safety:**
• Wear layered clothing
• Keep elderly and infants warm
• Watch for hypothermia signs: shivering, confusion, slurred speech
• Avoid alcohol (increases heat loss)"""
    },
    "wind": {
        "keywords": ["wind", "gust", "breeze", "gale", "storm", "wind speed", "beaufort"],
        "answer": """**Wind Speed Guide (Beaufort Scale):**

| Scale | Speed (km/h) | Description | Effect |
|-------|-------------|-------------|--------|
| 0 | < 1 | Calm | Smoke rises vertically |
| 3 | 12-19 | Gentle Breeze | Leaves move |
| 6 | 39-49 | Strong Breeze | Large branches move |
| 8 | 62-74 | Gale | Twigs break |
| 10 | 89-102 | Storm | Trees uprooted |
| 12 | > 118 | Hurricane Force | Widespread damage |

**Cyclone Wind Safety:**
• Winds > 60 km/h: Secure outdoor objects
• Winds > 90 km/h: Stay indoors
• Winds > 120 km/h: Extreme danger — stay away from windows"""
    },
    "uv": {
        "keywords": ["uv", "ultraviolet", "sun", "sunburn", "sunscreen", "uv index"],
        "answer": """**UV Index Guide:**

| UV Index | Risk Level | Protection Needed |
|---------|-----------|-------------------|
| 0-2 | Low (SAFE) | Minimal |
| 3-5 | Moderate (CAUTION) | Sunscreen SPF 30+ |
| 6-7 | High (WARNING) | SPF 50+, hat, shade |
| 8-10 | Very High (DANGER) | Stay indoors 10am-4pm |
| 11+ | Extreme (DANGER) | Avoid sun entirely |

**India UV Context:** UV index often reaches 10-12 during summer months (April-June), especially in Rajasthan and peninsular India.

**Protection Tips:**
• Apply SPF 30+ sunscreen 20 mins before going out
• Reapply every 2 hours
• Wear UV-protective sunglasses
• Seek shade during peak hours (10 AM - 4 PM)"""
    },
    "forecast": {
        "keywords": ["forecast", "prediction", "tomorrow", "next week", "weather next", "predict", "outlook"],
        "answer": """**About Weather Forecasting:**

**Forecast Accuracy by Range:**
• 1-3 days: ~90% accurate
• 4-7 days: ~80% accurate
• 8-10 days: ~60% accurate
• 11-15 days: ~50% accurate (trend-level)

**WeatherSense AI uses:**
• **Open-Meteo** — European Centre for Medium-Range Weather Forecasts (ECMWF) model data
• **GFS (Global Forecast System)** — NOAA data
• Real-time updates every 30 minutes

**India's Official Forecast Agencies:**
• **IMD (India Meteorological Department):** www.imd.gov.in
• **INCOIS:** Ocean and coastal forecasts
• **NDMA:** Disaster management advisories

This app provides **15-day forecasts** with daily temperature, rain probability, wind speed, UV index, and risk level color coding."""
    },
    "humidity": {
        "keywords": ["humidity", "humid", "moisture", "damp", "dry air", "relative humidity"],
        "answer": """**Understanding Humidity:**

**Relative Humidity (RH) Guide:**
• 20-30%: Very Dry (risk of static, cracked skin)
• 30-50%: Comfortable (ideal indoor range)
• 50-60%: Moderate
• 60-80%: Humid (sweating less effective)
• 80%+: Very Humid (feel much hotter)

**Heat Index (Feels Like Temperature):**
High humidity makes it feel hotter because sweat doesn't evaporate:
• 35°C + 80% RH = feels like 47°C!
• 30°C + 90% RH = feels like 40°C

**Health Effects of High Humidity:**
• Heat exhaustion and heatstroke risk
• Mold and fungal growth
• Respiratory issues in asthma patients

**India's Highest Humidity:** Kerala, Assam, coastal Bengal during monsoon — often 90%+"""
    },
    "lightning": {
        "keywords": ["lightning", "thunder", "thunderstorm", "lightning bolt", "electrical storm"],
        "answer": """**Lightning Safety:**

**India Lightning Statistics:**
• India records ~2,500 lightning deaths per year (highest globally)
• Most vulnerable: Farmers in open fields during monsoon
• Peak season: Pre-monsoon (April-June)

**The 30-30 Rule:**
• If lightning-to-thunder gap < 30 seconds: Seek shelter
• After last thunder: Wait 30 minutes before going out

**Safe Shelters:** Solid buildings, hard-top vehicles
**Unsafe Places:** Open fields, under trees, near metal objects, hilltops, open water

**If Caught Outdoors:**
• Crouch low on feet (don't lie flat)
• Keep feet together
• Don't hold metal objects
• Stay away from isolated trees

**Emergency:** In India, lightning strike medical emergency — call 112"""
    },
    "pollution": {
        "keywords": ["pollution", "aqi", "air quality", "smog", "pm2.5", "pm10", "air pollution"],
        "answer": """**Air Quality & Pollution:**

**AQI Scale (India CPCB):**
| AQI | Category | Health Impact |
|-----|---------|---------------|
| 0-50 | Good | Minimal impact |
| 51-100 | Satisfactory | Minor discomfort |
| 101-200 | Moderate | Sensitive groups affected |
| 201-300 | Poor | Everyone affected |
| 301-400 | Very Poor | Serious health effects |
| 401-500 | Severe | Emergency conditions |

**India's Most Polluted Cities (typically):** Delhi, Ghaziabad, Noida, Gurugram

**Protection:**
• N95 masks for AQI > 200
• Avoid outdoor exercise when AQI > 150
• Keep windows closed on high-AQI days
• Purify indoor air with plants (Snake plant, Peace lily)"""
    },
    "general": {
        "keywords": ["weather", "climate", "season", "india", "world", "global", "map"],
        "answer": """**WeatherSense AI — Your Complete Weather Guide**

I can answer questions about:
• **Tsunamis** — Warning signs, safety, risk zones
• **Cyclones** — Categories, seasons, safety
• **Floods** — Types, prevention, flood zones
• **Rain & Monsoon** — Patterns, safety, statistics
• **Temperature** — Heat waves, cold waves, safety
• **Wind** — Speed scales, safety thresholds
• **UV Index** — Protection guide
• **Lightning** — Safety rules
• **Air Quality** — AQI guide
• **Forecasts** — How predictions work

**Try asking:**
- "What should I do during a cyclone?"
- "Is it safe to go to the beach today?"
- "What does red alert mean?"
- "How to stay safe in heavy rain?"
- "What is the UV index right now?" """
    }
}


def detect_topic(question_en):
    """Detect the topic of the question."""
    q_lower = question_en.lower()
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in q_lower for kw in data["keywords"]):
            return topic
    return "general"


def get_answer_local(question_en):
    """Get answer from local knowledge base."""
    topic = detect_topic(question_en)
    return KNOWLEDGE_BASE[topic]["answer"]


def get_answer_gemini(question_en, weather_context=""):
    """Get AI-powered answer from Google Gemini."""
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel("gemini-1.5-flash")

        system_prompt = f"""You are WeatherSense AI, an expert weather assistant. 
        Answer weather-related questions accurately, practically and helpfully.
        Focus on safety, actionable advice, and Indian context where relevant.
        Format with emojis and clear sections. Keep answers under 300 words.
        
        Current weather context (if available): {weather_context}
        """

        response = model.generate_content(
            f"{system_prompt}\n\nUser Question: {question_en}"
        )
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return None


def translate_text(text, target_lang="en"):
    """Translate text to target language."""
    if target_lang in ("en", "english"):
        return text
    try:
        translator = GoogleTranslator(source="auto", target=target_lang)
        # Split text into chunks (translator has 5000 char limit)
        chunk_size = 4500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return "\n".join(translated_chunks)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Fallback to English


def translate_to_english(text, source_lang="auto"):
    """Translate any language to English."""
    if source_lang == "en":
        return text
    try:
        translator = GoogleTranslator(source=source_lang, target="en")
        return translator.translate(text)
    except Exception as e:
        print(f"Translation to English error: {e}")
        return text


def process_question(question, lang="en", weather_context=""):
    """
    Main entry point: process user question in any language,
    return answer in the same language.
    """
    # Step 1: Translate question to English
    question_en = translate_to_english(question, source_lang=lang if lang != "en" else "auto")

    # Step 2: Get answer (try Gemini first, fall back to local KB)
    if GEMINI_AVAILABLE:
        answer_en = get_answer_gemini(question_en, weather_context)
        if not answer_en:
            answer_en = get_answer_local(question_en)
    else:
        answer_en = get_answer_local(question_en)

    # Step 3: Translate answer back to user's language
    if lang and lang not in ("en", "auto"):
        answer = translate_text(answer_en, target_lang=lang)
    else:
        answer = answer_en

    return {
        "question_original": question,
        "question_english": question_en,
        "answer": answer,
        "answer_english": answer_en,
        "language": lang,
        "powered_by": "Gemini AI" if GEMINI_AVAILABLE else "WeatherSense KB",
    }


def get_greeting(lang="en"):
    """Return a greeting in the specified language."""
    greetings = {
        "en": "Hello! I'm your WeatherSense AI tutor. Ask me anything about weather, safety, or climate!",
        "hi": "नमस्ते! मैं आपका WeatherSense AI ट्यूटर हूं। मुझसे मौसम, सुरक्षा या जलवायु के बारे में कुछ भी पूछें!",
        "ta": "வணக்கம்! நான் உங்கள் WeatherSense AI ஆசிரியர். வானிலை, பாதுகாப்பு அல்லது காலநிலை பற்றி எதையும் கேளுங்கள்!",
        "te": "నమస్కారం! నేను మీ WeatherSense AI ట్యూటర్. వాతావరణం, భద్రత లేదా వాతావరణం గురించి నన్ను ఏదైనా అడగండి!",
        "kn": "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ WeatherSense AI ಟ್ಯೂಟರ್. ಹವಾಮಾನ, ಸುರಕ್ಷತೆ ಅಥವಾ ಹವಾಮಾನದ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ!",
        "ml": "നമസ്കാരം! ഞാൻ നിങ്ങളുടെ WeatherSense AI ട്യൂട്ടറാണ്. കാലാവസ്ഥ, സുരക്ഷ, അല്ലെങ്കിൽ കാലാവസ്ഥ എന്നതിനെക്കുറിച്ച് എന്നോട് ഏതെങ്കിലും ചോദ്യം ചോദിക്കൂ!",
        "bn": "নমস্কার! আমি আপনার WeatherSense AI টিউটর। আবহাওয়া, নিরাপত্তা বা জলবায়ু সম্পর্কে আমাকে যেকোনো প্রশ্ন করুন!",
        "mr": "नमस्कार! मी तुमचा WeatherSense AI ट्यूटर आहे. हवामान, सुरक्षा किंवा हवामानाबद्दल मला काहीही विचारा!",
        "gu": "નમસ્તે! હું તમારો WeatherSense AI ટ્યૂટર છું. હવામાન, સુરક્ષા અથવા આબોહવા વિશે મને કંઈ પણ પૂછો!",
        "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ ਤੁਹਾਡਾ WeatherSense AI ਟਿਊਟਰ ਹਾਂ। ਮੌਸਮ, ਸੁਰੱਖਿਆ ਜਾਂ ਜਲਵਾਯੂ ਬਾਰੇ ਮੈਨੂੰ ਕੁਝ ਵੀ ਪੁੱਛੋ!",
        "fr": "Bonjour! Je suis votre tuteur WeatherSense AI. Posez-moi n'importe quelle question sur la météo, la sécurité ou le climat!",
        "es": "¡Hola! Soy tu tutor WeatherSense AI. ¡Pregúntame cualquier cosa sobre el clima, la seguridad o el tiempo!",
        "de": "Hallo! Ich bin Ihr WeatherSense AI-Tutor. Fragen Sie mich alles über Wetter, Sicherheit oder Klima!",
        "ja": "こんにちは！私はWeatherSense AIチューターです。天気、安全、気候について何でも聞いてください！",
        "zh-cn": "你好！我是您的WeatherSense AI导师。请随时向我询问有关天气、安全或气候的任何问题！",
        "ar": "مرحباً! أنا مدربك WeatherSense AI. اسألني أي شيء عن الطقس والسلامة والمناخ!",
    }
    return greetings.get(lang, greetings["en"])
