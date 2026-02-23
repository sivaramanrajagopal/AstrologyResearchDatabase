"""
PredictionService: orchestrates career prediction using ChartService, ParasaraRulesEngine, DasaService.
Uses chart_id (astrology_charts) as native identifier; fetches chart, computes D1/D10, applies rules.
"""
import logging
from typing import Any, Dict, List, Optional

from services.chart_service import ChartService
from services.dasa_service import DasaService
from services.rules_engine import ParasaraRulesEngine

logger = logging.getLogger(__name__)


class PredictionService:
    """Orchestrates full career prediction and explanation."""

    def __init__(
        self,
        chart_service: Optional[ChartService] = None,
        rules_engine: Optional[ParasaraRulesEngine] = None,
        dasa_service: Optional[DasaService] = None,
    ):
        self.chart_service = chart_service or ChartService()
        self.rules_engine = rules_engine or ParasaraRulesEngine()
        self.dasa_service = dasa_service or DasaService()

    def _get_birth_data(self, chart_id: int) -> Optional[Dict[str, Any]]:
        """Load chart from Supabase and return birth_data dict."""
        try:
            from supabase_config import supabase_manager
            if not supabase_manager:
                return None
            row = supabase_manager.get_birth_chart(chart_id)
            if not row:
                return None
            dob = row.get("date_of_birth")
            tob = row.get("time_of_birth")
            if isinstance(tob, str) and len(tob) > 5:
                tob = tob[:5]
            return {
                "date_of_birth": dob,
                "time_of_birth": tob,
                "latitude": row.get("latitude"),
                "longitude": row.get("longitude"),
                "timezone_name": row.get("timezone_name") or "UTC",
            }
        except Exception as e:
            logger.warning("_get_birth_data failed for chart_id=%s: %s", chart_id, e)
            return None

    def predict_career(self, chart_id: int) -> Dict[str, Any]:
        """
        Full prediction for one chart: fetch profile, compute D1/D10, get Dasa,
        analyze charts, apply Parasara rules, rank careers, confidence, store.
        Returns CareerPredictionResponse-like dict.
        """
        birth_data = self._get_birth_data(chart_id)
        if not birth_data:
            return {"error": "Chart not found", "chart_id": chart_id}
        dob = birth_data["date_of_birth"]
        tob = birth_data["time_of_birth"]
        lat = birth_data["latitude"]
        lon = birth_data["longitude"]
        tz = birth_data["timezone_name"]
        if lat is None or lon is None:
            return {"error": "Missing latitude/longitude", "chart_id": chart_id}
        from datetime import datetime
        try:
            dt = datetime.strptime(str(dob), "%Y-%m-%d").date()
        except Exception:
            return {"error": "Invalid date_of_birth", "chart_id": chart_id}
        try:
            tot = datetime.strptime(str(tob)[:5], "%H:%M").time()
        except Exception:
            tot = datetime.strptime("12:00", "%H:%M").time()
        charts = self.chart_service.calculate_birth_chart(
            date_of_birth=dt,
            time_of_birth=tot,
            latitude=float(lat),
            longitude=float(lon),
            timezone_name=tz,
            chart_types=["D1", "D10"],
        )
        d1 = charts.get("d1")
        d10 = charts.get("d10")
        if not d1 or not d10:
            return {"error": "D1/D10 calculation failed", "chart_id": chart_id}
        d1_analysis = self.chart_service.analyze_d1_chart(d1)
        d10_analysis = self.chart_service.analyze_d10_chart(d10, d1)
        birth_data_for_dasa = {
            "dob": dob, "tob": tob, "latitude": lat, "longitude": lon, "timezone_name": tz,
        }
        dasa_periods = self.dasa_service.calculate_vimshottari_dasa(birth_data_for_dasa)
        current_dasa = self.dasa_service.get_current_dasa(birth_data_for_dasa)
        career_scores = self.rules_engine.apply_all_rules(d1, d10, current_dasa)
        confidence = self.calculate_confidence_score(career_scores, d1_analysis, d10_analysis)
        top_career = career_scores[0][0] if career_scores else None
        supporting = self.generate_supporting_indicators(top_career, d1, d10) if top_career else []
        response = {
            "chart_id": chart_id,
            "career_strength": "strong" if confidence >= 60 else "moderate" if confidence >= 40 else "weak",
            "ranked_careers": career_scores,
            "confidence_score": confidence,
            "d1_analysis": d1_analysis,
            "d10_analysis": d10_analysis,
            "supporting_indicators": supporting,
            "current_dasa": current_dasa,
        }
        try:
            from supabase_config import supabase_manager
            if supabase_manager:
                from services.career_rules import career_rules
                cr_result = career_rules(d1, d10, dasha_current=current_dasa)
                supabase_manager.upsert_career_prediction(
                    chart_id=chart_id,
                    career_strength=cr_result["career_strength"],
                    factors=cr_result["factors"],
                    scores=cr_result["scores"],
                    d10_snapshot=d10,
                    dasha_bukti_snapshot=current_dasa,
                    bav_sav_snapshot=None,
                )
        except Exception as e:
            logger.warning("Could not store prediction: %s", e)
        return response

    def calculate_confidence_score(
        self,
        career_scores: List[tuple],
        d1_analysis: Dict[str, Any],
        d10_analysis: Dict[str, Any],
    ) -> float:
        """
        Confidence 0-100: score spread, strength of indicators, D1-D10 agreement.
        """
        if not career_scores:
            return 0.0
        scores_only = [s[1] for s in career_scores]
        spread = max(scores_only) - min(scores_only) if len(scores_only) > 1 else scores_only[0]
        spread_factor = min(100, spread * 2)
        strong_indicators = 0
        if d1_analysis.get("tenth_lord_house") in (1, 4, 5, 7, 9, 10, 11):
            strong_indicators += 20
        if d10_analysis.get("vargottama"):
            strong_indicators += min(30, len(d10_analysis["vargottama"]) * 10)
        agreement = 25 if (d1_analysis.get("planets_in_10th") and d10_analysis.get("planets_in_10th")) else 0
        return min(100, spread_factor * 0.4 + strong_indicators + agreement)

    def generate_supporting_indicators(
        self,
        career: str,
        d1_chart: Dict[str, Any],
        d10_chart: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """For the predicted career, list which planets/houses support it."""
        indicators = []
        from services.rules_engine import CAREER_SIGNIFICATIONS
        for planet, careers in CAREER_SIGNIFICATIONS.items():
            if career not in careers:
                continue
            if planet in d1_chart and isinstance(d1_chart[planet], dict):
                house = None
                for h in range(1, 13):
                    if planet in self.chart_service.get_planets_in_house(d1_chart, h):
                        house = h
                        break
                indicators.append({
                    "source": "D1",
                    "planet": planet,
                    "house": house,
                    "strength": "supports",
                })
        return indicators[:10]

    def explain_prediction(self, prediction: Dict[str, Any]) -> str:
        """Human-readable explanation of the prediction. Works with full response or stored row."""
        parts = []
        if prediction.get("error"):
            return f"Prediction failed: {prediction['error']}."
        ranked = prediction.get("ranked_careers", [])
        if ranked:
            top = ranked[0]
            parts.append(f"Top career suggestion: {top[0]} (score {top[1]:.1f}).")
        else:
            strength = prediction.get("career_strength", "")
            if strength:
                parts.append(f"Career strength: {strength}.")
        conf = prediction.get("confidence_score")
        if conf is not None:
            parts.append(f"Confidence: {conf:.0f}%.")
        d1 = prediction.get("d1_analysis", {})
        if d1.get("tenth_lord"):
            parts.append(f"10th lord ({d1['tenth_lord']}) in house {d1.get('tenth_lord_house', '?')}.")
        if d1.get("planets_in_10th"):
            parts.append(f"Planets in 10th house (D1): {', '.join(d1['planets_in_10th'])}.")
        factors = prediction.get("factors", [])
        if factors and not parts:
            parts.append("Factors: " + "; ".join(factors[:5]) + ".")
        return " ".join(parts) if parts else "No detailed explanation available."
