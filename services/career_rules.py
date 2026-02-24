"""
Deterministic Parasara-based career prediction rules.
Inputs: D1 chart, D10 chart, optional Dasha/BAV-SAV data.
Output: structured scores, contributing factors, and applied_rules (with names and explanations).
"""
from typing import Dict, Any, List, Optional

# Import additional Parasara career rules
try:
    from services.additional_career_rules import (
        check_yogakaraka_in_10th,
        check_parivartana_yoga_10th,
        check_neechabhanga_10th,
        check_sun_in_10th,
        check_9th_10th_lord_connection,
        check_exalted_planets_in_10th,
        check_rahu_ketu_in_10th,
        check_combust_planets_in_10th,
    )
except ImportError:
    check_yogakaraka_in_10th = None
    check_parivartana_yoga_10th = None
    check_neechabhanga_10th = None
    check_sun_in_10th = None
    check_9th_10th_lord_connection = None
    check_exalted_planets_in_10th = None
    check_rahu_ketu_in_10th = None
    check_combust_planets_in_10th = None

# Import aspects calculator
try:
    from services.aspects_calculator import (
        get_planets_aspecting_10th_house,
        get_planets_aspecting_10th_lord,
    )
except ImportError:
    get_planets_aspecting_10th_house = None
    get_planets_aspecting_10th_lord = None

# Helpers for D9, Chara Karakas, Chandra Lagna, house connections, yogas, Upachaya, 8th, Amsa
try:
    from services.astrology_helpers import (
        chara_karakas,
        chandra_lagna_10th_lord_and_occupants,
        house_connections_10_11_lagna,
        raja_yoga_participants_in_d10,
        upachaya_sun_saturn,
        eighth_house_factors,
        navamsha_amsa_deity,
    )
    from services.d9_navamsha import calculate_d9_chart, get_d9_dispositor_of_planet
except Exception:
    chara_karakas = None
    chandra_lagna_10th_lord_and_occupants = None
    house_connections_10_11_lagna = None
    raja_yoga_participants_in_d10 = None
    upachaya_sun_saturn = None
    eighth_house_factors = None
    navamsha_amsa_deity = None
    calculate_d9_chart = None
    get_d9_dispositor_of_planet = None

# Human-readable names and explanations for each rule (for UI display)
RULE_META: Dict[str, Dict[str, str]] = {
    "D1_10th_lord_in_10th": {
        "name": "10th lord in 10th house (D1)",
        "explanation": "The lord of the 10th house (career) placed in the 10th house in the birth chart. This is a strong Parasara combination for career and authority.",
    },
    "D1_10th_lord_in_own_sign": {
        "name": "10th lord in own sign (D1)",
        "explanation": "The 10th house lord is in its own rasi in D1, strengthening career significations.",
    },
    "D1_10th_lord_exalted": {
        "name": "10th lord exalted (D1)",
        "explanation": "The 10th house lord is in its exaltation sign in the birth chart, indicating strong career potential.",
    },
    "d1_10th_lord_placement": {
        "name": "10th lord placement score",
        "explanation": "Composite score for where the 10th lord is placed (own house, own sign, or exaltation).",
    },
    "D1_planets_in_10th": {
        "name": "Planets in 10th house (D1)",
        "explanation": "Planets occupying the 10th house influence career. Benefics (Jupiter, Venus, Mercury, Moon) support; malefics (Saturn, Mars, Rahu, Ketu) can create challenges or drive ambition.",
    },
    "d1_10th_benefics": {
        "name": "Benefics in 10th house",
        "explanation": "Number of benefic planets (Jupiter, Venus, Mercury, Moon) in the 10th house. More benefics generally support reputation and career growth.",
    },
    "d1_10th_malefics": {
        "name": "Malefics in 10th house",
        "explanation": "Number of malefic planets (Saturn, Mars, Rahu, Ketu) in the 10th. Can indicate drive and authority or obstacles depending on dignity.",
    },
    "D10_10th_rasi": {
        "name": "D10 (Dasamsa) 10th house",
        "explanation": "The 10th house of the career divisional chart (D10) shows profession and status. Its sign is evaluated for strength.",
    },
    "current_dasa_lord_is_10th_lord": {
        "name": "Current Dasha lord is 10th lord",
        "explanation": "The running major period (Mahadasha) is of the planet that rules the 10th house. Career matters are highlighted in this period.",
    },
    "current_bhukti_lord_is_10th_lord": {
        "name": "Current Bhukti lord is 10th lord",
        "explanation": "The running sub-period (Antardasha) is of the 10th lord. Strong timing for career events.",
    },
    "dasha_10th_link": {
        "name": "Dasha–10th link",
        "explanation": "Major period lord connected to career (10th house).",
    },
    "bhukti_10th_link": {
        "name": "Bhukti–10th link",
        "explanation": "Sub-period lord connected to career (10th house).",
    },
    "SAV_10th_house_bindus": {
        "name": "SAV (Ashtakavarga) 10th house",
        "explanation": "Sodhya Pindas (bindus) in the 10th house from Ashtakavarga. 30+ bindus indicate strong career support; 26+ good; below 26 moderate.",
    },
    "sav_10th": {
        "name": "SAV 10th house score",
        "explanation": "Strength of the 10th house from the Ashtakavarga SAV chart. Higher score means better planetary support for career.",
    },
    "D10_10th_lord_transposition": {
        "name": "10th lord transposition (D1→D10)",
        "explanation": "The 10th lord from D1 is located in D10. If strong and well-placed in D10, success in profession is likely (Parasara interactive rule).",
    },
    "D10_10th_lord_weak": {
        "name": "10th lord weak in D10",
        "explanation": "Contradictory strength: 10th lord strong in D1 but weak in D10 can indicate gifted ability with vacillating public status or success.",
    },
    "Vargottama": {
        "name": "Vargottama (same sign in D1 and D10)",
        "explanation": "Planets in the same sign in Rashi and Dashamsha are exceptionally powerful for professional talents.",
    },
    "D10_Kendra_benefics": {
        "name": "Benefics in Kendra in D10",
        "explanation": "Benefics in Kendra (1, 4, 7, 10) in D10 promise promotions and success during their Dasha periods.",
    },
    "D10_Kendra_malefics": {
        "name": "Malefics in Kendra in D10",
        "explanation": "Malefics in Kendra in D10 may cause setbacks; their Dashas need care.",
    },
    "D10_sign_nature_10th": {
        "name": "Sign nature (Tatwa) of 10th house in D10",
        "explanation": "The element (fire/earth/air/water) of the sign in the 10th house in D10 gives clues to the type of profession.",
    },
    "D1_10th_lord_in_2nd_3rd": {
        "name": "10th lord in 2nd or 3rd house",
        "explanation": "10th lord in 2nd (speech) or 3rd (travel) often indicates sales, marketing, or communication-related profession.",
    },
    "aspects_to_10th_house": {
        "name": "Aspects to 10th house",
        "explanation": "Planets aspecting the 10th house (Karma house) influence the profession (Vedic drishti).",
    },
    "aspects_to_10th_lord": {
        "name": "Aspects to 10th lord",
        "explanation": "Planets aspecting the 10th lord influence career and authority.",
    },
    "D9_dispositor_10th_lord": {
        "name": "D9 (Navamsha) dispositor of 10th lord",
        "explanation": "The dispositor of the 10th lord in D9 refines the profession indication.",
    },
    "house_connections_10_11_lagna": {
        "name": "House connections (10th–11th–Ascendant)",
        "explanation": "Connections between 10th (career), 11th (gains), and Ascendant (self) strengthen professional promise.",
    },
    "chandra_lagna_10th": {
        "name": "10th from Moon (Chandra Lagna)",
        "explanation": "Profession should also be analyzed from the 10th house relative to the Moon.",
    },
    "chara_karakas": {
        "name": "Chara Karakas (AmK, DK, etc.)",
        "explanation": "Amatyakaraka indicates nature of work; Darakaraka can show financial position.",
    },
    "raja_yoga_in_D10": {
        "name": "Raja Yogas in D1 and strength in D10",
        "explanation": "Raja Yogas in D1 must be checked for their strength and placement in D10.",
    },
    "upachaya_sun_saturn": {
        "name": "Upachaya (Sun/Saturn in 3,6,10,11)",
        "explanation": "Sun or Saturn in Upachaya houses (3, 6, 10, 11) indicates good job and capacity for hard labor.",
    },
    "eighth_house": {
        "name": "8th house (transformations / retirement)",
        "explanation": "8th house shows sudden transformations, setbacks, or retirement; strong 8th can also give sudden professional boost.",
    },
    "amsa_deities": {
        "name": "Amsa deities (Navamsha)",
        "explanation": "The presiding deity of a planet's Navamsha division gives the flavor of professional success (e.g. Indra for power, Kubera for wealth).",
    },
    "yogakaraka_in_10th": {
        "name": "Yogakaraka planet in 10th house",
        "explanation": "Yogakaraka (planet ruling both kendra and trikona for the lagna) in 10th house is extremely auspicious for career success and authority.",
    },
    "parivartana_yoga_10th": {
        "name": "Parivartana Yoga involving 10th",
        "explanation": "Exchange (Parivartana) between 10th lord and another planet creates special career combinations. Maha Parivartana (between kendras/trikonas) is best.",
    },
    "neechabhanga_10th": {
        "name": "Neechabhanga Raja Yoga in 10th",
        "explanation": "Debilitated planet in 10th with cancellation (Neechabhanga) creates powerful rags-to-riches career effect.",
    },
    "sun_in_10th": {
        "name": "Sun in 10th house",
        "explanation": "Sun is the natural karaka (significator) for authority and government. In 10th, strongly indicates leadership/government career.",
    },
    "dharma_karma_yoga": {
        "name": "9th-10th lord connection (Dharma-Karma Yoga)",
        "explanation": "Connection between 9th lord (fortune, dharma) and 10th lord (career, karma) creates fortunate career opportunities.",
    },
    "exalted_in_10th": {
        "name": "Exalted planets in 10th",
        "explanation": "Exalted planets in 10th house are extremely powerful and give excellent career results in their respective domains.",
    },
    "rahu_ketu_in_10th": {
        "name": "Rahu or Ketu in 10th house",
        "explanation": "Rahu in 10th indicates foreign/unconventional career. Ketu in 10th indicates spiritual/research career with detachment from worldly success.",
    },
    "combust_in_10th": {
        "name": "Combust planets in 10th",
        "explanation": "Planets combust (too close to Sun) in 10th house are weakened and may indicate career obstacles or delayed success.",
    },
    # Phase 1 Enhancements
    "d10_lagna_strength": {
        "name": "D10 Lagna (Ascendant) strength",
        "explanation": "The D10 Ascendant sign and its lord show the native's professional personality and approach to career. Strong placement indicates confidence and capability.",
    },
    "d10_lagna_lord_placement": {
        "name": "D10 Lagna lord placement",
        "explanation": "D10 Lagna lord in Kendra (1,4,7,10) or Trikona (1,5,9) houses shows strong professional foundation and positive approach to work.",
    },
    "d10_10th_lord_placement": {
        "name": "D10 10th lord placement",
        "explanation": "The lord of the 10th house in D10 chart shows career actions and professional achievements. Strong placement brings success.",
    },
    "big_three_lords": {
        "name": "Big Three Lords (D10 Lagna + D10 10th + D1 10th)",
        "explanation": "Combined strength of the three most important career lords: D10 Lagna lord (personality), D10 10th lord (career actions), D1 10th lord (life purpose).",
    },
    "artha_trikona": {
        "name": "Artha Trikona (2nd, 6th, 10th houses)",
        "explanation": "The wealth triangle houses. Strong 2nd (income), 6th (service), and 10th (career) houses indicate financial success through profession.",
    },
    "business_vs_job": {
        "name": "Business vs. Job indicator",
        "explanation": "6th house strength (service/job) vs. 7th house strength (business/partnerships). Stronger 7th indicates entrepreneurial path.",
    },
    "saturn_in_d10": {
        "name": "Saturn placement in D10",
        "explanation": "Saturn's position in D10 shows obstacles, discipline requirements, and delayed but lasting success. Favorable placement in 3,6,10,11 (Upachaya) is beneficial.",
    },
    # Phase 2 Enhancements
    "planetary_career_indicators": {
        "name": "Planetary Career Type Indicators",
        "explanation": "Strong planets in 10th house or as 10th lord indicate specific career fields: Sun=Government/Authority, Moon=Healthcare/Public, Mars=Military/Technical, Mercury=Communication/Business, Jupiter=Teaching/Finance, Venus=Arts/Luxury, Saturn=Labor/Service.",
    },
    "d10_2nd_house": {
        "name": "D10 2nd house (Speech & Finance)",
        "explanation": "The 2nd house in D10 shows income from profession, speech/communication in career, and financial gains. Strong 2nd house indicates good earning potential.",
    },
    "d10_4th_house": {
        "name": "D10 4th house (Assets & Peace)",
        "explanation": "The 4th house in D10 shows assets through career, workplace environment, and inner peace in profession. Benefics here indicate comfortable work conditions.",
    },
    "d10_8th_house": {
        "name": "D10 8th house (Research & Transformation)",
        "explanation": "The 8th house in D10 indicates research-oriented career, sudden changes, inheritance, and transformation through profession. Strong 8th can give occult/mystical careers.",
    },
    "d10_9th_house": {
        "name": "D10 9th house (Fortune & Teaching)",
        "explanation": "The 9th house in D10 shows fortune in career, higher learning, teaching, philosophy, and long-distance work. Benefics bring luck and recognition.",
    },
    "dasha_career_timing": {
        "name": "Dasha periods for career timing",
        "explanation": "Current and upcoming Dasha periods show timing for career events. Dasha of 10th lord, planets in 10th, or planets aspecting 10th bring career opportunities.",
    },
    "d1_d10_strength_comparison": {
        "name": "D1 vs D10 strength comparison",
        "explanation": "Comparing planet strength in D1 (birth chart) and D10 (career chart). Planets strong in both give consistent success; strong in D10 only gives career-specific talent.",
    },
    "moon_10th_career": {
        "name": "10th house from Moon (Chandra Lagna)",
        "explanation": "The 10th house counted from Moon shows emotional satisfaction in career and public perception. Should align with 10th from Ascendant for fulfillment.",
    },
    "d10_benefic_malefic_ratio": {
        "name": "Benefics vs Malefics ratio in D10",
        "explanation": "The ratio of benefic to malefic planets in D10 shows overall career environment. More benefics indicate smooth progress; more malefics indicate struggle and effort.",
    },
    # Phase 3 Advanced Enhancements
    "exalted_in_both_d1_d10": {
        "name": "Planets exalted in both D1 and D10",
        "explanation": "Planets exalted in both birth chart and career chart show exceptional, consistent talent that manifests strongly in profession. These are rare and highly auspicious.",
    },
    "jupiter_aspects_d10": {
        "name": "Jupiter aspects in D10",
        "explanation": "Jupiter's aspects in D10 bring wisdom, expansion, opportunities, and protection to the aspected houses/planets. Jupiter's 5th, 7th, and 9th aspects are particularly beneficial.",
    },
    "saturn_aspects_d10": {
        "name": "Saturn aspects in D10",
        "explanation": "Saturn's aspects in D10 bring discipline, structure, delays, and responsibility to aspected houses/planets. Can indicate areas requiring patience and systematic effort.",
    },
    "retrograde_planets_d10": {
        "name": "Retrograde planets in D10",
        "explanation": "Retrograde planets in D10 indicate unconventional career approaches, unique methods, and non-traditional paths. Can show genius in specialized fields or alternative career trajectories.",
    },
}

