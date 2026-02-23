"""
Rule Categories for organizing career prediction rules
Groups rules into logical categories for better UI presentation
"""

RULE_CATEGORIES = {
    # Category 1: D1 (Birth Chart) - 10th House and Lord
    "D1_10th_lord_in_10th": "d1_tenth_house",
    "D1_10th_lord_in_own_sign": "d1_tenth_house",
    "D1_10th_lord_exalted": "d1_tenth_house",
    "d1_10th_lord_placement": "d1_tenth_house",
    "D1_planets_in_10th": "d1_tenth_house",
    "d1_10th_benefics": "d1_tenth_house",
    "d1_10th_malefics": "d1_tenth_house",
    "D1_10th_lord_in_2nd_3rd": "d1_tenth_house",
    "aspects_to_10th_house": "d1_tenth_house",
    "aspects_to_10th_lord": "d1_tenth_house",

    # Category 2: D10 (Career Divisional Chart)
    "D10_10th_rasi": "d10_career_chart",
    "D10_10th_lord_transposition": "d10_career_chart",
    "D10_10th_lord_weak": "d10_career_chart",
    "D10_Kendra_benefics": "d10_career_chart",
    "D10_Kendra_malefics": "d10_career_chart",
    "D10_sign_nature_10th": "d10_career_chart",
    "Vargottama": "d10_career_chart",
    "raja_yoga_in_D10": "d10_career_chart",

    # Category 3: Dasha (Planetary Periods)
    "current_dasa_lord_is_10th_lord": "dasha_timing",
    "current_bhukti_lord_is_10th_lord": "dasha_timing",
    "dasha_10th_link": "dasha_timing",
    "bhukti_10th_link": "dasha_timing",

    # Category 4: Ashtakavarga (Point System)
    "SAV_10th_house_bindus": "ashtakavarga",
    "sav_10th": "ashtakavarga",

    # Category 5: Special Yogas (Combinations)
    "yogakaraka_in_10th": "special_yogas",
    "parivartana_yoga_10th": "special_yogas",
    "neechabhanga_10th": "special_yogas",
    "dharma_karma_yoga": "special_yogas",
    "sun_in_10th": "special_yogas",
    "exalted_in_10th": "special_yogas",
    "rahu_ketu_in_10th": "special_yogas",
    "combust_in_10th": "special_yogas",

    # Category 6: Advanced Analysis
    "D9_dispositor_10th_lord": "advanced",
    "house_connections_10_11_lagna": "advanced",
    "chandra_lagna_10th": "advanced",
    "chara_karakas": "advanced",
    "upachaya_sun_saturn": "advanced",
    "eighth_house": "advanced",
    "amsa_deities": "advanced",
}

CATEGORY_NAMES = {
    "d1_tenth_house": "📊 D1 (Birth Chart) - 10th House Analysis",
    "d10_career_chart": "💼 D10 (Career Chart) Analysis",
    "dasha_timing": "⏰ Dasha (Planetary Periods)",
    "ashtakavarga": "🎯 Ashtakavarga (Point System)",
    "special_yogas": "✨ Special Yogas (Combinations)",
    "advanced": "🔬 Advanced Analysis",
}

CATEGORY_ORDER = [
    "d1_tenth_house",
    "d10_career_chart",
    "special_yogas",
    "dasha_timing",
    "ashtakavarga",
    "advanced",
]

def get_rule_category(rule_id: str) -> str:
    """Get category for a rule ID"""
    return RULE_CATEGORIES.get(rule_id, "advanced")

def get_category_name(category: str) -> str:
    """Get display name for a category"""
    return CATEGORY_NAMES.get(category, "Other Rules")

def group_rules_by_category(rules_checklist):
    """
    Group rules into categories for better UI organization

    Args:
        rules_checklist: List of rule dictionaries

    Returns:
        List of category dictionaries with grouped rules
    """
    from collections import defaultdict

    grouped = defaultdict(list)

    for rule in rules_checklist:
        category = get_rule_category(rule['rule_id'])
        grouped[category].append(rule)

    # Build result in order
    result = []
    for cat in CATEGORY_ORDER:
        if cat in grouped:
            result.append({
                'category': cat,
                'name': get_category_name(cat),
                'rules': grouped[cat],
                'matched_count': sum(1 for r in grouped[cat] if r['matched']),
                'total_count': len(grouped[cat]),
            })

    # Add any remaining categories not in order
    for cat, rules in grouped.items():
        if cat not in CATEGORY_ORDER:
            result.append({
                'category': cat,
                'name': get_category_name(cat),
                'rules': rules,
                'matched_count': sum(1 for r in rules if r['matched']),
                'total_count': len(rules),
            })

    return result
