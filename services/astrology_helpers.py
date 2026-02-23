"""
Helpers for career rules: aspects (Vedic), Chara Karakas, Chandra Lagna, house connections,
Raja Yogas in D10, Upachaya, 8th house, Amsa deities.
"""
from typing import Dict, Any, List, Optional, Tuple

# Vedic aspect orb (degrees)
ASPECT_ORB = 8.0
# 7th house = full aspect (opposition from planet's house)
# Jupiter 5,7,9; Saturn 3,7,10; Mars 4,7,8; Rahu/Ketu 5,7,9
VEDIC_ASPECTS = {
    "Mars": [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus": [7],
    "Saturn": [3, 7, 10],
    "Sun": [7],
    "Moon": [7],
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9],
}

RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}
RASIS = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
]

# Chara Karaka order (highest degree = Atmakaraka, then Amatyakaraka, ...)
CHARA_KARAKA_NAMES = ["Atmakaraka", "Amatyakaraka", "Bhratrukaraka", "Matrukaraka", "Pitrukaraka", "Putrakaraka", "Gnatikaraka", "Darakaraka"]

# Navamsha amsa deities (9 parts per sign; first deity for part 0 of Aries, etc. – simplified 9 deities repeating)
NAVAMSA_DEITIES = [
    "Agni", "Brahma", "Vishnu", "Shiva", "Skanda", "Indra", "Kubera", "Varuna", "Mitra"
]


def _get_cusps(chart: Dict[str, Any]) -> List[float]:
    cusps = []
    if "_enhanced" in chart and "houses" in chart["_enhanced"]:
        for i in range(1, 13):
            key = f"House_{i}"
            if key in chart["_enhanced"]["houses"]:
                cusps.append(chart["_enhanced"]["houses"][key]["longitude"])
            else:
                cusps.append((i - 1) * 30.0)
    else:
        cusps = [i * 30.0 for i in range(12)]
    return cusps


def _which_house(lon: float, cusps: List[float]) -> int:
    lon = lon % 360
    for i in range(12):
        c, n = cusps[i], cusps[(i + 1) % 12]
        if n > c and c <= lon < n:
            return i + 1
        if n <= c and (lon >= c or lon < n):
            return i + 1
    return 10


def _planet_aspects_house(planet_house: int, aspect_house: int, planet: str) -> bool:
    """Vedic: planet in planet_house aspects aspect_house if (aspect_house - planet_house) % 12 is in aspect list."""
    diff = (aspect_house - planet_house) % 12
    if diff == 0:
        return True  # same house
    aspects = VEDIC_ASPECTS.get(planet, [7])
    return diff in aspects