# 10th house significator: career, authority, profession
# Rasi lords for 10th house (house index 9 in 0-based)
RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter"
}
# Exaltation (simplified): lord in exaltation sign -> strong
EXALTATION = {
    "Sun": "Mesha", "Moon": "Vrischika", "Mars": "Makara", "Mercury": "Kanni",
    "Jupiter": "Kataka", "Venus": "Meena", "Saturn": "Thula",
}
# Own signs (lord in own sign -> strong)
OWN_SIGNS = {
    "Sun": ["Simha"], "Moon": ["Kataka"], "Mars": ["Mesha", "Vrischika"],
    "Mercury": ["Mithuna", "Kanni"], "Jupiter": ["Dhanus", "Meena"],
    "Venus": ["Rishaba", "Thula"], "Saturn": ["Makara", "Kumbha"],
}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu"}


def _which_house_d1(longitude: float, cusps: List[float]) -> int:
    """Return 1-based house number for a longitude given D1 house cusps (12 longitudes)."""
    lon = longitude % 360
    for i, cusp in enumerate(cusps):
        next_cusp = cusps[(i + 1) % 12]
        if next_cusp > cusp:
            if cusp <= lon < next_cusp:
                return i + 1
        else:
            if lon >= cusp or lon < next_cusp:
                return i + 1
    return 10


def _get_d1_cusps(d1: Dict[str, Any]) -> List[float]:
    """Extract house cusp longitudes from D1 chart."""
    cusps = []
    if "_enhanced" in d1 and "houses" in d1["_enhanced"]:
        houses = d1["_enhanced"]["houses"]
        for i in range(1, 13):
            key = f"House_{i}"
            if key in houses:
                cusps.append(houses[key]["longitude"])
            else:
                cusps.append((i - 1) * 30.0)  # fallback
    else:
        cusps = [i * 30.0 for i in range(12)]
    return cusps


def _d10_house_for_planet(d10: Dict[str, Any], planet: str) -> Optional[int]:
    """Get 1-based house of planet in D10 (simplified: use D10 cusps if present)."""
    if planet not in d10:
        return None
    if "_enhanced" in d10 and "houses" in d10["_enhanced"]:
        houses = d10["_enhanced"]["houses"]
        lon = d10[planet]["longitude"]
        cusps = [houses[f"House_{i}"]["longitude"] for i in range(1, 13)]
        return _which_house_d1(lon, cusps)
    return None


def _rule_meta(rule_id: str) -> Dict[str, str]:
    """Get name and explanation for a rule; support prefix match for parameterized ids."""
    if rule_id in RULE_META:
        return RULE_META[rule_id].copy()
    for key, meta in RULE_META.items():
        if rule_id.startswith(key) or key in rule_id:
            return meta.copy()
    return {"name": rule_id.replace("_", " ").title(), "explanation": "Vedic career rule applied."}


