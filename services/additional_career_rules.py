"""
Additional Parasara Career Rules
Comprehensive classical principles for career analysis
To be integrated into career_rules.py
"""
from typing import Dict, Any, List, Optional, Tuple


# ============================================================================
# ADDITIONAL PARASARA CONSTANTS
# ============================================================================

# Yogakaraka planets for each lagna (rule kendra + trikona)
YOGAKARAKA_FOR_LAGNA = {
    "Mesha": None,         # No yogakaraka (Mars rules 1 & 8)
    "Rishaba": "Saturn",   # Rules 9th and 10th
    "Mithuna": "Venus",    # Rules 5th and 12th (weak YK)
    "Kataka": "Mars",      # Rules 5th and 10th
    "Simha": "Mars",       # Rules 4th and 9th
    "Kanni": None,         # No yogakaraka
    "Thula": "Saturn",     # Rules 4th and 5th
    "Vrischika": None,     # No strong yogakaraka
    "Dhanus": None,        # No yogakaraka
    "Makara": "Venus",     # Rules 5th and 10th
    "Kumbha": "Venus",     # Rules 4th and 9th
    "Meena": None,         # No yogakaraka (Mars rules 2 & 9)
}

# Natural benefics and malefics
NATURAL_BENEFICS = ["Jupiter", "Venus", "Moon", "Mercury"]
NATURAL_MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

# Pushkara Navamsa degrees (highly auspicious)
# Pushkara occurs at specific degrees in each sign
PUSHKARA_NAVAMSA_RANGES = {
    # Movable signs: 21°20' - 24°
    "Mesha": [(21.333, 24.0)],
    "Kataka": [(21.333, 24.0)],
    "Thula": [(21.333, 24.0)],
    "Makara": [(21.333, 24.0)],
    # Fixed signs: 24° - 26°40'
    "Rishaba": [(24.0, 26.667)],
    "Simha": [(24.0, 26.667)],
    "Vrischika": [(24.0, 26.667)],
    "Kumbha": [(24.0, 26.667)],
    # Dual signs: 26°40' - 30°
    "Mithuna": [(26.667, 30.0)],
    "Kanni": [(26.667, 30.0)],
    "Dhanus": [(26.667, 30.0)],
    "Meena": [(26.667, 30.0)],
}

# Planets that give good results in specific houses
PLANET_HOUSE_COMFORT = {
    "Sun": [1, 5, 9, 10, 11],      # Kendra and trikona
    "Moon": [1, 4, 7, 10],         # Kendras
    "Mars": [3, 6, 10, 11],        # Upachayas
    "Mercury": [1, 2, 4, 5, 9, 10, 11],  # Versatile
    "Jupiter": [1, 2, 5, 7, 9, 10, 11],  # Most houses good
    "Venus": [1, 2, 4, 5, 7, 8, 9, 12],  # Luxury houses
    "Saturn": [3, 6, 10, 11],      # Upachayas
    "Rahu": [3, 6, 10, 11],        # Upachayas, foreign
    "Ketu": [3, 6, 12],            # Moksha houses
}

# Rasi lords
RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}

# Exaltation signs
EXALTATION = {
    "Sun": "Mesha", "Moon": "Rishaba", "Mars": "Makara",
    "Mercury": "Kanni", "Jupiter": "Kataka", "Venus": "Meena",
    "Saturn": "Thula"
}

# Debilitation signs
DEBILITATION = {
    "Sun": "Thula", "Moon": "Vrischika", "Mars": "Kataka",
    "Mercury": "Meena", "Jupiter": "Makara", "Venus": "Kanni",
    "Saturn": "Mesha"
}

