#!/usr/bin/env python3
"""
Demonstration of D10 (Dasamsa) 10th House Calculation
Shows step-by-step how the 10th house sign is determined in D10 chart
"""

import sys
sys.path.insert(0, '/Users/sivaramanrajagopal/Documents/Astro-birthchart-Database')

from services.d10_dasamsa import d1_longitude_to_d10, d10_longitude_to_rasi


def demonstrate_d10_calculation(d1_asc_longitude: float, chart_name: str = "Example"):
    """
    Demonstrate D10 10th house calculation step by step

    Args:
        d1_asc_longitude: Ascendant longitude in D1 chart (0-360°)
        chart_name: Name for the demonstration
    """

    signs = [
        'Mesha (Aries)', 'Rishaba (Taurus)', 'Mithuna (Gemini)',
        'Kataka (Cancer)', 'Simha (Leo)', 'Kanni (Virgo)',
        'Thula (Libra)', 'Vrischika (Scorpio)', 'Dhanus (Sagittarius)',
        'Makara (Capricorn)', 'Kumbha (Aquarius)', 'Meena (Pisces)'
    ]

    elements = ['Fire', 'Earth', 'Air', 'Water'] * 3

    print("=" * 80)
    print(f"D10 (DASAMSA) 10TH HOUSE CALCULATION - {chart_name}")
    print("=" * 80)
    print()

    # STEP 1: D1 Ascendant
    print("STEP 1: D1 ASCENDANT")
    print("-" * 80)
    d1_rasi_index = int(d1_asc_longitude // 30) % 12
    d1_degrees = d1_asc_longitude % 30
    print(f"D1 Ascendant Longitude: {d1_asc_longitude:.4f}°")
    print(f"D1 Ascendant Sign: {signs[d1_rasi_index]}")
    print(f"Degrees in sign: {d1_degrees:.4f}°")
    print()

    # STEP 2: D10 Ascendant Calculation
    print("STEP 2: D10 ASCENDANT CALCULATION (Parasara Method)")
    print("-" * 80)

    part = int(d1_degrees / 3)
    print(f"Each sign is divided into 10 parts of 3° each")
    print(f"Part number: {d1_degrees:.2f}° ÷ 3° = {part} (range 0-9)")
    print()

    # Determine if odd or even sign
    is_odd_sign = (d1_rasi_index % 2 == 0)  # 0-indexed: even index = odd sign

    if is_odd_sign:
        print(f"{signs[d1_rasi_index]} is an ODD sign (Movable/Dual)")
        print(f"Formula: Start from the same sign and count forward")
        d10_rasi_index = (d1_rasi_index + part) % 12
        print(f"D10 Rasi Index = ({d1_rasi_index} + {part}) % 12 = {d10_rasi_index}")
    else:
        print(f"{signs[d1_rasi_index]} is an EVEN sign (Fixed)")
        print(f"Formula: Start from the 9th sign (8 positions ahead) and count forward")
        start_index = (d1_rasi_index + 8) % 12
        print(f"9th sign from {signs[d1_rasi_index].split()[0]} = {signs[start_index]}")
        d10_rasi_index = (start_index + part) % 12
        print(f"D10 Rasi Index = ({start_index} + {part}) % 12 = {d10_rasi_index}")

    # Calculate actual D10 longitude
    d10_asc_longitude = d1_longitude_to_d10(d1_asc_longitude)
    print()
    print(f"D10 Ascendant Sign: {signs[d10_rasi_index]}")
    print(f"D10 Ascendant Longitude: {d10_asc_longitude:.4f}°")
    print()

    # STEP 3: D10 10th House
    print("STEP 3: D10 10TH HOUSE CALCULATION")
    print("-" * 80)
    print("The 10th house is 9 houses (270°) from the Ascendant")
    print()

    tenth_house_longitude = (d10_asc_longitude + 270) % 360
    tenth_house_index = int(tenth_house_longitude // 30)

    print(f"D10 Ascendant Longitude: {d10_asc_longitude:.4f}°")
    print(f"Add 270° (9 houses): ({d10_asc_longitude:.4f}° + 270°) % 360°")
    print(f"D10 10th House Longitude: {tenth_house_longitude:.4f}°")
    print(f"Rasi Index: {tenth_house_index}")
    print()
    print(f"✓ D10 10th House Sign: {signs[tenth_house_index]}")
    print(f"✓ Element (Tatwa): {elements[tenth_house_index]}")
    print()

    # Element interpretation
    print("ELEMENT INTERPRETATION")
    print("-" * 80)
    element = elements[tenth_house_index]

    interpretations = {
        'Fire': 'Leadership, authority, politics, administration',
        'Earth': 'Practical fields, business, finance, construction',
        'Air': 'Communication, media, consulting, education',
        'Water': 'Creative fields, IT/Tech (creative/design-oriented), research, healing, '
                 'spirituality, service, adaptable professions (Agile/DevOps)'
    }

    print(f"{element}: {interpretations[element]}")
    print()
    print("=" * 80)
    print()


def main():
    """Run demonstrations for various ascendant positions"""

    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "D10 DASAMSA 10TH HOUSE CALCULATOR" + " " * 25 + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Example 1: Chart ID 3 approximation
    # Based on Chennai birth, assuming Aquarius Ascendant around 320°
    print("\n" + "█" * 80)
    print("EXAMPLE 1: AQUARIUS ASCENDANT AT 320°")
    print("█" * 80 + "\n")
    demonstrate_d10_calculation(320.0, "Aquarius Rising @ 320°")

    # Example 2: Different ascendant to show variation
    print("\n" + "█" * 80)
    print("EXAMPLE 2: SCORPIO ASCENDANT AT 225°")
    print("█" * 80 + "\n")
    demonstrate_d10_calculation(225.0, "Scorpio Rising @ 225°")

    # Example 3: Taurus ascendant (even sign)
    print("\n" + "█" * 80)
    print("EXAMPLE 3: TAURUS ASCENDANT AT 45°")
    print("█" * 80 + "\n")
    demonstrate_d10_calculation(45.0, "Taurus Rising @ 45°")

    print()
    print("═" * 80)
    print("NOTES:")
    print("═" * 80)
    print("1. ODD signs (Aries, Gemini, Leo, Libra, Sagittarius, Aquarius):")
    print("   Start counting D10 position from the same sign")
    print()
    print("2. EVEN signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces):")
    print("   Start counting from the 9th sign (8 positions ahead)")
    print()
    print("3. Each 30° sign is divided into 10 parts of 3° each")
    print()
    print("4. The 10th house is always 9 houses (270°) from the Ascendant")
    print()
    print("5. For Chart ID 3 verification, run:")
    print("   curl -X POST http://127.0.0.1:8000/career/predict \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{\"chart_id\": 3}' | grep D10_10th")
    print()
    print("═" * 80)


if __name__ == "__main__":
    main()
