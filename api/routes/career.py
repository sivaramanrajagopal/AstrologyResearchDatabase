"""
Career prediction endpoint: D1 + D10 + optional Dasha/BAV-SAV -> career rules.
"""
import os
import sys
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/career", tags=["career"])

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


class CareerPredictRequest(BaseModel):
    """Request: either chart_id (Supabase) or birth data."""
    chart_id: Optional[int] = Field(None, description="Supabase astrology_charts id")
    dob: Optional[str] = Field(None, description="Date of birth YYYY-MM-DD")
    tob: Optional[str] = Field(None, description="Time of birth HH:MM or HH:MM:SS")
    place: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone_name: Optional[str] = None
    use_dasha: bool = Field(True, description="Call Ashtavargam for current Dasha/Bhukti")
    use_bav_sav: bool = Field(True, description="Call Ashtavargam for BAV/SAV")


def _get_d1_from_db(chart_id: int) -> dict:
    """Load chart from Supabase and build D1 positions dict for career_rules."""
    from supabase_config import supabase_manager
    if not supabase_manager:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    row = supabase_manager.get_birth_chart(chart_id)
    if not row:
        raise HTTPException(status_code=404, detail="Chart not found")
    # Build D1-like structure from stored columns
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Ascendant"]
    d1 = {}
    for p in planets:
        key = p.lower()
        lon = row.get(f"{key}_longitude")
        if lon is None:
            continue
        d1[p] = {
            "longitude": float(lon),
            "rasi": row.get(f"{key}_rasi") or "",
            "rasi_lord": row.get(f"{key}_rasi_lord") or "",
            "retrograde": row.get(f"{key}_retrograde") or False,
        }
    houses = {}
    for i in range(1, 13):
        lon = row.get(f"house_{i}_longitude")
        if lon is not None:
            rasi = row.get(f"house_{i}_rasi") or ""
            houses[f"House_{i}"] = {"longitude": float(lon), "rasi": rasi, "degrees_in_rasi": float(lon % 30)}
    if houses:
        d1["_enhanced"] = {"houses": houses}
    return d1


def _compute_d1_d10_from_birth(dob: str, tob: str, lat: float, lon: float, tz_name: str) -> tuple:
    """Compute D1 and D10 from birth data."""
    from datetime import datetime
    from enhanced_swiss_ephemeris import calculate_enhanced_planetary_positions
    from services.d10_dasamsa import calculate_d10_chart

    dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    t = tob.strip()
    if len(t) == 5:
        tot = datetime.strptime(t, "%H:%M").time()
    else:
        tot = datetime.strptime(t[:8], "%H:%M:%S").time()
    d1 = calculate_enhanced_planetary_positions(
        date_of_birth=dob_date,
        time_of_birth=tot,
        latitude=lat,
        longitude=lon,
        timezone_name=tz_name,
    )
    if not d1:
        return None, None
    d10 = calculate_d10_chart(d1)
    return d1, d10


