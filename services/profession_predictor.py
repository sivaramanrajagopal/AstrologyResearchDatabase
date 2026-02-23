"""
Profession Probability Predictor
Analyzes birth chart to predict suitable professions with probability percentages
Based on Vedic astrology principles
"""

from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict


# Profession categories and their planetary/sign indicators
PROFESSION_INDICATORS = {
    'Technology/IT/Engineering': {
        'planets': {
            'Mercury': 30,  # Logic, communication, analytical
            'Rahu': 25,     # Modern technology, innovation
            'Saturn': 20,   # Systematic, structured work
            'Mars': 15,     # Engineering, technical
        },
        'signs': {
            'Gemini': 25, 'Virgo': 25, 'Aquarius': 20, 'Capricorn': 15,
        },
        'nakshatras': {
            'Ashlesha': 15, 'Jyeshtha': 15, 'Revati': 15, 'Shatabhisha': 20,
        },
        'tatwa': {'Air': 25, 'Earth': 15},
        'houses': [3, 6, 10, 11],  # Communication, service, career, gains
    },
    'Business/Finance/Management': {
        'planets': {
            'Venus': 25,    # Business acumen, luxury goods
            'Jupiter': 25,  # Expansion, banking, advisory
            'Mercury': 20,  # Trade, commerce
            'Sun': 15,      # Leadership, management
        },
        'signs': {
            'Taurus': 25, 'Libra': 20, 'Sagittarius': 20, 'Capricorn': 20,
        },
        'nakshatras': {
            'Rohini': 20, 'Pushya': 20, 'Uttara Phalguni': 15, 'Uttara Ashadha': 15,
        },
        'tatwa': {'Earth': 30, 'Fire': 15},
        'houses': [2, 7, 10, 11],  # Wealth, partnerships, career, gains
    },
    'Government/Law/Administration': {
        'planets': {
            'Sun': 30,      # Authority, government
            'Saturn': 25,   # Law, discipline, administration
            'Jupiter': 20,  # Justice, law, advisory
            'Mars': 15,     # Executive power
        },
        'signs': {
            'Leo': 30, 'Capricorn': 25, 'Sagittarius': 20, 'Aries': 15,
        },
        'nakshatras': {
            'Krittika': 20, 'Magha': 25, 'Uttara Phalguni': 15, 'Uttara Bhadrapada': 15,
        },
        'tatwa': {'Fire': 30, 'Earth': 20},
        'houses': [1, 9, 10],  # Self, dharma, authority
    },
    'Medicine/Healthcare/Healing': {
        'planets': {
            'Moon': 25,     # Healing, nurturing, medicine
            'Ketu': 25,     # Spirituality, alternative medicine
            'Jupiter': 20,  # Wisdom, guidance
            'Venus': 15,    # Comfort, care
        },
        'signs': {
            'Cancer': 25, 'Scorpio': 25, 'Pisces': 20, 'Virgo': 20,
        },
        'nakshatras': {
            'Ashwini': 30, 'Rohini': 20, 'Ardra': 15, 'Pushya': 20,
        },
        'tatwa': {'Water': 30, 'Earth': 15},
        'houses': [6, 8, 12],  # Health, transformation, loss/healing
    },
    'Teaching/Academia/Research': {
        'planets': {
            'Jupiter': 35,  # Teacher, wisdom, knowledge
            'Mercury': 25,  # Communication, learning
            'Moon': 15,     # Nurturing, education
            'Ketu': 15,     # Research, deep knowledge
        },
        'signs': {
            'Sagittarius': 30, 'Pisces': 25, 'Gemini': 20, 'Virgo': 15,
        },
        'nakshatras': {
            'Punarvasu': 25, 'Vishakha': 20, 'Purva Bhadrapada': 20, 'Revati': 20,
        },
        'tatwa': {'Fire': 25, 'Water': 20},
        'houses': [4, 5, 9],  # Learning, intelligence, higher knowledge
    },
    'Arts/Entertainment/Creative': {
        'planets': {
            'Venus': 35,    # Arts, beauty, entertainment
            'Moon': 25,     # Creativity, imagination
            'Mercury': 20,  # Communication, writing
            'Rahu': 15,     # Glamour, cinema, fame
        },
        'signs': {
            'Taurus': 25, 'Libra': 25, 'Pisces': 25, 'Cancer': 15,
        },
        'nakshatras': {
            'Bharani': 25, 'Rohini': 25, 'Purva Phalguni': 25, 'Revati': 20,
        },
        'tatwa': {'Water': 30, 'Earth': 20},
        'houses': [3, 5, 10, 11],  # Communication, creativity, profession, gains
    },
    'Sports/Military/Physical': {
        'planets': {
            'Mars': 40,     # Strength, aggression, sports
            'Sun': 25,      # Vitality, leadership
            'Saturn': 20,   # Discipline, endurance
            'Ketu': 10,     # Martial arts
        },
        'signs': {
            'Aries': 30, 'Scorpio': 25, 'Leo': 20, 'Capricorn': 15,
        },
        'nakshatras': {
            'Mrigashira': 20, 'Ardra': 20, 'Magha': 20, 'Moola': 20,
        },
        'tatwa': {'Fire': 35, 'Water': 15},
        'houses': [1, 3, 6, 10],  # Self, courage, competition, profession
    },
}


def get_tatwa(rasi: str) -> str:
    """Get element (tatwa) for a rasi"""
    fire_signs = ['Aries', 'Leo', 'Sagittarius', 'Mesha', 'Simha', 'Dhanus']
    earth_signs = ['Taurus', 'Virgo', 'Capricorn', 'Rishaba', 'Kanya', 'Makara']
    air_signs = ['Gemini', 'Libra', 'Aquarius', 'Mithuna', 'Tula', 'Kumbha']
    water_signs = ['Cancer', 'Scorpio', 'Pisces', 'Kataka', 'Vrishchika', 'Meena']

    if rasi in fire_signs:
        return 'Fire'
    elif rasi in earth_signs:
        return 'Earth'
    elif rasi in air_signs:
        return 'Air'
    elif rasi in water_signs:
        return 'Water'
    return 'Unknown'


