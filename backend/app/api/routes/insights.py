from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.insight import InsightReportResponse
from app.services.insight_service import InsightService
from app.services.experiment_service import ExperimentService

router = APIRouter(prefix="/api/experiments", tags=["Insights"])

@router.post("/{experiment_id}/insights", response_model=InsightReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_insights(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """
    Synthesize survey and interview response data for an experiment into a structured insight report.
    Returns recurring themes, sentiment distribution, agreements, disagreements, behavioral trends, supporting references, and limitations.
    """
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )

    try:
        report = await InsightService.generate_insights_for_experiment(db, experiment_id)
        return InsightReportResponse.model_validate(report)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/{experiment_id}/insights", response_model=InsightReportResponse)
def get_latest_insights(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """Get the latest generated insight report for an experiment."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )

    report = InsightService.get_latest_insight(db, experiment_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No insight report generated yet for experiment '{experiment_id}'. Call POST /api/experiments/{experiment_id}/insights first."
        )

    return InsightReportResponse.model_validate(report)
