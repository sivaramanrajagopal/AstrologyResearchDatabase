"""
Ashtakavarga Service - Local BAV/SAV Calculator
Based on Tamil/South Indian Ashtakavarga methodology
Extracted from reference repository: https://github.com/sivaramanrajagopal/Ashtavargam
"""

from typing import Dict, Any, Optional, List

# South Indian/Tamil Ashtakavarga Benefic Position Rules
# Based on Parasara Hora Shastra with Tamil regional methodology
TAMIL_ASHTAKAVARGA_RULES = {
    'SUN': {
        'SUN': [1,2,4,7,8,9,10,11],
        'MOON': [3,6,10,11],
        'MARS': [1,2,4,7,8,9,10,11],
        'MERCURY': [3,5,6,9,10,11,12],
        'JUPITER': [5,6,9,11],
        'VENUS': [6,7,12],
        'SATURN': [1,2,4,7,8,9,10,11],
        'ASCENDANT': [3,4,6,10,11,12]
    },
    'MOON': {
        'SUN': [3,6,7,8,10,11],
        'MOON': [1,3,6,7,10,11],
        'MARS': [2,3,5,6,9,10,11],
        'MERCURY': [1,3,4,5,7,8,10,11],
        'JUPITER': [1,4,7,8,10,11,12],
        'VENUS': [3,4,5,7,9,10,11],
        'SATURN': [3,5,6,11],
        'ASCENDANT': [3,6,10,11]
    },
    'MARS': {
        'SUN': [3,5,6,10,11],
        'MOON': [3,6,11],
        'MARS': [1,2,4,7,8,10,11],
        'MERCURY': [3,5,6,11],
        'JUPITER': [6,10,11,12],
        'VENUS': [6,8,11,12],
        'SATURN': [1,4,7,8,9,10,11],
        'ASCENDANT': [1,3,6,10,11]
    },
    'MERCURY': {
        'SUN': [5,6,9,11,12],
        'MOON': [2,4,6,8,10,11],
        'MARS': [1,2,4,7,8,9,10,11],
        'MERCURY': [1,3,5,6,9,10,11,12],
        'JUPITER': [6,8,11,12],
        'VENUS': [1,2,3,4,5,8,9,11],
        'SATURN': [1,2,4,7,8,9,10,11],
        'ASCENDANT': [1,2,4,6,8,10,11]
    },
    'JUPITER': {
        'SUN': [1,2,3,4,7,8,9,10,11],
        'MOON': [2,5,7,9,11],
        'MARS': [1,2,4,7,8,10,11],
        'MERCURY': [1,2,4,5,6,9,10,11],
        'JUPITER': [1,2,3,4,7,8,10,11],
        'VENUS': [2,5,6,9,10,11],
        'SATURN': [3,5,6,12],
        'ASCENDANT': [1,2,4,5,6,7,9,10,11]
    },
    'VENUS': {
        'SUN': [8,11,12],
        'MOON': [1,2,3,4,5,8,9,11,12],
        'MARS': [3,5,6,9,11,12],
        'MERCURY': [3,5,6,9,11],
        'JUPITER': [5,8,9,10,11],
        'VENUS': [1,2,3,4,5,8,9,10,11],
        'SATURN': [3,4,5,8,9,10,11],
        'ASCENDANT': [1,2,3,4,5,8,9,11]
    },
    'SATURN': {
        'SUN': [1,2,4,7,8,10,11],
        'MOON': [3,6,11],
        'MARS': [3,5,6,10,11,12],
        'MERCURY': [6,8,9,10,11,12],
        'JUPITER': [5,6,11,12],
        'VENUS': [6,11,12],
        'SATURN': [3,5,6,11],
        'ASCENDANT': [1,3,4,6,10,11]
    },
    'ASCENDANT': {
        'SUN': [3,4,6,10,11,12],
        'MOON': [3,6,10,11],
        'MARS': [1,3,6,10,11],
        'MERCURY': [1,2,4,6,8,10,11],
        'JUPITER': [1,2,4,5,6,7,9,10,11],
        'VENUS': [1,2,3,4,5,8,9,11],
        'SATURN': [1,3,4,6,10,11],
        'ASCENDANT': [3,6,10,11]
    }
}

