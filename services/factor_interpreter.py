"""
Factor Code Interpreter
Converts technical factor codes into human-readable explanations
"""

from typing import Dict, List, Tuple


# Factor code patterns and their base explanations
FACTOR_PATTERNS = {
    'D1_planets_in_10th': {
        'title': 'Planets in 10th House (D1)',
        'description': 'Shows which planets occupy the career house in the main birth chart',
        'interpretation': 'Benefics (Jupiter, Venus, Mercury, Moon) support career. Malefics (Saturn, Mars, Rahu, Ketu) can create challenges or drive ambition.',
    },
    'D10_10th_rasi': {
        'title': '10th House Sign in D10 Chart',
        'description': 'The zodiac sign in the 10th house of the career divisional chart (D10)',
        'interpretation': 'Different signs indicate different career fields and professional approach.',
        'signs': {
            'Mesha': 'Aries - Leadership, pioneering, entrepreneurship',
            'Rishaba': 'Taurus - Finance, luxury goods, steady growth',
            'Mithuna': 'Gemini - Communication, media, versatile careers',
            'Kataka': 'Cancer - Nurturing, hospitality, public service',
            'Simha': 'Leo - Authority, government, creative fields',
            'Kanya': 'Virgo - Analysis, health, service-oriented',
            'Tula': 'Libra - Law, diplomacy, partnerships',
            'Vrishchika': 'Scorpio - Research, occult, transformative work',
            'Dhanus': 'Sagittarius - Teaching, philosophy, international',
            'Makara': 'Capricorn - Administration, structured careers',
            'Kumbha': 'Aquarius - Innovation, social work, technology',
            'Meena': 'Pisces - Spirituality, creativity, healing',
        },
    },
    'D10_Kendra_benefics': {
        'title': 'Benefic Planets in Kendra (D10)',
        'description': 'Beneficial planets (Jupiter, Venus, Mercury, Moon) in angular houses (1st, 4th, 7th, 10th) of D10 chart',
        'interpretation': 'These planets promise promotions, success, and smooth career growth during their Dasha periods.',
    },
    'D10_Kendra_malefics': {
        'title': 'Malefic Planets in Kendra (D10)',
        'description': 'Challenging planets (Mars, Saturn, Rahu, Ketu) in angular houses of D10 chart',
        'interpretation': 'These planets may cause obstacles, setbacks, or require extra effort during their Dasha periods. However, well-placed malefics can also give power and determination.',
    },
    'D10_10th_tatwa': {
        'title': '10th House Element (Tatwa)',
        'description': 'The elemental nature of the 10th house sign in D10 chart',
        'interpretation': 'Elements indicate career type:',
        'elements': {
            'fire': 'Fire - Leadership, authority, politics, administration',
            'earth': 'Earth - Practical fields, business, finance, construction',
            'air': 'Air - Communication, IT/Tech (analytical/system design), media, consulting, education, data science, networking',
            'water': 'Water - Creative fields, IT/Tech (creative/design-oriented), research, healing, spirituality, service, adaptable professions (Agile/DevOps)',
        },
    },
    'D1_10th_lord_in': {
        'title': '10th Lord Position',
        'description': 'The house where the lord of the 10th house is placed in D1 chart',
        'interpretation': 'Different house placements indicate different career paths and opportunities.',
    },
    'D10_10th_lord_transposition': {
        'title': '10th Lord Strength in D10',
        'description': 'The strength and position of 10th lord in the D10 career chart',
        'interpretation': 'Strong placement indicates excellent career prospects and professional success.',
    },
    'dharma_karma_yoga': {
        'title': 'Dharma-Karma Yoga',
        'description': 'Connection between 9th lord (dharma/higher purpose) and 10th lord (karma/career)',
        'interpretation': 'This yoga indicates a career aligned with your higher purpose, ethical success, and recognition.',
    },
    'Vargottama': {
        'title': 'Vargottama Planets',
        'description': 'Planets occupying the same sign in both D1 and D10 charts',
        'interpretation': 'Vargottama planets are exceptionally powerful for professional talents and skills.',
    },
}

# Score explanations
SCORE_EXPLANATIONS = {
    'd10_10th_rasi': 'D10 10th house sign strength (max 1.0)',
    'd1_10th_benefics': 'Benefic planets in D1 10th house (max 1.0 per planet)',
    'd1_10th_malefics': 'Malefic planets in D1 10th house (varies)',
    'd10_kendra_benefics': 'Benefics in D10 angular houses (0.75 max)',
    'd10_kendra_malefics': 'Malefics in D10 angular houses (0.3 max)',
    'd10_10th_tatwa': 'Element of D10 10th house (0.5)',
    'd1_10th_lord_2nd_3rd': '10th lord in 2nd/3rd house (0.8)',
    'd10_10th_lord_transposition': '10th lord strength in D10 (max 1.0)',
    'dharma_karma_yoga': '9th-10th lord connection (1.1)',
    'vargottama': 'Same sign in D1 and D10 (0.5 per planet)',
}


