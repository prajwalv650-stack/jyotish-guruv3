"""
Jyotish Guru v3 — Flask + Swiss Ephemeris + Gemini AI
Astronomical accuracy: real planetary positions via pyswisseph
Gemini 2.0 Flash: 8192 output tokens, fast, free tier
"""

import os
import json
import math
import datetime
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

try:
    import swisseph as swe
    SWISSEPH_AVAILABLE = True
except ImportError:
    SWISSEPH_AVAILABLE = False
    print("⚠️  pyswisseph not available — will use AI-only mode")

app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL   = "gemini-2.0-flash"
GEMINI_URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def call_gemini(system_text: str, user_text: str) -> str:
    """Call Gemini API and return the text response."""
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set on server.")

    payload = {
        "system_instruction": {"parts": [{"text": system_text}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.65,
            "topP": 0.95,
        }
    }
    resp = requests.post(
        GEMINI_URL,
        params={"key": GEMINI_API_KEY},
        headers={"Content-Type": "application/json"},
        json=payload,
        timeout=120
    )
    if not resp.ok:
        err = resp.json().get("error", {}).get("message", f"HTTP {resp.status_code}")
        raise RuntimeError(f"Gemini API error: {err}")

    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

# ─── VEDIC CONSTANTS ───────────────────────────────────────────────────────────

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
         "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

SIGN_LORDS = {
    "Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
    "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
    "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"
}

NAKSHATRAS = [
    {"name":"Ashwini",    "lord":"Ketu",    "gana":"Deva",    "nadi":"Vata",  "yoni":"Horse",    "yg":"M","varna":"Vaishya",  "rashi":"Aries"},
    {"name":"Bharani",    "lord":"Venus",   "gana":"Manushya","nadi":"Pitta", "yoni":"Elephant", "yg":"M","varna":"Mleccha",  "rashi":"Aries"},
    {"name":"Krittika",   "lord":"Sun",     "gana":"Rakshasa","nadi":"Kapha", "yoni":"Goat",     "yg":"F","varna":"Brahmin",  "rashi":"Aries"},
    {"name":"Rohini",     "lord":"Moon",    "gana":"Manushya","nadi":"Kapha", "yoni":"Snake",    "yg":"M","varna":"Shudra",   "rashi":"Taurus"},
    {"name":"Mrigashira", "lord":"Mars",    "gana":"Deva",    "nadi":"Pitta", "yoni":"Snake",    "yg":"F","varna":"Vaishya",  "rashi":"Taurus"},
    {"name":"Ardra",      "lord":"Rahu",    "gana":"Manushya","nadi":"Vata",  "yoni":"Dog",      "yg":"F","varna":"Mleccha",  "rashi":"Gemini"},
    {"name":"Punarvasu",  "lord":"Jupiter", "gana":"Deva",    "nadi":"Vata",  "yoni":"Cat",      "yg":"F","varna":"Vaishya",  "rashi":"Gemini"},
    {"name":"Pushya",     "lord":"Saturn",  "gana":"Deva",    "nadi":"Pitta", "yoni":"Goat",     "yg":"M","varna":"Kshatriya","rashi":"Cancer"},
    {"name":"Ashlesha",   "lord":"Mercury", "gana":"Rakshasa","nadi":"Kapha", "yoni":"Cat",      "yg":"M","varna":"Mleccha",  "rashi":"Cancer"},
    {"name":"Magha",      "lord":"Ketu",    "gana":"Rakshasa","nadi":"Kapha", "yoni":"Rat",      "yg":"M","varna":"Shudra",   "rashi":"Leo"},
    {"name":"Purva Phalguni","lord":"Venus","gana":"Manushya","nadi":"Pitta", "yoni":"Rat",      "yg":"F","varna":"Brahmin",  "rashi":"Leo"},
    {"name":"Uttara Phalguni","lord":"Sun", "gana":"Manushya","nadi":"Vata",  "yoni":"Cow",      "yg":"M","varna":"Kshatriya","rashi":"Leo"},
    {"name":"Hasta",      "lord":"Moon",    "gana":"Deva",    "nadi":"Vata",  "yoni":"Buffalo",  "yg":"F","varna":"Vaishya",  "rashi":"Virgo"},
    {"name":"Chitra",     "lord":"Mars",    "gana":"Rakshasa","nadi":"Pitta", "yoni":"Tiger",    "yg":"F","varna":"Mleccha",  "rashi":"Virgo"},
    {"name":"Swati",      "lord":"Rahu",    "gana":"Deva",    "nadi":"Kapha", "yoni":"Buffalo",  "yg":"M","varna":"Mleccha",  "rashi":"Libra"},
    {"name":"Vishakha",   "lord":"Jupiter", "gana":"Rakshasa","nadi":"Kapha", "yoni":"Tiger",    "yg":"M","varna":"Mleccha",  "rashi":"Libra"},
    {"name":"Anuradha",   "lord":"Saturn",  "gana":"Deva",    "nadi":"Pitta", "yoni":"Deer",     "yg":"F","varna":"Shudra",   "rashi":"Scorpio"},
    {"name":"Jyeshtha",   "lord":"Mercury", "gana":"Rakshasa","nadi":"Vata",  "yoni":"Deer",     "yg":"M","varna":"Mleccha",  "rashi":"Scorpio"},
    {"name":"Mula",       "lord":"Ketu",    "gana":"Rakshasa","nadi":"Vata",  "yoni":"Dog",      "yg":"M","varna":"Mleccha",  "rashi":"Sagittarius"},
    {"name":"Purva Ashadha","lord":"Venus", "gana":"Manushya","nadi":"Pitta", "yoni":"Monkey",   "yg":"M","varna":"Brahmin",  "rashi":"Sagittarius"},
    {"name":"Uttara Ashadha","lord":"Sun",  "gana":"Manushya","nadi":"Kapha", "yoni":"Mongoose", "yg":"M","varna":"Kshatriya","rashi":"Sagittarius"},
    {"name":"Shravana",   "lord":"Moon",    "gana":"Deva",    "nadi":"Kapha", "yoni":"Monkey",   "yg":"F","varna":"Mleccha",  "rashi":"Capricorn"},
    {"name":"Dhanishtha", "lord":"Mars",    "gana":"Rakshasa","nadi":"Pitta", "yoni":"Lion",     "yg":"F","varna":"Shudra",   "rashi":"Capricorn"},
    {"name":"Shatabhisha","lord":"Rahu",    "gana":"Rakshasa","nadi":"Vata",  "yoni":"Horse",    "yg":"F","varna":"Mleccha",  "rashi":"Aquarius"},
    {"name":"Purva Bhadrapada","lord":"Jupiter","gana":"Manushya","nadi":"Vata","yoni":"Lion",   "yg":"M","varna":"Brahmin",  "rashi":"Aquarius"},
    {"name":"Uttara Bhadrapada","lord":"Saturn","gana":"Manushya","nadi":"Pitta","yoni":"Cow",   "yg":"F","varna":"Kshatriya","rashi":"Pisces"},
    {"name":"Revati",     "lord":"Mercury", "gana":"Deva",    "nadi":"Kapha", "yoni":"Elephant", "yg":"F","varna":"Shudra",   "rashi":"Pisces"},
]

DASHA_LORDS_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DASHA_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN
} if SWISSEPH_AVAILABLE else {}

