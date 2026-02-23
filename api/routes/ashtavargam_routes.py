"""
Proxy routes to Ashtavargam APIs: BAV/SAV, Dasha/Bhukti, Gochara.
Requires Ashtavargam services running (BAV/SAV on 8000, Dasha-Gochara on 8001).
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.adapters.ashtavargam_client import (
    birth_data_to_ashtavargam_body,
    bav_sav_full,
    sav_only,
    dasha_calculate,
    dasha_bhukti,
    dasha_current,
    gochara_calculate,
)
from api.routes.charts import BirthDataRequest, _parse_birth_data

router = APIRouter(tags=["ashtavargam"])


def _ashtavargam_body(req: BirthDataRequest) -> dict:
    dob, tot, lat, lon, tz_name = _parse_birth_data(req)
    tob_str = req.tob.strip()
    if len(tob_str) == 5:
        tob = tob_str
    else:
        tob = tob_str[:5]  # HH:MM
    return birth_data_to_ashtavargam_body(
        dob=dob.isoformat(),
        tob=tob,
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
    )


@router.post("/bav-sav/full")
def bav_sav_full_route(req: BirthDataRequest):
    """Full BAV + SAV calculation (calls Ashtavargam BAV/SAV API)."""
    try:
        body = _ashtavargam_body(req)
        return bav_sav_full(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam BAV/SAV error: {str(e)}")


@router.post("/bav-sav/sav")
def bav_sav_sav_only_route(req: BirthDataRequest):
    """SAV only (calls Ashtavargam)."""
    try:
        body = _ashtavargam_body(req)
        return sav_only(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam SAV error: {str(e)}")


@router.post("/dasha/calculate")
def dasha_calculate_route(req: BirthDataRequest, total_years: int = 120):
    """Vimshottari Dasha periods (calls Ashtavargam Dasha-Gochara API)."""
    try:
        body = _ashtavargam_body(req)
        return dasha_calculate(body, total_years=total_years)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam Dasha error: {str(e)}")


@router.post("/dasha/bhukti")
def dasha_bhukti_route(req: BirthDataRequest):
    """Dasha-Bhukti table (calls Ashtavargam)."""
    try:
        body = _ashtavargam_body(req)
        return dasha_bhukti(body)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam Dasha-Bhukti error: {str(e)}")


@router.post("/dasha/current")
def dasha_current_route(req: BirthDataRequest, current_date: Optional[str] = None):
    """Current Dasha/Bhukti (calls Ashtavargam)."""
    try:
        body = _ashtavargam_body(req)
        return dasha_current(body, current_date=current_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam Dasha current error: {str(e)}")


@router.post("/gochara/calculate")
def gochara_calculate_route(req: BirthDataRequest, transit_date: Optional[str] = None):
    """Gochara (transits) for a date (calls Ashtavargam)."""
    try:
        body = _ashtavargam_body(req)
        return gochara_calculate(body, transit_date=transit_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ashtavargam Gochara error: {str(e)}")
