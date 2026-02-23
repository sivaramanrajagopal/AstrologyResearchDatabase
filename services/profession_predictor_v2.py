"""
Enhanced Profession Probability Predictor V2
Analyzes D1 + D10 charts with proper yoga detection and nakshatra analysis
Based on Vedic astrology principles with modern profession mapping
"""

from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict


# Modern profession mapping with classical indicators
PROFESSION_CATEGORIES = {
    'Technology/IT/Software': {
        'description': 'Software, IT, Engineering, Data Science, AI/ML, Tech CEO',
        'primary_planets': ['Mercury', 'Rahu', 'Saturn', 'Mars'],
        'secondary_planets': ['Jupiter', 'Venus'],
        'signs': ['Gemini', 'Virgo', 'Aquarius', 'Scorpio', 'Mithuna', 'Kanya', 'Kumbha', 'Vrischika', 'Vrishchika'],
        'nakshatras': ['Ashlesha', 'Jyeshtha', 'Revati', 'Shatabhisha', 'Swati', 'Mrigashira', 'Punarvasu', 'Chitra'],
        'houses': [3, 5, 6, 9, 10, 11],
        'combinations': [
            {'planets': ['Mercury', 'Jupiter'], 'bonus': 30, 'name': 'Tech Business Leadership Yoga'},
            {'planets': ['Mercury', 'Mars'], 'bonus': 30, 'name': 'Tech Engineering Yoga'},
            {'planets': ['Mars', 'Venus'], 'bonus': 25, 'name': 'Tech Design/UX Yoga'},
            {'planets': ['Mercury', 'Venus'], 'bonus': 25, 'name': 'Creative Tech/Design Yoga'},
            {'planets': ['Mercury', 'Rahu'], 'bonus': 25, 'name': 'Tech Innovation Yoga'},
            {'planets': ['Mercury', 'Saturn'], 'bonus': 20, 'name': 'Systematic Tech Yoga'},
        ],
    },
    'Business/Corporate Leadership': {
        'description': 'CEO, Business Management, Entrepreneurship, Corporate',
        'primary_planets': ['Sun', 'Mercury', 'Jupiter'],
        'secondary_planets': ['Venus', 'Mars'],
        'signs': ['Leo', 'Sagittarius', 'Capricorn', 'Simha', 'Dhanus', 'Makara'],
        'nakshatras': ['Pushya', 'Uttara Phalguni', 'Uttara Ashadha', 'Ashlesha', 'Rohini'],
        'houses': [1, 2, 7, 10, 11],
        'combinations': [
            {'planets': ['Sun', 'Mercury'], 'bonus': 30, 'name': 'Budha-Aditya Yoga (Leadership)'},
            {'planets': ['Mercury', 'Jupiter'], 'bonus': 35, 'name': 'Budha-Guru Yoga (Business Wisdom)'},
            {'planets': ['Sun', 'Jupiter'], 'bonus': 25, 'name': 'Guru-Aditya Yoga (Authority)'},
        ],
    },
    'Finance/Banking/Investment': {
        'description': 'Banking, Finance, Investment, Accounting, Stock Market',
        'primary_planets': ['Venus', 'Jupiter', 'Mercury'],
        'secondary_planets': ['Moon'],
        'signs': ['Taurus', 'Libra', 'Sagittarius', 'Rishaba', 'Tula', 'Dhanus'],
        'nakshatras': ['Rohini', 'Pushya', 'Uttara Phalguni', 'Purva Bhadrapada'],
        'houses': [2, 5, 9, 10, 11],
        'combinations': [
            {'planets': ['Venus', 'Jupiter'], 'bonus': 30, 'name': 'Lakshmi Yoga (Wealth)'},
            {'planets': ['Mercury', 'Jupiter'], 'bonus': 25, 'name': 'Financial Wisdom Yoga'},
        ],
    },
    'Government/Administration/Politics': {
        'description': 'Government Service, Politics, Public Administration, IAS/IPS',
        'primary_planets': ['Sun', 'Saturn', 'Jupiter'],
        'secondary_planets': ['Mars', 'Rahu'],
        'signs': ['Leo', 'Capricorn', 'Sagittarius', 'Simha', 'Makara', 'Dhanus'],
        'nakshatras': ['Krittika', 'Magha', 'Uttara Phalguni', 'Uttara Ashadha', 'Uttara Bhadrapada'],
        'houses': [1, 6, 9, 10],
        'combinations': [
            {'planets': ['Sun', 'Saturn'], 'bonus': 25, 'name': 'Administrative Yoga'},
            {'planets': ['Sun', 'Rahu'], 'bonus': 30, 'name': 'Political Power Yoga'},
        ],
    },
    'Medicine/Healthcare': {
        'description': 'Doctor, Healthcare, Medicine, Surgery, Nursing',
        'primary_planets': ['Moon', 'Ketu', 'Mars'],
        'secondary_planets': ['Jupiter', 'Venus'],
        'signs': ['Cancer', 'Scorpio', 'Pisces', 'Virgo', 'Kataka', 'Vrishchika', 'Meena', 'Kanya'],
        'nakshatras': ['Ashwini', 'Rohini', 'Ardra', 'Pushya', 'Hasta'],
        'houses': [6, 8, 10, 12],
        'combinations': [
            {'planets': ['Moon', 'Mars'], 'bonus': 25, 'name': 'Surgeon Yoga'},
            {'planets': ['Moon', 'Ketu'], 'bonus': 20, 'name': 'Healer Yoga'},
        ],
    },
    'Teaching/Education/Research': {
        'description': 'Professor, Teacher, Academic Research, Training',
        'primary_planets': ['Jupiter', 'Mercury'],
        'secondary_planets': ['Moon'],
        'signs': ['Sagittarius', 'Pisces', 'Gemini', 'Dhanus', 'Meena', 'Mithuna'],
        'nakshatras': ['Punarvasu', 'Vishakha', 'Purva Bhadrapada', 'Revati'],
        'houses': [4, 5, 9, 10],
        'combinations': [
            {'planets': ['Jupiter', 'Moon'], 'bonus': 25, 'name': 'Gajakesari Yoga (Teacher)'},
            {'planets': ['Jupiter', 'Mercury'], 'bonus': -15, 'name': 'Business over Teaching'},  # Negative when teaching context
        ],
    },
    'Arts/Media/Entertainment': {
        'description': 'Acting, Music, Writing, Media, Journalism, Creative Arts',
        'primary_planets': ['Venus', 'Moon', 'Mercury'],
        'secondary_planets': ['Rahu'],
        'signs': ['Taurus', 'Libra', 'Pisces', 'Cancer', 'Rishaba', 'Tula', 'Meena', 'Kataka'],
        'nakshatras': ['Bharani', 'Rohini', 'Purva Phalguni', 'Revati', 'Ashwini'],
        'houses': [3, 5, 10, 11],
        'combinations': [
            {'planets': ['Venus', 'Moon'], 'bonus': 30, 'name': 'Creative Arts Yoga'},
            {'planets': ['Venus', 'Rahu'], 'bonus': 25, 'name': 'Fame/Cinema Yoga'},
        ],
    },
    'Law/Judiciary': {
        'description': 'Lawyer, Judge, Legal Services, Court',
        'primary_planets': ['Jupiter', 'Saturn', 'Sun'],
        'secondary_planets': ['Mercury'],
        'signs': ['Sagittarius', 'Capricorn', 'Libra', 'Dhanus', 'Makara', 'Tula'],
        'nakshatras': ['Uttara Ashadha', 'Uttara Bhadrapada', 'Pushya', 'Swati'],
        'houses': [6, 7, 9, 10],
        'combinations': [
            {'planets': ['Jupiter', 'Saturn'], 'bonus': 30, 'name': 'Justice Yoga'},
        ],
    },
    'Sales/Marketing/Communication': {
        'description': 'Sales, Marketing, PR, Communication, Consulting',
        'primary_planets': ['Mercury', 'Venus', 'Moon'],
        'secondary_planets': ['Jupiter'],
        'signs': ['Gemini', 'Virgo', 'Libra', 'Mithuna', 'Kanya', 'Tula'],
        'nakshatras': ['Ashlesha', 'Jyeshtha', 'Mrigashira', 'Ardra'],
        'houses': [2, 3, 7, 10, 11],
        'combinations': [
            {'planets': ['Mercury', 'Venus'], 'bonus': 25, 'name': 'Communication Excellence Yoga'},
        ],
    },
    'Sports/Military/Defense': {
        'description': 'Sports, Military, Police, Defense, Athletics',
        'primary_planets': ['Mars', 'Sun'],
        'secondary_planets': ['Saturn', 'Ketu'],
        'signs': ['Aries', 'Scorpio', 'Leo', 'Mesha', 'Vrishchika', 'Simha'],
        'nakshatras': ['Mrigashira', 'Ardra', 'Magha', 'Moola', 'Dhanishta'],
        'houses': [1, 3, 6, 10],
        'combinations': [
            {'planets': ['Mars', 'Sun'], 'bonus': 35, 'name': 'Warrior Yoga'},
        ],
    },
}