@router.post("/predict")
def career_predict(req: CareerPredictRequest):
    """
    Career prediction: D1 + D10 + optional Dasha/BAV-SAV -> deterministic career strength and factors.
    Provide either chart_id or (dob, tob, place or lat/lon, timezone_name).
    """
    d1 = None
    d10 = None

    if req.chart_id is not None:
        d1 = _get_d1_from_db(req.chart_id)
        # D10 from D1
        from services.d10_dasamsa import calculate_d10_chart
        d10 = calculate_d10_chart(d1)
    elif req.dob and req.tob and (req.place or (req.latitude is not None and req.longitude is not None)):
        from api.routes.charts import BirthDataRequest, _parse_birth_data  # noqa: E402
        birth_req = BirthDataRequest(
            dob=req.dob,
            tob=req.tob,
            place=req.place,
            latitude=req.latitude,
            longitude=req.longitude,
            timezone_name=req.timezone_name,
        )
        dob, tot, lat, lon, tz_name = _parse_birth_data(birth_req)
        d1, d10 = _compute_d1_d10_from_birth(
            dob.isoformat(),
            tot.strftime("%H:%M") if tot.second == 0 else tot.strftime("%H:%M:%S"),
            lat, lon, tz_name,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide chart_id or (dob, tob, and place or latitude/longitude)",
        )

    if not d1 or not d10:
        raise HTTPException(status_code=500, detail="D1/D10 calculation failed")

    dasha_current = None
    bav_sav_full = None
    if req.use_dasha:
        try:
            from api.adapters.ashtavargam_client import (
                birth_data_to_ashtavargam_body,
                dasha_current as dasha_current_call,
            )
            if req.chart_id is not None:
                from supabase_config import supabase_manager
                row = supabase_manager.get_birth_chart(req.chart_id)
                body = birth_data_to_ashtavargam_body(
                    dob=row["date_of_birth"],
                    tob=row["time_of_birth"][:5] if isinstance(row["time_of_birth"], str) else "12:00",
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    timezone_name=row.get("timezone_name") or "UTC",
                )
            else:
                from api.routes.charts import BirthDataRequest, _parse_birth_data as parse_birth
                birth_req = BirthDataRequest(dob=req.dob, tob=req.tob, place=req.place, latitude=req.latitude, longitude=req.longitude, timezone_name=req.timezone_name)
                dob, tot, lat, lon, tz_name = parse_birth(birth_req)
                body = birth_data_to_ashtavargam_body(dob.isoformat(), tot.strftime("%H:%M"), lat, lon, tz_name)
            dasha_current = dasha_current_call(body)
        except Exception:
            dasha_current = None
    if req.use_bav_sav:
        try:
            # Use local Ashtakavarga calculator instead of external service
            from services.ashtakavarga_service import calculate_ashtakavarga_full

            # Calculate Ashtakavarga from D1 chart data
            ashtakavarga_data = calculate_ashtakavarga_full(d1)

            if ashtakavarga_data:
                # Transform to format expected by career_rules
                # career_rules expects: bav_sav_full["sav_chart"] = list of 12 SAV values
                bav_sav_full = {
                    "sav_chart": ashtakavarga_data['sav']['chart'],
                    "sav_total": ashtakavarga_data['sav']['total'],
                    "bav": ashtakavarga_data['bav'],  # Include full BAV data for future use
                }
            else:
                bav_sav_full = None
        except Exception as e:
            print(f"Error calculating local Ashtakavarga: {e}")
            import traceback
            traceback.print_exc()
            bav_sav_full = None

    from services.career_rules import career_rules
    result = career_rules(d1, d10, dasha_current=dasha_current, bav_sav_full=bav_sav_full)

    # Calculate profession probabilities (V2 - Enhanced with yogas) - ALWAYS
    profession_summary = None
    chart_data = None

    # Get chart data for profession predictor
    if req.chart_id is not None:
        # From database
        try:
            from supabase_config import supabase_manager
            if supabase_manager:
                chart_data = supabase_manager.get_birth_chart(req.chart_id)
        except Exception as e:
            print(f"Error fetching chart from DB: {e}")
    else:
        # From D1 data (when using birth data directly)
        # Build chart_data structure from D1
        chart_data = {}
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu', 'Ascendant']:
            if planet in d1:
                planet_key = planet.lower()
                chart_data[f'{planet_key}_rasi'] = d1[planet].get('rasi', '')
                chart_data[f'{planet_key}_nakshatra'] = d1[planet].get('nakshatra', '')
                chart_data[f'{planet_key}_retrograde'] = d1[planet].get('retrograde', False)

        # Add houses
        if '_enhanced' in d1 and 'houses' in d1['_enhanced']:
            for i in range(1, 13):
                house_key = f'House_{i}'
                if house_key in d1['_enhanced']['houses']:
                    chart_data[f'house_{i}_rasi'] = d1['_enhanced']['houses'][house_key].get('rasi', '')

        # Add 10th lord (calculate from ascendant)
        asc_rasi = chart_data.get('ascendant_rasi', '')
        lords = {
            'Mesha': 'Mars', 'Rishaba': 'Venus', 'Mithuna': 'Mercury',
            'Kataka': 'Moon', 'Simha': 'Sun', 'Kanya': 'Mercury',
            'Tula': 'Venus', 'Vrishchika': 'Mars', 'Dhanus': 'Jupiter',
            'Makara': 'Saturn', 'Kumbha': 'Saturn', 'Meena': 'Jupiter',
        }
        # 10th from ascendant
        chart_data['tenth_lord'] = lords.get(chart_data.get('house_10_rasi', ''), '')

    # Calculate profession probabilities for ALL requests (chart_id or birth data)
    if chart_data:
        try:
            from services.profession_predictor_v2 import get_profession_summary_v2
            profession_summary = get_profession_summary_v2(chart_data)
        except Exception as e:
            print(f"Error calculating profession probabilities: {e}")
            import traceback
            traceback.print_exc()
            profession_summary = None

    # Generate simple profession list from top probabilities (replaces old ParasaraRulesEngine)
    profession_suggestion = []
    if profession_summary and profession_summary.get('top_professions'):
        profession_suggestion = [p['name'] for p in profession_summary['top_professions'][:5]]

    response = {
        "career_strength": result["career_strength"],
        "factors": result["factors"],
        "scores": result["scores"],
        "applied_rules": result.get("applied_rules", []),
        "rules_checklist": result.get("rules_checklist", []),
        "rules_score": result.get("rules_score", "0/0"),
        "profession_suggestion": profession_suggestion,
        "profession_probabilities": profession_summary,
        "dasha_current": dasha_current,
        "bav_sav_10th": bav_sav_full.get("sav_chart", [None] * 12)[9] if bav_sav_full and bav_sav_full.get("sav_chart") else None,
    }
    if req.chart_id is not None:
        try:
            from supabase_config import supabase_manager
            if supabase_manager:
                supabase_manager.upsert_career_prediction(
                    chart_id=req.chart_id,
                    career_strength=result["career_strength"],
                    factors=result["factors"],
                    scores=result["scores"],
                    d10_snapshot=d10,
                    dasha_bukti_snapshot=dasha_current,
                    bav_sav_snapshot=bav_sav_full,
                )
        except Exception:
            pass
    return response


