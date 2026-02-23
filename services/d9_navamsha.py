"""
D9 (Navamsha) calculation – Parasara method.
Each sign divided into 9 equal parts of 3°20'; starting sign depends on sign nature:
- Movable (Chara): Aries, Cancer, Libra, Capricorn – start from same sign
- Fixed (Sthira): Taurus, Leo, Scorpio, Aquarius – start from 9th sign
- Dual (Dwiswabhava): Gemini, Virgo, Sagittarius, Pisces – start from 5th sign
"""
from typing import Dict, Any, List

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
# Movable=0,3,6,9; Fixed=1,4,7,10; Dual=2,5,8,11
# Chara: part 0 = same sign. Sthira: part 0 = 9th sign = Capricorn (9) for Taurus -> start 8. Dual: part 0 = 5th sign = Libra (6) for Gemini -> start 4.
NAVAMSA_START_OFFSET = {
    0: 0, 3: 0, 6: 0, 9: 0,   # Chara: start from self
    1: 8, 4: 8, 7: 8, 10: 8,   # Sthira: start from 9th sign (Capricorn for Taurus 0-3°20')
    2: 4, 5: 4, 8: 4, 11: 4,   # Dual: start from 5th sign (Libra for Gemini 0-3°20')
}


def d1_longitude_to_d9_rasi_index(longitude: float) -> int:
    """Return 0-11 rasi index of the Navamsha sign for a D1 longitude."""
    lon = longitude % 360
    rasi_index = int(lon // 30) % 12
    degrees_in_rasi = lon % 30
    part = int(degrees_in_rasi / (30.0 / 9.0))  # 0..8
    if part >= 9:
        part = 8
    offset = NAVAMSA_START_OFFSET.get(rasi_index, 0)
    # FIXED: Add rasi_index to offset, not just offset alone
    navamsha_rasi_index = (rasi_index + offset + part) % 12
    return navamsha_rasi_index


# One navamsha = 30/9 = 3°20'
NAVAMSA_PART_SIZE = 30.0 / 9.0


def d1_longitude_to_d9_longitude(longitude: float) -> float:
    """Return D9 longitude (0-360): position within the 3°20' part scaled to 0-30 in navamsha sign."""
    lon = float(longitude % 360)
    rasi_index = d1_longitude_to_d9_rasi_index(lon)
    degrees_in_rasi = lon % 30
    part = int(degrees_in_rasi / NAVAMSA_PART_SIZE)
    if part >= 9:
        part = 8
    position_in_part = degrees_in_rasi - part * NAVAMSA_PART_SIZE  # 0 to 3°20'
    d9_degrees = position_in_part * (30.0 / NAVAMSA_PART_SIZE)  # scale to 0-30 in D9 sign
    return rasi_index * 30.0 + d9_degrees


def _get_planet_data(d1_positions: Dict[str, Any], name: str) -> Any:
    """Get planet data from d1, trying exact name and case variations."""
    if name in d1_positions:
        return d1_positions[name]
    low = name.lower()
    for k, v in d1_positions.items():
        if k.startswith("_"):
            continue
        if k.lower() == low:
            return v
    return None


def calculate_d9_chart(d1_positions: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build D9 chart from D1 planetary positions (Parasara Navamsha).
    Each sign divided into 9 parts of 3°20'; Chara=start from self, Sthira=9th sign, Dual=5th sign.
    Returns dict with planet -> {longitude, rasi, rasi_lord, retrograde, ...}.
    """
    if not d1_positions or not isinstance(d1_positions, dict):
        return {}
    result = {}
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    for name in planets:
        data = _get_planet_data(d1_positions, name)
        if not data or not isinstance(data, dict):
            continue
        lon = data.get("longitude")
        if lon is None:
            continue
        try:
            lon = float(lon)
        except (TypeError, ValueError):
            continue
        d9_rasi_idx = d1_longitude_to_d9_rasi_index(lon)
        d9_lon = d1_longitude_to_d9_longitude(lon)
        rasi = RASIS[d9_rasi_idx]
        result[name] = {
            "longitude": float(d9_lon),
            "rasi": rasi,
            "rasi_lord": RASI_LORDS.get(rasi, ""),
            "degrees_in_rasi": d9_lon % 30,
            "retrograde": bool(data.get("retrograde", False)),
        }
    if "_enhanced" in d1_positions and isinstance(d1_positions["_enhanced"], dict):
        houses = d1_positions["_enhanced"].get("houses") or {}
        if houses:
            d9_houses = {}
            for i in range(1, 13):
                key = f"House_{i}"
                if key in houses:
                    h = houses[key]
                    if isinstance(h, dict):
                        h_lon = h.get("longitude")
                        if h_lon is not None:
                            try:
                                h_lon = float(h_lon)
                            except (TypeError, ValueError):
                                continue
                            d9_rasi_idx = d1_longitude_to_d9_rasi_index(h_lon)
                            d9_lon = d1_longitude_to_d9_longitude(h_lon)
                            d9_houses[key] = {
                                "longitude": float(d9_lon),
                                "rasi": RASIS[d9_rasi_idx],
                                "degrees_in_rasi": d9_lon % 30,
                            }
            if d9_houses:
                result["_enhanced"] = {"houses": d9_houses}
    return result


def get_d9_dispositor_of_planet(d9_chart: Dict[str, Any], planet: str) -> str:
    """Return the dispositor (rasi lord) of the given planet in D9. Empty if not found."""
    if planet not in d9_chart or not isinstance(d9_chart[planet], dict):
        return ""
    return d9_chart[planet].get("rasi_lord", "")