def parse_factor_code(factor: str) -> Dict[str, str]:
    """
    Parse a factor code and return structured information

    Args:
        factor: Factor code like "D10_10th_rasi_Meena" or "D1_planets_in_10th_Sun,Venus"

    Returns:
        Dictionary with title, description, interpretation, and value
    """
    parts = factor.split('_')

    # Find matching pattern
    matched_pattern = None
    pattern_key = None

    for key in FACTOR_PATTERNS.keys():
        if factor.startswith(key):
            matched_pattern = FACTOR_PATTERNS[key]
            pattern_key = key
            break

    if not matched_pattern:
        # Try partial match
        for key in FACTOR_PATTERNS.keys():
            if key in factor:
                matched_pattern = FACTOR_PATTERNS[key]
                pattern_key = key
                break

    if not matched_pattern:
        return {
            'title': factor.replace('_', ' ').title(),
            'description': 'Career strength factor',
            'interpretation': '',
            'value': '',
        }

    # Extract value from factor code
    value = ''
    if len(parts) > len(pattern_key.split('_')):
        value_parts = parts[len(pattern_key.split('_')):]
        value = ' '.join(value_parts)

    # Get specific interpretation for the value
    specific_interpretation = matched_pattern['interpretation']

    # Add sign-specific or element-specific interpretation
    if 'signs' in matched_pattern and value:
        for sign_key, sign_desc in matched_pattern['signs'].items():
            if sign_key in value:
                specific_interpretation = f"{matched_pattern['interpretation']}\n\n**{value}**: {sign_desc}"
                break

    if 'elements' in matched_pattern and value:
        for elem_key, elem_desc in matched_pattern['elements'].items():
            if elem_key in value.lower():
                specific_interpretation = f"{matched_pattern['interpretation']}\n\n**{value.title()}**: {elem_desc}"
                break

    return {
        'title': matched_pattern['title'],
        'description': matched_pattern['description'],
        'interpretation': specific_interpretation,
        'value': value.replace(',', ', ') if value else '',
        'raw_code': factor,
    }


def interpret_factors(factors: List[str]) -> List[Dict[str, str]]:
    """
    Convert a list of factor codes into interpretable information

    Args:
        factors: List of factor code strings

    Returns:
        List of dictionaries with factor interpretations
    """
    return [parse_factor_code(factor) for factor in factors]


def interpret_score(score_key: str, score_value: float) -> Dict[str, str]:
    """
    Interpret a score breakdown entry

    Args:
        score_key: Score key like "d10_10th_rasi"
        score_value: Numeric score value

    Returns:
        Dictionary with interpretation
    """
    explanation = SCORE_EXPLANATIONS.get(score_key, 'Career strength component')

    # Determine strength level
    if score_value >= 0.8:
        strength = 'Excellent'
        color = 'success'
    elif score_value >= 0.5:
        strength = 'Good'
        color = 'primary'
    elif score_value >= 0.3:
        strength = 'Moderate'
        color = 'warning'
    elif score_value > 0:
        strength = 'Present'
        color = 'info'
    else:
        strength = 'Weak'
        color = 'secondary'

    return {
        'key': score_key,
        'value': score_value,
        'explanation': explanation,
        'strength': strength,
        'color': color,
        'display_name': score_key.replace('_', ' ').title(),
    }


def interpret_scores(scores: Dict[str, float]) -> List[Dict[str, str]]:
    """
    Convert score breakdown into interpretable information

    Args:
        scores: Dictionary of score keys and values

    Returns:
        List of dictionaries with score interpretations
    """
    return [interpret_score(key, val) for key, val in scores.items()]


def get_factor_summary(factors: List[str], scores: Dict[str, float]) -> Dict[str, any]:
    """
    Get a comprehensive summary of factors and scores

    Args:
        factors: List of factor codes
        scores: Dictionary of scores

    Returns:
        Dictionary with interpreted factors, scores, and overall summary
    """
    interpreted_factors = interpret_factors(factors)
    interpreted_scores = interpret_scores(scores)

    # Calculate total score
    total_score = sum(scores.values())
    max_possible = len(scores) * 1.0  # Rough estimate
    percentage = (total_score / max_possible * 100) if max_possible > 0 else 0

    # Overall assessment
    if percentage >= 70:
        overall = 'Excellent career potential'
    elif percentage >= 50:
        overall = 'Good career prospects'
    elif percentage >= 30:
        overall = 'Moderate career strength'
    else:
        overall = 'Developing career indicators'

    return {
        'factors': interpreted_factors,
        'scores': interpreted_scores,
        'total_score': round(total_score, 2),
        'percentage': round(percentage, 1),
        'overall_assessment': overall,
    }
