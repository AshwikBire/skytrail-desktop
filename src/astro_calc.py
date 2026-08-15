"""
Advanced Astrology Calculation Engine — Vedic (sidereal) and Western (tropical)
with Multiple Ayanamsa, Navamsa (D9), Full Dasha System, and Kundali Milan
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import math

# Try to import swisseph, fallback to ephem
try:
    import swisseph as swe
    USING_SWISSEPH = True
    print("Using Swiss Ephemeris for accurate calculations")
except ImportError:
    import ephem
    USING_SWISSEPH = False
    print("Using PyEphem as fallback (less accurate but works without compilation)")

# Ayanamsa Options
AYANAMSA_OPTIONS = {
    "Lahiri": swe.SIDM_LAHIRI if USING_SWISSEPH else 0,
    "Raman": swe.SIDM_RAMAN if USING_SWISSEPH else 1,
    "KP": swe.SIDM_KRISHNAMURTI if USING_SWISSEPH else 2,
    "True Citra": swe.SIDM_TRUE_CITRA if USING_SWISSEPH else 3,
    "Fagan-Bradley": swe.SIDM_FAGAN if USING_SWISSEPH else 4,
    "J2000": 5,
}

# Dasha System
DASHA_LORDS = ["ketu", "venus", "sun", "moon", "mars", "rahu", "jupiter", "saturn", "mercury"]
DASHA_PERIODS = {
    "ketu": 7, "venus": 20, "sun": 6, "moon": 10, "mars": 7,
    "rahu": 18, "jupiter": 16, "saturn": 19, "mercury": 17
}

PLANET_CODES = {
    "sun": swe.SUN if USING_SWISSEPH else None,
    "moon": swe.MOON if USING_SWISSEPH else None,
    "mercury": swe.MERCURY if USING_SWISSEPH else None,
    "venus": swe.VENUS if USING_SWISSEPH else None,
    "mars": swe.MARS if USING_SWISSEPH else None,
    "jupiter": swe.JUPITER if USING_SWISSEPH else None,
    "saturn": swe.SATURN if USING_SWISSEPH else None,
    "rahu": swe.MEAN_NODE if USING_SWISSEPH else None,
}


@dataclass
class PlanetPosition:
    key: str
    longitude: float
    sign_index: int
    degree_in_sign: float
    retrograde: bool
    house: int = 0
    strength: float = 0.0
    navamsa_sign: int = 0
    navamsa_degree: float = 0.0


@dataclass
class BirthChart:
    system: str
    ayanamsa: str
    julian_day: float
    ascendant: PlanetPosition
    planets: list
    nakshatra_index: int
    nakshatra_pada: int
    navamsa_ascendant: PlanetPosition = None
    navamsa_planets: list = None
    houses: dict = None
    yogas: list = None
    dasha: dict = None
    aspects: dict = None
    strengths: dict = None


def _to_sign_and_degree(longitude: float):
    longitude = longitude % 360
    sign_index = int(longitude // 30)
    degree = longitude % 30
    return sign_index, degree


def compute_chart(dt_local: datetime, tz_offset: float, latitude: float,
                   longitude: float, system: str = "vedic", ayanamsa: str = "Lahiri") -> BirthChart:
    """Compute birth chart with multiple ayanamsa and navamsa"""
    
    if USING_SWISSEPH:
        chart = _compute_chart_swisseph(dt_local, tz_offset, latitude, longitude, system, ayanamsa)
    else:
        chart = _compute_chart_ephem(dt_local, tz_offset, latitude, longitude, system)
    
    # Add advanced features
    chart.ayanamsa = ayanamsa
    chart.houses = _calculate_houses(chart)
    chart.yogas = _detect_yogas(chart)
    chart.dasha = _calculate_full_dasha(chart)
    chart.aspects = _calculate_aspects(chart)
    chart.strengths = _calculate_strengths(chart)
    
    # Calculate Navamsa (D9)
    navamsa_data = _calculate_navamsa(chart)
    chart.navamsa_ascendant = navamsa_data["ascendant"]
    chart.navamsa_planets = navamsa_data["planets"]
    
    return chart


def _compute_chart_swisseph(dt_local: datetime, tz_offset: float, latitude: float,
                            longitude: float, system: str = "vedic", ayanamsa: str = "Lahiri") -> BirthChart:
    """Compute chart using Swiss Ephemeris with selected ayanamsa"""
    
    utc_hour = dt_local.hour + dt_local.minute / 60.0 + dt_local.second / 3600.0 - tz_offset
    jd = swe.julday(dt_local.year, dt_local.month, dt_local.day, utc_hour)

    use_sidereal = (system == "vedic")
    if use_sidereal:
        if ayanamsa in AYANAMSA_OPTIONS:
            if ayanamsa != "J2000":
                swe.set_sid_mode(AYANAMSA_OPTIONS[ayanamsa])
            else:
                swe.set_sid_mode(swe.SIDM_J2000)
        else:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    flag = swe.FLG_SIDEREAL if use_sidereal else swe.FLG_SWIEPH | swe.FLG_MOSEPH

    planets = []
    moon_longitude = None
    
    for key, code in PLANET_CODES.items():
        if code is None:
            continue
        pos, ret = swe.calc_ut(jd, code, flag)
        lon = pos[0]
        speed = pos[3]
        sign_index, degree = _to_sign_and_degree(lon)
        planets.append(PlanetPosition(key, lon, sign_index, degree, retrograde=(speed < 0)))
        if key == "moon":
            moon_longitude = lon

    # Ketu is always exactly opposite Rahu
    rahu = next(p for p in planets if p.key == "rahu")
    ketu_lon = (rahu.longitude + 180) % 360
    k_sign, k_deg = _to_sign_and_degree(ketu_lon)
    planets.append(PlanetPosition("ketu", ketu_lon, k_sign, k_deg, retrograde=True))

    # Ascendant
    hsys = b'W' if use_sidereal else b'P'
    try:
        houses = swe.houses_ex(jd, latitude, longitude, hsys, flag & swe.FLG_SIDEREAL if use_sidereal else 0)
        asc_lon = houses[1][0]
    except Exception:
        houses = swe.houses(jd, latitude, longitude)
        asc_lon = houses[0][0]
        if use_sidereal:
            ayanamsa_val = swe.get_ayanamsa_ut(jd)
            asc_lon = (asc_lon - ayanamsa_val) % 360

    a_sign, a_deg = _to_sign_and_degree(asc_lon)
    ascendant = PlanetPosition("ascendant", asc_lon, a_sign, a_deg, retrograde=False)

    # Nakshatra
    if use_sidereal and moon_longitude is not None:
        moon_sidereal = moon_longitude
    else:
        ayanamsa_val = swe.get_ayanamsa_ut(jd)
        moon_sidereal = (moon_longitude - ayanamsa_val) % 360 if moon_longitude is not None else 0
    
    nak_span = 360 / 27
    nakshatra_index = int(moon_sidereal // nak_span)
    pada = int((moon_sidereal % nak_span) // (nak_span / 4)) + 1

    return BirthChart(
        system=system,
        ayanamsa=ayanamsa,
        julian_day=jd,
        ascendant=ascendant,
        planets=planets,
        nakshatra_index=nakshatra_index,
        nakshatra_pada=pada,
        houses={},
        yogas=[],
        dasha={},
        aspects={},
        strengths={}
    )


def _compute_chart_ephem(dt_local: datetime, tz_offset: float, latitude: float,
                         longitude: float, system: str = "vedic") -> BirthChart:
    """Compute chart using PyEphem (fallback)"""
    obs = ephem.Observer()
    obs.lat = str(latitude)
    obs.lon = str(longitude)
    obs.date = f"{dt_local.year}/{dt_local.month}/{dt_local.day} {dt_local.hour:02d}:{dt_local.minute:02d}:{dt_local.second:02d}"
    obs.date = ephem.Date(obs.date - ephem.hour * tz_offset)
    
    jd = float(obs.date) + 2415020.0
    
    planets = []
    moon_longitude = None
    
    planet_bodies = {
        "sun": ephem.Sun,
        "moon": ephem.Moon,
        "mercury": ephem.Mercury,
        "venus": ephem.Venus,
        "mars": ephem.Mars,
        "jupiter": ephem.Jupiter,
        "saturn": ephem.Saturn,
        "rahu": None,
    }
    
    for key, body_class in planet_bodies.items():
        if body_class is None:
            continue
        body = body_class()
        body.compute(obs)
        lon = float(body.ra) * 180 / math.pi
        speed = 0
        
        if system == "vedic":
            ayanamsa = _calculate_ayanamsa_ephem(obs)
            lon = (lon - ayanamsa) % 360
        
        sign_index, degree = _to_sign_and_degree(lon)
        planets.append(PlanetPosition(key, lon, sign_index, degree, retrograde=(speed < 0)))
        
        if key == "moon":
            moon_longitude = lon
    
    # Rahu approximation
    rahu_lon = (moon_longitude + 180) % 360 if moon_longitude is not None else 0
    r_sign, r_deg = _to_sign_and_degree(rahu_lon)
    planets.append(PlanetPosition("rahu", rahu_lon, r_sign, r_deg, retrograde=True))
    
    # Ketu
    rahu = next(p for p in planets if p.key == "rahu")
    ketu_lon = (rahu.longitude + 180) % 360
    k_sign, k_deg = _to_sign_and_degree(ketu_lon)
    planets.append(PlanetPosition("ketu", ketu_lon, k_sign, k_deg, retrograde=True))
    
    # Ascendant
    asc_lon = _calculate_ascendant_ephem(obs, latitude, longitude)
    if system == "vedic":
        ayanamsa = _calculate_ayanamsa_ephem(obs)
        asc_lon = (asc_lon - ayanamsa) % 360
    
    a_sign, a_deg = _to_sign_and_degree(asc_lon)
    ascendant = PlanetPosition("ascendant", asc_lon, a_sign, a_deg, retrograde=False)
    
    # Nakshatra
    if moon_longitude is not None:
        if system == "vedic":
            moon_sidereal = moon_longitude
        else:
            ayanamsa = _calculate_ayanamsa_ephem(obs)
            moon_sidereal = (moon_longitude - ayanamsa) % 360
        nak_span = 360 / 27
        nakshatra_index = int(moon_sidereal // nak_span)
        pada = int((moon_sidereal % nak_span) // (nak_span / 4)) + 1
    else:
        nakshatra_index = 0
        pada = 1
    
    return BirthChart(
        system=system,
        ayanamsa="Lahiri",
        julian_day=jd,
        ascendant=ascendant,
        planets=planets,
        nakshatra_index=nakshatra_index,
        nakshatra_pada=pada,
        houses={},
        yogas=[],
        dasha={},
        aspects={},
        strengths={}
    )


def _calculate_ascendant_ephem(obs, latitude, longitude):
    """Calculate ascendant using ephem"""
    lst = float(obs.sidereal_time()) * 180 / math.pi
    asc = (lst + 90) % 360
    asc_adjusted = asc + (90 - latitude) * 0.3
    return asc_adjusted % 360


def _calculate_ayanamsa_ephem(obs):
    """Calculate approximate ayanamsa"""
    date_str = str(obs.date)
    parts = date_str.split('/')
    if len(parts) >= 3:
        try:
            year = float(parts[0])
            base_year = 1900
            ayanamsa = (year - base_year) * 50.29 / 3600
            return ayanamsa
        except:
            pass
    return 0.0


def _calculate_navamsa(chart: BirthChart) -> dict:
    """Calculate Navamsa (D9) chart"""
    navamsa_planets = []
    
    for planet in chart.planets:
        total_degrees = planet.sign_index * 30 + planet.degree_in_sign
        navamsa_index = int(total_degrees / 3.3333) % 12
        navamsa_degree = (total_degrees % 3.3333) / 3.3333 * 30
        
        planet.navamsa_sign = navamsa_index
        planet.navamsa_degree = navamsa_degree
        navamsa_planets.append(planet)
    
    asc_total_degrees = chart.ascendant.sign_index * 30 + chart.ascendant.degree_in_sign
    navamsa_asc_index = int(asc_total_degrees / 3.3333) % 12
    navamsa_asc_degree = (asc_total_degrees % 3.3333) / 3.3333 * 30
    
    navamsa_asc = PlanetPosition(
        "ascendant",
        navamsa_asc_index * 30 + navamsa_asc_degree,
        navamsa_asc_index,
        navamsa_asc_degree,
        retrograde=False
    )
    
    return {
        "ascendant": navamsa_asc,
        "planets": navamsa_planets
    }


def _calculate_full_dasha(chart: BirthChart) -> dict:
    """Calculate complete Vimshottari Dasha with all sub-periods"""
    
    nakshatra = chart.nakshatra_index
    lord_index = nakshatra % 9
    current_lord = DASHA_LORDS[lord_index]
    total_period = DASHA_PERIODS[current_lord]
    remaining = total_period
    
    all_dashas = []
    for i in range(9):
        lord = DASHA_LORDS[(lord_index + i) % 9]
        years = DASHA_PERIODS[lord]
        
        sub_dashas = []
        for j in range(9):
            sub_lord = DASHA_LORDS[(lord_index + i + j) % 9]
            sub_years = years * DASHA_PERIODS[sub_lord] / total_period
            
            sub_sub_dashas = []
            for k in range(9):
                sub_sub_lord = DASHA_LORDS[(lord_index + i + j + k) % 9]
                sub_sub_years = sub_years * DASHA_PERIODS[sub_sub_lord] / DASHA_PERIODS[sub_lord]
                sub_sub_dashas.append({
                    "lord": sub_sub_lord,
                    "years": sub_sub_years,
                    "name": sub_sub_lord.capitalize()
                })
            
            sub_dashas.append({
                "lord": sub_lord,
                "years": sub_years,
                "name": sub_lord.capitalize(),
                "sub_sub": sub_sub_dashas
            })
        
        all_dashas.append({
            "lord": lord,
            "years": years,
            "name": lord.capitalize(),
            "sub_dashas": sub_dashas
        })
    
    return {
        "current_dasha": current_lord,
        "current_dasha_name": current_lord.capitalize(),
        "remaining_years": remaining,
        "total_period": total_period,
        "lord_index": lord_index,
        "all_dashas": all_dashas,
        "balance": remaining / total_period * 100
    }


def _calculate_houses(chart: BirthChart) -> dict:
    """Calculate house cusps and assign planets to houses"""
    houses = {}
    asc_lon = chart.ascendant.longitude
    
    for i in range(12):
        house_start = (asc_lon + i * 30) % 360
        house_end = (asc_lon + (i + 1) * 30) % 360
        houses[f"House_{i+1}"] = {
            "start": house_start,
            "end": house_end,
            "planets": []
        }
    
    for planet in chart.planets:
        lon = planet.longitude
        for i in range(12):
            house_start = (asc_lon + i * 30) % 360
            house_end = (asc_lon + (i + 1) * 30) % 360
            
            if i == 11:
                if lon >= house_start or lon < house_end:
                    houses[f"House_{i+1}"]["planets"].append(planet.key)
                    planet.house = i + 1
                    break
            else:
                if house_start <= lon < house_end:
                    houses[f"House_{i+1}"]["planets"].append(planet.key)
                    planet.house = i + 1
                    break
    
    return houses


def _detect_yogas(chart: BirthChart) -> list:
    """Detect important yogas"""
    yogas = []
    planets = {p.key: p for p in chart.planets}
    
    # Gajakesari Yoga
    if "moon" in planets and "jupiter" in planets:
        moon_house = planets["moon"].house
        jupiter_house = planets["jupiter"].house
        diff = (jupiter_house - moon_house) % 12
        if diff in [0, 3, 6, 9]:
            yogas.append({
                "name": "Gajakesari Yoga",
                "type": "Benefic",
                "description": "Wisdom, intelligence, and prosperity.",
                "strength": "Strong"
            })
    
    # Pancha Mahapurusha Yoga
    strong_planets = []
    for planet in chart.planets:
        if _get_planet_strength(planet) > 2.0:
            strong_planets.append(planet.key)
    
    if len(strong_planets) >= 3:
        yogas.append({
            "name": "Pancha Mahapurusha Yoga",
            "type": "Benefic",
            "description": "Strong placement in exalted/own signs. Leadership and authority.",
            "strength": "Very Strong"
        })
    
    # Lakshmi Yoga (Wealth)
    if "jupiter" in planets and "venus" in planets:
        if planets["jupiter"].house in [1, 5, 9] and planets["venus"].house in [2, 4, 6, 11]:
            yogas.append({
                "name": "Lakshmi Yoga",
                "type": "Benefic",
                "description": "Wealth, prosperity, and abundance.",
                "strength": "Strong"
            })
    
    return yogas


def _get_planet_strength(planet: PlanetPosition) -> float:
    """Calculate individual planet strength"""
    strength = 0.0
    
    if _is_exalted(planet):
        strength += 3.0
    elif _is_debilitated(planet):
        strength -= 2.0
    
    if _is_own_sign(planet):
        strength += 2.0
    
    if planet.degree_in_sign < 5 or planet.degree_in_sign > 25:
        strength += 0.5
    
    return strength


def _is_exalted(planet: PlanetPosition) -> bool:
    exaltation = {
        "sun": 1, "moon": 3, "mars": 4, "mercury": 6,
        "jupiter": 2, "venus": 6, "saturn": 4, "rahu": 2, "ketu": 8
    }
    return planet.sign_index == exaltation.get(planet.key, -1)


def _is_debilitated(planet: PlanetPosition) -> bool:
    debilitation = {
        "sun": 7, "moon": 9, "mars": 6, "mercury": 8,
        "jupiter": 10, "venus": 10, "saturn": 8, "rahu": 6, "ketu": 2
    }
    return planet.sign_index == debilitation.get(planet.key, -1)


def _is_own_sign(planet: PlanetPosition) -> bool:
    own_signs = {
        "sun": [1], "moon": [3], "mars": [1, 8], "mercury": [3, 6],
        "jupiter": [2, 9], "venus": [4, 7], "saturn": [5, 10],
        "rahu": [2, 6], "ketu": [2, 6]
    }
    return planet.sign_index in own_signs.get(planet.key, [])


def _calculate_aspects(chart: BirthChart) -> dict:
    """Calculate planetary aspects"""
    aspects = {}
    aspect_patterns = {
        "sun": [1, 7],
        "moon": [1, 7],
        "mars": [1, 4, 7, 8],
        "mercury": [1, 7],
        "jupiter": [1, 5, 7, 9],
        "venus": [1, 7],
        "saturn": [1, 3, 7, 10],
        "rahu": [1, 5, 7, 9],
        "ketu": [1, 5, 7, 9]
    }
    
    for planet in chart.planets:
        if planet.key in aspect_patterns:
            aspects[planet.key] = {
                "aspects": aspect_patterns[planet.key],
                "house": planet.house
            }
    
    return aspects


def _calculate_strengths(chart: BirthChart) -> dict:
    """Calculate planetary strengths"""
    strengths = {}
    for planet in chart.planets:
        strength = _get_planet_strength(planet)
        strengths[planet.key] = {
            "strength": strength,
            "level": "Strong" if strength > 2.0 else "Medium" if strength > 1.0 else "Weak",
            "score": min(strength * 10, 10)
        }
    return strengths


# ---------- EXTERNAL FUNCTIONS ----------

def get_prediction(chart: BirthChart, category: str) -> dict:
    """
    Get prediction for a specific category
    Categories: "career", "marriage", "children", "success", "personality", "face"
    """
    predictions = {
        "career": _get_career_prediction(chart),
        "marriage": _get_marriage_prediction(chart),
        "children": _get_children_prediction(chart),
        "success": _get_success_prediction(chart),
        "personality": _get_personality_prediction(chart),
        "face": _get_face_prediction(chart)
    }
    return predictions.get(category, {})


def _get_career_prediction(chart: BirthChart) -> dict:
    """Career prediction"""
    career_planets = []
    
    for planet in chart.planets:
        if planet.key in ["sun", "mercury", "jupiter", "saturn"]:
            if planet.house in [1, 5, 9, 10]:
                career_planets.append(planet.key)
    
    careers = {
        "sun": "Leadership, government, politics, administration",
        "mercury": "Communication, writing, teaching, business",
        "jupiter": "Finance, law, education, counseling",
        "saturn": "Engineering, construction, management, service",
        "mars": "Military, sports, surgery, entrepreneurship",
        "venus": "Arts, design, beauty, luxury, entertainment",
        "moon": "Healthcare, hospitality, psychology, travel"
    }
    
    top_careers = [careers.get(p, "General profession") for p in career_planets[:3]]
    
    return {
        "category": "Career",
        "strength": "Strong" if len(career_planets) >= 2 else "Moderate",
        "suitable_fields": top_careers,
        "advice": "Focus on fields that align with your natural strengths.",
        "planets": career_planets
    }


def _get_marriage_prediction(chart: BirthChart) -> dict:
    """Marriage prediction"""
    marriage_planets = []
    venus_found = False
    
    for planet in chart.planets:
        if planet.key == "venus":
            venus_found = True
            if planet.house in [1, 5, 7, 9]:
                marriage_planets.append("venus")
        if planet.house == 7:
            marriage_planets.append(planet.key)
    
    timing = "Early" if len(marriage_planets) >= 2 else "Moderate" if len(marriage_planets) >= 1 else "Late"
    
    return {
        "category": "Marriage",
        "timing": timing,
        "indicators": marriage_planets[:3],
        "compatibility": "High" if venus_found and "jupiter" in [p.key for p in chart.planets] else "Moderate",
        "advice": "Focus on emotional compatibility and mutual understanding."
    }


def _get_children_prediction(chart: BirthChart) -> dict:
    """Children prediction"""
    children_planets = []
    
    for planet in chart.planets:
        if planet.house == 5:
            children_planets.append(planet.key)
    
    jupiter_in_5th = any(p.key == "jupiter" and p.house == 5 for p in chart.planets)
    
    return {
        "category": "Children",
        "indications": "Favorable" if jupiter_in_5th or len(children_planets) >= 2 else "Moderate",
        "planets_in_5th": children_planets[:3],
        "advice": "Nurture and support your children's unique talents."
    }


def _get_success_prediction(chart: BirthChart) -> dict:
    """Success prediction"""
    success_indicators = []
    
    for planet in chart.planets:
        if planet.house in [1, 5, 9, 10] and planet.key not in ["rahu", "ketu"]:
            success_indicators.append(planet.key)
    
    sun_strong = any(p.key == "sun" and p.house in [1, 5, 9, 10] for p in chart.planets)
    jupiter_strong = any(p.key == "jupiter" and p.house in [1, 5, 9, 10] for p in chart.planets)
    
    saturn = next((p for p in chart.planets if p.key == "saturn"), None)
    saturn_strong = saturn and saturn.house in [1, 5, 9, 10]
    
    success_level = "High" if (sun_strong and jupiter_strong) else "Good" if (sun_strong or jupiter_strong) else "Moderate"
    
    return {
        "category": "Success",
        "level": success_level,
        "indicators": success_indicators[:3],
        "timing": "After age 30" if saturn_strong else "Throughout life",
        "advice": "Stay consistent and work on your strengths."
    }


def _get_personality_prediction(chart: BirthChart) -> dict:
    """Personality prediction based on Ascendant and planets"""
    asc_sign = chart.ascendant.sign_index
    
    sun = next((p for p in chart.planets if p.key == "sun"), None)
    sun_sign = sun.sign_index if sun else 0
    
    moon = next((p for p in chart.planets if p.key == "moon"), None)
    moon_sign = moon.sign_index if moon else 0
    
    personality_traits = [
        "Determined" if asc_sign in [1, 5, 9] else "Adaptable",
        "Creative" if sun_sign in [1, 4, 7, 10] else "Practical",
        "Emotional" if moon_sign in [2, 5, 8, 11] else "Rational",
        "Leadership" if asc_sign in [1, 5, 9] else "Supportive"
    ]
    
    return {
        "category": "Personality",
        "ascendant": asc_sign,
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "traits": personality_traits[:3],
        "strengths": "Confident, creative, resilient" if asc_sign in [1, 5, 9] else "Practical, grounded, loyal",
        "weaknesses": "Impulsive" if asc_sign in [1, 5, 9] else "Inflexible"
    }


def _get_face_prediction(chart: BirthChart) -> dict:
    """Face reading based on Ascendant and planets"""
    asc_sign = chart.ascendant.sign_index
    
    face_features = {
        0: {"shape": "Round", "eyes": "Bright", "nose": "Well-proportioned"},
        1: {"shape": "Long", "eyes": "Sharp", "nose": "Prominent"},
        2: {"shape": "Square", "eyes": "Wide", "nose": "Straight"},
        3: {"shape": "Oval", "eyes": "Intense", "nose": "Delicate"},
        4: {"shape": "Round", "eyes": "Warm", "nose": "Small"},
        5: {"shape": "Heart", "eyes": "Expressive", "nose": "Medium"},
        6: {"shape": "Diamond", "eyes": "Deep-set", "nose": "Aquiline"},
        7: {"shape": "Long", "eyes": "Sleepy", "nose": "Large"},
        8: {"shape": "Square", "eyes": "Piercing", "nose": "Straight"},
        9: {"shape": "Oval", "eyes": "Gentle", "nose": "Curved"},
        10: {"shape": "Round", "eyes": "Hypnotic", "nose": "Sharp"},
        11: {"shape": "Heart", "eyes": "Soulful", "nose": "Small"}
    }
    
    features = face_features.get(asc_sign, face_features[0])
    
    return {
        "category": "Face",
        "shape": features["shape"],
        "eyes": features["eyes"],
        "nose": features["nose"],
        "expression": "Confident" if asc_sign in [1, 5, 9] else "Gentle" if asc_sign in [2, 6, 10] else "Mysterious",
        "advice": "Your face reflects your inner strength and character."
    }


# ---------- KUNDALI MILAN (Matchmaking) ----------

def kundali_milan(chart1: BirthChart, chart2: BirthChart) -> dict:
    """
    Kundali Milan - Ashtakoot matching system
    Returns: Compatibility score out of 36
    """
    score = 0
    total = 36
    details = []
    
    # 1. Varna (1 point)
    if chart1.ascendant.sign_index % 4 == chart2.ascendant.sign_index % 4:
        score += 1
        details.append({"Varna": "Same category - 1 point"})
    else:
        details.append({"Varna": "Different category - 0 points"})
    
    # 2. Vashya (2 points)
    vashya_signs = {0: "M", 1: "F", 2: "M", 3: "F", 4: "M", 5: "F",
                    6: "M", 7: "F", 8: "M", 9: "F", 10: "M", 11: "F"}
    if vashya_signs.get(chart1.ascendant.sign_index) != vashya_signs.get(chart2.ascendant.sign_index):
        score += 2
        details.append({"Vashya": "Opposite sexes - 2 points"})
    
    # 3. Tara (3 points)
    nakshatra1 = chart1.nakshatra_index
    nakshatra2 = chart2.nakshatra_index
    diff = abs(nakshatra1 - nakshatra2) % 27
    if diff in [1, 2, 3]:
        score += 3
        details.append({"Tara": "Good compatibility - 3 points"})
    elif diff in [4, 5, 6]:
        score += 2
        details.append({"Tara": "Average compatibility - 2 points"})
    
    # 4. Yoni (4 points)
    yoni_signs = {0: "Horse", 1: "Elephant", 2: "Sheep", 3: "Snake", 4: "Dog",
                  5: "Cat", 6: "Rat", 7: "Cow", 8: "Buffalo", 9: "Tiger",
                  10: "Deer", 11: "Monkey"}
    yoni1 = yoni_signs.get(chart1.nakshatra_index % 12, "Unknown")
    yoni2 = yoni_signs.get(chart2.nakshatra_index % 12, "Unknown")
    if yoni1 == yoni2:
        score += 4
        details.append({"Yoni": f"Same {yoni1} - 4 points"})
    else:
        score += 2
        details.append({"Yoni": f"Different ({yoni1}/{yoni2}) - 2 points"})
    
    # 5. Graha Maitri (5 points)
    friend_groups = [["sun", "moon"], ["mars", "jupiter"], ["venus", "saturn"]]
    moon_sign1 = next((p for p in chart1.planets if p.key == "moon"), None)
    moon_sign2 = next((p for p in chart2.planets if p.key == "moon"), None)
    if moon_sign1 and moon_sign2:
        if any(moon_sign1.key in group and moon_sign2.key in group for group in friend_groups):
            score += 5
            details.append({"Graha Maitri": "Friendly planets - 5 points"})
        else:
            score += 3
            details.append({"Graha Maitri": "Neutral planets - 3 points"})
    
    # 6. Gana (6 points)
    gana_groups = {0: "Deva", 1: "Manushya", 2: "Rakshasa"}
    gana1 = gana_groups.get(chart1.nakshatra_index % 3, "Manushya")
    gana2 = gana_groups.get(chart2.nakshatra_index % 3, "Manushya")
    if gana1 == gana2:
        score += 6
        details.append({"Gana": f"Same {gana1} - 6 points"})
    else:
        score += 3
        details.append({"Gana": f"Different ({gana1}/{gana2}) - 3 points"})
    
    # 7. Bhakoot (7 points)
    bhava_diff = abs(chart1.ascendant.sign_index - chart2.ascendant.sign_index)
    if bhava_diff in [1, 7, 9]:
        score += 7
        details.append({"Bhakoot": "Harmonious signs - 7 points"})
    elif bhava_diff in [2, 8, 10]:
        score += 4
        details.append({"Bhakoot": "Moderate signs - 4 points"})
    
    # 8. Nadi (8 points)
    nadi_groups = {0: "Adi", 1: "Madhya", 2: "Antya"}
    nadi1 = nadi_groups.get(chart1.nakshatra_index % 3, "Madhya")
    nadi2 = nadi_groups.get(chart2.nakshatra_index % 3, "Madhya")
    if nadi1 != nadi2:
        score += 8
        details.append({"Nadi": f"Different nadis ({nadi1}/{nadi2}) - 8 points"})
    
    percentage = (score / total) * 100
    if percentage >= 85:
        level = "Excellent"
    elif percentage >= 70:
        level = "Very Good"
    elif percentage >= 55:
        level = "Good"
    elif percentage >= 40:
        level = "Moderate"
    else:
        level = "Low"
    
    return {
        "score": score,
        "total": total,
        "percentage": percentage,
        "level": level,
        "details": details,
        "compatible": score >= 18
    }


def get_navamsa_interpretation(chart: BirthChart) -> dict:
    """Get Navamsa (D9) chart interpretation"""
    interpretations = {}
    
    if chart.navamsa_ascendant:
        navamsa_sign = chart.navamsa_ascendant.sign_index
        interpretations["ascendant"] = {
            "sign": navamsa_sign,
            "meaning": _get_navamsa_sign_meaning(navamsa_sign)
        }
    
    for planet in chart.navamsa_planets:
        interpretations[planet.key] = {
            "sign": planet.navamsa_sign,
            "degree": planet.navamsa_degree,
            "meaning": f"Planet {planet.key} in Navamsa sign {planet.navamsa_sign}"
        }
    
    return interpretations


def _get_navamsa_sign_meaning(sign_index: int) -> str:
    """Get meaning of Navamsa sign"""
    meanings = {
        0: "Spiritual inclination, leadership qualities",
        1: "Practical, grounded, material success",
        2: "Intellectual, communicative, artistic",
        3: "Emotional, nurturing, family-oriented",
        4: "Creative, dramatic, generous",
        5: "Analytical, perfectionist, service-oriented",
        6: "Harmonious, diplomatic, aesthetic",
        7: "Intense, passionate, transformative",
        8: "Adventurous, philosophical, expansive",
        9: "Ambitious, disciplined, responsible",
        10: "Progressive, humanitarian, innovative",
        11: "Intuitive, compassionate, spiritual",
    }
    return meanings.get(sign_index % 12, "Balanced, adaptable")


def chart_summary_text(chart: BirthChart, lang: str = "en") -> str:
    """Enhanced chart summary with all features"""
    from translations import sign_name, planet_name, nakshatra_name
    
    lines = [
        f"System: {'Vedic sidereal' if chart.system == 'vedic' else 'Western tropical'}",
        f"Ayanamsa: {chart.ayanamsa}",
        f"Ascendant: {sign_name(chart.ascendant.sign_index, lang)} at {chart.ascendant.degree_in_sign:.1f}°",
    ]
    
    for p in chart.planets:
        retro = " (retrograde)" if p.retrograde else ""
        lines.append(
            f"{planet_name(p.key, lang)}: {sign_name(p.sign_index, lang)} "
            f"{p.degree_in_sign:.1f}°{retro} (H{p.house})"
        )
    
    if chart.system == "vedic":
        lines.append(f"\n🌙 Nakshatra: {nakshatra_name(chart.nakshatra_index, lang)} (Pada {chart.nakshatra_pada})")
    
    if chart.yogas:
        lines.append("\n🌟 Yogas:")
        for yoga in chart.yogas[:5]:
            lines.append(f"  • {yoga['name']}: {yoga['description']}")
    
    if chart.dasha:
        lines.append(f"\n📅 Current Dasha: {chart.dasha.get('current_dasha_name', 'Unknown')} "
                    f"({chart.dasha.get('remaining_years', 0):.1f} years remaining)")
    
    return "\n".join(lines)