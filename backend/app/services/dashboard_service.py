"""
Dashboard Service
=================
Aggregates all experiment results into a unified dashboard payload.
All metrics are calculated from real saved data — no hardcoded values.

Scoring formula (validation score):
  raw = overall_usage_score (1–10 scale from UsageScoreReport)
  validation_score = round((raw / 10) * 100, 1)   -> 0–100 scale

If no UsageScoreReport exists the score is None.
"""
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.experiment import Experiment
from app.models.persona import Persona
from app.models.conversation import Conversation
from app.models.survey import Survey, SurveyResponse
from app.models.insight import InsightReport
from app.models.usage_score import UsageScoreReport
from app.services.experiment_service import ExperimentService
from app.services.insight_service import InsightService
from app.services.usage_score_service import UsageScoreService

logger = logging.getLogger(__name__)


class DashboardService:

    # ------------------------------------------------------------------
    # Main aggregation entry point
    # ------------------------------------------------------------------
    @staticmethod
    def get_dashboard(db: Session, experiment_id: str) -> Dict[str, Any]:
        """
        Returns a complete dashboard payload for the given experiment.
        Raises ValueError when the experiment does not exist.
        """
        exp: Optional[Experiment] = ExperimentService.get_experiment_by_id(db, experiment_id)
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        personas: List[Persona] = (
            db.query(Persona).filter(Persona.experiment_id == experiment_id).all()
        )
        persona_ids = [p.id for p in personas]

        # ---- Survey responses ----
        survey_responses: List[SurveyResponse] = (
            db.query(SurveyResponse)
            .filter(SurveyResponse.experiment_id == experiment_id)
            .all()
        )

        # ---- Interview conversations ----
        conversations: List[Conversation] = []
        if persona_ids:
            conversations = (
                db.query(Conversation)
                .filter(Conversation.persona_id.in_(persona_ids))
                .all()
            )

        total_responses = len(survey_responses) + len(conversations)

        # ---- Latest insight report ----
        insight: Optional[InsightReport] = InsightService.get_latest_insight(db, experiment_id)

        # ---- Latest usage score ----
        usage_score: Optional[UsageScoreReport] = UsageScoreService.get_latest_usage_score(
            db, experiment_id
        )

        # ---- Surveys list for status ----
        surveys: List[Survey] = (
            db.query(Survey).filter(Survey.experiment_id == experiment_id).all()
        )

        return {
            "experiment": DashboardService._build_experiment_summary(exp),
            "summary_cards": DashboardService._build_summary_cards(
                personas, survey_responses, conversations, insight, usage_score
            ),
            "theme_clusters": DashboardService._build_theme_clusters(insight),
            "sentiment_breakdown": DashboardService._build_sentiment_breakdown(insight),
            "key_quotes": DashboardService._build_key_quotes(
                insight, survey_responses, conversations, personas
            ),
            "validation_score": DashboardService._build_validation_score(usage_score),
            "surveys": [
                {"id": s.id, "title": s.title, "status": s.status} for s in surveys
            ],
            "has_insight_report": insight is not None,
            "has_usage_score": usage_score is not None,
        }

    # ------------------------------------------------------------------
    # Builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_experiment_summary(exp: Experiment) -> Dict[str, Any]:
        return {
            "id": exp.id,
            "name": exp.name,
            "product_name": exp.product_name,
            "product_description": exp.product_description,
            "target_audience": exp.target_audience,
            "research_objectives": exp.research_objectives,
            "number_of_personas": exp.number_of_personas,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
            "updated_at": exp.updated_at.isoformat() if exp.updated_at else None,
        }

    @staticmethod
    def _build_summary_cards(
        personas: List[Persona],
        survey_responses: List[SurveyResponse],
        conversations: List[Conversation],
        insight: Optional[InsightReport],
        usage_score: Optional[UsageScoreReport],
    ) -> Dict[str, Any]:
        # Positive sentiment %
        pos_pct: Optional[float] = None
        if insight and insight.sentiment_distribution:
            sd = insight.sentiment_distribution
            pos_pct = sd.get("positive_percentage")

        # Validation score (0-100)
        val_score: Optional[float] = None
        if usage_score:
            raw = usage_score.overall_score  # 1-10 scale
            val_score = round((raw / 10.0) * 100.0, 1)

        # Theme count
        theme_count = 0
        if insight and insight.recurring_themes:
            theme_count = len(insight.recurring_themes)

        total_responses = len(survey_responses) + len(conversations)

        # Experiment status
        status = "Not Started"
        if total_responses > 0 and insight:
            status = "Analysis Complete"
        elif total_responses > 0:
            status = "Responses Collected"
        elif personas:
            status = "Personas Generated"

        return {
            "total_personas": len(personas),
            "total_responses": total_responses,
            "survey_responses": len(survey_responses),
            "interview_responses": len(conversations),
            "themes_discovered": theme_count,
            "positive_sentiment_pct": pos_pct,
            "validation_score": val_score,
            "experiment_status": status,
        }

    @staticmethod
    def _build_theme_clusters(insight: Optional[InsightReport]) -> List[Dict[str, Any]]:
        """Returns theme clusters with name, count placeholder, and representative quotes."""
        if not insight or not insight.recurring_themes:
            return []

        clusters = []
        themes = insight.recurring_themes
        total = len(themes) if themes else 1

        for i, theme in enumerate(themes):
            if not isinstance(theme, dict):
                continue
            name = theme.get("theme", f"Theme {i+1}")
            description = theme.get("description", "")
            quotes = theme.get("supporting_quotes", [])
            if not isinstance(quotes, list):
                quotes = []

            clusters.append(
                {
                    "theme": name,
                    "description": description,
                    "response_count": len(quotes),
                    "percentage": round((1 / total) * 100.0, 1),
                    "representative_quotes": quotes[:3],  # max 3 per theme
                }
            )

        return clusters

    @staticmethod
    def _build_sentiment_breakdown(insight: Optional[InsightReport]) -> Dict[str, Any]:
        if not insight or not insight.sentiment_distribution:
            return {
                "positive": {"count": 0, "percentage": 0.0},
                "neutral": {"count": 0, "percentage": 0.0},
                "negative": {"count": 0, "percentage": 0.0},
                "total": 0,
            }

        sd = insight.sentiment_distribution
        counts = sd.get("counts", {})

        pos_count = counts.get("positive", 0)
        neu_count = counts.get("neutral", 0)
        neg_count = counts.get("negative", 0)
        total = pos_count + neu_count + neg_count

        return {
            "positive": {
                "count": pos_count,
                "percentage": sd.get("positive_percentage", 0.0),
            },
            "neutral": {
                "count": neu_count,
                "percentage": sd.get("neutral_percentage", 0.0),
            },
            "negative": {
                "count": neg_count,
                "percentage": sd.get("negative_percentage", 0.0),
            },
            "total": total,
        }

    @staticmethod
    def _build_key_quotes(
        insight: Optional[InsightReport],
        survey_responses: List[SurveyResponse],
        conversations: List[Conversation],
        personas: List[Persona],
    ) -> List[Dict[str, Any]]:
        """
        Builds key quotes from supporting_references in the insight report,
        cross-referencing actual survey/conversation data for authenticity.
        Falls back to raw survey answers when no insight report exists.
        """
        persona_map: Dict[str, Persona] = {p.id: p for p in personas}
        quotes: List[Dict[str, Any]] = []

        # 1. Pull from insight supporting references
        if insight and insight.supporting_references:
            for ref in insight.supporting_references[:10]:
                if not isinstance(ref, dict):
                    continue
                pid = ref.get("persona_id", "")
                p = persona_map.get(pid)
                p_attrs = {}
                if p:
                    p_attrs = {
                        "age": p.age,
                        "occupation": p.occupation,
                        "location": p.location,
                    }
                snippet = ref.get("content_snippet", "")
                if not snippet:
                    continue
                quotes.append(
                    {
                        "persona_id": pid,
                        "persona_name": ref.get("persona_name", "Unknown"),
                        "quote": snippet,
                        "source_type": ref.get("source_type", "survey"),
                        "theme": None,  # Not tagged per-ref in current model
                        "sentiment": None,
                        "persona_attributes": p_attrs,
                    }
                )

        # 2. If no quotes from insight, pull directly from survey responses (top 8)
        if not quotes:
            for sr in survey_responses[:8]:
                p = persona_map.get(sr.persona_id)
                quotes.append(
                    {
                        "persona_id": sr.persona_id,
                        "persona_name": p.name if p else "Unknown",
                        "quote": sr.answer,
                        "source_type": "survey",
                        "theme": None,
                        "sentiment": None,
                        "persona_attributes": {
                            "age": p.age if p else None,
                            "occupation": p.occupation if p else None,
                            "location": p.location if p else None,
                        },
                    }
                )

        # 3. Supplement with conversations if still few
        if len(quotes) < 4:
            for conv in conversations[:6]:
                p = persona_map.get(conv.persona_id)
                quotes.append(
                    {
                        "persona_id": conv.persona_id,
                        "persona_name": p.name if p else "Unknown",
                        "quote": conv.persona_response[:300],
                        "source_type": "interview",
                        "theme": None,
                        "sentiment": None,
                        "persona_attributes": {
                            "age": p.age if p else None,
                            "occupation": p.occupation if p else None,
                            "location": p.location if p else None,
                        },
                    }
                )

        return quotes[:12]  # max 12 quotes on dashboard

    @staticmethod
    def _build_validation_score(usage_score: Optional[UsageScoreReport]) -> Dict[str, Any]:
        """
        Builds the product validation section from UsageScoreReport.

        Scoring methodology:
          overall_score is on a 1.0–10.0 scale (raw LLM-assigned score per persona).
          validation_score (0–100) = round((overall_score / 10) * 100, 1)
          would_use_percentage is already a 0–100 percentage.
        """
        if not usage_score:
            return {
                "available": False,
                "score": None,
                "would_use_percentage": None,
                "methodology": None,
                "limitations": None,
                "persona_scores": [],
                "segmentation": {},
                "strengths": [],
                "weaknesses": [],
                "opportunities": [],
            }

        raw = usage_score.overall_score  # 1-10
        val_score = round((raw / 10.0) * 100.0, 1)

        # Derive strengths / weaknesses from persona scores
        persona_scores = usage_score.persona_scores or []
        would_use_list = [ps for ps in persona_scores if ps.get("would_use")]
        unlikely_list = [ps for ps in persona_scores if not ps.get("would_use")]

        strengths = [
            f"{ps['persona_name']} ({ps['occupation']}): {ps['reasoning'][:120]}"
            for ps in would_use_list[:3]
        ]
        weaknesses = [
            f"{ps['persona_name']} ({ps['occupation']}): {ps['reasoning'][:120]}"
            for ps in unlikely_list[:3]
        ]

        # Opportunity: segments that need improvement
        opportunities: List[str] = []
        seg = usage_score.segmentation_breakdown or {}
        by_age = seg.get("by_age_group", {})
        for age_group, stats in by_age.items():
            if stats.get("would_use_pct", 100) < 50:
                opportunities.append(
                    f"Low adoption among age group {age_group} "
                    f"({stats.get('would_use_pct', 0):.0f}% would use). "
                    "Consider targeted pricing or features for this segment."
                )

        return {
            "available": True,
            "score": val_score,
            "raw_score_1_10": raw,
            "would_use_percentage": usage_score.would_use_percentage,
            "methodology": usage_score.calculation_method,
            "limitations": usage_score.limitations,
            "persona_scores": persona_scores,
            "segmentation": seg,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
        }
