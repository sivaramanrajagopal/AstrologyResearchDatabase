#!/usr/bin/env python3
"""
Verify career prediction rules one-by-one for Native (Chart) ID 3.
Loads chart from DB, builds D1/D10, gets Dasha, runs career_rules, then reports
for each rule: chart values used, whether it fired, and confirmation.
Run from project root: python3 scripts/verify_native_3_career_rules.py
"""
import os
import sys
from datetime import datetime

# Project root
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Load env before supabase
try:
    import environment_config  # noqa: F401
except Exception:
    pass

RASI_NAMES = [
    "Mesha", "Rishaba", "Mithuna", "Kataka", "Simha", "Kanni",
    "Thula", "Vrischika", "Dhanus", "Makara", "Kumbha", "Meena",
]
RASI_LORDS = {
    "Mesha": "Mars", "Rishaba": "Venus", "Mithuna": "Mercury",
    "Kataka": "Moon", "Simha": "Sun", "Kanni": "Mercury",
    "Thula": "Venus", "Vrischika": "Mars", "Dhanus": "Jupiter",
    "Makara": "Saturn", "Kumbha": "Saturn", "Meena": "Jupiter",
}


def _get_d1_cusps(d1):
    cusps = []
    if "_enhanced" in d1 and "houses" in d1["_enhanced"]:
        for i in range(1, 13):
            key = f"House_{i}"
            if key in d1["_enhanced"]["houses"]:
                cusps.append(d1["_enhanced"]["houses"][key]["longitude"])
            else:
                cusps.append((i - 1) * 30.0)
    else:
        cusps = [i * 30.0 for i in range(12)]
    return cusps


def _which_house(lon, cusps):
    lon = lon % 360
    for i in range(12):
        c = cusps[i]
        n = cusps[(i + 1) % 12]
        if n > c:
            if c <= lon < n:
                return i + 1
        else:
            if lon >= c or lon < n:
                return i + 1
    return 10


def get_d1_from_db(chart_id):
    from supabase_config import supabase_manager
    if not supabase_manager:
        raise RuntimeError("Supabase not configured")
    row = supabase_manager.get_birth_chart(chart_id)
    if not row:
        raise RuntimeError(f"Chart {chart_id} not found")
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    d1 = {}
    for p in planets:
        key = p.lower()
        lon = row.get(f"{key}_longitude")
        if lon is None:
            continue
        d1[p] = {
            "longitude": float(lon),
            "rasi": row.get(f"{key}_rasi") or "",
            "rasi_lord": row.get(f"{key}_rasi_lord") or "",
            "retrograde": row.get(f"{key}_retrograde") or False,
        }
    houses = {}
    for i in range(1, 13):
        lon = row.get(f"house_{i}_longitude")
        if lon is not None:
            rasi = row.get(f"house_{i}_rasi") or ""
            houses[f"House_{i}"] = {"longitude": float(lon), "rasi": rasi, "degrees_in_rasi": float(lon % 30)}
    if houses:
        d1["_enhanced"] = {"houses": houses}
    return d1, row


