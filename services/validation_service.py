"""
ValidationService: run career prediction on the 30 notable charts and compute accuracy metrics.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Chart IDs 16-44: 30 notable profiles with known profession in description
VALIDATION_CHART_IDS = list(range(16, 45))


class ValidationService:
    """Run validation and produce accuracy report."""

    def __init__(self, prediction_service=None):
        from services.prediction_service import PredictionService
        self.prediction_service = prediction_service or PredictionService()

    def run_complete_validation(self) -> Dict[str, Any]:
        """
        Run prediction for all 30 validation charts; compare with actual career (description);
        compute Top-1, Top-3, Top-5, Category accuracy; return ValidationReport dict.
        """
        from supabase_config import supabase_manager
        if not supabase_manager:
            return {"error": "Supabase not configured", "results": []}
        results = []
        for chart_id in VALIDATION_CHART_IDS:
            row = supabase_manager.get_birth_chart(chart_id)
            if not row:
                continue
            actual = (row.get("description") or "").strip()
            try:
                pred = self.prediction_service.predict_career(chart_id)
                ranked = pred.get("ranked_careers", [])
                predicted_careers = [c[0] for c in ranked]
                acc = self.calculate_accuracy(predicted_careers, actual)
                results.append({
                    "chart_id": chart_id,
                    "name": row.get("name"),
                    "actual": actual,
                    "predicted_top": predicted_careers[:5],
                    "accuracy": acc,
                })
            except Exception as e:
                logger.warning("Validation chart_id=%s failed: %s", chart_id, e)
                results.append({
                    "chart_id": chart_id,
                    "name": row.get("name"),
                    "actual": actual,
                    "predicted_top": [],
                    "accuracy": {"top1": False, "top3": False, "top5": False, "category_match": False},
                    "error": str(e),
                })
        report = self.generate_validation_report(results)
        return report

    def calculate_accuracy(self, predicted: List[str], actual: str) -> Dict[str, Any]:
        """
        Check if actual career in top 1, 3, or 5; check category match.
        actual can be a single profession or comma-separated; we take first as main.
        """
        actual_clean = actual.split(",")[0].strip() if actual else ""
        if not actual_clean:
            return {"top1": False, "top3": False, "top5": False, "category_match": False}
        from utils.helpers import career_category_mapping
        actual_cat = career_category_mapping(actual_clean)
        pred_cats = [career_category_mapping(c) for c in predicted[:5]]
        top1 = len(predicted) >= 1 and predicted[0].strip() == actual_clean
        top3 = actual_clean in [p.strip() for p in predicted[:3]]
        top5 = actual_clean in [p.strip() for p in predicted[:5]]
        category_match = actual_cat in pred_cats[:3] if pred_cats else False
        return {
            "top1": top1,
            "top3": top3,
            "top5": top5,
            "category_match": category_match,
        }

    def generate_validation_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate accuracy metrics and return report."""
        n = len(results)
        if n == 0:
            return {"count": 0, "top1_accuracy": 0, "top3_accuracy": 0, "top5_accuracy": 0, "category_accuracy": 0, "results": []}
        top1 = sum(1 for r in results if r.get("accuracy", {}).get("top1"))
        top3 = sum(1 for r in results if r.get("accuracy", {}).get("top3"))
        top5 = sum(1 for r in results if r.get("accuracy", {}).get("top5"))
        cat = sum(1 for r in results if r.get("accuracy", {}).get("category_match"))
        return {
            "count": n,
            "top1_accuracy": round(100 * top1 / n, 1),
            "top3_accuracy": round(100 * top3 / n, 1),
            "top5_accuracy": round(100 * top5 / n, 1),
            "category_accuracy": round(100 * cat / n, 1),
            "results": results,
        }
