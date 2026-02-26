"""
ParasaraRulesEngine: traditional career significations and weighted rules.
Returns (career, score) tuples; normalizes to 0-100; supports career categories.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from utils.helpers import career_category_mapping

logger = logging.getLogger(__name__)

# Career significations per planet (Parasara/D10 source: Sun Gov, Moon Sales/PR, Mercury Trade/Writing, Mars Eng/Defense, Jupiter Law/Education, Venus Arts, Saturn Labor/Admin, Rahu/Ketu Tech/Occult)
CAREER_SIGNIFICATIONS = {
    "Sun": ["Government", "Administration", "Politics", "Leadership", "Medicine", "Authority"],
    "Moon": ["Sales", "Public Relations", "Nursing", "Hospitality", "Psychology", "Travel", "Catering"],
    "Mars": ["Engineering", "Military", "Police", "Surgery", "Real Estate", "Sports"],
    "Mercury": ["Business", "Communication", "Writing", "Accounting", "Mathematics", "IT", "Trade"],
    "Jupiter": ["Teaching", "Law", "Finance", "Banking", "Advisory", "Philosophy", "Education"],
    "Venus": ["Arts", "Entertainment", "Fashion", "Beauty", "Luxury Goods", "Hotels"],
    "Saturn": ["Labor", "Service", "Technology", "Research", "Mining", "Agriculture", "Oil", "Administration"],
    "Rahu": ["Foreign", "Technology", "Media", "Unconventional", "Aviation", "Electronics"],
    "Ketu": ["Spirituality", "Research", "Occult", "Psychology", "Investigation", "Astrology"],
}

# Rule weights (sum to 138; we normalize)
RULE_WEIGHTS = {
    "rule_10th_house_occupants": 30,
    "rule_10th_lord_placement": 25,
    "rule_d10_10th_house": 20,
    "rule_atmakaraka": 15,
    "rule_current_mahadasa": 10,
    "rule_planet_strength_d10": 18,
}

# Good houses for 10th lord (Kendra 1,4,7,10 + Trikona 5,9 + 2nd wealth/speech + 11th gains; Parasara/traditional)
GOOD_HOUSES_10TH_LORD = {1, 2, 4, 5, 7, 9, 10, 11}


def _planet_career_scores(planets: List[str], weight: float) -> Dict[str, float]:
    """Convert list of planets to career -> score dict (equal share of weight per career)."""
    scores = {}
    if not planets:
        return scores
    per_planet = weight / len(planets)
    for planet in planets:
        careers = CAREER_SIGNIFICATIONS.get(planet, [])
        if not careers:
            continue
        per_career = per_planet / len(careers)
        for c in careers:
            scores[c] = scores.get(c, 0) + per_career
    return scores


def _merge_scores(acc: Dict[str, float], new: Dict[str, float]) -> None:
    for k, v in new.items():
        acc[k] = acc.get(k, 0) + v


class ParasaraRulesEngine:
    """Apply Parasara career rules and aggregate scores."""

    def __init__(self):
        self.weights = RULE_WEIGHTS.copy()

    def rule_10th_house_occupants(self, d1_chart: Dict[str, Any]) -> Dict[str, float]:
        """Weight 30. Planets in 10th house in D1 -> career scores."""
        planets = _get_planets_in_house(d1_chart, 10)
        return _planet_career_scores(planets, self.weights["rule_10th_house_occupants"])

    def rule_10th_lord_placement(self, d1_chart: Dict[str, Any]) -> Dict[str, float]:
        """Weight 25. 10th lord in good houses (1,4,5,7,9,10,11) -> higher weight for its significations."""
        tenth_lord = _get_house_lord(d1_chart, 10)
        if not tenth_lord:
            return {}
        house = _planet_house(d1_chart, tenth_lord)
        weight = self.weights["rule_10th_lord_placement"]
        if house in GOOD_HOUSES_10TH_LORD:
            weight = weight * 1.2
        return _planet_career_scores([tenth_lord], weight)

    def rule_d10_10th_house(self, d10_chart: Dict[str, Any]) -> Dict[str, float]:
        """Weight 20. Planets in 10th house in D10 -> career scores."""
        planets = _get_planets_in_house(d10_chart, 10)
        return _planet_career_scores(planets, self.weights["rule_d10_10th_house"])

    def rule_atmakaraka(self, d1_chart: Dict[str, Any]) -> Dict[str, float]:
        """Weight 15. Planet with highest degree (excluding Rahu) -> career scores."""
        atmakaraka = _get_atmakaraka(d1_chart)
        if not atmakaraka:
            return {}
        return _planet_career_scores([atmakaraka], self.weights["rule_atmakaraka"])

    def rule_current_mahadasa(self, dasa_data: Dict[str, Any], current_date: Any = None) -> Dict[str, float]:
        """Weight 10. Current Mahadasa lord -> career scores."""
        lord = None
        if isinstance(dasa_data, dict):
            lord = dasa_data.get("current_dasa") or dasa_data.get("current_mahadasa")
        if not lord:
            return {}
        return _planet_career_scores([lord], self.weights["rule_current_mahadasa"])

    def rule_planet_strength_d10(self, d10_chart: Dict[str, Any]) -> Dict[str, float]:
        """Weight 18. Strongest planet in D10 (own sign / exalted / vargottama) -> career scores."""
        strong = _strong_planets_d10(d10_chart)
        return _planet_career_scores(strong, self.weights["rule_planet_strength_d10"])

    def rule_service_vs_business(self, d10_chart: Dict[str, Any]) -> Dict[str, float]:
        """D10: 6th stronger than 7th -> service; 7th stronger -> business (Status Trinity / Artha)."""
        planets_6 = _get_planets_in_house(d10_chart, 6)
        planets_7 = _get_planets_in_house(d10_chart, 7)
        weight = 8.0
        if len(planets_6) > len(planets_7):
            return {"Service": weight}
        if len(planets_7) > len(planets_6):
            return {"Business": weight}
        return {}

    def rule_10th_lord_2nd_3rd_sales(self, d1_chart: Dict[str, Any]) -> Dict[str, float]:
        """10th lord in 2nd (speech) or 3rd (travel) -> Sales/Marketing emphasis (Parasara sales markers)."""
        tenth_lord = _get_house_lord(d1_chart, 10)
        if not tenth_lord:
            return {}
        house = _planet_house(d1_chart, tenth_lord)
        if house not in (2, 3):
            return {}
        return {"Sales": 12.0, "Marketing": 10.0}

    def apply_all_rules(
        self,
        d1_chart: Dict[str, Any],
        d10_chart: Dict[str, Any],
        dasa_data: Dict[str, Any],
    ) -> List[Tuple[str, float]]:
        """Apply all rules and return sorted list of (career, score) tuples."""
        total = {}
        # D1
        _merge_scores(total, self.rule_10th_house_occupants(d1_chart))
        _merge_scores(total, self.rule_10th_lord_placement(d1_chart))
        _merge_scores(total, self.rule_atmakaraka(d1_chart))
        # D10
        _merge_scores(total, self.rule_d10_10th_house(d10_chart))
        _merge_scores(total, self.rule_planet_strength_d10(d10_chart))
        _merge_scores(total, self.rule_service_vs_business(d10_chart))
        # D1 sales markers
        _merge_scores(total, self.rule_10th_lord_2nd_3rd_sales(d1_chart))
        # Dasa
        _merge_scores(total, self.rule_current_mahadasa(dasa_data))
        return self.normalize_scores(total)

    def normalize_scores(self, career_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """Normalize to 0-100, sort descending, return top 10."""
        if not career_scores:
            return []
        m = max(career_scores.values())
        if m <= 0:
            return []
        normalized = [(c, (s / m) * 100) for c, s in career_scores.items()]
        normalized.sort(key=lambda x: -x[1])
        return normalized[:10]

    def get_career_category(self, career: str) -> str:
        """Map specific career to category."""
        return career_category_mapping(career)


# Helpers used by rules
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


def _get_house_lord(chart: Dict[str, Any], house_num: int) -> str:
    if house_num < 1 or house_num > 12:
        return ""
    cusps = _get_cusps(chart)
    if len(cusps) < house_num:
        return ""
    rasi_idx = int(cusps[house_num - 1] // 30) % 12
    return RASI_LORDS.get(RASIS[rasi_idx], "")


def _get_planets_in_house(chart: Dict[str, Any], house_num: int) -> List[str]:
    cusps = _get_cusps(chart)
    out = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]:
        if name not in chart or not isinstance(chart[name], dict):
            continue
        lon = chart[name].get("longitude")
        if lon is None:
            continue
        if _which_house(lon, cusps) == house_num:
            out.append(name)
    return out


def _planet_house(chart: Dict[str, Any], planet: str) -> Optional[int]:
    cusps = _get_cusps(chart)
    for name, data in chart.items():
        if name.startswith("_") or not isinstance(data, dict):
            continue
        if name != planet:
            continue
        lon = data.get("longitude")
        if lon is not None:
            return _which_house(lon, cusps)
    return None


def _get_atmakaraka(chart: Dict[str, Any]) -> str:
    max_lon = -1.0
    out = ""
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ketu"]:
        if name not in chart:
            continue
        lon = chart[name].get("longitude")
        if lon is not None and lon > max_lon:
            max_lon = lon
            out = name
    return out


def _strong_planets_d10(d10_chart: Dict[str, Any]) -> List[str]:
    """Planets in own sign or exalted in D10 (simplified)."""
    strong = []
    for name, data in d10_chart.items():
        if name.startswith("_") or not isinstance(data, dict):
            continue
        rasi = data.get("rasi", "")
        lord = RASI_LORDS.get(rasi, "")
        if name == lord:
            strong.append(name)
    return strong
