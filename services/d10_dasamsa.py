"""
D10 (Dasamsa) calculation – Parasara method.
Each D1 sign is divided into 10 equal parts of 3°; each part maps to a sign in order.
D10 Lagna = 10th harmonic of D1 Lagna.
"""
from typing import Dict, Any

# Reuse Rasi list from enhanced_swiss_ephemeris (same order)
RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]
RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}


def d1_longitude_to_d10(longitude: float) -> float:
    """
    Convert D1 longitude to D10 longitude (Parasara Dasamsa).
    Each 30° sign is split into 10 parts of 3°.
    Odd signs (1,3,5,7,9,11): part 0 → same sign, part 1 → next, ... part 9 → 9 signs ahead.
    Even signs (2,4,6,8,10,12): start from 9th sign (Parasara), then proceed forward.
    """
    longitude = longitude % 360
    rasi_index = int(longitude // 30) % 12  # 0=Aries, 1=Taurus, ...
    degrees_in_rasi = longitude % 30
    part = int(degrees_in_rasi / 3)  # 0..9
    if part >= 10:
        part = 9
    # Odd signs (0,2,4,6,8,10): Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    # Even signs (1,3,5,7,9,11): Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces
    if rasi_index % 2 == 0:  # odd sign (0-based: 0,2,4,6,8,10)
        d10_rasi_index = (rasi_index + part) % 12
    else:  # even sign: start from 9th sign, then forward
        # FIXED: 9th sign is 8 positions ahead (counting from rasi as 1st)
        start = (rasi_index + 8) % 12
        d10_rasi_index = (start + part) % 12
    # Within the 3° slice, map 0-3° to 0-30° in D10 sign
    d10_degrees = (degrees_in_rasi % 3) * 10.0
    return d10_rasi_index * 30.0 + d10_degrees


def d10_longitude_to_rasi(longitude: float) -> str:
    """Get rasi name from D10 longitude."""
    idx = int(longitude // 30) % 12
    return RASIS[idx]


def calculate_d10_chart(d1_positions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build D10 chart from D1 planetary positions.
    d1_positions: dict with keys Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu, Ascendant
                  each value has 'longitude' and optionally 'retrograde'.
    """
    result = {}
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    for name in planets:
        if name not in d1_positions:
            continue
        data = d1_positions[name]
        lon = data.get("longitude")
        if lon is None:
            continue
        d10_lon = d1_longitude_to_d10(lon)
        rasi = d10_longitude_to_rasi(d10_lon)
        result[name] = {
            "longitude": d10_lon,
            "rasi": rasi,
            "rasi_lord": RASI_LORDS.get(rasi, ""),
            "degrees_in_rasi": d10_lon % 30,
            "retrograde": data.get("retrograde", False),
        }
    # D10 house cusps: Equal houses from D10 Ascendant (Vedic method)
    # In Vedic astrology, divisional charts use equal 30° houses from the divisional Ascendant
    if "Ascendant" in result:
        d10_asc_lon = result["Ascendant"]["longitude"]
        d10_houses = {}
        for i in range(1, 13):
            # Each house is exactly 30° from the previous one
            house_lon = (d10_asc_lon + (i - 1) * 30) % 360
            key = f"House_{i}"
            d10_houses[key] = {
                "longitude": house_lon,
                "rasi": d10_longitude_to_rasi(house_lon),
                "degrees_in_rasi": house_lon % 30,
            }
        result["_enhanced"] = {"houses": d10_houses}
    return result