# ─── EPHEMERIS CALCULATIONS ────────────────────────────────────────────────────

def parse_birth(dob: str, tob: str, place: str) -> dict:
    """Parse birth details. place is 'City, Country' — we use a simple timezone offset."""
    # Basic UTC offset from place name heuristics (fallback; ideally use geocoding API)
    tz_offsets = {
        "india":5.5,"mumbai":5.5,"delhi":5.5,"bangalore":5.5,"bengaluru":5.5,
        "chennai":5.5,"kolkata":5.5,"hyderabad":5.5,"pune":5.5,"ahmedabad":5.5,
        "jaipur":5.5,"lucknow":5.5,"kanpur":5.5,"surat":5.5,"patna":5.5,
        "london":0,"uk":0,"england":0,
        "new york":-5,"usa":-5,"us":-5,"america":-5,"california":-8,"chicago":-6,
        "dubai":4,"uae":4,
        "singapore":8,"malaysia":8,
        "australia":10,"sydney":10,"melbourne":10,
        "germany":1,"france":1,"italy":1,"spain":1,"europe":1,
        "canada":-5,"toronto":-5,"vancouver":-8,
        "japan":9,"tokyo":9,
        "china":8,"beijing":8,"shanghai":8,
        "nepal":5.75,"kathmandu":5.75,
        "sri lanka":5.5,"pakistan":5,"bangladesh":6,
    }
    place_lower = place.lower()
    tz = 5.5  # default India
    for key, offset in tz_offsets.items():
        if key in place_lower:
            tz = offset
            break

    # Parse date and time
    try:
        date_obj = datetime.date.fromisoformat(dob)
        if tob:
            h, m = map(int, tob.split(":"))
        else:
            h, m = 6, 0  # default sunrise if unknown
    except:
        date_obj = datetime.date.today()
        h, m = 6, 0

    # Convert local time to UT
    local_decimal = h + m/60.0
    ut = local_decimal - tz
    if ut < 0:
        ut += 24
        date_obj -= datetime.timedelta(days=1)
    elif ut >= 24:
        ut -= 24
        date_obj += datetime.timedelta(days=1)

    return {
        "year": date_obj.year,
        "month": date_obj.month,
        "day": date_obj.day,
        "ut": ut,
        "tz": tz,
        "place": place
    }


def get_julian_day(year, month, day, ut):
    if SWISSEPH_AVAILABLE:
        return swe.julday(year, month, day, ut)
    return None


def sidereal_longitude(jd, planet_id):
    """Get sidereal longitude using Lahiri ayanamsa (most common in India)."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result, _ = swe.calc_ut(jd, planet_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    return result[0]


def get_rahu_ketu(jd):
    """Rahu = True Node, Ketu = True Node + 180."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    result, _ = swe.calc_ut(jd, swe.TRUE_NODE, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
    rahu = result[0] % 360
    ketu = (rahu + 180) % 360
    return rahu, ketu


