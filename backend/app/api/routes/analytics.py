from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.usage_score import UsageScoreRequest, UsageScoreResponse
from app.services.usage_score_service import UsageScoreService
from app.services.experiment_service import ExperimentService
from app.models.experiment import Experiment
from app.models.persona import Persona
from app.models.usage_score import UsageScoreReport
from app.models.insight import InsightReport
from app.models.survey import Survey, SurveyResponse
from app.models.conversation import Conversation

router = APIRouter(prefix="/api/experiments", tags=["Product Usage Scoring"])

# Separate router for the /api/analytics prefix
analytics_overview_router = APIRouter(prefix="/api/analytics", tags=["Analytics Overview"])


@analytics_overview_router.get("/overview")
def get_analytics_overview(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns platform-wide analytics overview aggregating metrics across experiments,
    personas, surveys, responses, insight reports, and usage scoring.
    """
    total_experiments = db.query(Experiment).count()
    total_personas = db.query(Persona).count()
    total_surveys = db.query(Survey).count()
    total_survey_responses = db.query(SurveyResponse).count()
    total_conversations = db.query(Conversation).count()
    total_insights = db.query(InsightReport).count()
    total_usage_scores = db.query(UsageScoreReport).count()

    total_responses = total_survey_responses + total_conversations

    usage_reports = db.query(UsageScoreReport).all()
    avg_usage_score = None
    avg_would_use_pct = None
    if usage_reports:
        avg_usage_score = round(sum(r.overall_score for r in usage_reports) / len(usage_reports), 2)
        avg_would_use_pct = round(sum(r.would_use_percentage for r in usage_reports) / len(usage_reports), 2)

    return {
        "total_experiments": total_experiments,
        "total_personas": total_personas,
        "total_surveys": total_surveys,
        "total_responses": total_responses,
        "survey_responses": total_survey_responses,
        "interview_responses": total_conversations,
        "total_insights": total_insights,
        "total_usage_scores": total_usage_scores,
        "average_usage_score": avg_usage_score,
        "average_would_use_percentage": avg_would_use_pct,
    }


@router.post("/{experiment_id}/usage-score", response_model=UsageScoreResponse, status_code=status.HTTP_201_CREATED)
async def calculate_usage_score(
    experiment_id: str,
    payload: Optional[UsageScoreRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Evaluates product usage likelihood ("Would Use This Product") across experiment personas.
    Computes overall score, percentage, segment breakdowns (age, occupation), calculation method, and explicit simulation disclaimers.
    """
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )

    custom_q = payload.custom_question if payload else None

    try:
        report = await UsageScoreService.calculate_usage_score(
            db=db,
            experiment_id=experiment_id,
            custom_question=custom_q
        )
        return UsageScoreResponse.model_validate(report)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/{experiment_id}/usage-score", response_model=UsageScoreResponse)
def get_latest_usage_score(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve the latest usage score evaluation report for an experiment."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )

    report = UsageScoreService.get_latest_usage_score(db, experiment_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No usage score report calculated yet for experiment '{experiment_id}'."
        )

    return UsageScoreResponse.model_validate(report)
