"""
HTTP client for Ashtavargam APIs (BAV/SAV on 8000, Dasha/Gochara on 8001).
Converts timezone_name to tz_offset for Ashtavargam request shape.
"""
import os
from datetime import datetime
from typing import Any, Dict, Optional

import pytz
import requests


def timezone_name_to_offset_hours(timezone_name: str, at_date: Optional[datetime] = None) -> float:
    """Return UTC offset in hours for a given timezone (e.g. Asia/Kolkata -> 5.5)."""
    try:
        tz = pytz.timezone(timezone_name)
        if at_date is None:
            at_date = datetime.now(tz)
        elif at_date.tzinfo is None:
            at_date = tz.localize(at_date)
        return at_date.utcoffset().total_seconds() / 3600.0
    except Exception:
        return 0.0


def birth_data_to_ashtavargam_body(
    dob: str,
    tob: str,
    latitude: float,
    longitude: float,
    timezone_name: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Build request body for Ashtavargam APIs: dob, tob, lat, lon, tz_offset."""
    # Compute tz_offset from timezone_name at birth date
    try:
        dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M:%S")
    tz = pytz.timezone(timezone_name)
    dt = tz.localize(dt)
    offset = dt.utcoffset().total_seconds() / 3600.0
    body = {
        "dob": dob,
        "tob": tob if len(tob) == 5 else tob[:5],  # HH:MM
        "lat": latitude,
        "lon": longitude,
        "tz_offset": offset,
    }
    if name:
        body["name"] = name
    return body


# Base URLs from env or default (for local Ashtavargam services)
BAV_SAV_BASE = os.environ.get("ASHTAVARGAM_BAV_SAV_URL", "http://localhost:8000")
DASHA_GOCHARA_BASE = os.environ.get("ASHTAVARGAM_DASHA_GOCHARA_URL", "http://localhost:8001")
REQUEST_TIMEOUT = float(os.environ.get("ASHTAVARGAM_TIMEOUT", "30"))


def bav_sav_full(body: Dict[str, Any]) -> Dict[str, Any]:
    """POST /api/v1/calculate/full - full BAV + SAV."""
    r = requests.post(
        f"{BAV_SAV_BASE}/api/v1/calculate/full",
        json=body,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def bav_planet(body: Dict[str, Any], planet: str) -> Dict[str, Any]:
    """POST /api/v1/calculate/bav/{planet}."""
    r = requests.post(
        f"{BAV_SAV_BASE}/api/v1/calculate/bav/{planet}",
        json=body,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def sav_only(body: Dict[str, Any]) -> Dict[str, Any]:
    """POST /api/v1/calculate/sav."""
    r = requests.post(
        f"{BAV_SAV_BASE}/api/v1/calculate/sav",
        json=body,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def dasha_calculate(body: Dict[str, Any], total_years: int = 120) -> Dict[str, Any]:
    """POST /api/v1/dasha/calculate."""
    r = requests.post(
        f"{DASHA_GOCHARA_BASE}/api/v1/dasha/calculate",
        json=body,
        params={"total_years": total_years} if total_years != 120 else None,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def dasha_bhukti(body: Dict[str, Any]) -> Dict[str, Any]:
    """POST /api/v1/dasha/bhukti."""
    r = requests.post(
        f"{DASHA_GOCHARA_BASE}/api/v1/dasha/bhukti",
        json=body,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def dasha_current(body: Dict[str, Any], current_date: Optional[str] = None) -> Dict[str, Any]:
    """POST /api/v1/dasha/current."""
    params = {}
    if current_date:
        params["current_date"] = current_date
    r = requests.post(
        f"{DASHA_GOCHARA_BASE}/api/v1/dasha/current",
        json=body,
        params=params or None,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def gochara_calculate(body: Dict[str, Any], transit_date: Optional[str] = None) -> Dict[str, Any]:
    """POST /api/v1/gochara/calculate."""
    params = {}
    if transit_date:
        params["transit_date"] = transit_date
    r = requests.post(
        f"{DASHA_GOCHARA_BASE}/api/v1/gochara/calculate",
        json=body,
        params=params or None,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()
