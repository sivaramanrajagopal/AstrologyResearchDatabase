"""
DasaService: wraps Vimshottari Dasa calculation and current/at-date period lookup.
Uses Ashtavargam client when available; otherwise returns minimal structure.
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DasaService:
    """Vimshottari Dasa periods and current/at-date lookup."""

    def __init__(self):
        pass

    def calculate_vimshottari_dasa(self, birth_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Vimshottari Dasa periods (120 years).
        birth_data: datetime (or date+time), lat, lon, timezone_name.
        Returns nested dict: Mahadasa -> Antardasa list (or as returned by Ashtavargam).
        """
        try:
            from api.adapters.ashtavargam_client import (
                birth_data_to_ashtavargam_body,
                dasha_calculate,
            )
            dob = birth_data.get("date_of_birth") or birth_data.get("dob")
            tob = birth_data.get("time_of_birth") or birth_data.get("tob")
            if isinstance(tob, str) and len(tob) > 5:
                tob = tob[:5]
            lat = birth_data.get("latitude")
            lon = birth_data.get("longitude")
            tz = birth_data.get("timezone_name", "UTC")
            if dob is None or tob is None or lat is None or lon is None:
                return {"error": "Missing birth_data: dob, tob, lat, lon"}
            body = birth_data_to_ashtavargam_body(str(dob), str(tob), float(lat), float(lon), tz)
            return dasha_calculate(body, total_years=120)
        except Exception as e:
            logger.warning("calculate_vimshottari_dasa failed: %s", e)
            return {"error": str(e)}

    def get_current_dasa(
        self,
        dasa_periods: Dict[str, Any],
        current_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Find which Mahadasa and Antardasa are currently running.
        Returns dict with current_dasa, current_bhukti, start/end if available.
        """
        try:
            from api.adapters.ashtavargam_client import (
                birth_data_to_ashtavargam_body,
                dasha_current,
            )
            # If dasa_periods has birth info, call dasha_current API
            dob = dasa_periods.get("dob") or dasa_periods.get("date_of_birth")
            tob = dasa_periods.get("tob") or dasa_periods.get("time_of_birth")
            lat = dasa_periods.get("lat") or dasa_periods.get("latitude")
            lon = dasa_periods.get("lon") or dasa_periods.get("longitude")
            tz = dasa_periods.get("timezone_name", "UTC")
            if dob and tob and lat is not None and lon is not None:
                body = birth_data_to_ashtavargam_body(
                    str(dob), str(tob)[:5], float(lat), float(lon), tz
                )
                target = (current_date or datetime.utcnow()).strftime("%Y-%m-%d") if current_date else None
                return dasha_current(body, current_date=target)
            # Else parse dasa_periods structure if it contains periods list
            return {"current_dasa": None, "current_bhukti": None}
        except Exception as e:
            logger.warning("get_current_dasa failed: %s", e)
            return {"current_dasa": None, "current_bhukti": None, "error": str(e)}

    def get_dasa_at_date(
        self,
        dasa_periods: Dict[str, Any],
        target_date: datetime,
    ) -> Dict[str, Any]:
        """
        Find which Dasa periods were running at target_date.
        Uses Ashtavargam dasha_current with target_date if birth data present.
        """
        return self.get_current_dasa(dasa_periods, current_date=target_date)