def get_ascendant(jd, lat, lon):
    """Calculate Lagna (Ascendant) using birth coordinates."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    return ascmc[0] % 360  # ascendant longitude


def longitude_to_sign_degree(lon):
    sign_index = int(lon / 30)
    degree = lon % 30
    return SIGNS[sign_index % 12], degree, sign_index


def longitude_to_nakshatra(lon):
    nak_index = int(lon / (360/27))
    pada = int((lon % (360/27)) / (360/108)) + 1
    return nak_index % 27, pada


def get_house(planet_lon, asc_lon):
    """Get house number (1-12) from planet longitude and ascendant longitude."""
    diff = (planet_lon - asc_lon) % 360
    return int(diff / 30) + 1


def compute_vimshottari_dasha(moon_lon, birth_date_str):
    """Compute current Mahadasha and Antardasha from Moon's nakshatra."""
    nak_idx, pada = longitude_to_nakshatra(moon_lon)
    nak = NAKSHATRAS[nak_idx]
    nak_lord = nak["lord"]

    # Position within nakshatra
    nak_span = 360 / 27  # 13.333...
    pos_in_nak = moon_lon % nak_span
    fraction_elapsed = pos_in_nak / nak_span

    # Starting dasha is the nakshatra lord
    lord_idx = DASHA_LORDS_ORDER.index(nak_lord)
    years_elapsed_in_start = fraction_elapsed * DASHA_YEARS[nak_lord]

    # Build dasha sequence from birth
    try:
        birth_date = datetime.date.fromisoformat(birth_date_str)
    except:
        birth_date = datetime.date.today()

    today = datetime.date.today()
    years_since_birth = (today - birth_date).days / 365.25

    # Remaining years in starting dasha
    remaining_start = DASHA_YEARS[nak_lord] - years_elapsed_in_start

    # Walk through dashas to find current one
    cumulative = 0
    current_dasha_lord = None
    years_into_dasha = 0

    dasha_sequence = []
    idx = lord_idx
    cum = -years_elapsed_in_start  # account for partial start
    for _ in range(9):
        lord = DASHA_LORDS_ORDER[idx % 9]
        start_yr = cum
        end_yr = cum + DASHA_YEARS[lord]
        dasha_sequence.append({
            "lord": lord,
            "start_yr": start_yr,
            "end_yr": end_yr,
            "duration": DASHA_YEARS[lord]
        })
        if start_yr <= years_since_birth < end_yr:
            current_dasha_lord = lord
            years_into_dasha = years_since_birth - start_yr
        cum = end_yr
        idx += 1

    if not current_dasha_lord:
        current_dasha_lord = DASHA_LORDS_ORDER[lord_idx]
        years_into_dasha = years_since_birth

    # Compute Antardasha within current Mahadasha
    maha_duration = DASHA_YEARS[current_dasha_lord]
    maha_idx = DASHA_LORDS_ORDER.index(current_dasha_lord)
    antar_cumulative = 0
    current_antardasha = current_dasha_lord
    years_remaining_maha = maha_duration - years_into_dasha

    for i in range(9):
        antar_lord = DASHA_LORDS_ORDER[(maha_idx + i) % 9]
        antar_duration = (DASHA_YEARS[antar_lord] / 120) * maha_duration
        if years_into_dasha <= antar_cumulative + antar_duration:
            current_antardasha = antar_lord
            break
        antar_cumulative += antar_duration

    return {
        "mahadasha": current_dasha_lord,
        "antardasha": current_antardasha,
        "years_into_mahadasha": round(years_into_dasha, 2),
        "years_remaining_mahadasha": round(years_remaining_maha, 2),
        "sequence": dasha_sequence[:4]
    }


def check_mangal_dosha(mars_house):
    """Mangal Dosha if Mars in houses 1,2,4,7,8,12."""
    return mars_house in [1, 2, 4, 7, 8, 12]