def main():
    chart_id = 3
    print("=" * 70)
    print(f"CAREER RULES VERIFICATION — Native (Chart) ID {chart_id}")
    print("=" * 70)

    # 1) Load chart and build D1
    try:
        d1, row = get_d1_from_db(chart_id)
    except Exception as e:
        print(f"ERROR: Could not load chart {chart_id}: {e}")
        print("Ensure Supabase is configured and chart 3 exists.")
        return 1

    name = row.get("name") or "Native"
    dob = row.get("date_of_birth")
    tob = row.get("time_of_birth") or "12:00"
    if isinstance(tob, str) and len(tob) > 5:
        tob = tob[:5]
    print(f"\nChart: {name}  DOB: {dob}  TOB: {tob}")

    # 2) Compute D10
    from services.d10_dasamsa import calculate_d10_chart
    d10 = calculate_d10_chart(d1)
    if not d10:
        print("ERROR: D10 calculation failed")
        return 1

    # 3) Current Dasha
    dasha_current = None
    try:
        from services.dasha_service import calculate_current_dasha
        birth_date = str(dob) if dob else "2000-01-01"
        dasha_current = calculate_current_dasha(d1, birth_date, tob)
    except Exception as e:
        print(f"Note: Dasha not calculated: {e}")

    # 4) BAV/SAV (optional)
    bav_sav_full = None
    try:
        from services.ashtakavarga_service import calculate_ashtakavarga_full
        av = calculate_ashtakavarga_full(d1)
        if av and "sav" in av:
            bav_sav_full = {
                "sav_chart": av["sav"]["chart"],
                "sav_total": av["sav"]["total"],
            }
    except Exception:
        pass

    cusps = _get_d1_cusps(d1)
    d10_cusps = _get_d1_cusps(d10) if "_enhanced" in d10 and "houses" in d10["_enhanced"] else [i * 30.0 for i in range(12)]

    # ---- Chart facts (used by rules) ----
    house_10_rasi = None
    if len(cusps) >= 10:
        idx = int(cusps[9] // 30) % 12
        house_10_rasi = RASI_NAMES[idx]
    tenth_lord = RASI_LORDS.get(house_10_rasi, "") if house_10_rasi else ""

    tenth_lord_house_d1 = None
    tenth_lord_rasi_d1 = None
    if tenth_lord:
        for pname, pdata in d1.items():
            if pname.startswith("_") or not isinstance(pdata, dict):
                continue
            if pname == tenth_lord or RASI_LORDS.get(pdata.get("rasi")) == tenth_lord:
                tenth_lord_rasi_d1 = pdata.get("rasi")
                lon = pdata.get("longitude")
                if lon is not None:
                    tenth_lord_house_d1 = _which_house(lon, cusps)
                break

    planets_in_10_d1 = []
    for pname, pdata in d1.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        if _which_house(pdata["longitude"], cusps) == 10:
            planets_in_10_d1.append(pname)

    d10_house_10_rasi = None
    if "_enhanced" in d10 and "houses" in d10["_enhanced"] and "House_10" in d10["_enhanced"]["houses"]:
        d10_house_10_rasi = d10["_enhanced"]["houses"]["House_10"].get("rasi")

    print("\n" + "-" * 70)
    print("CHART FACTS (inputs to rules)")
    print("-" * 70)
    print(f"  D1 10th house sign (rasi):     {house_10_rasi}")
    print(f"  D1 10th lord (athipadi):       {tenth_lord}")
    print(f"  D1 10th lord in house:         {tenth_lord_house_d1}")
    print(f"  D1 10th lord in rasi:          {tenth_lord_rasi_d1}")
    print(f"  D1 planets in 10th house:      {planets_in_10_d1 or 'None'}")
    print(f"  D10 10th house sign:           {d10_house_10_rasi}")
    print(f"  Current Dasha (Mahadasha):     {dasha_current.get('current_dasa') if dasha_current else 'N/A'}")
    print(f"  Current Bhukti (Antardasha):   {dasha_current.get('current_bhukti') if dasha_current else 'N/A'}")

    # D10: planets in 10th, Kendra benefics/malefics
    planets_in_10_d10 = []
    for pname, pdata in d10.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        if _which_house(pdata["longitude"], d10_cusps) == 10:
            planets_in_10_d10.append(pname)
    kendra_benefics_d10 = []
    kendra_malefics_d10 = []
    BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
    MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu"}
    for pname, pdata in d10.items():
        if pname.startswith("_") or not isinstance(pdata, dict) or "longitude" not in pdata:
            continue
        h = _which_house(pdata["longitude"], d10_cusps)
        if h in (1, 4, 7, 10):
            if pname in BENEFICS:
                kendra_benefics_d10.append(pname)
            if pname in MALEFICS:
                kendra_malefics_d10.append(pname)
    print(f"  D10 planets in 10th house:      {planets_in_10_d10 or 'None'}")
    print(f"  D10 Kendra benefics:            {kendra_benefics_d10 or 'None'}")
    print(f"  D10 Kendra malefics:            {kendra_malefics_d10 or 'None'}")

    if bav_sav_full and "sav_chart" in bav_sav_full and len(bav_sav_full["sav_chart"]) > 9:
        print(f"  SAV 10th house bindus:          {bav_sav_full['sav_chart'][9]}")
    else:
        print("  SAV 10th house bindus:          N/A")

    # 5) Run career_rules
    from services.career_rules import career_rules
    result = career_rules(d1, d10, dasha_current=dasha_current, bav_sav_full=bav_sav_full)

    strength = result.get("career_strength", "?")
    factors = result.get("factors", [])
    scores = result.get("scores", {})
    applied_rules = result.get("applied_rules", [])
    rules_checklist = result.get("rules_checklist", [])

    print("\n" + "-" * 70)
    print("CAREER RULES RESULT")
    print("-" * 70)
    print(f"  Career strength:    {strength}")
    print(f"  Factors (tags):    {factors[:15]}{'...' if len(factors) > 15 else ''}")
    print(f"  Number of rules applied: {len(applied_rules)}")

    # 6) Rule-by-rule verification
    print("\n" + "=" * 70)
    print("RULE-BY-RULE VERIFICATION")
    print("=" * 70)

    applied_by_id = {r.get("rule_id"): r for r in applied_rules}

    # Top 10 + key rules in order of appearance in career_rules
    rules_to_verify = [
        ("D1_10th_lord_in_10th", "10th lord in 10th house (D1)",
         f"10th lord = {tenth_lord}, in house = {tenth_lord_house_d1}, in rasi = {tenth_lord_rasi_d1}. Rule fires if 10th lord's rasi equals 10th house rasi ({house_10_rasi})."),
        ("D1_10th_lord_in_own_sign", "10th lord in own sign (D1)",
         f"10th lord = {tenth_lord}, rasi = {tenth_lord_rasi_d1}. Fires if rasi in own signs."),
        ("D1_10th_lord_exalted", "10th lord exalted (D1)",
         f"10th lord = {tenth_lord}, rasi = {tenth_lord_rasi_d1}. Fires if rasi is exaltation sign."),
        ("D1_planets_in_10th", "Planets in 10th house (D1)",
         f"Planets in 10th = {planets_in_10_d1}. Fires if non-empty; benefics/malefics counted."),
        ("D10_10th_rasi", "D10 10th house sign",
         f"D10 10th rasi = {d10_house_10_rasi}. Fires if present."),
        ("current_dasa_lord_is_10th_lord", "Current Dasha lord is 10th lord",
         f"Current Dasha = {dasha_current.get('current_dasa') if dasha_current else 'N/A'}, 10th lord = {tenth_lord}. Fires if equal."),
        ("current_bhukti_lord_is_10th_lord", "Current Bhukti lord is 10th lord",
         f"Current Bhukti = {dasha_current.get('current_bhukti') if dasha_current else 'N/A'}, 10th lord = {tenth_lord}. Fires if equal."),
        ("SAV_10th_house_bindus", "SAV 10th house bindus",
         "Fires if SAV chart available; score by bindus >= 30 (1.0), >= 26 (0.7), else 0.4."),
        ("D1_10th_lord_in_2nd_3rd", "10th lord in 2nd or 3rd house (sales)",
         f"10th lord house = {tenth_lord_house_d1}. Fires if 2 or 3."),
        ("D10_Kendra_benefics", "Benefics in Kendra in D10",
         f"Kendra benefics in D10 = {kendra_benefics_d10}. Fires if non-empty."),
        ("D10_Kendra_malefics", "Malefics in Kendra in D10",
         f"Kendra malefics in D10 = {kendra_malefics_d10}. Fires if non-empty."),
        ("D10_sign_nature_10th", "Sign nature (Tatwa) of 10th in D10",
         f"D10 10th rasi = {d10_house_10_rasi}. Fires if present (fire/earth/air/water)."),
        ("Vargottama", "Vargottama (same sign D1 and D10)",
         "Fires for each planet with same rasi in D1 and D10."),
        ("D10_10th_lord_transposition", "10th lord strong in D10",
         f"10th lord = {tenth_lord}. Fires if in D10 lord is in own/exaltation and in good house (1,4,5,7,9,10,11)."),
        ("D10_10th_lord_weak", "10th lord weak in D10",
         "Fires if D1 10th lord strong but in D10 not strong and not in good house."),
        ("d10_lagna_strength", "D10 Lagna lord strength",
         "D10 Ascendant lord and its placement (Kendra/Trikona/own/exaltation)."),
        ("d10_10th_lord_placement", "D10 10th lord placement",
         "D10 10th house lord and its house/sign strength."),
        ("saturn_in_d10", "Saturn in D10",
         "Saturn's house and sign in D10; Upachaya (3,6,10,11) favourable."),
    ]

    for rule_id, rule_name, context in rules_to_verify:
        r = applied_by_id.get(rule_id)
        if r:
            print(f"\n  [MATCH] {rule_id}")
            print(f"    Name: {rule_name}")
            print(f"    Context: {context}")
            print(f"    Score: {r.get('score')}")
            print(f"    Explanation: {(r.get('explanation') or '')[:200]}...")
        else:
            print(f"\n  [NO MATCH] {rule_id}")
            print(f"    Name: {rule_name}")
            print(f"    Context: {context}")
            print("    Reason: Rule conditions not satisfied for this chart.")

    # Any other applied rules not in the short list
    other_applied = [rid for rid in applied_by_id if not any(rid == r[0] for r in rules_to_verify)]
    if other_applied:
        print("\n  --- Other rules that fired ---")
        for rid in other_applied[:20]:
            r = applied_by_id[rid]
            print(f"    [MATCH] {rid}  score={r.get('score')}  {(r.get('explanation') or '')[:80]}...")

    # Checklist summary (from career_rules output)
    if rules_checklist:
        print("\n" + "-" * 70)
        print("RULES CHECKLIST (matched vs not matched)")
        print("-" * 70)
        matched = [c for c in rules_checklist if c.get("matched")]
        not_matched = [c for c in rules_checklist if not c.get("matched")]
        print(f"  Matched:   {len(matched)}  — {[c.get('rule_id') for c in matched[:12]]}{'...' if len(matched) > 12 else ''}")
        print(f"  Not matched: {len(not_matched)} rules (conditions not met for this chart)")

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