# Planet name mappings
PLANET_KEY_MAP = {
    'Sun': 'SUN',
    'Moon': 'MOON',
    'Mars': 'MARS',
    'Mercury': 'MERCURY',
    'Jupiter': 'JUPITER',
    'Venus': 'VENUS',
    'Saturn': 'SATURN',
    'Ascendant': 'ASCENDANT'
}

# Rasi names (South Indian order)
RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]


def calculate_relative_position_tamil(target_house: int, reference_rasi: int) -> int:
    """
    Calculate relative position using Tamil method

    Args:
        target_house: The house number (1-12) being analyzed
        reference_rasi: The rasi/sign (1-12) of the reference planet

    Returns:
        Relative position (1-12) from reference_rasi to target_house
    """
    # Tamil method uses forward counting
    if target_house >= reference_rasi:
        relative_pos = target_house - reference_rasi + 1
    else:
        relative_pos = target_house - reference_rasi + 13

    return relative_pos


def extract_planet_positions(chart_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract planetary positions (rasi numbers) from chart data

    Args:
        chart_data: D1 chart data with planetary positions

    Returns:
        Dict mapping planet names (UPPERCASE) to rasi numbers (1-12)
    """
    positions = {}

    # Extract planets from chart_data
    for planet_key, planet_name in PLANET_KEY_MAP.items():
        if planet_key in chart_data:
            planet_info = chart_data[planet_key]

            # Get rasi number from longitude
            if 'longitude' in planet_info:
                longitude = planet_info['longitude']
                rasi_num = int(longitude // 30) + 1

                # Ensure rasi is in valid range 1-12
                while rasi_num > 12:
                    rasi_num -= 12
                while rasi_num < 1:
                    rasi_num += 12

                positions[planet_name] = rasi_num
            elif 'rasi' in planet_info:
                # Directly use rasi if available
                positions[planet_name] = planet_info['rasi']

    return positions


def calculate_binnashtakavarga(target_planet: str, planet_positions: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate Binnashtakavarga (BAV) for a single planet

    Args:
        target_planet: Planet name in UPPERCASE (e.g., 'SUN', 'MOON')
        planet_positions: Dict of planet positions {planet_name: rasi_number}

    Returns:
        Dict with:
            - chart: List of 12 values (points in each rasi)
            - contributions: Dict mapping house_num to list of contributing planets
            - total: Total BAV points for this planet
    """
    if target_planet not in TAMIL_ASHTAKAVARGA_RULES:
        return {
            'chart': [0] * 12,
            'contributions': {i+1: [] for i in range(12)},
            'total': 0
        }

    rules = TAMIL_ASHTAKAVARGA_RULES[target_planet]
    chart = [0] * 12
    contributions = {i+1: [] for i in range(12)}

    # Calculate based on rules and planetary positions
    for reference_key, benefic_positions in rules.items():
        if reference_key in planet_positions:
            reference_rasi = planet_positions[reference_key]

            for house_num in range(1, 13):
                relative_pos = calculate_relative_position_tamil(house_num, reference_rasi)

                if relative_pos in benefic_positions:
                    chart[house_num - 1] += 1
                    display_name = reference_key.capitalize() if reference_key != 'ASCENDANT' else 'Ascendant'
                    contributions[house_num].append(display_name)

    total = sum(chart)

    return {
        'chart': chart,
        'contributions': contributions,
        'total': total
    }


def calculate_all_binnashtakavarga(planet_positions: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate BAV for all 7 planets

    Args:
        planet_positions: Dict of planet positions {planet_name: rasi_number}

    Returns:
        Dict with BAV data for each planet:
        {
            'SUN': {'chart': [...], 'contributions': {...}, 'total': 48},
            'MOON': {...},
            ...
        }
    """
    planets = ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN']

    bav_data = {}
    for planet in planets:
        bav_data[planet] = calculate_binnashtakavarga(planet, planet_positions)

    return bav_data


def calculate_sarvashtakavarga(bav_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate Sarvashtakavarga (SAV) - combined points from all planets

    Args:
        bav_data: BAV data from calculate_all_binnashtakavarga()

    Returns:
        Dict with:
            - chart: List of 12 values (combined points in each rasi)
            - total: Total SAV points (should be ~337)
            - by_planet: Dict showing each planet's contribution to each rasi
    """
    planets = ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN']

    sav_chart = [0] * 12
    by_planet = {planet: [0] * 12 for planet in planets}

    # Sum BAV contributions from all 7 planets
    for planet in planets:
        if planet in bav_data:
            planet_chart = bav_data[planet]['chart']
            for i in range(12):
                sav_chart[i] += planet_chart[i]
                by_planet[planet][i] = planet_chart[i]

    total = sum(sav_chart)

    return {
        'chart': sav_chart,
        'by_planet': by_planet,
        'total': total
    }


def calculate_ashtakavarga_full(chart_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Calculate complete Ashtakavarga (BAV + SAV) from chart data

    Args:
        chart_data: D1 chart data with planetary positions

    Returns:
        Dict with full Ashtakavarga data:
        {
            'bav': {planet: {chart, contributions, total}, ...},
            'sav': {chart, by_planet, total},
            'planet_positions': {planet: rasi_num, ...}
        }
        or None if calculation fails
    """
    try:
        # Extract planet positions from chart data
        planet_positions = extract_planet_positions(chart_data)

        # Ensure we have minimum required positions
        required_planets = ['SUN', 'MOON', 'ASCENDANT']
        if not all(p in planet_positions for p in required_planets):
            return None

        # Calculate BAV for all planets
        bav_data = calculate_all_binnashtakavarga(planet_positions)

        # Calculate SAV
        sav_data = calculate_sarvashtakavarga(bav_data)

        return {
            'bav': bav_data,
            'sav': sav_data,
            'planet_positions': planet_positions
        }

    except Exception as e:
        # Silently fail - Ashtakavarga is optional
        return None


def get_sav_10th_house(ashtakavarga_data: Optional[Dict[str, Any]]) -> Optional[int]:
    """
    Get SAV points for 10th house (career strength indicator)

    Args:
        ashtakavarga_data: Output from calculate_ashtakavarga_full()

    Returns:
        SAV points in 10th house, or None if not available
    """
    if not ashtakavarga_data or 'sav' not in ashtakavarga_data:
        return None

    sav_chart = ashtakavarga_data['sav']['chart']

    # 10th house is index 9 (0-indexed)
    return sav_chart[9] if len(sav_chart) >= 10 else None


def get_bav_for_planet_in_house(ashtakavarga_data: Optional[Dict[str, Any]],
                                  planet: str, house: int) -> Optional[int]:
    """
    Get BAV points for a specific planet in a specific house

    Args:
        ashtakavarga_data: Output from calculate_ashtakavarga_full()
        planet: Planet name (e.g., 'SUN', 'MOON', 'JUPITER')
        house: House number (1-12)

    Returns:
        BAV points for the planet in that house, or None if not available
    """
    if not ashtakavarga_data or 'bav' not in ashtakavarga_data:
        return None

    planet_upper = planet.upper()
    if planet_upper not in ashtakavarga_data['bav']:
        return None

    bav_chart = ashtakavarga_data['bav'][planet_upper]['chart']

    # House is 1-indexed, chart is 0-indexed
    return bav_chart[house - 1] if 1 <= house <= 12 else None


def format_ashtakavarga_for_display(ashtakavarga_data: Optional[Dict[str, Any]]) -> str:
    """
    Format Ashtakavarga data for display

    Args:
        ashtakavarga_data: Output from calculate_ashtakavarga_full()

    Returns:
        Formatted string with BAV/SAV summary
    """
    if not ashtakavarga_data:
        return "Not calculated"

    bav_data = ashtakavarga_data.get('bav', {})
    sav_data = ashtakavarga_data.get('sav', {})

    lines = []
    lines.append("Binnashtakavarga (BAV) - Individual Planet Points:")

    for planet in ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN']:
        if planet in bav_data:
            total = bav_data[planet]['total']
            lines.append(f"  {planet}: {total} points")

    if sav_data:
        sav_total = sav_data.get('total', 0)
        lines.append(f"\nSarvashtakavarga (SAV) Total: {sav_total} points")

        sav_10th = get_sav_10th_house(ashtakavarga_data)
        if sav_10th is not None:
            lines.append(f"SAV 10th House (Career): {sav_10th} points")

    return "\n".join(lines)