def compute_chart(dob: str, tob: str, place: str, lat: float = 12.9716, lon: float = 77.5946) -> dict:
    """
    Compute complete Vedic birth chart using Swiss Ephemeris.
    lat/lon defaults to Bengaluru. Frontend should pass actual coordinates.
    """
    if not SWISSEPH_AVAILABLE:
        return {"error": "ephemeris_unavailable", "mode": "ai_only"}

    birth = parse_birth(dob, tob, place)
    jd = get_julian_day(birth["year"], birth["month"], birth["day"], birth["ut"])

    planets = {}
    for name, pid in PLANET_IDS.items():
        try:
            lon_p = sidereal_longitude(jd, pid)
            sign, deg, sign_idx = longitude_to_sign_degree(lon_p)
            nak_idx, pada = longitude_to_nakshatra(lon_p)
            planets[name] = {
                "longitude": round(lon_p, 4),
                "sign": sign,
                "degree": round(deg, 2),
                "sign_index": sign_idx,
                "nakshatra": NAKSHATRAS[nak_idx]["name"],
                "nakshatra_lord": NAKSHATRAS[nak_idx]["lord"],
                "pada": pada,
            }
        except Exception as e:
            planets[name] = {"error": str(e)}

    # Rahu / Ketu
    try:
        rahu_lon, ketu_lon = get_rahu_ketu(jd)
        for name, lon_p in [("Rahu", rahu_lon), ("Ketu", ketu_lon)]:
            sign, deg, sign_idx = longitude_to_sign_degree(lon_p)
            nak_idx, pada = longitude_to_nakshatra(lon_p)
            planets[name] = {
                "longitude": round(lon_p, 4),
                "sign": sign,
                "degree": round(deg, 2),
                "sign_index": sign_idx,
                "nakshatra": NAKSHATRAS[nak_idx]["name"],
                "nakshatra_lord": NAKSHATRAS[nak_idx]["lord"],
                "pada": pada,
            }
    except Exception as e:
        planets["Rahu"] = {"error": str(e)}
        planets["Ketu"] = {"error": str(e)}

    # Ascendant
    try:
        asc_lon = get_ascendant(jd, lat, lon)
        asc_sign, asc_deg, asc_sign_idx = longitude_to_sign_degree(asc_lon)
    except Exception as e:
        asc_lon, asc_sign, asc_deg, asc_sign_idx = 0, "Aries", 0, 0

    # House placements
    for name, p in planets.items():
        if "longitude" in p:
            p["house"] = get_house(p["longitude"], asc_lon)

    # Moon nakshatra details
    moon_lon = planets.get("Moon", {}).get("longitude", 0)
    moon_nak_idx, moon_pada = longitude_to_nakshatra(moon_lon)
    moon_nak = NAKSHATRAS[moon_nak_idx]

    # Dasha
    dasha = compute_vimshottari_dasha(moon_lon, dob)

    # Mangal Dosha
    mars_house = planets.get("Mars", {}).get("house", 0)
    mangal_dosha = check_mangal_dosha(mars_house)

    # Atmakaraka (planet with highest degree in sign)
    atmakaraka = None
    max_deg = -1
    for name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        p = planets.get(name, {})
        if p.get("degree", -1) > max_deg:
            max_deg = p["degree"]
            atmakaraka = name

    return {
        "lagna": {
            "sign": asc_sign,
            "degree": round(asc_deg, 2),
            "sign_index": asc_sign_idx,
            "longitude": round(asc_lon, 4)
        },
        "planets": planets,
        "moon_nakshatra": moon_nak["name"],
        "moon_nakshatra_index": moon_nak_idx,
        "moon_pada": moon_pada,
        "moon_rashi": planets.get("Moon", {}).get("sign", ""),
        "moon_nakshatra_lord": moon_nak["lord"],
        "moon_gana": moon_nak["gana"],
        "moon_nadi": moon_nak["nadi"],
        "moon_yoni": moon_nak["yoni"],
        "moon_varna": moon_nak["varna"],
        "dasha": dasha,
        "mangal_dosha": mangal_dosha,
        "atmakaraka": atmakaraka,
        "ayanamsa": "Lahiri",
        "ephemeris": "Swiss Ephemeris"
    }


# ─── KOOTA MATCHING ─────────────────────────────────────────────────────────────

YONI_COMPAT = {
    "Horse-Horse":4,"Horse-Elephant":0,"Horse-Goat":3,"Horse-Snake":2,"Horse-Dog":3,
    "Horse-Cat":2,"Horse-Rat":2,"Horse-Cow":2,"Horse-Buffalo":2,"Horse-Tiger":1,
    "Horse-Deer":2,"Horse-Monkey":2,"Horse-Mongoose":3,"Horse-Lion":1,
    "Elephant-Elephant":4,"Elephant-Goat":3,"Elephant-Snake":3,"Elephant-Dog":2,
    "Elephant-Cat":2,"Elephant-Rat":2,"Elephant-Cow":3,"Elephant-Buffalo":3,
    "Elephant-Tiger":2,"Elephant-Deer":3,"Elephant-Monkey":2,"Elephant-Mongoose":3,"Elephant-Lion":2,
    "Goat-Goat":4,"Goat-Snake":2,"Goat-Dog":2,"Goat-Cat":3,"Goat-Rat":2,
    "Goat-Cow":3,"Goat-Buffalo":3,"Goat-Tiger":2,"Goat-Deer":3,"Goat-Monkey":3,
    "Goat-Mongoose":3,"Goat-Lion":2,
    "Snake-Snake":4,"Snake-Dog":0,"Snake-Cat":3,"Snake-Rat":2,"Snake-Cow":2,
    "Snake-Buffalo":2,"Snake-Tiger":2,"Snake-Deer":2,"Snake-Monkey":2,
    "Snake-Mongoose":0,"Snake-Lion":2,
    "Dog-Dog":4,"Dog-Cat":2,"Dog-Rat":2,"Dog-Cow":2,"Dog-Buffalo":2,
    "Dog-Tiger":2,"Dog-Deer":2,"Dog-Monkey":2,"Dog-Mongoose":2,"Dog-Lion":2,
    "Cat-Cat":4,"Cat-Rat":0,"Cat-Cow":2,"Cat-Buffalo":2,"Cat-Tiger":2,
    "Cat-Deer":2,"Cat-Monkey":3,"Cat-Mongoose":2,"Cat-Lion":2,
    "Rat-Rat":4,"Rat-Cow":2,"Rat-Buffalo":2,"Rat-Tiger":2,"Rat-Deer":2,
    "Rat-Monkey":2,"Rat-Mongoose":2,"Rat-Lion":2,
    "Cow-Cow":4,"Cow-Buffalo":3,"Cow-Tiger":2,"Cow-Deer":3,"Cow-Monkey":2,
    "Cow-Mongoose":2,"Cow-Lion":2,
    "Buffalo-Buffalo":4,"Buffalo-Tiger":2,"Buffalo-Deer":2,"Buffalo-Monkey":2,
    "Buffalo-Mongoose":2,"Buffalo-Lion":2,
    "Tiger-Tiger":4,"Tiger-Deer":2,"Tiger-Monkey":2,"Tiger-Mongoose":2,"Tiger-Lion":3,
    "Deer-Deer":4,"Deer-Monkey":2,"Deer-Mongoose":2,"Deer-Lion":2,
    "Monkey-Monkey":4,"Monkey-Mongoose":2,"Monkey-Lion":2,
    "Mongoose-Mongoose":4,"Mongoose-Lion":0,
    "Lion-Lion":4,
}
PLANET_FRIENDS = {
    "Sun":    {"friends":["Moon","Mars","Jupiter"],        "enemies":["Venus","Saturn"],     "neutral":["Mercury"]},
    "Moon":   {"friends":["Sun","Mercury"],                "enemies":[],                     "neutral":["Mars","Jupiter","Venus","Saturn"]},
    "Mars":   {"friends":["Sun","Moon","Jupiter"],         "enemies":["Mercury"],            "neutral":["Venus","Saturn"]},
    "Mercury":{"friends":["Sun","Venus"],                  "enemies":["Moon"],               "neutral":["Mars","Jupiter","Saturn"]},
    "Jupiter":{"friends":["Sun","Moon","Mars"],            "enemies":["Mercury","Venus"],    "neutral":["Saturn"]},
    "Venus":  {"friends":["Mercury","Saturn"],             "enemies":["Sun","Moon"],         "neutral":["Mars","Jupiter"]},
    "Saturn": {"friends":["Mercury","Venus"],              "enemies":["Sun","Moon","Mars"],  "neutral":["Jupiter"]},
    "Rahu":   {"friends":["Venus","Saturn","Mercury"],     "enemies":["Sun","Moon","Mars"],  "neutral":["Jupiter"]},
    "Ketu":   {"friends":["Mars","Venus","Saturn"],        "enemies":["Sun","Moon","Mercury"],"neutral":["Jupiter"]},
}
RASHI_ORDER = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
VASHYA = {
    "Aries":["Leo","Scorpio"],"Taurus":["Cancer","Libra"],"Gemini":["Virgo","Pisces"],
    "Cancer":["Scorpio","Sagittarius"],"Leo":["Libra"],"Virgo":["Gemini","Pisces"],
    "Libra":["Capricorn","Virgo"],"Scorpio":["Cancer"],"Sagittarius":["Pisces"],
    "Capricorn":["Aries","Aquarius"],"Aquarius":["Aries"],"Pisces":["Capricorn"]
}
VARNA_RANK = {"Brahmin":4,"Kshatriya":3,"Vaishya":2,"Shudra":1,"Mleccha":1}

