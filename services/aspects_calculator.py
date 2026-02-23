"""
Planetary Aspects Calculator for Vedic Astrology
Calculates which planets aspect which houses/planets based on Vedic drishti rules
Extracted and adapted from Ashtavargam/calculators/transit_calculator.py
"""

from typing import List, Tuple, Set, Dict, Any


def get_nth_house_from(from_house: int, n: int) -> int:
    """
    Get nth house from a given house

    Args:
        from_house: Starting house (1-12)
        n: Number of houses to count (e.g., 7 for 7th aspect)

    Returns:
        House number (1-12)
    """
    return ((from_house + n - 2) % 12) + 1


def get_planet_aspects(planet: str, from_house: int) -> Set[int]:
    """
    Get houses aspected by a planet based on Vedic drishti rules

    All planets aspect the 7th house from their position.
    Special aspects:
    - Mars: 4th, 7th, 8th houses
    - Jupiter: 5th, 7th, 9th houses
    - Saturn: 3rd, 7th, 10th houses

    Args:
        planet: Planet name (e.g., 'Mars', 'Jupiter', 'Saturn')
        from_house: House where planet is placed (1-12)

    Returns:
        Set of house numbers that the planet aspects
    """
    aspects = set()

    # All planets aspect the 7th house from their position
    seventh_house = get_nth_house_from(from_house, 7)
    aspects.add(seventh_house)

    # Special aspects
    if planet == 'Mars':
        aspects.add(get_nth_house_from(from_house, 4))  # 4th aspect
        aspects.add(get_nth_house_from(from_house, 8))  # 8th aspect
    elif planet == 'Jupiter':
        aspects.add(get_nth_house_from(from_house, 5))  # 5th aspect
        aspects.add(get_nth_house_from(from_house, 9))  # 9th aspect
    elif planet == 'Saturn':
        aspects.add(get_nth_house_from(from_house, 3))  # 3rd aspect
        aspects.add(get_nth_house_from(from_house, 10))  # 10th aspect

    return aspects


