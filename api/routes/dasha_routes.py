"""
Dasha/Bhukti API Routes
Provides Vimshottari Dasha calculations for birth charts
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
import swisseph as swe

from services.dasha_calculator import (
    generate_dasa_table,
    generate_dasa_bhukti_table,
    get_current_dasa_bhukti
)

router = APIRouter(prefix="/dasha", tags=["Dasha/Bhukti"])

# Initialize Swiss Ephemeris
swe.set_sid_mode(swe.SIDM_LAHIRI)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class DashaPeriod(BaseModel):
    planet: str
    start_age: float
    end_age: float
    start_date: str
    end_date: str
    duration: float


class DashaResponse(BaseModel):
    birth_nakshatra: str
    birth_pada: int
    dasa_periods: List[DashaPeriod]


class BhuktiPeriod(BaseModel):
    maha_dasa: str
    bhukti: str
    start_date: str
    end_date: str
    duration: float


class DashaBhuktiResponse(BaseModel):
    birth_nakshatra: str
    birth_pada: int
    dasa_bhukti_table: List[BhuktiPeriod]


class CurrentDashaResponse(BaseModel):
    current_dasa: str
    current_bhukti: Optional[str]
    start_date: str
    end_date: str
    remaining_years: float
    age: float


class DashaRequest(BaseModel):
    jd: float = Field(..., description="Julian Day number for birth time")
    moon_longitude: float = Field(..., description="Moon's longitude in degrees (0-360)")
    total_years: int = Field(120, description="Total years to calculate (default 120)")


class CurrentDashaRequest(BaseModel):
    jd: float = Field(..., description="Julian Day number for birth time")
    moon_longitude: float = Field(..., description="Moon's longitude in degrees (0-360)")
    current_date: Optional[str] = Field(None, description="Current date in YYYY-MM-DD format (defaults to today)")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/calculate", response_model=DashaResponse)
async def calculate_dasha(request: DashaRequest):
    """
    Calculate Vimshottari Dasa periods.

    Returns all Dasa periods up to total_years (default 120 for full cycle).

    Example request:
    ```json
    {
        "jd": 2440178.5,
        "moon_longitude": 292.402721,
        "total_years": 120
    }
    ```
    """
    try:
        birth_nakshatra, birth_pada, dasa_table = generate_dasa_table(
            request.jd,
            request.moon_longitude,
            request.total_years
        )

        return DashaResponse(
            birth_nakshatra=birth_nakshatra,
            birth_pada=birth_pada,
            dasa_periods=[DashaPeriod(**period) for period in dasa_table]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dasha calculation error: {str(e)}")


@router.post("/bhukti", response_model=DashaBhuktiResponse)
async def calculate_dasha_bhukti(request: DashaRequest):
    """
    Calculate Dasha-Bhukti table with all sub-periods.

    Returns complete Dasha-Bhukti table showing all Maha Dasa periods
    with their corresponding Bhukti (sub-period) breakdowns.

    Example request:
    ```json
    {
        "jd": 2440178.5,
        "moon_longitude": 292.402721
    }
    ```
    """
    try:
        birth_nakshatra, birth_pada, bhukti_table = generate_dasa_bhukti_table(
            request.jd,
            request.moon_longitude
        )

        return DashaBhuktiResponse(
            birth_nakshatra=birth_nakshatra,
            birth_pada=birth_pada,
            dasa_bhukti_table=[BhuktiPeriod(**period) for period in bhukti_table]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dasha-Bhukti calculation error: {str(e)}")


@router.post("/current", response_model=CurrentDashaResponse)
async def get_current_dasha(request: CurrentDashaRequest):
    """
    Get current Dasha and Bhukti periods.

    Returns the current Maha Dasa, Bhukti, remaining time, and age.
    If current_date is not provided, uses today's date.

    Example request:
    ```json
    {
        "jd": 2440178.5,
        "moon_longitude": 292.402721,
        "current_date": "2026-02-23"
    }
    ```
    """
    try:
        if request.current_date:
            current_dt = datetime.strptime(request.current_date, '%Y-%m-%d')
        else:
            current_dt = datetime.now()

        current_info = get_current_dasa_bhukti(
            request.jd,
            request.moon_longitude,
            current_dt
        )

        return CurrentDashaResponse(**current_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Current Dasha calculation error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for Dasha calculator"""
    return {
        "status": "healthy",
        "service": "Dasha/Bhukti Calculator",
        "system": "Vimshottari Dasha (120 year cycle)"
    }