def yoni_score(a, b):
    k1, k2 = f"{a}-{b}", f"{b}-{a}"
    return YONI_COMPAT.get(k1, YONI_COMPAT.get(k2, 2))

def graha_maitri(r1, r2):
    l1, l2 = SIGN_LORDS.get(r1), SIGN_LORDS.get(r2)
    if not l1 or not l2: return 3
    if l1 == l2: return 5
    f1, f2 = PLANET_FRIENDS.get(l1,{}), PLANET_FRIENDS.get(l2,{})
    rel1 = 'F' if l2 in f1.get("friends",[]) else ('E' if l2 in f1.get("enemies",[]) else 'N')
    rel2 = 'F' if l1 in f2.get("friends",[]) else ('E' if l1 in f2.get("enemies",[]) else 'N')
    combo = rel1 + rel2
    return {"FF":5,"FN":4,"NF":4,"NN":3,"FE":1,"EF":1,"NE":1,"EN":1,"EE":0}.get(combo, 3)

def gana_score(g1, g2):
    if g1 == g2: return 6
    if {g1,g2} == {"Deva","Manushya"}: return 5
    if "Rakshasa" in {g1,g2}: return 0 if g1!=g2 else 6
    return 0

def nadi_score(n1, n2): return 0 if n1 == n2 else 8

def varna_score(v1, v2):
    return 1 if (VARNA_RANK.get(v1,1) >= VARNA_RANK.get(v2,1)) else 0

def vashya_score(r1, r2):
    v1 = r2 in VASHYA.get(r1, [])
    v2 = r1 in VASHYA.get(r2, [])
    return 2 if (v1 and v2) else (1 if (v1 or v2) else 0)

def bhakoot_score(r1, r2):
    i1, i2 = RASHI_ORDER.index(r1) if r1 in RASHI_ORDER else 0, RASHI_ORDER.index(r2) if r2 in RASHI_ORDER else 0
    fwd = (i2 - i1 + 12) % 12 + 1
    bwd = (i1 - i2 + 12) % 12 + 1
    return 0 if (6 in {fwd,bwd} or 8 in {fwd,bwd}) else 7

def tara_score(nk1, nk2):
    count = ((nk2 - nk1 + 27) % 27) + 1
    tara = ((count - 1) % 9) + 1
    return 0 if tara in [3,5,7] else 3

