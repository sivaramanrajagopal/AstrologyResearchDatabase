"""
Dasha/Bhukti Calculator
Extracted and adapted from OpenAIAstroPrediction/backend/modules/dasa_bhukti.py
Removed OpenAI dependencies, made standalone for FastAPI integration
"""

import swisseph as swe
import datetime
from collections import OrderedDict
from typing import Tuple, List, Dict

# --- CONSTANTS ---
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Nakshatra lords cycle (9 planets repeated 3 times for 27 nakshatras)
NAKSHATRA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"] * 3

# Dasa durations in years (Vimshottari Dasa system - 120 year cycle)
DASA_DURATIONS = OrderedDict([
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10),
    ("Mars", 7), ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17)
])

# Initialize Swiss Ephemeris (will be set properly in functions)
swe.set_sid_mode(swe.SIDM_LAHIRI)


def get_nakshatra(longitude: float) -> Tuple[str, int, int]:
    """
    Return nakshatra, pada, and index for a given longitude.
    
    Args:
        longitude: Planetary longitude in degrees (0-360)
    
    Returns:
        Tuple of (nakshatra_name, pada, nakshatra_index)
    """
    nakshatra_index = int((longitude % 360) // (360 / 27))
    pada = int(((longitude % (360 / 27)) / (360 / 27 / 4)) + 1)
    return NAKSHATRAS[nakshatra_index], pada, nakshatra_index


def calculate_dasa_start(moon_longitude: float) -> Tuple[str, int, str, float]:
    """
    Calculate starting dasa and remaining years based on Moon's position.
    
    Args:
        moon_longitude: Moon's longitude in degrees (0-360)
    
    Returns:
        Tuple of (birth_nakshatra, birth_pada, current_dasa_lord, remaining_years)
    """
    nakshatra, pada, nakshatra_index = get_nakshatra(moon_longitude)
    nakshatra_length = 360 / 27
    remainder = moon_longitude % nakshatra_length
    portion_completed = remainder / nakshatra_length

    current_dasa_lord = NAKSHATRA_LORDS[nakshatra_index]
    total_dasa_years = DASA_DURATIONS[current_dasa_lord]
    remaining_years = total_dasa_years * (1 - portion_completed)

    return nakshatra, pada, current_dasa_lord, remaining_years


def generate_dasa_table(jd: float, moon_longitude: float, total_years: int = 120) -> Tuple[str, int, List[Dict]]:
    """
    Generate full Vimshottari Dasa table.
    
    Args:
        jd: Julian Day number for birth time
        moon_longitude: Moon's longitude in degrees
        total_years: Total years to calculate (default 120 for full cycle)
    
    Returns:
        Tuple of (birth_nakshatra, birth_pada, dasa_table)
        dasa_table is a list of dicts with keys: planet, start_age, end_age, start_date, end_date, duration
    """
    nakshatra, pada, current_dasa_lord, remaining_years = calculate_dasa_start(moon_longitude)
    start_year, start_month, start_day = swe.revjul(jd)[:3]
    start_date = datetime.datetime(start_year, start_month, start_day)

    dasa_table = []
    current_year = 0
    current_index = list(DASA_DURATIONS.keys()).index(current_dasa_lord)

    while current_year < total_years:
        for i in range(current_index, current_index + len(DASA_DURATIONS)):
            planet = list(DASA_DURATIONS.keys())[i % len(DASA_DURATIONS)]
            duration = DASA_DURATIONS[planet]
            if i == current_index:
                duration = remaining_years

            end_year = current_year + duration
            if current_year >= total_years:
                break

            end_date = start_date + datetime.timedelta(days=duration * 365.25)
            dasa_table.append({
                "planet": planet,
                "start_age": round(current_year, 2),
                "end_age": round(end_year, 2),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration": round(duration, 2)
            })

            current_year = end_year
            start_date = end_date
        current_index = 0  # Reset after completing the cycle

    return nakshatra, pada, dasa_table


def generate_dasa_bhukti_table(jd: float, moon_longitude: float) -> Tuple[str, int, List[Dict]]:
    """
    Generate Dasa Bhukti table with sub-periods.
    
    Args:
        jd: Julian Day number for birth time
        moon_longitude: Moon's longitude in degrees
    
    Returns:
        Tuple of (birth_nakshatra, birth_pada, bhukti_table)
        bhukti_table is a list of dicts with keys: maha_dasa, bhukti, start_date, end_date, duration
    """
    # First get the main dasa periods
    birth_nakshatra, birth_pada, main_dasa_table = generate_dasa_table(jd, moon_longitude, total_years=120)

    # For each main dasa, calculate bhukti (sub-periods)
    bhukti_table = []

    for main_period in main_dasa_table:
        maha_dasa_planet = main_period['planet']
        maha_dasa_duration = main_period['duration']
        
        # Calculate bhukti periods within this maha dasa
        bhukti_durations = DASA_DURATIONS.copy()
        current_bhukti_index = list(bhukti_durations.keys()).index(maha_dasa_planet)
        
        current_date = datetime.datetime.strptime(main_period['start_date'], "%Y-%m-%d")
        remaining_duration = maha_dasa_duration
        
        for i in range(len(bhukti_durations)):
            bhukti_planet = list(bhukti_durations.keys())[(current_bhukti_index + i) % len(bhukti_durations)]
            bhukti_duration = bhukti_durations[bhukti_planet]
            
            # Calculate proportional duration within maha dasa
            total_dasa_years = sum(bhukti_durations.values())  # Should be 120
            proportional_duration = (bhukti_duration / total_dasa_years) * maha_dasa_duration
            
            if remaining_duration <= 0:
                break
                
            if proportional_duration > remaining_duration:
                proportional_duration = remaining_duration
            
            end_date = current_date + datetime.timedelta(days=proportional_duration * 365.25)
            
            bhukti_table.append({
                "maha_dasa": maha_dasa_planet,
                "bhukti": bhukti_planet,
                "start_date": current_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "duration": round(proportional_duration, 2)
            })
            
            current_date = end_date
            remaining_duration -= proportional_duration
    
    return birth_nakshatra, birth_pada, bhukti_table


def get_current_dasa_bhukti(jd: float, moon_longitude: float, current_date: datetime.datetime = None) -> Dict:
    """
    Get current Dasha and Bhukti for a given date.
    
    Args:
        jd: Julian Day number for birth time
        moon_longitude: Moon's longitude in degrees
        current_date: Current date (defaults to today)
    
    Returns:
        Dict with current_dasa, current_bhukti, start_date, end_date, remaining_years, age
    """
    if current_date is None:
        current_date = datetime.datetime.now()
    
    # Get birth date
    birth_date = datetime.datetime(*swe.revjul(jd)[:3])
    
    # Calculate age
    age = (current_date - birth_date).days / 365.25
    
    # Get all dasa periods
    _, _, dasa_table = generate_dasa_table(jd, moon_longitude, total_years=120)
    
    # Find current dasa
    current_dasa = None
    for period in dasa_table:
        if period['start_age'] <= age < period['end_age']:
            current_dasa = period
            break
    
    if not current_dasa:
        # If age exceeds all periods, return the last one
        current_dasa = dasa_table[-1]
    
    # Get bhukti table for current dasa period
    _, _, bhukti_table = generate_dasa_bhukti_table(jd, moon_longitude)
    
    # Find current bhukti
    current_bhukti = None
    for bhukti_period in bhukti_table:
        if bhukti_period['maha_dasa'] == current_dasa['planet']:
            bhukti_start = datetime.datetime.strptime(bhukti_period['start_date'], "%Y-%m-%d")
            bhukti_end = datetime.datetime.strptime(bhukti_period['end_date'], "%Y-%m-%d")
            if bhukti_start <= current_date < bhukti_end:
                current_bhukti = bhukti_period
                break
    
    if not current_bhukti:
        # Find the last bhukti for this dasa
        for bhukti_period in reversed(bhukti_table):
            if bhukti_period['maha_dasa'] == current_dasa['planet']:
                current_bhukti = bhukti_period
                break
    
    # Calculate remaining years in current dasa
    dasa_end_date = datetime.datetime.strptime(current_dasa['end_date'], "%Y-%m-%d")
    remaining_years = (dasa_end_date - current_date).days / 365.25
    
    return {
        "current_dasa": current_dasa['planet'],
        "current_bhukti": current_bhukti['bhukti'] if current_bhukti else None,
        "start_date": current_dasa['start_date'],
        "end_date": current_dasa['end_date'],
        "remaining_years": round(remaining_years, 2),
        "age": round(age, 2)
    }