def normalize_sign_name(sign: str) -> str:
    """Normalize sign names to English"""
    sign_map = {
        'Mesha': 'Aries', 'Rishaba': 'Taurus', 'Mithuna': 'Gemini',
        'Kataka': 'Cancer', 'Simha': 'Leo', 'Kanya': 'Virgo',
        'Tula': 'Libra', 'Vrishchika': 'Scorpio', 'Dhanus': 'Sagittarius',
        'Makara': 'Capricorn', 'Kumbha': 'Aquarius', 'Meena': 'Pisces',
    }
    return sign_map.get(sign, sign)


def calculate_profession_probabilities(chart_data: Dict[str, Any]) -> List[Tuple[str, float, List[str]]]:
    """
    Calculate probability percentages for different professions based on chart analysis

    Returns:
        List of (profession_name, probability_percentage, reasons) sorted by probability
    """
    profession_scores = defaultdict(lambda: {'score': 0.0, 'reasons': []})

    # Get 10th house information
    tenth_house_rasi = chart_data.get('house_10_rasi', '')
    tenth_house_rasi = normalize_sign_name(tenth_house_rasi)
    tenth_house_tatwa = get_tatwa(tenth_house_rasi)

    # Get 10th lord information
    tenth_lord = chart_data.get('tenth_lord', '')
    tenth_lord_rasi = chart_data.get(f'{tenth_lord.lower()}_rasi', '') if tenth_lord else ''
    tenth_lord_rasi = normalize_sign_name(tenth_lord_rasi)
    tenth_lord_nakshatra = chart_data.get(f'{tenth_lord.lower()}_nakshatra', '') if tenth_lord else ''

    # Analyze each profession
    for profession, indicators in PROFESSION_INDICATORS.items():
        score = 0.0
        reasons = []

        # Check planets in 10th house
        planets_in_10th = []
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']:
            planet_house = get_planet_house(chart_data, planet)
            if planet_house == 10:
                planets_in_10th.append(planet)
                if planet in indicators['planets']:
                    planet_score = indicators['planets'][planet]
                    score += planet_score
                    reasons.append(f"{planet} in 10th house (+{planet_score}%)")

        # Check 10th house sign
        if tenth_house_rasi in indicators['signs']:
            sign_score = indicators['signs'][tenth_house_rasi]
            score += sign_score
            reasons.append(f"10th house in {tenth_house_rasi} (+{sign_score}%)")

        # Check 10th house tatwa (element)
        if tenth_house_tatwa in indicators.get('tatwa', {}):
            tatwa_score = indicators['tatwa'][tenth_house_tatwa]
            score += tatwa_score
            reasons.append(f"10th house element: {tenth_house_tatwa} (+{tatwa_score}%)")

        # Check 10th lord sign
        if tenth_lord and tenth_lord in indicators['planets']:
            lord_score = indicators['planets'][tenth_lord] * 0.8  # Slightly less weight than direct placement
            score += lord_score
            reasons.append(f"{tenth_lord} as 10th lord (+{lord_score:.0f}%)")

        # Check 10th lord nakshatra
        if tenth_lord_nakshatra in indicators.get('nakshatras', {}):
            nak_score = indicators['nakshatras'][tenth_lord_nakshatra]
            score += nak_score
            reasons.append(f"10th lord in {tenth_lord_nakshatra} nakshatra (+{nak_score}%)")

        # Check ascendant lord position
        asc_rasi = chart_data.get('ascendant_rasi', '')
        asc_lord = get_rasi_lord(asc_rasi)
        if asc_lord:
            asc_lord_house = get_planet_house(chart_data, asc_lord)
            # If ascendant lord in profession-relevant houses
            if asc_lord_house in indicators.get('houses', []):
                score += 10
                reasons.append(f"Ascendant lord in {asc_lord_house}th house (+10%)")

        # Store results
        profession_scores[profession]['score'] = min(score, 100.0)  # Cap at 100%
        profession_scores[profession]['reasons'] = reasons

    # Sort by score and return top professions
    results = [
        (profession, data['score'], data['reasons'])
        for profession, data in profession_scores.items()
    ]
    results.sort(key=lambda x: x[1], reverse=True)

    # Normalize probabilities to sum to reasonable total (allow some professions to have low scores)
    return results


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


def get_rasi_lord(rasi: str) -> Optional[str]:
    """Get the lord of a rasi"""
    rasi = normalize_sign_name(rasi)

    lords = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
    }

    return lords.get(rasi)


def get_profession_summary(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a comprehensive profession prediction summary

    Returns:
        Dictionary with top professions, probabilities, and explanations
    """
    probabilities = calculate_profession_probabilities(chart_data)

    # Get top 5 professions
    top_professions = probabilities[:5]

    # Calculate overall career strength indicator
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
        career_strength = 'Challenging'
        strength_color = 'danger'

    return {
        'top_professions': [
            {
                'name': prof,
                'probability': round(prob, 1),
                'reasons': reasons[:3],  # Top 3 reasons
            }
            for prof, prob, reasons in top_professions
        ],
        'career_strength': career_strength,
        'strength_color': strength_color,
        'top_probability': round(top_professions[0][1], 1) if top_professions else 0,
        'all_professions': [
            {'name': prof, 'probability': round(prob, 1)}
            for prof, prob, _ in probabilities
        ],
    }
