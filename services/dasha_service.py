"""
Dasha Service - Wrapper for Dasha calculation
Provides a simple interface to calculate current Dasha/Bhukti from chart data
"""

from typing import Dict, Any, Optional
from datetime import datetime
import swisseph as swe


def calculate_current_dasha(chart_data: Dict[str, Any], birth_date: str, birth_time: str) -> Optional[Dict[str, Any]]:
    """
    Calculate current Dasha and Bhukti for a chart

    Args:
        chart_data: D1 chart data with planetary positions
        birth_date: Birth date in ISO format (YYYY-MM-DD)
        birth_time: Birth time in HH:MM format

    Returns:
        Dict with current_dasa, current_bhukti, or None if calculation fails
    """
    try:
        from services.dasha_calculator import get_current_dasa_bhukti

        # Get Moon longitude from chart data
        if "Moon" not in chart_data or "longitude" not in chart_data["Moon"]:
            return None

        moon_lon = chart_data["Moon"]["longitude"]

        # Parse birth details
        dob = datetime.fromisoformat(birth_date)
        hour, minute = map(int, birth_time.split(":"))

        # Calculate Julian Day
        jd = swe.julday(dob.year, dob.month, dob.day, hour + minute/60.0)

        # Get current Dasha/Bhukti
        dasha_result = get_current_dasa_bhukti(jd, moon_lon)

        return dasha_result

    except Exception as e:
        # Silently fail - Dasha is optional
        return None


def format_dasha_for_display(dasha_data: Optional[Dict[str, Any]]) -> str:
    """
    Format Dasha data for display

    Args:
        dasha_data: Dict from calculate_current_dasha()

    Returns:
        Formatted string like "Venus Mahadasha / Jupiter Antardasha"
    """
    if not dasha_data:
        return "Not calculated"

    dasa = dasha_data.get("current_dasa", "Unknown")
    bhukti = dasha_data.get("current_bhukti", "Unknown")

    return f"{dasa} Mahadasha / {bhukti} Antardasha"
