"""
Utility functions for birth data validation, formatting, and astrology helpers.
"""
from datetime import datetime, date, time
from typing import Optional
import uuid

# Sign and nakshatra names (match enhanced_swiss_ephemeris)
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
RASI_NAMES = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Career category mapping (broad categories)
CAREER_CATEGORY_MAP = {
    "Government": "Administration",
    "Administration": "Administration",
    "Politics": "Administration",
    "Leadership": "Administration",
    "Medicine": "Healthcare",
    "Authority": "Administration",
    "Public Relations": "Creative",
    "Nursing": "Healthcare",
    "Hospitality": "Service",
    "Psychology": "Healthcare",
    "Travel": "Service",
    "Catering": "Service",
    "Engineering": "Technical",
    "Military": "Service",
    "Police": "Service",
    "Surgery": "Healthcare",
    "Real Estate": "Business",
    "Sports": "Creative",
    "Business": "Business",
    "Communication": "Creative",
    "Writing": "Creative",
    "Accounting": "Business",
    "Mathematics": "Technical",
    "IT": "Technical",
    "Teaching": "Education",
    "Law": "Legal",
    "Finance": "Business",
    "Banking": "Business",
    "Advisory": "Business",
    "Philosophy": "Education",
    "Arts": "Creative",
    "Entertainment": "Creative",
    "Fashion": "Creative",
    "Beauty": "Creative",
    "Luxury Goods": "Business",
    "Hotels": "Service",
    "Labor": "Service",
    "Service": "Service",
    "Technology": "Technical",
    "Research": "Technical",
    "Mining": "Technical",
    "Agriculture": "Technical",
    "Oil": "Technical",
    "Foreign": "International",
    "Media": "Creative",
    "Unconventional": "Creative",
    "Aviation": "Technical",
    "Sales": "Business",
    "Marketing": "Business",
    "Trade": "Business",
    "Electronics": "Technical",
    "Spirituality": "Spiritual",
    "Occult": "Spiritual",
    "Investigation": "Technical",
    "Astrology": "Spiritual",
    "Healthcare": "Healthcare",
    "Education": "Education",
    "Legal": "Legal",
    "Creative": "Creative",
    "Technical": "Technical",
    "International": "International",
    "Spiritual": "Spiritual",
}


def validate_birth_data(
    lat: float,
    lon: float,
    birth_datetime: datetime,
) -> bool:
    """Validate latitude, longitude, and that datetime is not in future. Raises ValueError if invalid."""
    if not (-90 <= lat <= 90):
        raise ValueError("Latitude must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise ValueError("Longitude must be between -180 and 180")
    now = datetime.utcnow()
    if birth_datetime.tzinfo:
        import pytz
        now = datetime.now(pytz.UTC).replace(tzinfo=None)
        bt = birth_datetime
        if hasattr(bt, "astimezone"):
            bt = bt.astimezone(pytz.UTC).replace(tzinfo=None)
        if bt > now:
            raise ValueError("Birth datetime cannot be in the future")
    else:
        if birth_datetime > now:
            raise ValueError("Birth datetime cannot be in the future")
    return True


def format_longitude(longitude: float) -> str:
    """Convert decimal longitude to traditional format, e.g. 285.5 -> '15° Leo 30'."""
    lon = longitude % 360
    sign_num = int(lon // 30)
    degrees_in_sign = lon % 30
    deg = int(degrees_in_sign)
    minutes = int((degrees_in_sign - deg) * 60)
    sign_name = get_sign_name(sign_num)
    return f"{deg}° {sign_name} {minutes}'"


def get_sign_name(sign_num: int) -> str:
    """Convert sign number (0-11) to name. 0=Aries, 1=Taurus, etc."""
    if 0 <= sign_num <= 11:
        return SIGN_NAMES[sign_num]
    return RASI_NAMES[sign_num % 12]


def get_rasi_name(sign_num: int) -> str:
    """Convert sign number (0-11) to Vedic rasi name."""
    if 0 <= sign_num <= 11:
        return RASI_NAMES[sign_num]
    return RASI_NAMES[sign_num % 12]


def get_nakshatra_name(nakshatra_num: int) -> str:
    """Convert nakshatra number (0-26) to name."""
    if 0 <= nakshatra_num <= 26:
        return NAKSHATRA_NAMES[nakshatra_num]
    return NAKSHATRA_NAMES[nakshatra_num % 27]


def calculate_age(birth_datetime: datetime, target_date: Optional[datetime] = None) -> float:
    """Calculate age in years. If target_date is None, use current date."""
    target = target_date or datetime.utcnow()
    if birth_datetime.tzinfo or target.tzinfo:
        if hasattr(birth_datetime, "astimezone") and birth_datetime.tzinfo:
            birth_datetime = birth_datetime.astimezone(target.tzinfo if target.tzinfo else None)
    delta = target - birth_datetime
    return delta.total_seconds() / (365.25 * 24 * 3600)


def career_category_mapping(career: str) -> str:
    """Map specific career to category. Returns category name."""
    return CAREER_CATEGORY_MAP.get(career.strip(), "Other")


def generate_unique_id() -> str:
    """Generate UUID for new records."""
    return str(uuid.uuid4())


def serialize_datetime(dt: datetime) -> str:
    """Convert datetime to ISO format string; handle timezone."""
    if dt is None:
        return ""
    if dt.tzinfo is None:
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    return dt.isoformat()


def get_stronger_planet(planet1_data: dict, planet2_data: dict) -> str:
    """Compare two planets by dignity/position; return name of stronger. Simple heuristic."""
    # Prefer exalted > own sign > neutral > debilitated
    dignity_order = {"exalted": 4, "own_sign": 3, "friendly": 2, "neutral": 1, "debilitated": 0}
    p1 = (planet1_data.get("dignity") or "neutral").lower()
    p2 = (planet2_data.get("dignity") or "neutral").lower()
    s1 = dignity_order.get(p1, 1)
    s2 = dignity_order.get(p2, 1)
    if s1 != s2:
        return "planet1" if s1 > s2 else "planet2"
    # Fallback: higher longitude (later in zodiac) as tie-breaker
    lon1 = planet1_data.get("longitude", 0)
    lon2 = planet2_data.get("longitude", 0)
    return "planet1" if lon1 >= lon2 else "planet2"
