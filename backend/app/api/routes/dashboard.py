"""
Dashboard & PDF Report API Routes
==================================
GET  /api/experiments/{experiment_id}/dashboard       – Returns full dashboard payload
GET  /api/experiments/{experiment_id}/report/pdf      – Downloads PDF research report

Both endpoints derive all data from the saved experiment records.
No hardcoded demo values are used.
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.dashboard_service import DashboardService
from app.services.experiment_service import ExperimentService
from app.services.persona_service import PersonaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/experiments", tags=["Dashboard & Reports"])


# ---------------------------------------------------------------------------
# GET /api/experiments/{experiment_id}/dashboard
# ---------------------------------------------------------------------------
@router.get("/{experiment_id}/dashboard")
def get_experiment_dashboard(
    experiment_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Returns the complete insights dashboard payload for the given experiment.

    Includes:
    - Summary cards (total personas, responses, themes, sentiment %, validation score, status)
    - Theme clusters (from latest InsightReport)
    - Sentiment breakdown (positive/neutral/negative counts & percentages)
    - Key quotes (from supporting_references or raw survey/conversation data)
    - Product validation score (from latest UsageScoreReport, 0–100 scale)
    - Surveys list
    """
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment '{experiment_id}' not found.",
        )

    try:
        dashboard = DashboardService.get_dashboard(db, experiment_id)
        return dashboard
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as exc:
        logger.exception(f"Dashboard generation failed for {experiment_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard generation failed. See server logs for details.",
        )


# ---------------------------------------------------------------------------
# GET /api/experiments/{experiment_id}/report/pdf
# ---------------------------------------------------------------------------
@router.get("/{experiment_id}/report/pdf")
def download_experiment_report(
    experiment_id: str,
    db: Session = Depends(get_db),
):
    """
    Generates and downloads a PDF research report for the given experiment.

    Validates that the experiment exists and has at least one persona or response.
    Returns a real PDF file (application/pdf) — not an HTML or text file.

    Filename: research_report_{experiment_id}.pdf
    """
    # ── Validate experiment ──
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment '{experiment_id}' not found.",
        )

    # ── Build dashboard payload (contains all data) ──
    try:
        dashboard = DashboardService.get_dashboard(db, experiment_id)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))

    # ── Validate minimum data ──
    cards = dashboard.get("summary_cards", {})
    n_personas = cards.get("total_personas", 0)
    n_responses = cards.get("total_responses", 0)

    if n_personas == 0 and n_responses == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Experiment '{experiment_id}' has no personas or responses. "
                "Generate personas and run at least one survey or interview before downloading a report."
            ),
        )

    # ── Enrich dashboard with raw persona data for the persona profiles section ──
    personas = PersonaService.get_personas_by_experiment(db, experiment_id)
    dashboard["_personas_raw"] = [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "occupation": p.occupation,
            "location": p.location,
            "demographics": p.demographics or {},
            "personality_traits": p.personality_traits or [],
            "behavioral_patterns": p.behavioral_patterns or [],
            "psychological_profile": p.psychological_profile or {},
            "preferences": p.preferences or {},
            "opinions": p.opinions or {},
        }
        for p in personas
    ]

    # Also embed raw insight data for the Recommendations section
    from app.services.insight_service import InsightService
    insight = InsightService.get_latest_insight(db, experiment_id)
    if insight:
        dashboard["_insight_raw"] = {
            "agreement_patterns": insight.agreement_patterns or [],
            "disagreements": insight.disagreements or [],
            "behavioral_trends": insight.behavioral_trends or [],
        }
    else:
        dashboard["_insight_raw"] = {}

    # ── Generate PDF ──
    try:
        from app.services.pdf_generator import ReportPDFGenerator
        generator = ReportPDFGenerator(dashboard)
        pdf_bytes = generator.generate()
    except Exception as exc:
        logger.exception(f"PDF generation failed for {experiment_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(exc)}",
        )

    filename = f"research_report_{experiment_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )
