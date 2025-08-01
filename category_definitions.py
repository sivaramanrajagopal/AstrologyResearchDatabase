#!/usr/bin/env python3
"""
Simplified Category Definitions for Global Astrology Database
Reduced to 10-15 key categories for better usability
"""

# Primary Categories (10 key areas)
PRIMARY_CATEGORIES = {
    'career': 'Career & Business',
    'health': 'Health & Medical',
    'relationships': 'Relationships & Marriage',
    'education': 'Education & Learning',
    'financial': 'Financial & Wealth',
    'travel': 'Travel & Migration',
    'spiritual': 'Spiritual & Religious',
    'legal': 'Legal & Justice',
    'sports': 'Sports & Athletics',
    'creative': 'Creative Arts'
}

# Sub Categories (simplified to 10-15 per primary)
SUB_CATEGORIES = {
    'career': {
        'job_change': 'Job Change',
        'promotion': 'Promotion',
        'business_start': 'Starting Business',
        'career_advancement': 'Career Advancement',
        'workplace_conflict': 'Workplace Conflict',
        'entrepreneurship': 'Entrepreneurship',
        'job_loss': 'Job Loss',
        'career_switch': 'Career Switch',
        'leadership': 'Leadership Role',
        'partnership': 'Business Partnership',
        'government_job': 'Government Job',
        'teaching': 'Teaching',
        'police': 'Police Service',
        'civil_services': 'Civil Services',
        'medical_profession': 'Medical Profession',
        'legal_profession': 'Legal Profession',
        'engineering': 'Engineering',
        'it_software': 'IT & Software',
        'sales_marketing': 'Sales & Marketing',
        'consulting': 'Consulting'
    },
    'health': {
        'mental_health': 'Mental Health',
        'physical_illness': 'Physical Illness',
        'surgery': 'Surgery',
        'recovery': 'Recovery',
        'preventive': 'Preventive Care',
        'chronic_condition': 'Chronic Condition',
        'emergency': 'Medical Emergency',
        'diagnosis': 'Diagnosis',
        'treatment': 'Treatment',
        'wellness': 'General Wellness',
        'dental': 'Dental Health',
        'vision': 'Vision Problems',
        'cardiology': 'Cardiology',
        'neurology': 'Neurology',
        'orthopedics': 'Orthopedics'
    },
    'relationships': {
        'marriage': 'Marriage',
        'divorce': 'Divorce',
        'dating': 'Dating',
        'family_conflict': 'Family Conflict',
        'friendship': 'Friendship',
        'romance': 'Romance',
        'partnership': 'Partnership',
        'reconciliation': 'Reconciliation',
        'separation': 'Separation',
        'new_relationship': 'New Relationship',
        'parenting': 'Parenting',
        'sibling_relationship': 'Sibling Relationship',
        'extended_family': 'Extended Family',
        'work_relationship': 'Work Relationship',
        'social_network': 'Social Network'
    },
    'education': {
        'academic_performance': 'Academic Performance',
        'college_admission': 'College Admission',
        'exam_results': 'Exam Results',
        'study_abroad': 'Study Abroad',
        'skill_development': 'Skill Development',
        'certification': 'Certification',
        'research': 'Research',
        'graduation': 'Graduation',
        'learning_disability': 'Learning Disability',
        'career_training': 'Career Training',
        'competitive_exams': 'Competitive Exams',
        'entrance_tests': 'Entrance Tests',
        'scholarship': 'Scholarship',
        'online_learning': 'Online Learning',
        'vocational_training': 'Vocational Training'
    },
    'financial': {
        'investment': 'Investment',
        'property': 'Property',
        'debt': 'Debt',
        'inheritance': 'Inheritance',
        'business_finance': 'Business Finance',
        'savings': 'Savings',
        'insurance': 'Insurance',
        'tax': 'Tax Issues',
        'financial_loss': 'Financial Loss',
        'wealth_creation': 'Wealth Creation',
        'stock_market': 'Stock Market',
        'real_estate': 'Real Estate',
        'mutual_funds': 'Mutual Funds',
        'gold_investment': 'Gold Investment',
        'cryptocurrency': 'Cryptocurrency'
    },
    'travel': {
        'international_travel': 'International Travel',
        'domestic_travel': 'Domestic Travel',
        'migration': 'Migration',
        'visa': 'Visa Issues',
        'travel_planning': 'Travel Planning',
        'travel_delays': 'Travel Delays',
        'business_travel': 'Business Travel',
        'vacation': 'Vacation',
        'relocation': 'Relocation',
        'travel_emergency': 'Travel Emergency',
        'pilgrimage': 'Pilgrimage',
        'study_travel': 'Study Travel',
        'medical_travel': 'Medical Travel',
        'adventure_travel': 'Adventure Travel',
        'luxury_travel': 'Luxury Travel'
    },
    'spiritual': {
        'meditation': 'Meditation',
        'religious_practice': 'Religious Practice',
        'spiritual_awakening': 'Spiritual Awakening',
        'guru_guidance': 'Guru Guidance',
        'pilgrimage': 'Pilgrimage',
        'spiritual_healing': 'Spiritual Healing',
        'karma': 'Karma',
        'dharma': 'Dharma',
        'moksha': 'Moksha',
        'spiritual_growth': 'Spiritual Growth',
        'yoga': 'Yoga',
        'prayer': 'Prayer',
        'rituals': 'Rituals',
        'astrology_study': 'Astrology Study',
        'numerology': 'Numerology'
    },
    'legal': {
        'court_case': 'Court Case',
        'contract': 'Contract',
        'litigation': 'Litigation',
        'legal_advice': 'Legal Advice',
        'property_dispute': 'Property Dispute',
        'criminal_case': 'Criminal Case',
        'civil_case': 'Civil Case',
        'legal_document': 'Legal Document',
        'settlement': 'Settlement',
        'appeal': 'Appeal',
        'divorce_proceedings': 'Divorce Proceedings',
        'immigration': 'Immigration',
        'patent': 'Patent',
        'copyright': 'Copyright',
        'bankruptcy': 'Bankruptcy'
    },
    'sports': {
        'competition': 'Competition',
        'training': 'Training',
        'injury': 'Sports Injury',
        'performance': 'Performance',
        'team_selection': 'Team Selection',
        'coaching': 'Coaching',
        'fitness': 'Fitness',
        'recovery': 'Recovery',
        'achievement': 'Achievement',
        'career_sports': 'Sports Career',
        'olympics': 'Olympics',
        'championship': 'Championship',
        'individual_sports': 'Individual Sports',
        'team_sports': 'Team Sports',
        'fitness_training': 'Fitness Training'
    },
    'creative': {
        'art': 'Art',
        'music': 'Music',
        'writing': 'Writing',
        'acting': 'Acting',
        'design': 'Design',
        'photography': 'Photography',
        'dance': 'Dance',
        'craft': 'Craft',
        'performance': 'Performance',
        'creative_project': 'Creative Project',
        'film': 'Film',
        'theater': 'Theater',
        'poetry': 'Poetry',
        'sculpture': 'Sculpture',
        'digital_art': 'Digital Art'
    }
}

# Specific Conditions (comprehensive for all sub-categories)
SPECIFIC_CONDITIONS = {
    # Career specific conditions
    'job_change': {
        'successful': 'Successful Change',
        'challenging': 'Challenging Transition',
        'unexpected': 'Unexpected Change',
        'planned': 'Planned Change',
        'forced': 'Forced Change'
    },
    'promotion': {
        'achieved': 'Promotion Achieved',
        'denied': 'Promotion Denied',
        'delayed': 'Promotion Delayed',
        'expected': 'Expected Promotion',
        'unexpected': 'Unexpected Promotion'
    },
    'government_job': {
        'ias': 'IAS (Indian Administrative Service)',
        'ips': 'IPS (Indian Police Service)',
        'ifs': 'IFS (Indian Foreign Service)',
        'irs': 'IRS (Indian Revenue Service)',
        'banking': 'Banking Officer',
        'railway': 'Railway Service',
        'postal': 'Postal Service',
        'customs': 'Customs Service',
        'defense': 'Defense Service',
        'teaching': 'Government Teaching'
    },
    'teaching': {
        'school_teacher': 'School Teacher',
        'college_professor': 'College Professor',
        'university_lecturer': 'University Lecturer',
        'private_tutor': 'Private Tutor',
        'online_teaching': 'Online Teaching',
        'special_education': 'Special Education',
        'coaching': 'Coaching Institute',
        'research_teaching': 'Research & Teaching'
    },
    'medical_profession': {
        'doctor': 'Doctor (MBBS)',
        'surgeon': 'Surgeon',
        'specialist': 'Medical Specialist',
        'dentist': 'Dentist',
        'pharmacist': 'Pharmacist',
        'nurse': 'Nurse',
        'physiotherapist': 'Physiotherapist',
        'psychiatrist': 'Psychiatrist',
        'cardiologist': 'Cardiologist',
        'neurologist': 'Neurologist'
    },
    'legal_profession': {
        'lawyer': 'Lawyer',
        'judge': 'Judge',
        'advocate': 'Advocate',
        'legal_consultant': 'Legal Consultant',
        'corporate_lawyer': 'Corporate Lawyer',
        'criminal_lawyer': 'Criminal Lawyer',
        'civil_lawyer': 'Civil Lawyer',
        'family_lawyer': 'Family Lawyer',
        'notary': 'Notary',
        'legal_advisor': 'Legal Advisor'
    },
    'competitive_exams': {
        'neet': 'NEET (Medical)',
        'jee': 'JEE (Engineering)',
        'cat': 'CAT (Management)',
        'gate': 'GATE (Engineering)',
        'upsc': 'UPSC (Civil Services)',
        'bank_exam': 'Banking Exam',
        'ssc': 'SSC (Staff Selection)',
        'railway_exam': 'Railway Exam',
        'defense_exam': 'Defense Exam',
        'teaching_exam': 'Teaching Exam'
    },
    'police': {
        'ips_officer': 'IPS Officer',
        'constable': 'Police Constable',
        'sub_inspector': 'Sub Inspector',
        'inspector': 'Inspector',
        'superintendent': 'Superintendent',
        'commissioner': 'Commissioner',
        'crime_branch': 'Crime Branch',
        'traffic_police': 'Traffic Police',
        'cyber_crime': 'Cyber Crime',
        'special_forces': 'Special Forces'
    },
    'civil_services': {
        'ias': 'IAS (Administrative)',
        'ips': 'IPS (Police)',
        'ifs': 'IFS (Foreign)',
        'irs': 'IRS (Revenue)',
        'ifs_forest': 'IFS (Forest)',
        'ies': 'IES (Engineering)',
        'iss': 'ISS (Statistical)',
        'ifs_customs': 'IFS (Customs)',
        'ifs_audit': 'IFS (Audit)',
        'ifs_trade': 'IFS (Trade)'
    },
    'engineering': {
        'computer_engineering': 'Computer Engineering',
        'mechanical_engineering': 'Mechanical Engineering',
        'electrical_engineering': 'Electrical Engineering',
        'civil_engineering': 'Civil Engineering',
        'chemical_engineering': 'Chemical Engineering',
        'electronics': 'Electronics',
        'biotechnology': 'Biotechnology',
        'aerospace': 'Aerospace',
        'automotive': 'Automotive',
        'robotics': 'Robotics'
    },
    'it_software': {
        'software_developer': 'Software Developer',
        'data_scientist': 'Data Scientist',
        'web_developer': 'Web Developer',
        'mobile_developer': 'Mobile Developer',
        'system_admin': 'System Administrator',
        'network_engineer': 'Network Engineer',
        'cybersecurity': 'Cybersecurity',
        'cloud_computing': 'Cloud Computing',
        'ai_ml': 'AI/ML Engineer',
        'devops': 'DevOps Engineer'
    },
    # Health specific conditions
    'mental_health': {
        'anxiety': 'Anxiety',
        'depression': 'Depression',
        'stress': 'Stress',
        'panic': 'Panic Attacks',
        'mood_swings': 'Mood Swings',
        'bipolar': 'Bipolar Disorder',
        'schizophrenia': 'Schizophrenia',
        'ocd': 'OCD',
        'ptsd': 'PTSD',
        'addiction': 'Addiction'
    },
    'physical_illness': {
        'diabetes': 'Diabetes',
        'hypertension': 'Hypertension',
        'heart_disease': 'Heart Disease',
        'cancer': 'Cancer',
        'arthritis': 'Arthritis',
        'asthma': 'Asthma',
        'thyroid': 'Thyroid Issues',
        'obesity': 'Obesity',
        'migraine': 'Migraine',
        'back_pain': 'Back Pain'
    },
    # Relationship specific conditions
    'marriage': {
        'arranged': 'Arranged Marriage',
        'love': 'Love Marriage',
        'intercaste': 'Intercaste Marriage',
        'interfaith': 'Interfaith Marriage',
        'remarriage': 'Remarriage',
        'court_marriage': 'Court Marriage',
        'traditional': 'Traditional Marriage',
        'modern': 'Modern Marriage',
        'long_distance': 'Long Distance',
        'early_marriage': 'Early Marriage'
    },
    # Education specific conditions
    'academic_performance': {
        'excellent': 'Excellent Performance',
        'improving': 'Improving Performance',
        'declining': 'Declining Performance',
        'struggling': 'Struggling',
        'breakthrough': 'Breakthrough',
        'consistent': 'Consistent Performance',
        'inconsistent': 'Inconsistent Performance',
        'top_rank': 'Top Rank',
        'average': 'Average Performance',
        'below_average': 'Below Average'
    },
    # Financial specific conditions
    'investment': {
        'profitable': 'Profitable Investment',
        'loss': 'Investment Loss',
        'risky': 'Risky Investment',
        'safe': 'Safe Investment',
        'long_term': 'Long-term Investment',
        'short_term': 'Short-term Investment',
        'high_return': 'High Return',
        'low_return': 'Low Return',
        'diversified': 'Diversified Portfolio',
        'concentrated': 'Concentrated Investment'
    },
    # Travel specific conditions
    'international_travel': {
        'business': 'Business Travel',
        'leisure': 'Leisure Travel',
        'study': 'Study Abroad',
        'work': 'Work Assignment',
        'family': 'Family Visit',
        'medical': 'Medical Travel',
        'pilgrimage': 'Pilgrimage',
        'adventure': 'Adventure Travel',
        'luxury': 'Luxury Travel',
        'backpacking': 'Backpacking'
    },
    # Spiritual specific conditions
    'meditation': {
        'beginner': 'Beginner',
        'advanced': 'Advanced',
        'regular': 'Regular Practice',
        'irregular': 'Irregular Practice',
        'intensive': 'Intensive Practice',
        'vipassana': 'Vipassana',
        'transcendental': 'Transcendental',
        'mindfulness': 'Mindfulness',
        'zen': 'Zen',
        'yoga_meditation': 'Yoga Meditation'
    },
    # Legal specific conditions
    'court_case': {
        'winning': 'Winning Case',
        'losing': 'Losing Case',
        'settlement': 'Settlement',
        'appeal': 'Appeal',
        'pending': 'Pending Case',
        'dismissed': 'Dismissed Case',
        'compromise': 'Compromise',
        'arbitration': 'Arbitration',
        'mediation': 'Mediation',
        'out_of_court': 'Out of Court Settlement'
    },
    # Sports specific conditions
    'competition': {
        'winning': 'Winning',
        'losing': 'Losing',
        'participation': 'Participation',
        'qualification': 'Qualification',
        'disqualification': 'Disqualification',
        'medal': 'Medal Winner',
        'record': 'Record Breaking',
        'team_win': 'Team Victory',
        'individual_win': 'Individual Victory',
        'runner_up': 'Runner Up'
    },
    # Creative specific conditions
    'art': {
        'exhibition': 'Exhibition',
        'sale': 'Art Sale',
        'recognition': 'Recognition',
        'commission': 'Commission',
        'inspiration': 'Inspiration',
        'award': 'Award Winner',
        'gallery': 'Gallery Display',
        'auction': 'Auction',
        'private_collection': 'Private Collection',
        'public_art': 'Public Art'
    }
}

