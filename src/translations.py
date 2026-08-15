"""
Bilingual (English / Hindi) label dictionary for SkyTrail Desktop.
Usage: t("sun", lang) -> "Sun" or "सूर्य"
"""

SIGNS = {
    "en": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
           "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
    "hi": ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
           "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"],
}

PLANETS = {
    "en": {
        "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus",
        "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
        "rahu": "Rahu (N. Node)", "ketu": "Ketu (S. Node)", "ascendant": "Ascendant",
    },
    "hi": {
        "sun": "सूर्य", "moon": "चंद्र", "mercury": "बुध", "venus": "शुक्र",
        "mars": "मंगल", "jupiter": "गुरु", "saturn": "शनि",
        "rahu": "राहु", "ketu": "केतु", "ascendant": "लग्न",
    },
}

NAKSHATRAS = {
    "en": ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
           "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
           "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
           "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
           "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"],
    "hi": ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
           "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्व फाल्गुनी", "उत्तर फाल्गुनी",
           "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा", "ज्येष्ठा",
           "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण", "धनिष्ठा",
           "शतभिषा", "पूर्व भाद्रपद", "उत्तर भाद्रपद", "रेवती"],
}

UI = {
    "en": {
        "title": "S K Y T R A I L",
        "subtitle": "Vedic & Western Astrology  |  Local AI  |  Offline",
        "name": "Name",
        "birth_date": "Birth Date (DD-MM-YYYY)",
        "birth_time": "Birth Time (HH:MM, 24hr)",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "tz_offset": "Timezone Offset (e.g. 5.5 for IST)",
        "generate": "GENERATE CHART",
        "system_vedic": "VEDIC",
        "system_western": "WESTERN",
        "lang_en": "EN",
        "lang_hi": "हिं",
        "chart_title": "BIRTH CHART",
        "planet_positions": "PLANETARY POSITIONS",
        "horoscope_title": "AI READING",
        "generating": "Consulting the stars...",
        "sign": "Sign",
        "degree": "Degree",
        "nakshatra": "Nakshatra",
        "error_input": "Please check your birth details and try again.",
        "city_presets": "Quick City",
    },
    "hi": {
        "title": "स्काई ट्रेल",
        "subtitle": "वैदिक और पाश्चात्य ज्योतिष  |  लोकल AI  |  ऑफलाइन",
        "name": "नाम",
        "birth_date": "जन्म तिथि (DD-MM-YYYY)",
        "birth_time": "जन्म समय (HH:MM, 24 घंटे)",
        "latitude": "अक्षांश",
        "longitude": "देशांतर",
        "tz_offset": "समय क्षेत्र अंतर (जैसे IST के लिए 5.5)",
        "generate": "कुंडली बनाएं",
        "system_vedic": "वैदिक",
        "system_western": "पाश्चात्य",
        "lang_en": "EN",
        "lang_hi": "हिं",
        "chart_title": "जन्म कुंडली",
        "planet_positions": "ग्रह स्थिति",
        "horoscope_title": "AI भविष्यफल",
        "generating": "सितारों से पूछ रहे हैं...",
        "sign": "राशि",
        "degree": "अंश",
        "nakshatra": "नक्षत्र",
        "error_input": "कृपया अपना जन्म विवरण जांचें और पुनः प्रयास करें।",
        "city_presets": "शहर चुनें",
    },
}

CITY_PRESETS = {
    # name: (lat, lon, tz_offset)
    "Pune": (18.5204, 73.8567, 5.5),
    "Amravati": (20.9374, 77.7796, 5.5),
    "Mumbai": (19.0760, 72.8777, 5.5),
    "Delhi": (28.7041, 77.1025, 5.5),
    "Bengaluru": (12.9716, 77.5946, 5.5),
}


def t(key: str, lang: str) -> str:
    return UI.get(lang, UI["en"]).get(key, key)


def sign_name(index: int, lang: str) -> str:
    return SIGNS.get(lang, SIGNS["en"])[index % 12]


def planet_name(key: str, lang: str) -> str:
    return PLANETS.get(lang, PLANETS["en"]).get(key, key)


def nakshatra_name(index: int, lang: str) -> str:
    return NAKSHATRAS.get(lang, NAKSHATRAS["en"])[index % 27]