# Chart IDs 16-44 are the 30 notable profiles (batch 1 + batch 2)
VALIDATION_CHART_IDS = list(range(16, 45))


@router.get("/validate")
def career_validate():
    """
    Run career prediction for the 30 notable charts (ids 16-44).
    Returns per-chart prediction and comparison with stored description (profession).
    Optionally saves each result to career_predictions.
    """
    from supabase_config import supabase_manager
    if not supabase_manager:
        raise HTTPException(status_code=503, detail="Supabase not configured")
    from api.adapters.ashtavargam_client import (
        birth_data_to_ashtavargam_body,
        dasha_current as dasha_current_call,
        bav_sav_full as bav_sav_call,
    )
    from services.d10_dasamsa import calculate_d10_chart
    from services.career_rules import career_rules

    results = []
    for chart_id in VALIDATION_CHART_IDS:
        row = supabase_manager.get_birth_chart(chart_id)
        if not row:
            continue
        d1 = _get_d1_from_db(chart_id)
        d10 = calculate_d10_chart(d1)
        dasha_current = None
        bav_sav_full = None
        try:
            body = birth_data_to_ashtavargam_body(
                row["date_of_birth"],
                row["time_of_birth"][:5] if isinstance(row["time_of_birth"], str) else "12:00",
                row["latitude"], row["longitude"],
                row.get("timezone_name") or "UTC",
            )
            dasha_current = dasha_current_call(body)
        except Exception:
            pass
        try:
            # Use local Ashtakavarga calculator
            from services.ashtakavarga_service import calculate_ashtakavarga_full
            ashtakavarga_data = calculate_ashtakavarga_full(d1)
            if ashtakavarga_data:
                bav_sav_full = {
                    "sav_chart": ashtakavarga_data['sav']['chart'],
                    "sav_total": ashtakavarga_data['sav']['total'],
                    "bav": ashtakavarga_data['bav'],
                }
        except Exception as e:
            print(f"Error calculating Ashtakavarga for validation chart {chart_id}: {e}")
            pass
        result = career_rules(d1, d10, dasha_current=dasha_current, bav_sav_full=bav_sav_full)
        known_profession = (row.get("description") or "").strip()

        # Calculate profession probabilities (V2)
        profession_summary = None
        try:
            from services.profession_predictor_v2 import get_profession_summary_v2
            profession_summary = get_profession_summary_v2(row)
        except Exception as e:
            print(f"Error calculating profession for chart {chart_id}: {e}")

        # Get top predicted professions
        predicted_professions = []
        if profession_summary and profession_summary.get('top_professions'):
            predicted_professions = [
                f"{p['name']} ({p['probability']}%)"
                for p in profession_summary['top_professions'][:3]
            ]

        results.append({
            "chart_id": chart_id,
            "name": row.get("name"),
            "known_profession": known_profession,
            "predicted_professions": predicted_professions,
            "career_strength": result["career_strength"],
            "factors": result["factors"],
            "scores": result["scores"],
            "applied_rules": result.get("applied_rules", []),
            "profession_probabilities": profession_summary,
        })
        try:
            supabase_manager.upsert_career_prediction(
                chart_id=chart_id,
                career_strength=result["career_strength"],
                factors=result["factors"],
                scores=result["scores"],
                d10_snapshot=d10,
                dasha_bukti_snapshot=dasha_current,
                bav_sav_snapshot=bav_sav_full,
            )
        except Exception:
            pass
    return {"count": len(results), "charts": results}