# Outcomes
OUTCOMES = {
    'positive': 'Positive',
    'negative': 'Negative',
    'neutral': 'Neutral',
    'mixed': 'Mixed',
    'unknown': 'Unknown'
}

# Severity Levels
SEVERITY_LEVELS = {
    'mild': 'Mild',
    'moderate': 'Moderate',
    'severe': 'Severe',
    'critical': 'Critical',
    'unknown': 'Unknown'
}

# Timing Categories
TIMING_CATEGORIES = {
    'immediate': 'Immediate',
    'short_term': 'Short Term',
    'medium_term': 'Medium Term',
    'long_term': 'Long Term',
    'unknown': 'Unknown'
}

def get_category_options():
    """
    Get all category options for the frontend
    """
    return {
        'primary_categories': PRIMARY_CATEGORIES,
        'sub_categories': SUB_CATEGORIES,
        'specific_conditions': SPECIFIC_CONDITIONS,
        'outcomes': OUTCOMES,
        'severity_levels': SEVERITY_LEVELS,
        'timing_categories': TIMING_CATEGORIES
    }

def validate_categories(primary_category, sub_category=None, specific_condition=None):
    """
    Validate category combinations
    """
    if not primary_category:
        return False, "Primary category is required"
    
    if primary_category not in PRIMARY_CATEGORIES:
        return False, f"Invalid primary category: {primary_category}"
        
    if sub_category:
        if primary_category not in SUB_CATEGORIES:
            return False, f"No sub categories available for {primary_category}"
        
        if sub_category not in SUB_CATEGORIES[primary_category]:
            return False, f"Invalid sub category: {sub_category}"
            
        if specific_condition:
            if sub_category not in SPECIFIC_CONDITIONS:
                return False, f"No specific conditions available for {sub_category}"
            
            if specific_condition not in SPECIFIC_CONDITIONS[sub_category]:
                return False, f"Invalid specific condition: {specific_condition}"
        
    return True, "Valid categories"

if __name__ == '__main__':
    # Test the categories
    print("🌍 Comprehensive Category System")
    print("=" * 40)
    
    options = get_category_options()
    print(f"Primary Categories: {len(options['primary_categories'])}")
    print(f"Sub Categories: {sum(len(subs) for subs in options['sub_categories'].values())}")
    print(f"Specific Conditions: {sum(len(conds) for conds in options['specific_conditions'].values())}")
    
    # Test validation
    print("\n✅ Validation Tests:")
    print(f"Valid career/government_job/ias: {validate_categories('career', 'government_job', 'ias')}")
    print(f"Valid education/competitive_exams/neet: {validate_categories('education', 'competitive_exams', 'neet')}")
    print(f"Invalid primary: {validate_categories('invalid')}")
    print(f"Invalid sub: {validate_categories('career', 'invalid')}") 