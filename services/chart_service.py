"""
ChartService: orchestrates D1/D10 calculation and chart analysis.
Uses enhanced Swiss Ephemeris and D10 calculator; analyzes houses and lords.
"""
import logging
from datetime import date, time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Rasi lords (same as career_rules / enhanced_swiss_ephemeris)
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
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]


def _get_cusps(chart_data: Dict[str, Any]) -> List[float]:
    """Extract house cusp longitudes from chart (D1 or D10)."""
    cusps = []
    if "_enhanced" in chart_data and "houses" in chart_data["_enhanced"]:
        houses = chart_data["_enhanced"]["houses"]
        for i in range(1, 13):
            key = f"House_{i}"
            if key in houses:
                cusps.append(houses[key]["longitude"])
            else:
                cusps.append((i - 1) * 30.0)
    else:
        cusps = [i * 30.0 for i in range(12)]
    return cusps


def _which_house(longitude: float, cusps: List[float]) -> int:
    """Return 1-based house number for a longitude."""
    lon = longitude % 360
    for i in range(12):
        cusp = cusps[i]
        next_cusp = cusps[(i + 1) % 12]
        if next_cusp > cusp:
            if cusp <= lon < next_cusp:
                return i + 1
        else:
            if lon >= cusp or lon < next_cusp:
                return i + 1
    return 10


class ChartService:
    """Orchestrates chart calculation and analysis."""

    def __init__(self):
        pass

    def calculate_birth_chart(
        self,
        date_of_birth: date,
        time_of_birth: time,
        latitude: float,
        longitude: float,
        timezone_name: str = "UTC",
        chart_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Calculate D1 and optionally D10. Returns dict with d1, d10 (if requested).
        Uses sidereal (Lahiri) positions; tropical not stored separately (same module uses sidereal).
        """
        if chart_types is None:
            chart_types = ["D1", "D10"]
        result = {}
        try:
            from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions
            d1 = calculate_enhanced_planetary_positions(
                date_of_birth=date_of_birth,
                time_of_birth=time_of_birth,
                latitude=latitude,
                longitude=longitude,
                timezone_name=timezone_name,
            )
            if not d1:
                logger.warning("D1 calculation returned empty")
                return result
            result["d1"] = d1
            if "D10" in chart_types:
                from services.d10_dasamsa import calculate_d10_chart
                d10 = calculate_d10_chart(d1)
                result["d10"] = d10
            return result
        except Exception as e:
            logger.exception("calculate_birth_chart failed: %s", e)
            return result

    def get_house_lord(self, chart_data: Dict[str, Any], house_num: int) -> str:
        """Return planet that rules the sign on the cusp of the given house (1-12)."""
        if house_num < 1 or house_num > 12:
            return ""
        cusps = _get_cusps(chart_data)
        if len(cusps) < house_num:
            return ""
        cusp_lon = cusps[house_num - 1]
        rasi_index = int(cusp_lon // 30) % 12
        rasi = RASIS[rasi_index]
        return RASI_LORDS.get(rasi, "")

    def get_planets_in_house(self, chart_data: Dict[str, Any], house_num: int) -> List[str]:
        """Return list of planet names in the specified house (1-12). Handles house boundaries."""
        cusps = _get_cusps(chart_data)
        out = []
        for name in PLANETS:
            if name not in chart_data or not isinstance(chart_data[name], dict):
                continue
            lon = chart_data[name].get("longitude")
            if lon is None:
                continue
            if _which_house(lon, cusps) == house_num:
                out.append(name)
        return out

    def analyze_d1_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        D1 analysis: 10th house occupants, 10th lord and its placement,
        Ascendant lord placement, Atmakaraka (highest degree excluding Rahu), 2nd and 6th house.
        """
        cusps = _get_cusps(chart_data)
        analysis = {
            "planets_in_10th": [],
            "tenth_lord": "",
            "tenth_lord_house": None,
            "ascendant_lord": "",
            "ascendant_lord_house": None,
            "atmakaraka": "",
            "planets_in_2nd": [],
            "planets_in_6th": [],
        }
        analysis["planets_in_10th"] = self.get_planets_in_house(chart_data, 10)
        analysis["planets_in_2nd"] = self.get_planets_in_house(chart_data, 2)
        analysis["planets_in_6th"] = self.get_planets_in_house(chart_data, 6)
        analysis["tenth_lord"] = self.get_house_lord(chart_data, 10)
        analysis["ascendant_lord"] = self.get_house_lord(chart_data, 1)
        # Where is 10th lord?
        tenth_lord = analysis["tenth_lord"]
        for name, pdata in chart_data.items():
            if name.startswith("_") or not isinstance(pdata, dict):
                continue
            lon = pdata.get("longitude")
            if lon is None:
                continue
            if name == tenth_lord or (isinstance(pdata.get("rasi"), str) and RASI_LORDS.get(pdata["rasi"]) == tenth_lord):
                analysis["tenth_lord_house"] = _which_house(lon, cusps)
                break
        # Ascendant lord placement
        asc_lord = analysis["ascendant_lord"]
        for name, pdata in chart_data.items():
            if name.startswith("_") or not isinstance(pdata, dict):
                continue
            lon = pdata.get("longitude")
            if lon is None:
                continue
            if name == asc_lord or (isinstance(pdata.get("rasi"), str) and RASI_LORDS.get(pdata["rasi"]) == asc_lord):
                analysis["ascendant_lord_house"] = _which_house(lon, cusps)
                break
        # Atmakaraka: planet with highest longitude (excluding Rahu)
        max_lon = -1.0
        for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ketu"]:
            if name not in chart_data:
                continue
            lon = chart_data[name].get("longitude")
            if lon is not None and lon > max_lon:
                max_lon = lon
                analysis["atmakaraka"] = name
        return analysis

    def analyze_d10_chart(self, d10_data: Dict[str, Any], d1_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        D10 analysis: 10th house occupants, D10 10th lord, D10 Asc lord,
        planet strengths in D10, planets in Kendra (1,4,7,10), Vargottama (same sign in D1 and D10).
        """
        cusps = _get_cusps(d10_data)
        analysis = {
            "planets_in_10th": [],
            "tenth_lord": "",
            "ascendant_lord": "",
            "ascendant_lord_house": None,
            "planets_in_kendra": [],
            "vargottama": [],
            "strong_planets": [],
        }
        analysis["planets_in_10th"] = self.get_planets_in_house(d10_data, 10)
        analysis["tenth_lord"] = self.get_house_lord(d10_data, 10)
        analysis["ascendant_lord"] = self.get_house_lord(d10_data, 1)
        for name, pdata in d10_data.items():
            if name.startswith("_") or not isinstance(pdata, dict):
                continue
            lon = pdata.get("longitude")
            if lon is None:
                continue
            h = _which_house(lon, cusps)
            if h in (1, 4, 7, 10):
                analysis["planets_in_kendra"].append(name)
            # Vargottama: same rasi in D1 and D10
            if name in d1_data and isinstance(d1_data[name], dict):
                rasi_d1 = d1_data[name].get("rasi")
                rasi_d10 = pdata.get("rasi")
                if rasi_d1 and rasi_d1 == rasi_d10:
                    analysis["vargottama"].append(name)
            # Strength: own sign or exalted (simplified)
            rasi = pdata.get("rasi", "")
            lord = RASI_LORDS.get(rasi, "")
            if name == lord:
                analysis["strong_planets"].append(name)
        asc_lord = analysis["ascendant_lord"]
        for name, pdata in d10_data.items():
            if name.startswith("_") or not isinstance(pdata, dict):
                continue
            lon = pdata.get("longitude")
            if lon is None:
                continue
            if name == asc_lord or (pdata.get("rasi") and RASI_LORDS.get(pdata["rasi"]) == asc_lord):
                analysis["ascendant_lord_house"] = _which_house(lon, cusps)
                break
        return analysis
