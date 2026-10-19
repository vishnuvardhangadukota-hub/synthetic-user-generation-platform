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

router = APIRouter(prefix="/api/experiments", tags=["Product Usage Scoring"])

# Separate router for the /api/analytics prefix
analytics_overview_router = APIRouter(prefix="/api/analytics", tags=["Analytics Overview"])

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