def compute_kootas(nk1_idx, nk2_idx, rashi1, rashi2):
    n1, n2 = NAKSHATRAS[nk1_idx], NAKSHATRAS[nk2_idx]
    return {
        "varna":       {"score": varna_score(n2["varna"], n1["varna"]), "max":1,  "detail":f"{n1['varna']} × {n2['varna']}"},
        "vashya":      {"score": vashya_score(rashi1, rashi2),          "max":2,  "detail":f"{rashi1} × {rashi2}"},
        "tara":        {"score": tara_score(nk1_idx, nk2_idx),          "max":3,  "detail":f"Nakshatra gap {((nk2_idx-nk1_idx+27)%27)+1}, Tara {(((nk2_idx-nk1_idx+27)%27)%9)+1}"},
        "yoni":        {"score": yoni_score(n1["yoni"], n2["yoni"]),    "max":4,  "detail":f"{n1['yoni']} (P1) × {n2['yoni']} (P2)"},
        "grahaMaitri": {"score": graha_maitri(rashi1, rashi2),          "max":5,  "detail":f"{SIGN_LORDS.get(rashi1,'?')} × {SIGN_LORDS.get(rashi2,'?')}"},
        "gana":        {"score": gana_score(n1["gana"], n2["gana"]),    "max":6,  "detail":f"{n1['gana']} (P1) × {n2['gana']} (P2)"},
        "bhakoot":     {"score": bhakoot_score(rashi1, rashi2),         "max":7,  "detail":f"{rashi1} × {rashi2}"},
        "nadi":        {"score": nadi_score(n1["nadi"], n2["nadi"]),    "max":8,  "detail":f"{n1['nadi']} (P1) × {n2['nadi']} (P2)"},
    }

# ─── AI REPORT GENERATION ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are Jyotish Guru — a deeply learned Vedic astrologer with mastery of Parashari Jyotish, Nadi astrology, and classical texts including Brihat Parashara Hora Shastra, Phala Deepika, and Saravali.

You receive ASTRONOMICALLY ACCURATE chart data computed via Swiss Ephemeris with Lahiri ayanamsa. These positions are precise — trust them completely and build your analysis entirely from this data.

CORE PRINCIPLES:
1. Be specific to the actual chart data provided — never generic
2. Use correct house rulership and aspect theory (Parashari aspects)
3. Identify yogas from actual planetary positions (not assumptions)
4. Consider mutual aspects, conjunctions, and house lords
5. Acknowledge both benefic and malefic influences honestly
6. Connect dasha timing to specific life areas based on the chart
7. Use warm, wise, non-fear-based language
8. Employ proper Vedic terminology throughout
9. Note that Rahu/Ketu are always retrograde in Vedic astrology
10. Format all output with ### headings and bullet points for clarity

For yogas: check for Raj Yoga (lord of kendra + trikona in mutual angles), Dhana Yoga (2nd/11th lord connections), Gaja Kesari (Jupiter-Moon relationship), Kemadruma, Vipareeta Raja Yoga, etc. based on ACTUAL positions.

For remedies: recommend traditional Vedic remedies (mantra, gemstone, puja, charity, fasting) appropriate to the chart's specific challenges."""


def build_kundali_prompt(name, dob, tob, pob, chart: dict) -> str:
    planets = chart.get("planets", {})
    lagna = chart.get("lagna", {})
    dasha = chart.get("dasha", {})

    planet_lines = []
    for p_name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        p = planets.get(p_name, {})
        if "sign" in p:
            planet_lines.append(
                f"  {p_name}: {p['sign']} {p.get('degree',0):.1f}° | House {p.get('house','?')} | "
                f"Nakshatra: {p.get('nakshatra','?')} Pada {p.get('pada','?')}"
            )
        else:
            planet_lines.append(f"  {p_name}: [calculation unavailable]")

    dasha_seq = dasha.get("sequence", [])
    dasha_seq_str = " → ".join([f"{d['lord']} (until +{d['end_yr']:.1f}yr)" for d in dasha_seq])

    return f"""ASTRONOMICALLY COMPUTED VEDIC BIRTH CHART (Swiss Ephemeris, Lahiri Ayanamsa)
==========================================================================

NATIVE: {name}
Date of Birth: {dob}  |  Time: {tob}  |  Place: {pob}

LAGNA (ASCENDANT): {lagna.get('sign','?')} {lagna.get('degree',0):.2f}°

PLANETARY POSITIONS:
{chr(10).join(planet_lines)}

MOON: {chart.get('moon_nakshatra','?')} Nakshatra, Pada {chart.get('moon_pada','?')} | Rashi: {chart.get('moon_rashi','?')}
ATMAKARAKA: {chart.get('atmakaraka','?')}
MANGAL DOSHA: {'Present' if chart.get('mangal_dosha') else 'Absent'}

VIMSHOTTARI DASHA:
  Current Mahadasha: {dasha.get('mahadasha','?')} ({dasha.get('years_into_mahadasha',0):.1f} years elapsed, {dasha.get('years_remaining_mahadasha',0):.1f} years remaining)
  Current Antardasha: {dasha.get('antardasha','?')}
  Upcoming sequence: {dasha_seq_str}

==========================================================================
Please generate a comprehensive Kundali report with the following sections:

### Lagna & Fundamental Nature
Analyse the Lagna lord's placement, strength, and what it reveals about the native's core personality, body constitution (Prakriti), and life approach.

### Moon — Mind, Emotions & Nakshatra
Detailed analysis of the Moon sign, nakshatra (deity, symbol, shakti), pada significance, and what it says about the mind, mother, and emotional patterns.

### Planetary Overview & Key Yogas
For each planet: house lordship, placement strength (exaltation/debilitation/own sign/friend/enemy), and aspects. Identify all significant yogas (Raj Yoga, Dhana Yoga, Gaja Kesari, etc.) with exact reasons from the chart.

### Current Dasha Analysis — {dasha.get('mahadasha','?')} / {dasha.get('antardasha','?')}
What this dasha combination means specifically for {name} based on the chart's house placements. When does the next dasha shift occur and what will change?

### Career, Dharma & Finance
**Short term (1–2 years):** Based on current dasha and planetary transits.
**Medium term (3–5 years):** Upcoming dasha shifts and their impact.
**Long term:** Core career indicators from 10th house and its lord.
**Wealth indicators:** 2nd and 11th house analysis.

### Love, Marriage & Relationships
**7th house & its lord:** Spouse characteristics, timing indicators.
**Venus analysis:** Relationship approach and patterns.
**Short / Medium / Long term predictions.**
**If Mangal Dosha present:** Traditional cancellation conditions and remedies.

### Health & Vitality
**Prakriti:** Based on Lagna and its lord.
**Vulnerable areas:** Based on afflicted houses/planets.
**Protective factors:** Strong benefics and their role.
**Ayurvedic guidance:** Specific to this chart.

### Spiritual Path & Dharma
**9th house & Jupiter:** Dharmic inclinations.
**Ketu's placement:** Past life karma and innate gifts.
**Rahu's direction:** Soul's evolutionary calling this lifetime.
**Atmakaraka {chart.get('atmakaraka','?')}:** Core soul lessons.

### Remedies & Strengthening Measures
Specific traditional remedies based on weak or afflicted planets in this chart:
- Mantras (with specific names, not generic)
- Gemstones (with appropriate specifications)
- Charitable acts and fasting days
- Deity worship suited to this chart

Be deeply specific to this chart. Every statement should trace back to an actual planetary position provided above."""