def get_planets_aspecting_10th_house(d1: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return list of (planet, aspect_type) that aspect the 10th house cusp or 10th house."""
    cusps = _get_cusps(d1)
    if len(cusps) < 10:
        return []
    tenth_cusp = cusps[9]
    result = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        lon = pdata.get("longitude")
        if lon is None:
            continue
        ph = _which_house(lon, cusps)
        if not _planet_aspects_house(ph, 10, pname):
            continue
        diff = (10 - ph) % 12
        if diff == 0:
            result.append((pname, "occupation"))
        else:
            result.append((pname, "aspect"))
    return result


def get_planets_aspecting_10th_lord(d1: Dict[str, Any], tenth_lord: str) -> List[Tuple[str, str]]:
    """Return list of (planet, aspect_type) that aspect the 10th lord (by house position)."""
    if not tenth_lord:
        return []
    cusps = _get_cusps(d1)
    tenth_lord_house = None
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        if pname != tenth_lord and RASI_LORDS.get(pdata.get("rasi")) != tenth_lord:
            continue
        lon = pdata.get("longitude")
        if lon is not None:
            tenth_lord_house = _which_house(lon, cusps)
            break
    if tenth_lord_house is None:
        return []
    result = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        lon = pdata.get("longitude")
        if lon is None:
            continue
        ph = _which_house(lon, cusps)
        if not _planet_aspects_house(ph, tenth_lord_house, pname):
            continue
        if ph == tenth_lord_house:
            result.append((pname, "conjunction"))
        else:
            result.append((pname, "aspect"))
    return result


def chara_karakas(d1: Dict[str, Any]) -> Dict[str, str]:
    """
    Chara Karaka: order 8 bodies (7 planets + Rahu, exclude Ketu) by longitude descending.
    Assign Atmakaraka (highest), Amatyakaraka, Bhratrukaraka, Matrukaraka, Pitrukaraka, Putrakaraka, Gnatikaraka, Darakaraka (lowest).
    Returns dict karaka_name -> planet.
    """
    order = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]:
        if name not in d1 or not isinstance(d1[name], dict):
            continue
        lon = d1[name].get("longitude")
        if lon is not None:
            order.append((name, lon))
    order.sort(key=lambda x: -x[1])
    result = {}
    for i, (planet, _) in enumerate(order):
        if i < len(CHARA_KARAKA_NAMES):
            result[CHARA_KARAKA_NAMES[i]] = planet
    return result


def chandra_lagna_10th_house(d1: Dict[str, Any]) -> Optional[int]:
    """House number that is 10th from Moon (Chandra Lagna). Returns 1-12."""
    if "Moon" not in d1 or not isinstance(d1["Moon"], dict):
        return None
    cusps = _get_cusps(d1)
    moon_house = _which_house(d1["Moon"]["longitude"], cusps)
    return (moon_house + 9 - 1) % 12 + 1


def chandra_lagna_10th_lord_and_occupants(d1: Dict[str, Any]) -> Dict[str, Any]:
    """10th from Moon: that house number, its lord, and planets in it."""
    h10_from_moon = chandra_lagna_10th_house(d1)
    if h10_from_moon is None:
        return {}
    cusps = _get_cusps(d1)
    rasi_idx = int(cusps[h10_from_moon - 1] // 30) % 12
    lord = RASI_LORDS.get(RASIS[rasi_idx], "")
    occupants = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        lon = pdata.get("longitude")
        if lon is not None and _which_house(lon, cusps) == h10_from_moon:
            occupants.append(pname)
    return {"house": h10_from_moon, "lord": lord, "occupants": occupants}


def house_connections_10_11_lagna(d1: Dict[str, Any]) -> List[str]:
    """
    Connections between 10th, 11th, and Ascendant: same lord, exchange, or one lord in other's house.
    Returns list of description strings.
    """
    cusps = _get_cusps(d1)
    lord_10 = RASI_LORDS.get(RASIS[int(cusps[9] // 30) % 12], "") if len(cusps) >= 10 else ""
    lord_11 = RASI_LORDS.get(RASIS[int(cusps[10] // 30) % 12], "") if len(cusps) >= 11 else ""
    lord_1 = RASI_LORDS.get(RASIS[int(cusps[0] // 30) % 12], "") if cusps else ""
    if not lord_10 or not lord_11 or not lord_1:
        return []
    connections = []
    def house_of_lord(lord):
        for pname, pdata in d1.items():
            if pname.startswith("_") or not isinstance(pdata, dict):
                continue
            if pname == lord or RASI_LORDS.get(pdata.get("rasi")) == lord:
                lon = pdata.get("longitude")
                if lon is not None:
                    return _which_house(lon, cusps)
        return None
    h10L, h11L, h1L = house_of_lord(lord_10), house_of_lord(lord_11), house_of_lord(lord_1)
    if lord_10 == lord_11:
        connections.append("10th and 11th lord same")
    if lord_10 == lord_1:
        connections.append("10th and Lagna lord same")
    if lord_11 == lord_1:
        connections.append("11th and Lagna lord same")
    if h10L == 11:
        connections.append("10th lord in 11th")
    if h10L == 1:
        connections.append("10th lord in Lagna")
    if h11L == 10:
        connections.append("11th lord in 10th")
    if h1L == 10:
        connections.append("Lagna lord in 10th")
    return connections


def raja_yoga_participants_in_d10(d1: Dict[str, Any], d10: Dict[str, Any], yogas: List[Dict]]) -> List[Dict[str, Any]]:
    """
    For each yoga that involves planets, check if those planets are strong in D10 (own sign/exalted).
    Returns list of {yoga_name, planets, strong_in_d10: [list]}.
    """
    if not yogas:
        return []
    result = []
    for yoga in yogas:
        planets = yoga.get("planets", [])
        if not planets:
            continue
        strong = []
        for p in planets:
            if p not in d10 or not isinstance(d10[p], dict):
                continue
            rasi = d10[p].get("rasi", "")
            lord = RASI_LORDS.get(rasi, "")
            if p == lord:
                strong.append(p)
        result.append({"yoga_name": yoga.get("name", ""), "planets": planets, "strong_in_d10": strong})
    return result


def upachaya_sun_saturn(chart: Dict[str, Any]) -> Dict[str, List[str]]:
    """Sun or Saturn in Upachaya houses (3, 6, 10, 11). Returns {sun: [houses], saturn: [houses]}."""
    cusps = _get_cusps(chart)
    out = {"sun": [], "saturn": []}
    for pname in ["Sun", "Saturn"]:
        if pname not in chart or not isinstance(chart[pname], dict):
            continue
        lon = chart[pname].get("longitude")
        if lon is None:
            continue
        h = _which_house(lon, cusps)
        if h in (3, 6, 10, 11):
            out["sun" if pname == "Sun" else "saturn"].append(h)
    return out


def eighth_house_factors(chart: Dict[str, Any]) -> Dict[str, Any]:
    """8th house: lord, occupants, strength (for transformations/retirement)."""
    cusps = _get_cusps(chart)
    if len(cusps) < 8:
        return {}
    rasi_idx = int(cusps[7] // 30) % 12
    lord = RASI_LORDS.get(RASIS[rasi_idx], "")
    occupants = []
    for pname, pdata in chart.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        lon = pdata.get("longitude")
        if lon is not None and _which_house(lon, cusps) == 8:
            occupants.append(pname)
    return {"lord": lord, "occupants": occupants}


def navamsha_amsa_deity(longitude: float) -> str:
    """Return the presiding deity of the Navamsha amsa for this longitude (D1)."""
    lon = longitude % 360
    rasi_index = int(lon // 30)
    degrees_in_rasi = lon % 30
    part = int(degrees_in_rasi / (30.0 / 9.0))
    if part >= 9:
        part = 8
    idx = (rasi_index * 9 + part) % len(NAVAMSA_DEITIES)
    return NAVAMSA_DEITIES[idx]