def get_house_from_planet_position(planet_longitude: float, ascendant_longitude: float) -> int:
    """
    Calculate which house a planet is in based on whole sign houses

    Args:
        planet_longitude: Planet's sidereal longitude (0-360)
        ascendant_longitude: Ascendant's sidereal longitude (0-360)

    Returns:
        House number (1-12)
    """
    lagna_rasi = int(ascendant_longitude // 30)
    planet_rasi = int(planet_longitude // 30)
    return (planet_rasi - lagna_rasi) % 12 + 1


def get_planets_aspecting_house(target_house: int, chart_data: Dict[str, Any]) -> List[Tuple[str, int]]:
    """
    Find all planets that aspect a specific house

    Args:
        target_house: House number to check (1-12)
        chart_data: Chart data with planetary positions
                   Expected format: {'sun_longitude': ..., 'ascendant_longitude': ..., etc.}

    Returns:
        List of (planet_name, planet_house) tuples for planets aspecting the target house
    """
    aspecting_planets = []

    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    ascendant_lon = chart_data.get('ascendant_longitude')

    if not ascendant_lon:
        return aspecting_planets

    for planet in planets:
        planet_key = planet.lower()
        planet_lon_key = f'{planet_key}_longitude'

        if planet_lon_key not in chart_data:
            continue

        planet_lon = chart_data[planet_lon_key]
        planet_house = get_house_from_planet_position(planet_lon, ascendant_lon)

        # Get houses aspected by this planet
        aspected_houses = get_planet_aspects(planet, planet_house)

        if target_house in aspected_houses:
            aspecting_planets.append((planet, planet_house))

    return aspecting_planets


def get_planets_aspecting_10th_house(chart_data: Dict[str, Any]) -> List[Tuple[str, int]]:
    """
    Get all planets that aspect the 10th house (career/profession house)

    Args:
        chart_data: Chart data with planetary positions

    Returns:
        List of (planet_name, planet_house) tuples
    """
    return get_planets_aspecting_house(10, chart_data)


def get_planets_aspecting_planet(target_planet: str, chart_data: Dict[str, Any]) -> List[Tuple[str, int]]:
    """
    Find all planets that aspect a specific planet

    Args:
        target_planet: Planet to check (e.g., 'Sun', 'Mars', '10th_lord')
        chart_data: Chart data with planetary positions

    Returns:
        List of (planet_name, planet_house) tuples for planets aspecting the target planet
    """
    aspecting_planets = []

    # Get target planet's house
    target_planet_key = target_planet.lower()
    target_lon_key = f'{target_planet_key}_longitude'

    if target_lon_key not in chart_data:
        return aspecting_planets

    ascendant_lon = chart_data.get('ascendant_longitude')
    if not ascendant_lon:
        return aspecting_planets

    target_lon = chart_data[target_lon_key]
    target_house = get_house_from_planet_position(target_lon, ascendant_lon)

    return get_planets_aspecting_house(target_house, chart_data)


def get_planets_aspecting_10th_lord(chart_data: Dict[str, Any], tenth_lord: str) -> List[Tuple[str, int]]:
    """
    Get all planets that aspect the 10th lord

    Args:
        chart_data: Chart data with planetary positions
        tenth_lord: Name of the 10th lord planet (e.g., 'Mars', 'Jupiter')

    Returns:
        List of (planet_name, planet_house) tuples (excluding the 10th lord itself)
    """
    aspecting_planets = get_planets_aspecting_planet(tenth_lord, chart_data)

    # Remove the 10th lord from the list (a planet doesn't aspect itself)
    aspecting_planets = [(p, h) for p, h in aspecting_planets if p != tenth_lord]

    return aspecting_planets


def get_all_planetary_aspects(chart_data: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Calculate all planetary aspects for a chart

    Args:
        chart_data: Chart data with planetary positions

    Returns:
        Dictionary with aspect information for each planet
        Example: {
            'Mars': {
                'house': 5,
                'aspects_houses': [11, 12, 1],
                'aspected_by': [('Jupiter', 2), ('Saturn', 7)]
            }
        }
    """
    aspects_data = {}

    planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    ascendant_lon = chart_data.get('ascendant_longitude')

    if not ascendant_lon:
        return aspects_data

    for planet in planets:
        planet_key = planet.lower()
        planet_lon_key = f'{planet_key}_longitude'

        if planet_lon_key not in chart_data:
            continue

        planet_lon = chart_data[planet_lon_key]
        planet_house = get_house_from_planet_position(planet_lon, ascendant_lon)

        # Get houses this planet aspects
        aspected_houses = sorted(get_planet_aspects(planet, planet_house))

        # Get planets that aspect this planet
        aspected_by = get_planets_aspecting_planet(planet, chart_data)

        aspects_data[planet] = {
            'house': planet_house,
            'aspects_houses': aspected_houses,
            'aspected_by': aspected_by
        }

    return aspects_data


def format_aspect_analysis(aspects_data: Dict[str, Dict]) -> str:
    """
    Format aspects data into a readable text report

    Args:
        aspects_data: Output from get_all_planetary_aspects()

    Returns:
        Formatted text report
    """
    lines = []
    lines.append("=" * 80)
    lines.append("PLANETARY ASPECTS ANALYSIS")
    lines.append("=" * 80)

    for planet, data in aspects_data.items():
        lines.append(f"\n{planet} (House {data['house']}):")
        lines.append(f"  Aspects houses: {', '.join(str(h) for h in data['aspects_houses'])}")

        if data['aspected_by']:
            aspecting = [f"{p} (H{h})" for p, h in data['aspected_by']]
            lines.append(f"  Aspected by: {', '.join(aspecting)}")
        else:
            lines.append(f"  Aspected by: None")

    return "\n".join(lines)