def build_match_prompt(n1, n2, c1, c2, koota, total, mangal_status, nadi_exception, dob1, dob2) -> str:
    r1 = c1.get("moon_rashi","")
    r2 = c2.get("moon_rashi","")
    nak1 = c1.get("moon_nakshatra","")
    nak2 = c2.get("moon_nakshatra","")
    l1 = c1.get("lagna",{}).get("sign","")
    l2 = c2.get("lagna",{}).get("sign","")
    d1 = c1.get("dasha",{})
    d2 = c2.get("dasha",{})

    koota_lines = "\n".join([
        f"  {k.title()}: {v['score']}/{v['max']} — {v['detail']}"
        for k, v in koota.items()
    ])

    return f"""KUNDALI MATCHING — ASTRONOMICALLY COMPUTED (Swiss Ephemeris, Lahiri Ayanamsa)
===========================================================================

PERSON 1: {n1} | DOB: {dob1}
  Moon: {nak1} Nakshatra | Rashi: {r1} | Lagna: {l1}
  Current Dasha: {d1.get('mahadasha','?')}/{d1.get('antardasha','?')} ({d1.get('years_remaining_mahadasha',0):.1f} yrs remaining)
  Mangal Dosha: {'Present' if c1.get('mangal_dosha') else 'Absent'}

PERSON 2: {n2} | DOB: {dob2}
  Moon: {nak2} Nakshatra | Rashi: {r2} | Lagna: {l2}
  Current Dasha: {d2.get('mahadasha','?')}/{d2.get('antardasha','?')} ({d2.get('years_remaining_mahadasha',0):.1f} yrs remaining)
  Mangal Dosha: {'Present' if c2.get('mangal_dosha') else 'Absent'}

ASHTA-KOOTA SCORES (computed from traditional lookup tables):
{koota_lines}
TOTAL: {total}/36

MANGAL DOSHA STATUS: {mangal_status}
{f'NADI NOTE: {nadi_exception}' if nadi_exception else ''}

===========================================================================
Generate a comprehensive Kundali matching report:

### Individual Chart Overview — {n1}
Lagna {l1} characteristics, Moon in {nak1} — personality, strengths, relationship approach, current {d1.get('mahadasha','?')} dasha impact on life.

### Individual Chart Overview — {n2}
Lagna {l2} characteristics, Moon in {nak2} — personality, strengths, relationship approach, current {d2.get('mahadasha','?')} dasha impact on life.

### Ashta-Koota Deep Analysis
Interpret EACH of the 8 kootas specifically for {n1} and {n2}:
- What the score means for THIS couple (not generic definitions)
- Which kootas are their strengths and which need attention
- Overall compatibility narrative based on the total {total}/36

### Nakshatras & Natural Chemistry
How {nak1} and {nak2} interact by nature — temperament, values, communication style. What this predicts about daily life together.

### Gana Compatibility — Temperament Match
{c1.get('moon_nakshatra','?')} Gana vs {c2.get('moon_nakshatra','?')} Gana: detailed analysis of life approach compatibility.

### Dosha Assessment
{mangal_status}
{nadi_exception if nadi_exception else 'Nadi Dosha: Absent — highly auspicious.'}
Traditional cancellation conditions and remedies where applicable.

### Dasha Interaction — Timing Compatibility
How the current and upcoming dashas of both persons will interact:
- **Immediate (1–2 years):** {n1} in {d1.get('mahadasha','?')} | {n2} in {d2.get('mahadasha','?')}
- **Medium term (3–5 years):** Upcoming transitions and their relationship impact
- **Long term:** Overall life arc compatibility

### Strengths of This Union
3–5 specific, chart-grounded reasons this match works well.

### Areas Requiring Conscious Effort
Honest, compassionate analysis of challenges — with practical advice.

### Auspicious Muhurta Guidance
General guidance on timing for engagement/marriage based on upcoming favorable dasha periods for both.

### Final Compatibility Verdict & Remedies
Overall assessment, specific remedies for any doshas, and closing blessing for the couple."""