def _extract_chart_summary(d1: Dict[str, Any], d10: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key chart information for display in rules table."""
    summary = {}
    cusps = _get_d1_cusps(d1)

    # 10th house and lord
    if len(cusps) >= 10:
        house_10_rasi_idx = int(cusps[9] // 30) % 12
        rasis = ["Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
                 "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]
        house_10_rasi = rasis[house_10_rasi_idx]
        tenth_lord = RASI_LORDS.get(house_10_rasi, "")
        summary["tenth_house_rasi"] = house_10_rasi
        summary["tenth_lord"] = tenth_lord

        # Find 10th lord's position
        for pname, pdata in d1.items():
            if pname.startswith("_") or not isinstance(pdata, dict):
                continue
            if pname == tenth_lord or RASI_LORDS.get(pdata.get("rasi")) == tenth_lord:
                summary["tenth_lord_in_rasi"] = pdata.get("rasi", "")
                break

    # Planets in 10th house
    planets_in_10 = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict):
            continue
        if pdata.get("rasi") == summary.get("tenth_house_rasi"):
            planets_in_10.append(pname)
    summary["planets_in_10th"] = planets_in_10

    # Ascendant
    if "Ascendant" in d1 and isinstance(d1["Ascendant"], dict):
        summary["ascendant_rasi"] = d1["Ascendant"].get("rasi", "")

    return summary


def career_rules(
    d1: Dict[str, Any],
    d10: Dict[str, Any],
    dasha_current: Optional[Dict[str, Any]] = None,
    bav_sav_full: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Deterministic career strength and factors from D1, D10, optional Dasha/BAV-SAV.
    Returns: career_strength, factors, scores, applied_rules (list of {rule_id, name, explanation, score}).
    """
    factors: List[str] = []
    scores: Dict[str, float] = {}
    applied_rules: List[Dict[str, Any]] = []
    cusps = _get_d1_cusps(d1)

    # Extract chart summary for enhanced display
    chart_summary = _extract_chart_summary(d1, d10)

    # 1) 10th lord in D1
    house_10_rasi = None
    if len(cusps) >= 10:
        house_10_rasi_idx = int(cusps[9] // 30) % 12
        rasis = [
            "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
            "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"
        ]
        house_10_rasi = rasis[house_10_rasi_idx]
    tenth_lord = RASI_LORDS.get(house_10_rasi, "") if house_10_rasi else ""
    if tenth_lord:
        # Where is 10th lord in D1?
        for pname, pdata in d1.items():
            if pname.startswith("_") or pname == "House_Cusps":
                continue
            if not isinstance(pdata, dict) or "rasi" not in pdata:
                continue
            if RASI_LORDS.get(pdata["rasi"]) == tenth_lord or (pname == tenth_lord):
                if pdata.get("rasi") == house_10_rasi:
                    factors.append("D1_10th_lord_in_10th")
                    scores["d1_10th_lord_placement"] = 1.0
                    meta = _rule_meta("D1_10th_lord_in_10th")
                    applied_rules.append({"rule_id": "D1_10th_lord_in_10th", "name": meta["name"], "explanation": meta["explanation"], "score": 1.0})
                elif pdata.get("rasi") in OWN_SIGNS.get(tenth_lord, []):
                    factors.append("D1_10th_lord_in_own_sign")
                    scores["d1_10th_lord_placement"] = 0.9
                    meta = _rule_meta("D1_10th_lord_in_own_sign")
                    applied_rules.append({"rule_id": "D1_10th_lord_in_own_sign", "name": meta["name"], "explanation": meta["explanation"], "score": 0.9})
                elif pdata.get("rasi") == EXALTATION.get(tenth_lord):
                    factors.append("D1_10th_lord_exalted")
                    scores["d1_10th_lord_placement"] = 1.0
                    meta = _rule_meta("D1_10th_lord_exalted")
                    applied_rules.append({"rule_id": "D1_10th_lord_exalted", "name": meta["name"], "explanation": meta["explanation"], "score": 1.0})
                break

    # 2) Planets in 10th house D1
    planets_in_10 = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house_d1(pdata["longitude"], cusps)
        if h == 10:
            planets_in_10.append(pname)
    if planets_in_10:
        factors.append(f"D1_planets_in_10th_{','.join(planets_in_10)}")
        benefic_count = sum(1 for p in planets_in_10 if p in BENEFICS)
        malefic_count = sum(1 for p in planets_in_10 if p in MALEFICS)
        scores["d1_10th_benefics"] = float(benefic_count)
        scores["d1_10th_malefics"] = float(malefic_count)
        meta = _rule_meta("D1_planets_in_10th")
        applied_rules.append({
            "rule_id": "D1_planets_in_10th",
            "name": meta["name"],
            "explanation": meta["explanation"],
            "score": f"Benefics: {benefic_count}, Malefics: {malefic_count}",
        })

    # 3) D10 10th house
    if "Ascendant" in d10 and "_enhanced" in d10 and "houses" in d10["_enhanced"]:
        d10_houses = d10["_enhanced"]["houses"]
        if "House_10" in d10_houses:
            d10_10_rasi = d10_houses["House_10"].get("rasi")
            if d10_10_rasi:
                factors.append(f"D10_10th_rasi_{d10_10_rasi}")
                scores["d10_10th_rasi"] = 1.0
                meta = _rule_meta("D10_10th_rasi")
                applied_rules.append({"rule_id": "D10_10th_rasi", "name": meta["name"], "explanation": meta["explanation"] + f" Sign: {d10_10_rasi}.", "score": 1.0})

    # 4) Current Dasha/Bhukti touching 10th
    if dasha_current:
        current_dasa = dasha_current.get("current_dasa")
        current_bhukti = dasha_current.get("current_bhukti")
        if current_dasa and tenth_lord and current_dasa == tenth_lord:
            factors.append("current_dasa_lord_is_10th_lord")
            scores["dasha_10th_link"] = 1.0
            meta = _rule_meta("current_dasa_lord_is_10th_lord")
            applied_rules.append({"rule_id": "current_dasa_lord_is_10th_lord", "name": meta["name"], "explanation": meta["explanation"], "score": 1.0})
        if current_bhukti and tenth_lord and current_bhukti == tenth_lord:
            factors.append("current_bhukti_lord_is_10th_lord")
            scores["bhukti_10th_link"] = 1.0
            meta = _rule_meta("current_bhukti_lord_is_10th_lord")
            applied_rules.append({"rule_id": "current_bhukti_lord_is_10th_lord", "name": meta["name"], "explanation": meta["explanation"], "score": 1.0})

    # 5) SAV 10th house strength
    if bav_sav_full and "sav_chart" in bav_sav_full:
        sav = bav_sav_full["sav_chart"]
        if len(sav) > 9:
            tenth_sav = sav[9]
            factors.append(f"SAV_10th_house_bindus_{tenth_sav}")
            if tenth_sav >= 30:
                scores["sav_10th"] = 1.0
            elif tenth_sav >= 26:
                scores["sav_10th"] = 0.7
            else:
                scores["sav_10th"] = 0.4
            meta = _rule_meta("SAV_10th_house_bindus")
            applied_rules.append({
                "rule_id": "SAV_10th_house_bindus",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" This chart: {tenth_sav} bindus.",
                "score": scores.get("sav_10th", 0.4),
            })

    # 6) 10th lord in 2nd or 3rd (sales/marketing)
    if tenth_lord:
        tenth_lord_house_d1 = None
        for pname, pdata in d1.items():
            if pname.startswith("_") or not isinstance(pdata, dict):
                continue
            if pname != tenth_lord and RASI_LORDS.get(pdata.get("rasi")) != tenth_lord:
                continue
            lon = pdata.get("longitude")
            if lon is not None:
                tenth_lord_house_d1 = _which_house_d1(lon, cusps)
                break
        if tenth_lord_house_d1 in (2, 3):
            factors.append("D1_10th_lord_in_2nd_3rd")
            scores["d1_10th_lord_2nd_3rd"] = 0.8
            meta = _rule_meta("D1_10th_lord_in_2nd_3rd")
            applied_rules.append({"rule_id": "D1_10th_lord_in_2nd_3rd", "name": meta["name"], "explanation": meta["explanation"], "score": 0.8})

    # 7) D10: Kendra benefics / malefics
    d10_cusps = _get_d1_cusps(d10) if "_enhanced" in d10 and "houses" in d10["_enhanced"] else [i * 30.0 for i in range(12)]
    kendra_benefics_d10 = []
    kendra_malefics_d10 = []

    for pname, pdata in d10.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house_d1(pdata["longitude"], d10_cusps)

        if h not in (1, 4, 7, 10):
            continue
        if pname in BENEFICS:
            kendra_benefics_d10.append(pname)
        if pname in MALEFICS:
            kendra_malefics_d10.append(pname)
    if kendra_benefics_d10:
        factors.append(f"D10_Kendra_benefics_{','.join(kendra_benefics_d10)}")
        scores["d10_kendra_benefics"] = min(1.0, 0.25 * len(kendra_benefics_d10))
        meta = _rule_meta("D10_Kendra_benefics")
        applied_rules.append({"rule_id": "D10_Kendra_benefics", "name": meta["name"], "explanation": meta["explanation"], "score": scores["d10_kendra_benefics"]})
    if kendra_malefics_d10:
        factors.append(f"D10_Kendra_malefics_{','.join(kendra_malefics_d10)}")
        meta = _rule_meta("D10_Kendra_malefics")
        applied_rules.append({"rule_id": "D10_Kendra_malefics", "name": meta["name"], "explanation": meta["explanation"], "score": 0.3})

    # 8) Sign nature (Tatwa) of 10th house in D10
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_10" in d10["_enhanced"]["houses"]:
        d10_10_rasi = d10["_enhanced"]["houses"]["House_10"].get("rasi")
        if d10_10_rasi:
            tatwa = {"Mesha": "fire", "Simha": "fire", "Dhanus": "fire", "Rishaba": "earth", "Kanni": "earth", "Makara": "earth",
                     "Mithuna": "air", "Thula": "air", "Kumbha": "air", "Kataka": "water", "Vrischika": "water", "Meena": "water"}.get(d10_10_rasi, "")
            if tatwa:
                factors.append(f"D10_10th_tatwa_{tatwa}")
                scores["d10_10th_tatwa"] = 0.5
                meta = _rule_meta("D10_sign_nature_10th")
                applied_rules.append({"rule_id": "D10_sign_nature_10th", "name": meta["name"], "explanation": meta["explanation"] + f" 10th sign: {d10_10_rasi} ({tatwa}).", "score": 0.5})

    # 9) Vargottama (same sign in D1 and D10)
    vargottama = []
    for pname in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]:
        if pname not in d1 or pname not in d10:
            continue
        r1 = d1[pname].get("rasi") if isinstance(d1[pname], dict) else None
        r10 = d10[pname].get("rasi") if isinstance(d10[pname], dict) else None
        if r1 and r10 and r1 == r10:
            vargottama.append(pname)
    if vargottama:
        factors.append(f"Vargottama_{','.join(vargottama)}")
        scores["vargottama"] = min(1.0, 0.2 * len(vargottama) + 0.3)
        meta = _rule_meta("Vargottama")
        applied_rules.append({"rule_id": "Vargottama", "name": meta["name"], "explanation": meta["explanation"] + f" Planets: {', '.join(vargottama)}.", "score": scores["vargottama"]})

    # 10) 10th lord transposition (D1 10th lord in D10): strong and well-placed?
    if tenth_lord and tenth_lord in d10 and isinstance(d10[tenth_lord], dict):
        d10_lord_rasi = d10[tenth_lord].get("rasi")
        d10_lord_house = _d10_house_for_planet(d10, tenth_lord)
        strong_in_d10 = (d10_lord_rasi == EXALTATION.get(tenth_lord) or d10_lord_rasi in OWN_SIGNS.get(tenth_lord, []))
        good_house_d10 = d10_lord_house in (1, 4, 5, 7, 9, 10, 11) if d10_lord_house else False
        if strong_in_d10 and good_house_d10:
            factors.append("D10_10th_lord_transposition_strong")
            scores["d10_10th_lord_transposition"] = 1.0
            meta = _rule_meta("D10_10th_lord_transposition")
            applied_rules.append({"rule_id": "D10_10th_lord_transposition", "name": meta["name"], "explanation": meta["explanation"], "score": 1.0})
        elif tenth_lord and scores.get("d1_10th_lord_placement") and not strong_in_d10 and d10_lord_house not in (1, 4, 5, 7, 9, 10, 11):
            factors.append("D10_10th_lord_weak")
            meta = _rule_meta("D10_10th_lord_weak")
            applied_rules.append({"rule_id": "D10_10th_lord_weak", "name": meta["name"], "explanation": meta["explanation"], "score": 0.2})

    # 11) Aspects to 10th house and to 10th lord
    if get_planets_aspecting_10th_house:
        asp_10 = get_planets_aspecting_10th_house(d1)
        if asp_10:
            factors.append(f"aspects_to_10th_{','.join(p for p, _ in asp_10)}")
            scores["aspects_to_10th_house"] = min(1.0, 0.15 * len(asp_10) + 0.3)
            meta = _rule_meta("aspects_to_10th_house")
            applied_rules.append({"rule_id": "aspects_to_10th_house", "name": meta["name"], "explanation": meta["explanation"] + f" Planets: {', '.join(p for p, _ in asp_10)}.", "score": scores["aspects_to_10th_house"]})
    if tenth_lord and get_planets_aspecting_10th_lord:
        asp_lord = get_planets_aspecting_10th_lord(d1, tenth_lord)
        if asp_lord:
            factors.append(f"aspects_to_10th_lord_{','.join(p for p, _ in asp_lord)}")
            scores["aspects_to_10th_lord"] = min(1.0, 0.2 * len(asp_lord))
            meta = _rule_meta("aspects_to_10th_lord")
            applied_rules.append({"rule_id": "aspects_to_10th_lord", "name": meta["name"], "explanation": meta["explanation"], "score": scores["aspects_to_10th_lord"]})

    # 12) D9 (Navamsha) dispositor of 10th lord
    if tenth_lord and calculate_d9_chart and get_d9_dispositor_of_planet:
        d9 = calculate_d9_chart(d1)
        d9_disp = get_d9_dispositor_of_planet(d9, tenth_lord)
        if d9_disp:
            factors.append(f"D9_dispositor_10th_lord_{d9_disp}")
            scores["d9_dispositor_10th_lord"] = 0.6
            meta = _rule_meta("D9_dispositor_10th_lord")
            applied_rules.append({"rule_id": "D9_dispositor_10th_lord", "name": meta["name"], "explanation": meta["explanation"] + f" Dispositor: {d9_disp}.", "score": 0.6})

    # 13) House connections (10th–11th–Ascendant)
    if house_connections_10_11_lagna:
        conn = house_connections_10_11_lagna(d1)
        if conn:
            factors.append(f"house_connections_{'|'.join(conn)}")
            scores["house_connections_10_11_lagna"] = min(1.0, 0.25 * len(conn))
            meta = _rule_meta("house_connections_10_11_lagna")
            applied_rules.append({"rule_id": "house_connections_10_11_lagna", "name": meta["name"], "explanation": meta["explanation"] + f" {'; '.join(conn)}.", "score": scores["house_connections_10_11_lagna"]})

    # 14) Chandra Lagna (10th from Moon)
    if chandra_lagna_10th_lord_and_occupants:
        cl10 = chandra_lagna_10th_lord_and_occupants(d1)
        if cl10.get("lord") or cl10.get("occupants"):
            factors.append(f"chandra_lagna_10th_house_{cl10.get('house')}_lord_{cl10.get('lord', '')}")
            scores["chandra_lagna_10th"] = 0.5
            meta = _rule_meta("chandra_lagna_10th")
            applied_rules.append({"rule_id": "chandra_lagna_10th", "name": meta["name"], "explanation": meta["explanation"] + f" House {cl10.get('house')}, lord {cl10.get('lord', '')}, occupants: {', '.join(cl10.get('occupants', []))}.", "score": 0.5})

    # 15) Chara Karakas (AmK, DK, etc.)
    if chara_karakas:
        ck = chara_karakas(d1)
        if ck:
            amk = ck.get("Amatyakaraka")
            dk = ck.get("Darakaraka")
            factors.append(f"chara_karakas_AmK_{amk or ''}_DK_{dk or ''}")
            scores["chara_karakas"] = 0.5
            meta = _rule_meta("chara_karakas")
            applied_rules.append({"rule_id": "chara_karakas", "name": meta["name"], "explanation": meta["explanation"] + f" Amatyakaraka: {amk}; Darakaraka: {dk}.", "score": 0.5})

    # 16) Raja Yogas in D1 and strength in D10
    yogas = []
    if "_enhanced" in d1 and "yogas" in d1["_enhanced"]:
        yogas = d1["_enhanced"].get("yogas") or []
    if isinstance(yogas, str):
        try:
            import json
            yogas = json.loads(yogas)
        except Exception:
            yogas = []
    if raja_yoga_participants_in_d10 and yogas:
        yoga_d10 = raja_yoga_participants_in_d10(d1, d10, yogas)
        for item in yoga_d10:
            if item.get("strong_in_d10"):
                factors.append(f"raja_yoga_D10_strength_{item.get('yoga_name', '')}")
                scores["raja_yoga_d10_strength"] = min(1.0, 0.3 + 0.2 * len(item["strong_in_d10"]))
                meta = _rule_meta("raja_yoga_in_D10")
                applied_rules.append({"rule_id": "raja_yoga_in_D10", "name": meta["name"], "explanation": meta["explanation"] + f" {item.get('yoga_name')} planets strong in D10: {', '.join(item['strong_in_d10'])}.", "score": scores.get("raja_yoga_d10_strength", 0.5)})
                break

    # 17) Upachaya (Sun/Saturn in 3, 6, 10, 11)
    if upachaya_sun_saturn:
        for chart_label, chart_data in [("D1", d1), ("D10", d10)]:
            up = upachaya_sun_saturn(chart_data)
            if up["sun"] or up["saturn"]:
                factors.append(f"upachaya_{chart_label}_Sun_{up['sun']}_Sat_{up['saturn']}")
                scores["upachaya_sun_saturn"] = min(1.0, 0.2 * (len(up["sun"]) + len(up["saturn"])) + 0.2)
                meta = _rule_meta("upachaya_sun_saturn")
                applied_rules.append({"rule_id": "upachaya_sun_saturn", "name": meta["name"], "explanation": meta["explanation"] + f" In {chart_label}: Sun in houses {up['sun']}, Saturn in {up['saturn']}.", "score": scores.get("upachaya_sun_saturn", 0.3)})
                break

    # 18) 8th house (transformations / retirement)
    if eighth_house_factors:
        eighth_d1 = eighth_house_factors(d1)
        if eighth_d1.get("lord") or eighth_d1.get("occupants"):
            factors.append(f"8th_house_lord_{eighth_d1.get('lord', '')}_occ_{','.join(eighth_d1.get('occupants', []))}")
            scores["eighth_house"] = 0.4
            meta = _rule_meta("eighth_house")
            applied_rules.append({"rule_id": "eighth_house", "name": meta["name"], "explanation": meta["explanation"] + f" Lord: {eighth_d1.get('lord', '')}; occupants: {', '.join(eighth_d1.get('occupants', []))}.", "score": 0.4})

    # 19) Amsa deities (Navamsha) for 10th lord
    if tenth_lord and tenth_lord in d1 and isinstance(d1[tenth_lord], dict) and navamsha_amsa_deity:
        lon = d1[tenth_lord].get("longitude")
        if lon is not None:
            deity = navamsha_amsa_deity(lon)
            factors.append(f"amsa_deity_10th_lord_{deity}")
            scores["amsa_deities"] = 0.35
            meta = _rule_meta("amsa_deities")
            applied_rules.append({"rule_id": "amsa_deities", "name": meta["name"], "explanation": meta["explanation"] + f" 10th lord's Navamsha deity: {deity}.", "score": 0.35})

    # 20) Yogakaraka planet in 10th house
    if check_yogakaraka_in_10th:
        yk_result = check_yogakaraka_in_10th(d1)
        if yk_result:
            planet, score = yk_result
            factors.append(f"yogakaraka_in_10th_{planet}")
            scores["yogakaraka_in_10th"] = score
            meta = _rule_meta("yogakaraka_in_10th")
            applied_rules.append({"rule_id": "yogakaraka_in_10th", "name": meta["name"], "explanation": meta["explanation"] + f" Planet: {planet}.", "score": score})

    # 21) Parivartana Yoga involving 10th house/lord
    if check_parivartana_yoga_10th and tenth_lord:
        pv_result = check_parivartana_yoga_10th(d1, tenth_lord)
        if pv_result:
            p1, p2, yoga_type, score = pv_result
            factors.append(f"parivartana_yoga_{p1}_{p2}_{yoga_type}")
            scores["parivartana_yoga_10th"] = score
            meta = _rule_meta("parivartana_yoga_10th")
            applied_rules.append({"rule_id": "parivartana_yoga_10th", "name": meta["name"], "explanation": meta["explanation"] + f" {yoga_type} Parivartana between {p1} and {p2}.", "score": score})

    # 22) Neechabhanga Raja Yoga in 10th house
    if check_neechabhanga_10th:
        nb_results = check_neechabhanga_10th(d1)
        if nb_results:
            for planet, score in nb_results:
                factors.append(f"neechabhanga_10th_{planet}")
                scores["neechabhanga_10th"] = score
                meta = _rule_meta("neechabhanga_10th")
                applied_rules.append({"rule_id": "neechabhanga_10th", "name": meta["name"], "explanation": meta["explanation"] + f" Planet: {planet} (debilitation cancelled).", "score": score})
                break  # Only report first

    # 23) Sun in 10th house (natural karaka)
    if check_sun_in_10th:
        sun_score = check_sun_in_10th(d1)
        if sun_score:
            factors.append("sun_in_10th")
            scores["sun_in_10th"] = sun_score
            meta = _rule_meta("sun_in_10th")
            applied_rules.append({"rule_id": "sun_in_10th", "name": meta["name"], "explanation": meta["explanation"], "score": sun_score})

    # 24) 9th-10th lord connection (Dharma-Karma Yoga)
    if check_9th_10th_lord_connection and tenth_lord:
        dk_result = check_9th_10th_lord_connection(d1, tenth_lord)
        if dk_result:
            connection_type, score = dk_result
            factors.append(f"dharma_karma_yoga_{connection_type}")
            scores["dharma_karma_yoga"] = score
            meta = _rule_meta("dharma_karma_yoga")
            applied_rules.append({"rule_id": "dharma_karma_yoga", "name": meta["name"], "explanation": meta["explanation"] + f" Type: {connection_type}.", "score": score})

    # 25) Exalted planets in 10th house
    if check_exalted_planets_in_10th:
        ex_results = check_exalted_planets_in_10th(d1)
        if ex_results:
            for planet, score in ex_results:
                factors.append(f"exalted_in_10th_{planet}")
                scores["exalted_in_10th"] = max(scores.get("exalted_in_10th", 0), score)
            meta = _rule_meta("exalted_in_10th")
            planets_str = ", ".join([p for p, s in ex_results])
            applied_rules.append({"rule_id": "exalted_in_10th", "name": meta["name"], "explanation": meta["explanation"] + f" Planets: {planets_str}.", "score": scores.get("exalted_in_10th", 1.2)})

    # 26) Rahu or Ketu in 10th house
    if check_rahu_ketu_in_10th:
        rk_result = check_rahu_ketu_in_10th(d1)
        if rk_result:
            node, interpretation, score = rk_result
            factors.append(f"{node.lower()}_in_10th")
            scores["rahu_ketu_in_10th"] = score
            meta = _rule_meta("rahu_ketu_in_10th")
            applied_rules.append({"rule_id": "rahu_ketu_in_10th", "name": meta["name"], "explanation": meta["explanation"] + f" {node} indicates {interpretation}.", "score": score})

    # 27) Combust planets in 10th house (penalty)
    if check_combust_planets_in_10th:
        cb_results = check_combust_planets_in_10th(d1)
        if cb_results:
            for planet, penalty in cb_results:
                factors.append(f"combust_in_10th_{planet}")
                scores["combust_in_10th"] = penalty
            meta = _rule_meta("combust_in_10th")
            planets_str = ", ".join([p for p, s in cb_results])
            applied_rules.append({"rule_id": "combust_in_10th", "name": meta["name"], "explanation": meta["explanation"] + f" Planets: {planets_str}.", "score": scores.get("combust_in_10th", 0.3)})

    # ========== PHASE 1 ENHANCEMENTS ==========

    # 28) D10 Lagna strength and lord placement
    if "Ascendant" in d10 and isinstance(d10["Ascendant"], dict):
        d10_lagna_rasi = d10["Ascendant"].get("rasi")
        if d10_lagna_rasi:
            d10_lagna_lord = RASI_LORDS.get(d10_lagna_rasi, "")

            # Check D10 Lagna lord placement
            if d10_lagna_lord and d10_lagna_lord in d10 and isinstance(d10[d10_lagna_lord], dict):
                d10_lagna_lord_house = None
                if "longitude" in d10[d10_lagna_lord]:
                    d10_lagna_lord_house = _which_house_d1(d10[d10_lagna_lord]["longitude"], d10_cusps)

                # Calculate strength - Base score for all D10 Lagna lord placements
                lagna_strength = 0.3  # Base score
                strength_factors = [f"house {d10_lagna_lord_house}"]

                # Bonus for favorable house placement
                if d10_lagna_lord_house in (1, 4, 7, 10):
                    lagna_strength += 0.5
                    strength_factors.append("Kendra (strong)")
                elif d10_lagna_lord_house in (5, 9):
                    lagna_strength += 0.4
                    strength_factors.append("Trikona (fortunate)")
                elif d10_lagna_lord_house in (2, 11):
                    lagna_strength += 0.2
                    strength_factors.append("wealth house")
                elif d10_lagna_lord_house in (3, 6):
                    lagna_strength += 0.1
                    strength_factors.append("Upachaya (growth through effort)")
                else:
                    strength_factors.append("neutral placement")

                # Check if D10 Lagna lord is in own sign or exalted
                d10_lagna_lord_rasi = d10[d10_lagna_lord].get("rasi")
                if d10_lagna_lord_rasi in OWN_SIGNS.get(d10_lagna_lord, []):
                    lagna_strength += 0.3
                    strength_factors.append("own sign")
                elif d10_lagna_lord_rasi == EXALTATION.get(d10_lagna_lord):
                    lagna_strength += 0.4
                    strength_factors.append("exalted")

                # Always report D10 Lagna lord placement
                if d10_lagna_lord_house:
                    factors.append(f"D10_lagna_lord_{d10_lagna_lord}_{','.join(strength_factors)}")
                    scores["d10_lagna_strength"] = min(1.0, lagna_strength)
                    meta = _rule_meta("d10_lagna_strength")
                    applied_rules.append({
                        "rule_id": "d10_lagna_strength",
                        "name": meta["name"],
                        "explanation": meta["explanation"] + f" D10 Lagna: {d10_lagna_rasi}, Lord: {d10_lagna_lord} ({', '.join(strength_factors)}).",
                        "score": scores["d10_lagna_strength"]
                    })

    # 29) D10 10th lord placement and strength
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_10" in d10["_enhanced"]["houses"]:
        d10_10th_rasi = d10["_enhanced"]["houses"]["House_10"].get("rasi")
        if d10_10th_rasi:
            d10_10th_lord = RASI_LORDS.get(d10_10th_rasi, "")

            if d10_10th_lord and d10_10th_lord in d10 and isinstance(d10[d10_10th_lord], dict):
                d10_10th_lord_house = None
                if "longitude" in d10[d10_10th_lord]:
                    d10_10th_lord_house = _which_house_d1(d10[d10_10th_lord]["longitude"], d10_cusps)

                # Calculate D10 10th lord strength - Base score for all placements
                d10_10th_strength = 0.3  # Base score
                d10_10th_factors = [f"house {d10_10th_lord_house}"]

                # Bonus for favorable house placement
                if d10_10th_lord_house in (1, 4, 7, 10):
                    d10_10th_strength += 0.6
                    d10_10th_factors.append("Kendra (strong)")
                elif d10_10th_lord_house in (5, 9):
                    d10_10th_strength += 0.5
                    d10_10th_factors.append("Trikona (fortunate)")
                elif d10_10th_lord_house in (2, 11):
                    d10_10th_strength += 0.3
                    d10_10th_factors.append("wealth house")
                elif d10_10th_lord_house in (3, 6):
                    d10_10th_strength += 0.2
                    d10_10th_factors.append("Upachaya (growth)")
                else:
                    d10_10th_factors.append("neutral")

                # Check sign strength
                d10_10th_lord_rasi = d10[d10_10th_lord].get("rasi")
                if d10_10th_lord_rasi in OWN_SIGNS.get(d10_10th_lord, []):
                    d10_10th_strength += 0.3
                    d10_10th_factors.append("own sign")
                elif d10_10th_lord_rasi == EXALTATION.get(d10_10th_lord):
                    d10_10th_strength += 0.4
                    d10_10th_factors.append("exalted")

                # Always report D10 10th lord placement
                if d10_10th_lord_house:
                    factors.append(f"D10_10th_lord_{d10_10th_lord}_{','.join(d10_10th_factors)}")
                    scores["d10_10th_lord_placement"] = min(1.0, d10_10th_strength)
                    meta = _rule_meta("d10_10th_lord_placement")
                    applied_rules.append({
                        "rule_id": "d10_10th_lord_placement",
                        "name": meta["name"],
                        "explanation": meta["explanation"] + f" D10 10th house: {d10_10th_rasi}, Lord: {d10_10th_lord} ({', '.join(d10_10th_factors)}).",
                        "score": scores["d10_10th_lord_placement"]
                    })

    # 30) Big Three Lords combined analysis
    # The three most important lords: D10 Lagna lord, D10 10th lord, D1 10th lord
    big_three_score = 0.0
    big_three_details = []

    # D10 Lagna lord strength (already calculated above)
    if "d10_lagna_strength" in scores:
        big_three_score += scores["d10_lagna_strength"] * 0.33
        big_three_details.append(f"D10 Lagna lord: {scores['d10_lagna_strength']:.2f}")

    # D10 10th lord strength (already calculated above)
    if "d10_10th_lord_placement" in scores:
        big_three_score += scores["d10_10th_lord_placement"] * 0.33
        big_three_details.append(f"D10 10th lord: {scores['d10_10th_lord_placement']:.2f}")

    # D1 10th lord strength (already calculated above)
    if "d1_10th_lord_placement" in scores:
        big_three_score += scores["d1_10th_lord_placement"] * 0.34
        big_three_details.append(f"D1 10th lord: {scores['d1_10th_lord_placement']:.2f}")

    if big_three_score > 0 and len(big_three_details) >= 2:
        factors.append(f"big_three_lords_combined_{big_three_score:.2f}")
        scores["big_three_lords"] = big_three_score
        meta = _rule_meta("big_three_lords")
        applied_rules.append({
            "rule_id": "big_three_lords",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Combined score: {big_three_score:.2f}. Details: {'; '.join(big_three_details)}.",
            "score": big_three_score
        })

    # 31) Artha Trikona (2nd, 6th, 10th houses) - Wealth Triangle
    artha_trikona_score = 0.0
    artha_details = []

    # Analyze 2nd house (income)
    house_2_planets = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house_d1(pdata["longitude"], cusps)
        if h == 2:
            house_2_planets.append(pname)
            if pname in BENEFICS:
                artha_trikona_score += 0.15
                artha_details.append(f"2nd house: {pname} (benefic)")

    # Analyze 6th house (service/daily work)
    house_6_planets = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house_d1(pdata["longitude"], cusps)
        if h == 6:
            house_6_planets.append(pname)
            if pname in BENEFICS:
                artha_trikona_score += 0.1
                artha_details.append(f"6th house: {pname} (benefic)")

    # 10th house already analyzed (use existing benefics score)
    if "d1_10th_benefics" in scores and scores["d1_10th_benefics"] > 0:
        artha_trikona_score += scores["d1_10th_benefics"] * 0.2
        artha_details.append(f"10th house: {int(scores['d1_10th_benefics'])} benefics")

    # Check lords of these houses
    if len(cusps) >= 10:
        rasis = ["Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
                 "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]

        # 2nd house lord
        house_2_rasi_idx = int(cusps[1] // 30) % 12
        house_2_rasi = rasis[house_2_rasi_idx]
        house_2_lord = RASI_LORDS.get(house_2_rasi, "")

        # 6th house lord
        house_6_rasi_idx = int(cusps[5] // 30) % 12
        house_6_rasi = rasis[house_6_rasi_idx]
        house_6_lord = RASI_LORDS.get(house_6_rasi, "")

        # Check if any Artha Trikona lords are connected
        lords_connected = []
        if house_2_lord and tenth_lord and house_2_lord == tenth_lord:
            lords_connected.append("2nd-10th same lord")
            artha_trikona_score += 0.3
        if house_6_lord and tenth_lord and house_6_lord == tenth_lord:
            lords_connected.append("6th-10th same lord")
            artha_trikona_score += 0.3
        if house_2_lord and house_6_lord and house_2_lord == house_6_lord:
            lords_connected.append("2nd-6th same lord")
            artha_trikona_score += 0.2

        if lords_connected:
            artha_details.append(", ".join(lords_connected))

    if artha_trikona_score > 0:
        factors.append(f"artha_trikona_{artha_trikona_score:.2f}")
        scores["artha_trikona"] = min(1.0, artha_trikona_score)
        meta = _rule_meta("artha_trikona")
        applied_rules.append({
            "rule_id": "artha_trikona",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Score: {scores['artha_trikona']:.2f}. Details: {'; '.join(artha_details) if artha_details else 'Wealth houses occupied'}.",
            "score": scores["artha_trikona"]
        })

    # 32) Business vs. Job indicator
    # 6th house = service/job, 7th house = business/partnerships
    business_vs_job_score = 0.0
    business_job_details = []

    # Count benefics in 6th (job indicator)
    house_6_benefics = sum(1 for p in house_6_planets if p in BENEFICS)

    # Count benefics in 7th (business indicator)
    house_7_planets = []
    house_7_benefics = 0
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house_d1(pdata["longitude"], cusps)
        if h == 7:
            house_7_planets.append(pname)
            if pname in BENEFICS:
                house_7_benefics += 1

    # Determine career type
    if house_7_benefics > house_6_benefics:
        business_vs_job_score = 0.7
        business_job_details.append(f"Business tendency (7th house: {house_7_benefics} benefics > 6th house: {house_6_benefics} benefics)")
        career_type = "Business/Entrepreneurship"
    elif house_6_benefics > house_7_benefics:
        business_vs_job_score = 0.6
        business_job_details.append(f"Job/Service tendency (6th house: {house_6_benefics} benefics > 7th house: {house_7_benefics} benefics)")
        career_type = "Job/Service"
    else:
        business_vs_job_score = 0.5
        business_job_details.append(f"Balanced (6th house: {house_6_benefics} benefics, 7th house: {house_7_benefics} benefics)")
        career_type = "Flexible"

    if business_vs_job_score > 0:
        factors.append(f"business_vs_job_{career_type.replace('/', '_')}")
        scores["business_vs_job"] = business_vs_job_score
        meta = _rule_meta("business_vs_job")
        applied_rules.append({
            "rule_id": "business_vs_job",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Career type: {career_type}. {'; '.join(business_job_details)}.",
            "score": business_vs_job_score
        })

    # 33) Saturn placement in D10
    if "Saturn" in d10 and isinstance(d10["Saturn"], dict) and "longitude" in d10["Saturn"]:
        saturn_d10_house = _which_house_d1(d10["Saturn"]["longitude"], d10_cusps)
        saturn_d10_rasi = d10["Saturn"].get("rasi")

        saturn_score = 0.0
        saturn_details = []

        # Saturn in Upachaya houses (3,6,10,11) in D10 is favorable
        if saturn_d10_house in (3, 6, 10, 11):
            saturn_score = 0.8
            saturn_details.append(f"in Upachaya house {saturn_d10_house} (favorable for career discipline)")
        elif saturn_d10_house in (1, 4, 7):
            saturn_score = 0.4
            saturn_details.append(f"in Kendra house {saturn_d10_house} (brings responsibility)")
        else:
            saturn_score = 0.3
            saturn_details.append(f"in house {saturn_d10_house}")

        # Check Saturn's sign strength in D10
        if saturn_d10_rasi in OWN_SIGNS.get("Saturn", []):
            saturn_score += 0.2
            saturn_details.append("in own sign (disciplined success)")
        elif saturn_d10_rasi == EXALTATION.get("Saturn"):
            saturn_score += 0.3
            saturn_details.append("exalted (systematic growth)")

        factors.append(f"Saturn_in_D10_house_{saturn_d10_house}_{saturn_d10_rasi}")
        scores["saturn_in_d10"] = min(1.0, saturn_score)
        meta = _rule_meta("saturn_in_d10")
        applied_rules.append({
            "rule_id": "saturn_in_d10",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Saturn in D10: {', '.join(saturn_details)}.",
            "score": scores["saturn_in_d10"]
        })

    # ========== PHASE 2 ENHANCEMENTS ==========

    # 34) Planetary Career Type Indicators
    # Analyze which planets are strong in 10th house or as 10th lord to determine career field
    career_type_planets = {}
    planet_career_types = {
        "Sun": "Government/Authority/Leadership",
        "Moon": "Healthcare/Public Service/Hospitality",
        "Mars": "Military/Technical/Engineering/Sports",
        "Mercury": "Communication/Business/Writing/IT",
        "Jupiter": "Teaching/Finance/Law/Counseling",
        "Venus": "Arts/Entertainment/Luxury/Design",
        "Saturn": "Labor/Service/Mining/Real Estate"
    }

    # Check planets in 10th house D1
    for pname in planets_in_10:
        if pname in planet_career_types:
            if pname not in career_type_planets:
                career_type_planets[pname] = []
            career_type_planets[pname].append("in 10th house")

    # Check if 10th lord matches a career planet
    if tenth_lord in planet_career_types:
        if tenth_lord not in career_type_planets:
            career_type_planets[tenth_lord] = []
        career_type_planets[tenth_lord].append("10th lord")

    # Check strong planets aspecting 10th house
    if get_planets_aspecting_10th_house:
        asp_10 = get_planets_aspecting_10th_house(d1)
        for planet, aspect_type in asp_10:
            if planet in planet_career_types and planet not in planets_in_10:
                if planet not in career_type_planets:
                    career_type_planets[planet] = []
                career_type_planets[planet].append("aspects 10th")

    if career_type_planets:
        career_fields = []
        planet_details = []
        for planet, reasons in career_type_planets.items():
            career_fields.append(planet_career_types[planet])
            planet_details.append(f"{planet} ({', '.join(reasons)})")

        factors.append(f"planetary_career_indicators_{','.join(career_type_planets.keys())}")
        scores["planetary_career_indicators"] = min(1.0, 0.3 * len(career_type_planets))
        meta = _rule_meta("planetary_career_indicators")
        applied_rules.append({
            "rule_id": "planetary_career_indicators",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Indicated fields: {'; '.join(set(career_fields))}. Planets: {', '.join(planet_details)}.",
            "score": scores["planetary_career_indicators"]
        })

    # 35) D10 2nd house (Speech & Finance in career)
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_2" in d10["_enhanced"]["houses"]:
        d10_2nd_planets = []
        d10_2nd_rasi = d10["_enhanced"]["houses"]["House_2"].get("rasi")

        # Find planets in D10 2nd house
        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h == 2:
                d10_2nd_planets.append(pname)

        if d10_2nd_planets:
            benefic_count = sum(1 for p in d10_2nd_planets if p in BENEFICS)
            score = min(1.0, 0.2 * benefic_count + 0.3)

            factors.append(f"D10_2nd_house_{','.join(d10_2nd_planets)}")
            scores["d10_2nd_house"] = score
            meta = _rule_meta("d10_2nd_house")
            applied_rules.append({
                "rule_id": "d10_2nd_house",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Planets in D10 2nd: {', '.join(d10_2nd_planets)} ({benefic_count} benefics). Good for income and communication.",
                "score": score
            })

    # 36) D10 4th house (Assets & Peace in career)
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_4" in d10["_enhanced"]["houses"]:
        d10_4th_planets = []

        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h == 4:
                d10_4th_planets.append(pname)

        if d10_4th_planets:
            benefic_count = sum(1 for p in d10_4th_planets if p in BENEFICS)
            score = min(1.0, 0.25 * benefic_count + 0.2)

            factors.append(f"D10_4th_house_{','.join(d10_4th_planets)}")
            scores["d10_4th_house"] = score
            meta = _rule_meta("d10_4th_house")
            applied_rules.append({
                "rule_id": "d10_4th_house",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Planets in D10 4th: {', '.join(d10_4th_planets)} ({benefic_count} benefics). Comfortable work environment.",
                "score": score
            })

    # 37) D10 8th house (Research & Transformation)
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_8" in d10["_enhanced"]["houses"]:
        d10_8th_planets = []

        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h == 8:
                d10_8th_planets.append(pname)

        if d10_8th_planets:
            # 8th house is complex - malefics can be good for research careers
            score = min(1.0, 0.2 * len(d10_8th_planets) + 0.2)

            factors.append(f"D10_8th_house_{','.join(d10_8th_planets)}")
            scores["d10_8th_house"] = score
            meta = _rule_meta("d10_8th_house")
            applied_rules.append({
                "rule_id": "d10_8th_house",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Planets in D10 8th: {', '.join(d10_8th_planets)}. Research, occult, or transformative career.",
                "score": score
            })

    # 38) D10 9th house (Fortune & Teaching)
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_9" in d10["_enhanced"]["houses"]:
        d10_9th_planets = []

        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h == 9:
                d10_9th_planets.append(pname)

        if d10_9th_planets:
            benefic_count = sum(1 for p in d10_9th_planets if p in BENEFICS)
            score = min(1.0, 0.3 * benefic_count + 0.4)

            factors.append(f"D10_9th_house_{','.join(d10_9th_planets)}")
            scores["d10_9th_house"] = score
            meta = _rule_meta("d10_9th_house")
            applied_rules.append({
                "rule_id": "d10_9th_house",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Planets in D10 9th: {', '.join(d10_9th_planets)} ({benefic_count} benefics). Fortune and higher learning.",
                "score": score
            })

    # 39) Dasha Career Timing
    if dasha_current:
        current_dasa = dasha_current.get("current_dasa")
        current_bhukti = dasha_current.get("current_bhukti")

        timing_factors = []
        timing_score = 0.0

        # Check if current Dasha lord is in 10th or aspects 10th
        if current_dasa in planets_in_10:
            timing_factors.append(f"{current_dasa} Dasha (in 10th house)")
            timing_score += 0.5

        # Check if current Bhukti lord is related to career
        if current_bhukti in planets_in_10:
            timing_factors.append(f"{current_bhukti} Bhukti (in 10th house)")
            timing_score += 0.3

        # Check if Dasha lord is 10th lord (already covered in earlier rule, but add timing context)
        if current_dasa == tenth_lord:
            timing_factors.append(f"{current_dasa} is 10th lord")
            timing_score += 0.4

        if timing_factors:
            factors.append(f"dasha_career_timing_{current_dasa}_{current_bhukti}")
            scores["dasha_career_timing"] = min(1.0, timing_score)
            meta = _rule_meta("dasha_career_timing")
            applied_rules.append({
                "rule_id": "dasha_career_timing",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Current period: {current_dasa}/{current_bhukti}. {'; '.join(timing_factors)}. Favorable time for career moves.",
                "score": scores["dasha_career_timing"]
            })

    # 40) D1 vs D10 Strength Comparison
    # Compare planets that are strong in both D1 and D10
    strong_in_both = []
    strong_in_d10_only = []

    for pname in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if pname not in d1 or pname not in d10:
            continue

        # Check D1 strength
        d1_rasi = d1[pname].get("rasi") if isinstance(d1[pname], dict) else None
        d1_strong = (d1_rasi in OWN_SIGNS.get(pname, []) or d1_rasi == EXALTATION.get(pname))

        # Check D10 strength
        d10_rasi = d10[pname].get("rasi") if isinstance(d10[pname], dict) else None
        d10_strong = (d10_rasi in OWN_SIGNS.get(pname, []) or d10_rasi == EXALTATION.get(pname))

        if d1_strong and d10_strong:
            strong_in_both.append(pname)
        elif d10_strong and not d1_strong:
            strong_in_d10_only.append(pname)

    if strong_in_both or strong_in_d10_only:
        comparison_details = []
        score = 0.0

        if strong_in_both:
            comparison_details.append(f"Strong in both D1 & D10: {', '.join(strong_in_both)}")
            score += 0.3 * len(strong_in_both)

        if strong_in_d10_only:
            comparison_details.append(f"Strong in D10 only (career talent): {', '.join(strong_in_d10_only)}")
            score += 0.2 * len(strong_in_d10_only)

        factors.append(f"D1_D10_strength_comparison")
        scores["d1_d10_strength_comparison"] = min(1.0, score)
        meta = _rule_meta("d1_d10_strength_comparison")
        applied_rules.append({
            "rule_id": "d1_d10_strength_comparison",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" {'; '.join(comparison_details)}.",
            "score": scores["d1_d10_strength_comparison"]
        })

    # 41) 10th house from Moon (Chandra Lagna)
    if "Moon" in d1 and isinstance(d1["Moon"], dict) and "longitude" in d1["Moon"]:
        moon_lon = d1["Moon"]["longitude"]
        moon_house_idx = _which_house_d1(moon_lon, cusps) - 1  # 0-based index

        # 10th from Moon is 9 houses ahead (0-based)
        tenth_from_moon_idx = (moon_house_idx + 9) % 12

        # Get the rasi of 10th from Moon
        if len(cusps) > tenth_from_moon_idx:
            tenth_from_moon_cusp = cusps[tenth_from_moon_idx]
            tenth_from_moon_rasi_idx = int(tenth_from_moon_cusp // 30) % 12
            rasis = ["Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
                     "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena"]
            tenth_from_moon_rasi = rasis[tenth_from_moon_rasi_idx]
            tenth_from_moon_lord = RASI_LORDS.get(tenth_from_moon_rasi, "")

            # Find planets in 10th from Moon
            planets_in_10th_from_moon = []
            for pname, pdata in d1.items():
                if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                    continue
                h = _which_house_d1(pdata["longitude"], cusps)
                if h == (tenth_from_moon_idx + 1):  # Convert back to 1-based
                    planets_in_10th_from_moon.append(pname)

            if planets_in_10th_from_moon or tenth_from_moon_lord:
                score = min(1.0, 0.2 * len(planets_in_10th_from_moon) + 0.3)

                factors.append(f"moon_10th_career_{tenth_from_moon_rasi}")
                scores["moon_10th_career"] = score
                meta = _rule_meta("moon_10th_career")
                applied_rules.append({
                    "rule_id": "moon_10th_career",
                    "name": meta["name"],
                    "explanation": meta["explanation"] + f" 10th from Moon: {tenth_from_moon_rasi} (lord: {tenth_from_moon_lord}). Planets: {', '.join(planets_in_10th_from_moon) if planets_in_10th_from_moon else 'None'}.",
                    "score": score
                })

    # 42) Benefics vs Malefics Ratio in D10
    d10_benefics = []
    d10_malefics = []

    for pname, pdata in d10.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        if pname in BENEFICS:
            d10_benefics.append(pname)
        elif pname in MALEFICS:
            d10_malefics.append(pname)

    if d10_benefics or d10_malefics:
        benefic_count = len(d10_benefics)
        malefic_count = len(d10_malefics)
        total = benefic_count + malefic_count

        if total > 0:
            benefic_ratio = benefic_count / total

            # Higher benefic ratio = smoother career path
            if benefic_ratio >= 0.6:
                score = 0.8
                interpretation = "smooth progress"
            elif benefic_ratio >= 0.4:
                score = 0.5
                interpretation = "balanced (effort with support)"
            else:
                score = 0.3
                interpretation = "challenging (success through struggle)"

            factors.append(f"D10_benefic_malefic_ratio_{benefic_count}:{malefic_count}")
            scores["d10_benefic_malefic_ratio"] = score
            meta = _rule_meta("d10_benefic_malefic_ratio")
            applied_rules.append({
                "rule_id": "d10_benefic_malefic_ratio",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Benefics: {benefic_count} ({', '.join(d10_benefics)}), Malefics: {malefic_count} ({', '.join(d10_malefics)}). Career path: {interpretation}.",
                "score": score
            })

    # ========== PHASE 3 ADVANCED ENHANCEMENTS ==========

    # 43) Planets Exalted in Both D1 and D10
    # This is rare and highly auspicious - shows exceptional, consistent talent
    exalted_in_both = []

    for pname in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if pname not in d1 or pname not in d10:
            continue

        d1_rasi = d1[pname].get("rasi") if isinstance(d1[pname], dict) else None
        d10_rasi = d10[pname].get("rasi") if isinstance(d10[pname], dict) else None

        # Check if exalted in both
        if d1_rasi == EXALTATION.get(pname) and d10_rasi == EXALTATION.get(pname):
            exalted_in_both.append(pname)

    if exalted_in_both:
        # This is extremely rare and powerful
        score = min(1.5, 0.5 * len(exalted_in_both))  # Can exceed 1.0 for exceptional cases

        planet_details = []
        for planet in exalted_in_both:
            exalt_sign = EXALTATION.get(planet)
            planet_details.append(f"{planet} (exalted in {exalt_sign})")

        factors.append(f"exalted_in_both_D1_D10_{','.join(exalted_in_both)}")
        scores["exalted_in_both_d1_d10"] = score
        meta = _rule_meta("exalted_in_both_d1_d10")
        applied_rules.append({
            "rule_id": "exalted_in_both_d1_d10",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Planets: {', '.join(planet_details)}. Exceptional, consistent talent in career.",
            "score": score
        })

    # 44) Jupiter Aspects in D10
    # Jupiter aspects are highly beneficial - wisdom, expansion, opportunities
    if "Jupiter" in d10 and isinstance(d10["Jupiter"], dict) and "longitude" in d10["Jupiter"]:
        jupiter_lon = d10["Jupiter"]["longitude"]
        jupiter_house = _which_house_d1(jupiter_lon, d10_cusps)

        # Jupiter aspects: 5th, 7th, and 9th from its position
        # Calculate which houses Jupiter aspects
        jupiter_aspects_houses = [
            (jupiter_house + 4) % 12 + 1,  # 5th aspect (0-based: +4)
            (jupiter_house + 6) % 12 + 1,  # 7th aspect (0-based: +6)
            (jupiter_house + 8) % 12 + 1,  # 9th aspect (0-based: +8)
        ]

        # Find planets in aspected houses
        aspected_planets = []
        aspected_houses_with_planets = []

        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            if pname == "Jupiter":  # Skip Jupiter itself
                continue

            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h in jupiter_aspects_houses:
                aspected_planets.append(pname)
                if h not in aspected_houses_with_planets:
                    aspected_houses_with_planets.append(h)

        if aspected_planets or jupiter_aspects_houses:
            # Score based on benefic aspects and important houses (1,4,7,10)
            score = 0.4  # Base score for Jupiter having aspects
            benefic_aspects = sum(1 for p in aspected_planets if p in BENEFICS)
            important_houses = sum(1 for h in jupiter_aspects_houses if h in [1, 4, 7, 10])

            score += 0.1 * benefic_aspects
            score += 0.15 * important_houses
            score = min(1.0, score)

            factors.append(f"Jupiter_aspects_D10_houses_{','.join(map(str, jupiter_aspects_houses))}")
            scores["jupiter_aspects_d10"] = score
            meta = _rule_meta("jupiter_aspects_d10")
            applied_rules.append({
                "rule_id": "jupiter_aspects_d10",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Jupiter in house {jupiter_house} aspects houses {', '.join(map(str, jupiter_aspects_houses))}. Aspected planets: {', '.join(aspected_planets) if aspected_planets else 'None'}. Brings wisdom and opportunities.",
                "score": score
            })

    # 45) Saturn Aspects in D10
    # Saturn aspects bring discipline, structure, but also delays
    if "Saturn" in d10 and isinstance(d10["Saturn"], dict) and "longitude" in d10["Saturn"]:
        saturn_lon = d10["Saturn"]["longitude"]
        saturn_house = _which_house_d1(saturn_lon, d10_cusps)

        # Saturn aspects: 3rd, 7th, and 10th from its position
        saturn_aspects_houses = [
            (saturn_house + 2) % 12 + 1,  # 3rd aspect (0-based: +2)
            (saturn_house + 6) % 12 + 1,  # 7th aspect (0-based: +6)
            (saturn_house + 9) % 12 + 1,  # 10th aspect (0-based: +9)
        ]

        # Find planets in aspected houses
        aspected_planets = []
        aspected_houses_with_planets = []

        for pname, pdata in d10.items():
            if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
                continue
            if pname == "Saturn":  # Skip Saturn itself
                continue

            h = _which_house_d1(pdata["longitude"], d10_cusps)
            if h in saturn_aspects_houses:
                aspected_planets.append(pname)
                if h not in aspected_houses_with_planets:
                    aspected_houses_with_planets.append(h)

        if aspected_planets or saturn_aspects_houses:
            # Score is neutral to slightly positive (discipline can be good)
            score = 0.4  # Base score
            # Saturn aspecting Upachaya houses (3,6,10,11) is favorable
            upachaya_aspects = sum(1 for h in saturn_aspects_houses if h in [3, 6, 10, 11])
            score += 0.15 * upachaya_aspects
            score = min(1.0, score)

            factors.append(f"Saturn_aspects_D10_houses_{','.join(map(str, saturn_aspects_houses))}")
            scores["saturn_aspects_d10"] = score
            meta = _rule_meta("saturn_aspects_d10")
            applied_rules.append({
                "rule_id": "saturn_aspects_d10",
                "name": meta["name"],
                "explanation": meta["explanation"] + f" Saturn in house {saturn_house} aspects houses {', '.join(map(str, saturn_aspects_houses))}. Aspected planets: {', '.join(aspected_planets) if aspected_planets else 'None'}. Brings discipline and structure.",
                "score": score
            })

    # 46) Retrograde Planets in D10
    # Retrograde planets indicate unconventional approaches, unique methods
    retrograde_in_d10 = []

    for pname in ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:  # Exclude Sun/Moon (never retrograde)
        if pname not in d10 or not isinstance(d10[pname], dict):
            continue

        is_retrograde = d10[pname].get("retrograde", False)
        if is_retrograde:
            # Also check which house it's in
            planet_house = _which_house_d1(d10[pname]["longitude"], d10_cusps) if "longitude" in d10[pname] else None
            retrograde_in_d10.append((pname, planet_house))

    if retrograde_in_d10:
        # Retrograde planets are not necessarily bad - they show unique approaches
        score = min(1.0, 0.3 * len(retrograde_in_d10) + 0.2)

        planet_details = []
        for planet, house in retrograde_in_d10:
            if house:
                planet_details.append(f"{planet} in house {house}")
            else:
                planet_details.append(planet)

        factors.append(f"retrograde_in_D10_{','.join([p for p, h in retrograde_in_d10])}")
        scores["retrograde_planets_d10"] = score
        meta = _rule_meta("retrograde_planets_d10")
        applied_rules.append({
            "rule_id": "retrograde_planets_d10",
            "name": meta["name"],
            "explanation": meta["explanation"] + f" Retrograde planets: {', '.join(planet_details)}. Indicates unconventional career approach or unique specialized skills.",
            "score": score
        })

    # Aggregate strength
    total_score = sum(s for s in scores.values() if isinstance(s, (int, float))) / max(len(scores), 1)
    if total_score >= 0.7:
        career_strength = "strong"
    elif total_score >= 0.4:
        career_strength = "moderate"
    else:
        career_strength = "weak"
    if not scores:
        career_strength = "moderate"

    # Rules table: all predefined rules with tick (matched) or cross (not matched)
    # Enhanced with actual values and detailed explanations
    matched_rule_ids = set()
    applied_rules_map = {}
    for r in applied_rules:
        rid = r.get("rule_id", "")
        matched_rule_ids.add(rid)
        applied_rules_map[rid] = r
        for key in RULE_META:
            if key in rid or rid.startswith(key):
                matched_rule_ids.add(key)
                if key not in applied_rules_map:
                    applied_rules_map[key] = r

    rules_checklist = []
    for rule_id, meta in RULE_META.items():
        matched = rule_id in matched_rule_ids or any(rule_id in rid for rid in matched_rule_ids)

        # Get detailed information from applied_rules if available
        rule_info = applied_rules_map.get(rule_id, {})

        # Build current value and reason based on rule type
        current_value = ""
        reason = ""

        # Provide specific current values based on rule_id
        if rule_id == "D1_10th_lord_in_10th":
            tenth_lord = chart_summary.get("tenth_lord", "Unknown")
            tenth_lord_in_rasi = chart_summary.get("tenth_lord_in_rasi", "Unknown")
            tenth_house_rasi = chart_summary.get("tenth_house_rasi", "Unknown")
            if matched:
                current_value = f"10th lord: {tenth_lord} in {tenth_house_rasi}"
                reason = f"{tenth_lord} (10th lord) is placed in the 10th house ({tenth_house_rasi}), which is excellent for career."
            else:
                current_value = f"10th lord: {tenth_lord} in {tenth_lord_in_rasi}"
                reason = f"{tenth_lord} (10th lord) is in {tenth_lord_in_rasi}, not in the 10th house ({tenth_house_rasi})."

        elif rule_id == "D1_10th_lord_in_own_sign":
            tenth_lord = chart_summary.get("tenth_lord", "Unknown")
            tenth_lord_in_rasi = chart_summary.get("tenth_lord_in_rasi", "Unknown")
            if matched:
                current_value = f"{tenth_lord} in own sign ({tenth_lord_in_rasi})"
                reason = f"The 10th lord {tenth_lord} is in its own sign {tenth_lord_in_rasi}, strengthening career."
            else:
                current_value = f"{tenth_lord} in {tenth_lord_in_rasi}"
                reason = f"The 10th lord {tenth_lord} is not in its own sign."

        elif rule_id == "D1_planets_in_10th":
            planets = chart_summary.get("planets_in_10th", [])
            if matched and planets:
                current_value = f"{len(planets)} planets: {', '.join(planets)}"
                reason = rule_info.get("explanation", f"Planets in 10th house: {', '.join(planets)}")
            else:
                current_value = "No planets in 10th"
                reason = "No planets occupy the 10th house in D1."

        elif rule_id == "current_dasa_lord_is_10th_lord":
            tenth_lord = chart_summary.get("tenth_lord", "Unknown")
            if dasha_current:
                current_dasa = dasha_current.get("current_dasa", "Unknown")
                if matched:
                    current_value = f"Dasha: {current_dasa} (10th lord)"
                    reason = f"Currently running {current_dasa} Mahadasha, which rules the 10th house. Excellent time for career growth."
                else:
                    current_value = f"Dasha: {current_dasa} (10th lord: {tenth_lord})"
                    reason = f"Currently in {current_dasa} Mahadasha. The 10th lord is {tenth_lord}, not {current_dasa}."
            else:
                current_value = "Dasha not calculated"
                reason = "Current Dasha period could not be determined."

        elif rule_id == "current_bhukti_lord_is_10th_lord":
            tenth_lord = chart_summary.get("tenth_lord", "Unknown")
            if dasha_current:
                current_bhukti = dasha_current.get("current_bhukti", "Unknown")
                current_dasa = dasha_current.get("current_dasa", "Unknown")
                if matched:
                    current_value = f"Bhukti: {current_bhukti} (10th lord)"
                    reason = f"Currently in {current_bhukti} Antardasha within {current_dasa} Mahadasha. The 10th lord sub-period brings career opportunities."
                else:
                    current_value = f"Bhukti: {current_bhukti} (10th lord: {tenth_lord})"
                    reason = f"Currently in {current_bhukti} Antardasha. The 10th lord is {tenth_lord}, not {current_bhukti}."
            else:
                current_value = "Bhukti not calculated"
                reason = "Current Bhukti period could not be determined."

        elif rule_id in ["dasha_10th_link", "bhukti_10th_link"]:
            if dasha_current:
                current_dasa = dasha_current.get("current_dasa", "Unknown")
                current_bhukti = dasha_current.get("current_bhukti", "Unknown")
                if matched:
                    current_value = f"{current_dasa}/{current_bhukti}"
                    reason = rule_info.get("explanation", "Connected to 10th house")
                else:
                    current_value = f"{current_dasa}/{current_bhukti}"
                    reason = "Current Dasha/Bhukti periods not connected to 10th house or its lord."
            else:
                current_value = "Not calculated"
                reason = "Dasha periods not calculated."

        elif matched:
            # Generic matched case
            explanation = rule_info.get("explanation", meta.get("explanation", ""))
            score_val = rule_info.get("score", "")
            if isinstance(score_val, (int, float)):
                current_value = f"Score: {score_val:.2f}"
            else:
                current_value = str(score_val) if score_val else "✓ Present"
            reason = explanation
        else:
            # Generic not matched case
            current_value = "Not present"
            reason = meta.get("explanation", "") + " (Not found in this chart)"

        rules_checklist.append({
            "rule_id": rule_id,
            "name": meta.get("name", rule_id),
            "matched": matched,
            "current_value": current_value,
            "reason": reason,
            "score": rule_info.get("score") if matched else 0,
        })

    matched_count = sum(1 for r in rules_checklist if r["matched"])
    total_rules = len(rules_checklist)
    rules_score = f"{matched_count}/{total_rules}"

    return {
        "career_strength": career_strength,
        "factors": factors,
        "scores": scores,
        "applied_rules": applied_rules,
        "rules_checklist": rules_checklist,
        "rules_score": rules_score,
        "chart_summary": chart_summary,
    }
