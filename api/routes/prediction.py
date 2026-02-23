"""
Career prediction API routes: generate, get, history, batch, explain.
Uses chart_id as native identifier (astrology_charts.id).
"""
import logging
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/prediction", tags=["prediction"])


class BatchRequest(BaseModel):
    chart_ids: List[int]
logger = logging.getLogger(__name__)


def _get_prediction_service():
    from services.prediction_service import PredictionService
    return PredictionService()


def _get_supabase():
    from supabase_config import supabase_manager
    return supabase_manager


@router.post("/generate/{chart_id}")
def generate_prediction(chart_id: int):
    """
    Generate career prediction for chart (native). Saves to career_predictions.
    Returns full prediction with ranked careers and confidence.
    """
    try:
        svc = _get_prediction_service()
        result = svc.predict_career(chart_id)
        if result.get("error"):
            raise HTTPException(status_code=404 if "not found" in result["error"].lower() else 400, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("generate_prediction failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{chart_id}")
def get_latest_prediction(chart_id: int):
    """Get latest stored prediction for chart."""
    db = _get_supabase()
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    row = db.get_career_prediction(chart_id)
    if not row:
        raise HTTPException(status_code=404, detail="No prediction found")
    return row


@router.get("/history/{chart_id}")
def get_prediction_history(chart_id: int):
    """Get all predictions for chart. Current schema has one per chart (upsert); return as list."""
    db = _get_supabase()
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    row = db.get_career_prediction(chart_id)
    if not row:
        return []
    return [row]


@router.post("/batch")
def batch_predict(body: BatchRequest):
    """Generate predictions for multiple charts. Returns list of results."""
    chart_ids = (body.chart_ids or [])[:20]
    results = []
    svc = _get_prediction_service()
    for cid in chart_ids:
        try:
            r = svc.predict_career(cid)
            results.append(r)
        except Exception as e:
            results.append({"chart_id": cid, "error": str(e)})
    return results


@router.get("/explain/{chart_id}")
def explain_prediction(chart_id: int):
    """Get human-readable explanation for the latest prediction."""
    db = _get_supabase()
    if not db:
        raise HTTPException(status_code=503, detail="Database not configured")
    row = db.get_career_prediction(chart_id)
    if row:
        from services.prediction_service import PredictionService
        svc = PredictionService()
        return {"explanation": svc.explain_prediction(row), "prediction": row}
    svc = _get_prediction_service()
    pred = svc.predict_career(chart_id)
    if pred.get("error"):
        raise HTTPException(status_code=404, detail=pred["error"])
    return {"explanation": svc.explain_prediction(pred), "prediction": pred}


@router.get("/validation/run")
def run_validation():
    """Run full validation on 30 notable charts; return accuracy report."""
    from services.validation_service import ValidationService
    vs = ValidationService()
    return vs.run_complete_validation()