# ─── FLASK ROUTES ──────────────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "ephemeris": "Swiss Ephemeris (Lahiri)" if SWISSEPH_AVAILABLE else "AI-only mode",
        "ai": f"Gemini {GEMINI_MODEL}",
        "key_configured": bool(GEMINI_API_KEY)
    })


@app.route("/api/chart", methods=["POST"])
def api_chart():
    """Compute chart from birth data. Returns structured chart data."""
    d = request.json or {}
    dob = d.get("dob","")
    tob = d.get("tob","")
    pob = d.get("pob","")
    lat = float(d.get("lat", 12.9716))
    lon = float(d.get("lon", 77.5946))
    if not dob:
        return jsonify({"error": "dob required"}), 400
    chart = compute_chart(dob, tob, pob, lat, lon)
    return jsonify(chart)


@app.route("/api/kundali", methods=["POST"])
def api_kundali():
    """Generate full kundali report using Gemini AI."""
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not configured on server"}), 500

    d = request.json or {}
    name = d.get("name", "the native")
    dob  = d.get("dob","")
    tob  = d.get("tob","")
    pob  = d.get("pob","")
    lat  = float(d.get("lat", 12.9716))
    lon  = float(d.get("lon", 77.5946))

    if not dob:
        return jsonify({"error": "dob required"}), 400

    chart = compute_chart(dob, tob, pob, lat, lon)

    if chart.get("error") == "ephemeris_unavailable":
        prompt = f"""Compute and interpret the Vedic birth chart for:
Name: {name}, DOB: {dob}, TOB: {tob}, Place: {pob}

Calculate approximate planetary positions using traditional methods, then write the full report:
### Lagna & Fundamental Nature
### Moon — Mind, Emotions & Nakshatra
### Planetary Overview & Key Yogas
### Current Dasha Analysis
### Career, Dharma & Finance
### Love, Marriage & Relationships
### Health & Vitality
### Spiritual Path & Dharma
### Remedies & Strengthening Measures"""
    else:
        prompt = build_kundali_prompt(name, dob, tob, pob, chart)

    try:
        text = call_gemini(SYSTEM_PROMPT, prompt)
        return jsonify({"result": text, "chart": chart})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/match", methods=["POST"])
def api_match():
    """Kundali matching with computed koota scores + Gemini AI narrative."""
    if not GEMINI_API_KEY:
        return jsonify({"error": "GEMINI_API_KEY not configured on server"}), 500

    d = request.json or {}
    n1   = d.get("n1","Person 1")
    dob1 = d.get("dob1",""); tob1 = d.get("tob1",""); pob1 = d.get("pob1","")
    lat1 = float(d.get("lat1", 12.9716)); lon1 = float(d.get("lon1", 77.5946))

    n2   = d.get("n2","Person 2")
    dob2 = d.get("dob2",""); tob2 = d.get("tob2",""); pob2 = d.get("pob2","")
    lat2 = float(d.get("lat2", 12.9716)); lon2 = float(d.get("lon2", 77.5946))

    c1 = compute_chart(dob1, tob1, pob1, lat1, lon1)
    c2 = compute_chart(dob2, tob2, pob2, lat2, lon2)

    nk1 = c1.get("moon_nakshatra_index", 0)
    nk2 = c2.get("moon_nakshatra_index", 0)
    r1  = c1.get("moon_rashi", "Aries")
    r2  = c2.get("moon_rashi", "Aries")

    koota = compute_kootas(nk1, nk2, r1, r2)
    total = sum(v["score"] for v in koota.values())

    md1, md2 = c1.get("mangal_dosha", False), c2.get("mangal_dosha", False)
    if md1 and md2:
        mangal_status = "Both have Mangal Dosha — cancels out. No concern."
    elif md1:
        mangal_status = f"{n1} has Mangal Dosha, {n2} does not. Traditional remedies recommended."
    elif md2:
        mangal_status = f"{n2} has Mangal Dosha, {n1} does not. Traditional remedies recommended."
    else:
        mangal_status = "Neither has Mangal Dosha. Clear."

    nak1_data = NAKSHATRAS[nk1]
    nak2_data = NAKSHATRAS[nk2]
    nadi_exception = ""
    if koota["nadi"]["score"] == 0:
        if nak1_data["lord"] == nak2_data["lord"]:
            nadi_exception = f"Nadi Dosha may be cancelled — both nakshatras share lord {nak1_data['lord']}."
        else:
            nadi_exception = "Nadi Dosha present — most significant dosha. Remedies strongly advised."

    prompt = build_match_prompt(n1, n2, c1, c2, koota, total, mangal_status, nadi_exception, dob1, dob2)

    try:
        text = call_gemini(SYSTEM_PROMPT, prompt)
        return jsonify({
            "result": text,
            "koota": koota,
            "total": total,
            "chart1": c1,
            "chart2": c2,
            "mangal_status": mangal_status,
            "nadi_exception": nadi_exception
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 3000))
    debug = os.environ.get("FLASK_ENV") == "development"
    print(f"🪐 Jyotish Guru v3 running on http://localhost:{port}")
    print(f"🔭 Swiss Ephemeris: {'✓ Available' if SWISSEPH_AVAILABLE else '✗ Not available (AI-only mode)'}")
    print(f"🤖 Gemini AI: {'✓ Configured' if GEMINI_API_KEY else '✗ NOT SET'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