# Own signs
OWN_SIGNS = {
    "Sun": ["Simha"], "Moon": ["Kataka"],
    "Mars": ["Mesha", "Vrischika"], "Mercury": ["Mithuna", "Kanni"],
    "Jupiter": ["Dhanus", "Meena"], "Venus": ["Rishaba", "Thula"],
    "Saturn": ["Makara", "Kumbha"]
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_planet_degree_in_sign(longitude: float) -> float:
    """Get planet's degree within its sign (0-30)"""
    return longitude % 30


def is_planet_combust(planet: str, planet_lon: float, sun_lon: float) -> bool:
    """
    Check if planet is combust (too close to Sun)

    Combustion ranges (approximate):
    - Moon: 12°
    - Mars: 17°
    - Mercury: 14° (retrograde: 12°)
    - Jupiter: 11°
    - Venus: 10° (retrograde: 8°)
    - Saturn: 15°
    """
    if planet == "Sun":
        return False

    # Calculate angular distance
    diff = abs(planet_lon - sun_lon)
    if diff > 180:
        diff = 360 - diff

    combustion_ranges = {
        "Moon": 12.0,
        "Mars": 17.0,
        "Mercury": 14.0,
        "Jupiter": 11.0,
        "Venus": 10.0,
        "Saturn": 15.0
    }

    threshold = combustion_ranges.get(planet, 15.0)
    return diff < threshold


def is_in_pushkara_navamsa(rasi: str, degree: float) -> bool:
    """Check if planet is in Pushkara Navamsa (highly auspicious degrees)"""
    ranges = PUSHKARA_NAVAMSA_RANGES.get(rasi, [])
    for start, end in ranges:
        if start <= degree < end:
            return True
    return False


def get_house_from_longitude(planet_lon: float, ascendant_lon: float) -> int:
    """Calculate which house a planet is in (whole sign system)"""
    lagna_rasi = int(ascendant_lon // 30)
    planet_rasi = int(planet_lon // 30)
    return (planet_rasi - lagna_rasi) % 12 + 1


def detect_parivartana_yoga(d1: Dict[str, Any], planet1: str, planet2: str) -> Optional[str]:
    """
    Detect Parivartana Yoga (exchange) between two planets

    Returns:
        - "Maha" for kendra-kendra or trikona-trikona
        - "Khala" for dusthana-dusthana
        - "Dainya" for one in dusthana
        - "Simple" for others
        - None if no exchange
    """
    if planet1 not in d1 or planet2 not in d1:
        return None

    p1_data = d1[planet1]
    p2_data = d1[planet2]

    if not isinstance(p1_data, dict) or not isinstance(p2_data, dict):
        return None

    p1_rasi = p1_data.get("rasi")
    p2_rasi = p2_data.get("rasi")

    if not p1_rasi or not p2_rasi:
        return None

    # Check if they're in each other's signs
    p1_lord = RASI_LORDS.get(p1_rasi)
    p2_lord = RASI_LORDS.get(p2_rasi)

    if p1_lord == planet2 and p2_lord == planet1:
        # Exchange detected! Determine type
        ascendant_lon = d1.get("Ascendant", {}).get("longitude", 0)
        p1_house = get_house_from_longitude(p1_data.get("longitude", 0), ascendant_lon)
        p2_house = get_house_from_longitude(p2_data.get("longitude", 0), ascendant_lon)

        kendras = [1, 4, 7, 10]
        trikonas = [1, 5, 9]
        dusthanas = [6, 8, 12]

        if p1_house in kendras and p2_house in kendras:
            return "Maha"  # Great exchange
        elif p1_house in trikonas and p2_house in trikonas:
            return "Maha"
        elif p1_house in dusthanas and p2_house in dusthanas:
            return "Khala"  # Difficult exchange
        elif p1_house in dusthanas or p2_house in dusthanas:
            return "Dainya"  # Poverty exchange
        else:
            return "Simple"

    return None


def detect_neechabhanga_raja_yoga(planet: str, planet_data: Dict[str, Any], d1: Dict[str, Any]) -> bool:
    """
    Detect Neechabhanga Raja Yoga (debilitation cancellation)

    Conditions:
    1. Debilitated planet's lord is in kendra from lagna/moon
    2. Exaltation lord of the sign is in kendra from lagna/moon
    3. Debilitated planet is aspected by its own lord
    4. Debilitated planet in Navamsa of exaltation/own sign
    """
    rasi = planet_data.get("rasi")
    if not rasi:
        return False

    # Check if planet is debilitated
    if rasi != DEBILITATION.get(planet):
        return False

    # Condition 1: Debilitated planet's lord in kendra
    rasi_lord = RASI_LORDS.get(rasi)
    if rasi_lord and rasi_lord in d1:
        ascendant_lon = d1.get("Ascendant", {}).get("longitude", 0)
        lord_lon = d1[rasi_lord].get("longitude", 0) if isinstance(d1[rasi_lord], dict) else 0
        lord_house = get_house_from_longitude(lord_lon, ascendant_lon)
        if lord_house in [1, 4, 7, 10]:
            return True

    # Condition 2: Exaltation lord in kendra
    # Find which planet has exaltation in this sign
    for p, ex_sign in EXALTATION.items():
        if ex_sign == rasi and p in d1:
            ascendant_lon = d1.get("Ascendant", {}).get("longitude", 0)
            ex_lord_lon = d1[p].get("longitude", 0) if isinstance(d1[p], dict) else 0
            ex_lord_house = get_house_from_longitude(ex_lord_lon, ascendant_lon)
            if ex_lord_house in [1, 4, 7, 10]:
                return True

    return False


# ============================================================================
# ADDITIONAL CAREER RULES
# ============================================================================

def check_yogakaraka_in_10th(d1: Dict[str, Any]) -> Optional[Tuple[str, float]]:
    """
    Rule: Yogakaraka planet in 10th house

    Yogakaraka is the planet ruling both kendra and trikona for a lagna.
    This is extremely auspicious for career when placed in 10th.

    Returns: (planet_name, score) or None
    """
    if "Ascendant" not in d1:
        return None

    asc_data = d1["Ascendant"]
    if not isinstance(asc_data, dict):
        return None

    asc_rasi = asc_data.get("rasi")
    yogakaraka = YOGAKARAKA_FOR_LAGNA.get(asc_rasi)

    if not yogakaraka or yogakaraka not in d1:
        return None

    # Check if yogakaraka is in 10th house
    yk_data = d1[yogakaraka]
    if not isinstance(yk_data, dict):
        return None

    ascendant_lon = asc_data.get("longitude", 0)
    yk_lon = yk_data.get("longitude", 0)
    yk_house = get_house_from_longitude(yk_lon, ascendant_lon)

    if yk_house == 10:
        # Check if it's also exalted/own sign for even higher score
        yk_rasi = yk_data.get("rasi")
        if yk_rasi == EXALTATION.get(yogakaraka):
            return (yogakaraka, 1.5)  # Exalted yogakaraka in 10th
        elif yk_rasi in OWN_SIGNS.get(yogakaraka, []):
            return (yogakaraka, 1.3)  # Own sign yogakaraka in 10th
        else:
            return (yogakaraka, 1.0)  # Yogakaraka in 10th

    return None


def check_parivartana_yoga_10th(d1: Dict[str, Any], tenth_lord: str) -> Optional[Tuple[str, str, str, float]]:
    """
    Rule: Parivartana Yoga (exchange) involving 10th house or 10th lord

    Types:
    - Maha Parivartana: Between kendras or trikonas (best)
    - Khala Parivartana: Between dusthanas (difficult)
    - Dainya Parivartana: One in dusthana (poverty)

    Returns: (planet1, planet2, yoga_type, score) or None
    """
    if not tenth_lord:
        return None

    # Check exchanges involving 10th lord
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    for planet in planets:
        if planet == tenth_lord:
            continue

        yoga_type = detect_parivartana_yoga(d1, tenth_lord, planet)
        if yoga_type:
            if yoga_type == "Maha":
                return (tenth_lord, planet, yoga_type, 1.2)
            elif yoga_type == "Simple":
                return (tenth_lord, planet, yoga_type, 0.8)
            elif yoga_type == "Khala":
                return (tenth_lord, planet, yoga_type, 0.3)
            elif yoga_type == "Dainya":
                return (tenth_lord, planet, yoga_type, 0.2)

    return None


def check_neechabhanga_10th(d1: Dict[str, Any]) -> List[Tuple[str, float]]:
    """
    Rule: Neechabhanga Raja Yoga in 10th house

    A debilitated planet in 10th house with cancellation becomes
    very powerful for career (rags to riches effect).

    Returns: List of (planet_name, score) tuples
    """
    if "Ascendant" not in d1:
        return []

    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0
    results = []

    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    for planet in planets:
        if planet not in d1:
            continue

        planet_data = d1[planet]
        if not isinstance(planet_data, dict):
            continue

        # Check if in 10th house
        planet_lon = planet_data.get("longitude", 0)
        house = get_house_from_longitude(planet_lon, ascendant_lon)

        if house == 10:
            # Check for neechabhanga
            if detect_neechabhanga_raja_yoga(planet, planet_data, d1):
                results.append((planet, 0.9))  # High score for cancellation

    return results


def check_sun_in_10th(d1: Dict[str, Any]) -> Optional[float]:
    """
    Rule: Sun in 10th house (natural karaka for authority)

    Sun is the natural significator of authority, government, and leadership.
    In 10th house, it strongly indicates government/leadership careers.

    Returns: score or None
    """
    if "Sun" not in d1 or "Ascendant" not in d1:
        return None

    sun_data = d1["Sun"]
    if not isinstance(sun_data, dict):
        return None

    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0
    sun_lon = sun_data.get("longitude", 0)
    sun_house = get_house_from_longitude(sun_lon, ascendant_lon)

    if sun_house == 10:
        sun_rasi = sun_data.get("rasi")
        # Check dignity
        if sun_rasi == "Mesha":  # Exalted
            return 1.2
        elif sun_rasi == "Simha":  # Own sign
            return 1.0
        elif sun_rasi == "Thula":  # Debilitated
            return 0.3
        else:
            return 0.8

    return None


def check_9th_10th_lord_connection(d1: Dict[str, Any], tenth_lord: str) -> Optional[Tuple[str, float]]:
    """
    Rule: Connection between 9th lord and 10th lord (Dharma-Karma yoga)

    9th house = fortune, dharma
    10th house = career, karma
    Connection creates fortunate career (Bhagya-Karma yoga)

    Types:
    - Conjunction
    - Mutual aspect
    - Exchange

    Returns: (connection_type, score) or None
    """
    if not tenth_lord or "Ascendant" not in d1:
        return None

    # Get 9th house
    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0
    ninth_house_cusp = (ascendant_lon + 240) % 360  # 9th house is 8 signs (240°) from ascendant
    ninth_rasi = int(ninth_house_cusp // 30)

    rasis = ["Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
             "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]
    ninth_house_sign = rasis[ninth_rasi]
    ninth_lord = RASI_LORDS.get(ninth_house_sign)

    if not ninth_lord or ninth_lord not in d1 or ninth_lord == tenth_lord:
        return None

    # Check for exchange
    yoga_type = detect_parivartana_yoga(d1, tenth_lord, ninth_lord)
    if yoga_type:
        return ("Exchange (Parivartana)", 1.3)

    # Check for conjunction (same house)
    tenth_data = d1[tenth_lord]
    ninth_data = d1[ninth_lord]

    if isinstance(tenth_data, dict) and isinstance(ninth_data, dict):
        tenth_house = get_house_from_longitude(tenth_data.get("longitude", 0), ascendant_lon)
        ninth_house = get_house_from_longitude(ninth_data.get("longitude", 0), ascendant_lon)

        if tenth_house == ninth_house:
            return ("Conjunction", 1.1)

    # TODO: Check for mutual aspect (would need aspects calculator)

    return None


def check_exalted_planets_in_10th(d1: Dict[str, Any]) -> List[Tuple[str, float]]:
    """
    Rule: Exalted planets in 10th house

    Exalted planets are extremely strong and give excellent results.

    Returns: List of (planet_name, score) tuples
    """
    if "Ascendant" not in d1:
        return []

    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0
    results = []

    for planet, ex_sign in EXALTATION.items():
        if planet not in d1:
            continue

        planet_data = d1[planet]
        if not isinstance(planet_data, dict):
            continue

        # Check if exalted and in 10th
        if planet_data.get("rasi") == ex_sign:
            planet_lon = planet_data.get("longitude", 0)
            house = get_house_from_longitude(planet_lon, ascendant_lon)

            if house == 10:
                # Check for Pushkara Navamsa (extra auspicious)
                degree = get_planet_degree_in_sign(planet_lon)
                if is_in_pushkara_navamsa(ex_sign, degree):
                    results.append((planet, 1.5))  # Exalted + Pushkara
                else:
                    results.append((planet, 1.2))  # Just exalted

    return results


def check_rahu_ketu_in_10th(d1: Dict[str, Any]) -> Optional[Tuple[str, str, float]]:
    """
    Rule: Rahu or Ketu in 10th house

    Rahu in 10th: Foreign connections, unconventional career, technology, politics
    Ketu in 10th: Spiritual/research career, detachment from worldly success

    Returns: (node, interpretation, score) or None
    """
    if "Ascendant" not in d1:
        return None

    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0

    # Check Rahu
    if "Rahu" in d1 and isinstance(d1["Rahu"], dict):
        rahu_lon = d1["Rahu"].get("longitude", 0)
        rahu_house = get_house_from_longitude(rahu_lon, ascendant_lon)
        if rahu_house == 10:
            return ("Rahu", "Foreign/unconventional career", 0.8)

    # Check Ketu
    if "Ketu" in d1 and isinstance(d1["Ketu"], dict):
        ketu_lon = d1["Ketu"].get("longitude", 0)
        ketu_house = get_house_from_longitude(ketu_lon, ascendant_lon)
        if ketu_house == 10:
            return ("Ketu", "Spiritual/research career", 0.6)

    return None


def check_combust_planets_in_10th(d1: Dict[str, Any]) -> List[Tuple[str, float]]:
    """
    Rule: Combust planets in 10th house

    Combustion weakens a planet (too close to Sun).
    In 10th house, can indicate obstacles in career.

    Returns: List of (planet_name, penalty_score) tuples
    """
    if "Sun" not in d1 or "Ascendant" not in d1:
        return []

    sun_data = d1["Sun"]
    if not isinstance(sun_data, dict):
        return []

    sun_lon = sun_data.get("longitude", 0)
    ascendant_lon = d1["Ascendant"].get("longitude", 0) if isinstance(d1["Ascendant"], dict) else 0

    results = []
    planets = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

    for planet in planets:
        if planet not in d1:
            continue

        planet_data = d1[planet]
        if not isinstance(planet_data, dict):
            continue

        planet_lon = planet_data.get("longitude", 0)
        planet_house = get_house_from_longitude(planet_lon, ascendant_lon)

        # Check if in 10th and combust
        if planet_house == 10 and is_planet_combust(planet, planet_lon, sun_lon):
            results.append((planet, 0.3))  # Penalty for combustion

    return results