def normalize_sign_name(sign: str) -> str:
    """Normalize sign names to English"""
    sign_map = {
        'Mesha': 'Aries', 'Rishaba': 'Taurus', 'Mithuna': 'Gemini',
        'Kataka': 'Cancer', 'Simha': 'Leo', 'Kanya': 'Virgo',
        'Tula': 'Libra',
        'Vrishchika': 'Scorpio', 'Vrischika': 'Scorpio',  # Handle both spellings
        'Dhanus': 'Sagittarius',
        'Makara': 'Capricorn', 'Kumbha': 'Aquarius', 'Meena': 'Pisces',
    }
    return sign_map.get(sign, sign)


def get_planet_house(chart_data: Dict[str, Any], planet: str) -> Optional[int]:
    """Get which house a planet is in"""
    planet_rasi = chart_data.get(f'{planet.lower()}_rasi', '')
    if not planet_rasi:
        return None

    planet_rasi = normalize_sign_name(planet_rasi)

    # Find which house has this rasi
    for house_num in range(1, 13):
        house_rasi = chart_data.get(f'house_{house_num}_rasi', '')
        house_rasi = normalize_sign_name(house_rasi)
        if house_rasi == planet_rasi:
            return house_num

    return None


def get_planets_in_house(chart_data: Dict[str, Any], house_num: int) -> List[str]:
    """Get all planets in a specific house"""
    house_rasi = chart_data.get(f'house_{house_num}_rasi', '')
    if not house_rasi:
        return []

    house_rasi = normalize_sign_name(house_rasi)
    planets = []

    for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
        planet_rasi = chart_data.get(f'{planet.lower()}_rasi', '')
        planet_rasi = normalize_sign_name(planet_rasi)
        if planet_rasi == house_rasi:
            planets.append(planet)

    return planets


def detect_yogas(planets_in_10th: List[str], planets_with_tenth_lord: List[str], tenth_lord: str, profession_category: Dict) -> Tuple[int, List[str]]:
    """Detect special planetary combinations (yogas) for profession"""
    bonus_score = 0
    detected_yogas = []

    # Check combinations in 10th house
    for combo in profession_category.get('combinations', []):
        required_planets = combo['planets']
        if all(planet in planets_in_10th for planet in required_planets):
            bonus_score += combo['bonus']
            detected_yogas.append(combo['name'])

    # Also check combinations with 10th lord (important for empty 10th houses!)
    if tenth_lord and planets_with_tenth_lord:
        all_relevant_planets = [tenth_lord] + planets_with_tenth_lord
        for combo in profession_category.get('combinations', []):
            required_planets = combo['planets']
            if all(planet in all_relevant_planets for planet in required_planets):
                # Only add if not already detected in 10th house
                if combo['name'] not in detected_yogas:
                    bonus_score += combo['bonus']
                    detected_yogas.append(f"{combo['name']} (10th lord)")

    return bonus_score, detected_yogas


def calculate_profession_probabilities_v2(chart_data: Dict[str, Any]) -> List[Tuple[str, float, List[str]]]:
    """
    Enhanced profession probability calculator using D1 + D10 analysis

    Returns:
        List of (profession_name, probability_percentage, reasons) sorted by probability
    """
    profession_scores = defaultdict(lambda: {'score': 0.0, 'reasons': []})

    # Get 10th house planets
    planets_in_10th = get_planets_in_house(chart_data, 10)
    tenth_house_rasi = normalize_sign_name(chart_data.get('house_10_rasi', ''))
    tenth_house_nakshatra = chart_data.get('house_10_nakshatra', '')

    # Get 10th lord and its position
    tenth_lord = chart_data.get('tenth_lord', '')
    if not tenth_lord:
        # Calculate 10th lord from 10th house rasi
        lords = {
            'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
            'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
            'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
            'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
        }
        tenth_lord = lords.get(tenth_house_rasi, '')

    tenth_lord_nakshatra = chart_data.get(f'{tenth_lord.lower()}_nakshatra', '') if tenth_lord else ''
    tenth_lord_house = get_planet_house(chart_data, tenth_lord) if tenth_lord else None
    tenth_lord_rasi = normalize_sign_name(chart_data.get(f'{tenth_lord.lower()}_rasi', '')) if tenth_lord else ''

    # Get planets conjunct with 10th lord (IMPORTANT for empty 10th houses!)
    planets_with_tenth_lord = []
    if tenth_lord and tenth_lord_rasi:
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            if planet != tenth_lord:
                planet_rasi = normalize_sign_name(chart_data.get(f'{planet.lower()}_rasi', ''))
                if planet_rasi == tenth_lord_rasi:
                    planets_with_tenth_lord.append(planet)

    # Analyze each profession category
    for profession, indicators in PROFESSION_CATEGORIES.items():
        score = 0.0
        reasons = []

        # 1. Check for special yogas (combinations) - HIGH PRIORITY
        yoga_bonus, detected_yogas = detect_yogas(planets_in_10th, planets_with_tenth_lord, tenth_lord, indicators)
        if yoga_bonus > 0:
            score += yoga_bonus
            for yoga in detected_yogas:
                reasons.append(f"✨ {yoga} (+{yoga_bonus}%)")
        elif yoga_bonus < 0:  # Negative yoga (reduces probability)
            score += yoga_bonus
            reasons.append(f"⚠️ {detected_yogas[0]} ({yoga_bonus}%)")

        # 2. Primary planets in 10th house - HIGHEST WEIGHT
        for planet in planets_in_10th:
            if planet in indicators['primary_planets']:
                planet_score = 30
                score += planet_score
                reasons.append(f"{planet} in 10th (primary) (+{planet_score}%)")
            elif planet in indicators['secondary_planets']:
                planet_score = 15
                score += planet_score
                reasons.append(f"{planet} in 10th (secondary) (+{planet_score}%)")

        # 3. 10th house sign
        if tenth_house_rasi in indicators['signs']:
            sign_score = 20
            score += sign_score
            reasons.append(f"10th in {tenth_house_rasi} (+{sign_score}%)")

        # 4. Nakshatra influences
        relevant_nakshatras = [n for n in [tenth_lord_nakshatra, tenth_house_nakshatra] if n]
        for nak in relevant_nakshatras:
            if nak in indicators['nakshatras']:
                nak_score = 15
                score += nak_score
                reasons.append(f"Nakshatra {nak} (+{nak_score}%)")
                break  # Count only once

        # 5. 10th lord as primary/secondary planet (HIGHER WEIGHT for empty 10th houses)
        if tenth_lord and tenth_lord in indicators['primary_planets']:
            lord_score = 25
            score += lord_score
            reasons.append(f"{tenth_lord} as 10th lord (+{lord_score}%)")
        elif tenth_lord and tenth_lord in indicators['secondary_planets']:
            lord_score = 15
            score += lord_score
            reasons.append(f"{tenth_lord} as 10th lord (+{lord_score}%)")

        # 6. 10th lord in profession-relevant sign
        if tenth_lord_rasi in indicators['signs']:
            lord_sign_score = 20
            score += lord_sign_score
            reasons.append(f"10th lord in {tenth_lord_rasi} (+{lord_sign_score}%)")

        # 7. Planets conjunct with 10th lord (VERY IMPORTANT!)
        for planet in planets_with_tenth_lord:
            if planet in indicators['primary_planets']:
                conj_score = 25
                score += conj_score
                reasons.append(f"{planet} with 10th lord (+{conj_score}%)")
            elif planet in indicators['secondary_planets']:
                conj_score = 15
                score += conj_score
                reasons.append(f"{planet} with 10th lord (+{conj_score}%)")

        # 8. 10th lord house position (strength indicator)
        if tenth_lord_house and tenth_lord_house in [1, 2, 4, 5, 7, 9, 10, 11]:
            # Good houses for 10th lord
            house_bonus = 10
            score += house_bonus
            reasons.append(f"10th lord in {tenth_lord_house}th house (+{house_bonus}%)")

        # Store results
        profession_scores[profession]['score'] = min(score, 100.0)  # Cap at 100%
        profession_scores[profession]['reasons'] = reasons[:4]  # Top 4 reasons

    # Sort by score
    results = [
        (profession, data['score'], data['reasons'])
        for profession, data in profession_scores.items()
    ]
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def get_profession_summary_v2(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive profession prediction summary (V2 - Enhanced)

    Returns:
        Dictionary with top professions, probabilities, and explanations
    """
    probabilities = calculate_profession_probabilities_v2(chart_data)

    # Get top 5 professions
    top_professions = probabilities[:5]

    # Calculate overall career strength
    top_score = top_professions[0][1] if top_professions else 0
    if top_score >= 70:
        career_strength = 'Excellent'
        strength_color = 'success'
    elif top_score >= 50:
        career_strength = 'Good'
        strength_color = 'primary'
    elif top_score >= 30:
        career_strength = 'Moderate'
        strength_color = 'warning'
    else:
        career_strength = 'Developing'
        strength_color = 'danger'

    # Get profession description
    top_profession_desc = PROFESSION_CATEGORIES[top_professions[0][0]]['description'] if top_professions else ''

    return {
        'top_professions': [
            {
                'name': prof,
                'description': PROFESSION_CATEGORIES[prof]['description'],
                'probability': round(prob, 1),
                'reasons': reasons[:3],  # Top 3 reasons
            }
            for prof, prob, reasons in top_professions
        ],
        'career_strength': career_strength,
        'strength_color': strength_color,
        'top_probability': round(top_professions[0][1], 1) if top_professions else 0,
        'top_profession_desc': top_profession_desc,
        'all_professions': [
            {'name': prof, 'probability': round(prob, 1)}
            for prof, prob, _ in probabilities
        ],
    }
