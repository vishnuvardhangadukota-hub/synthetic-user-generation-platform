from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.survey import (
    SurveyCreate,
    SurveyResponseSchema,
    QuestionCreate,
    QuestionResponseSchema,
    SurveyRunResponse,
    SurveyResponsesGrouped,
    SurveyResponseItem
)
from app.services.survey_service import SurveyService
from app.services.experiment_service import ExperimentService

router = APIRouter(tags=["Surveys"])

@router.post("/api/experiments/{experiment_id}/surveys", response_model=SurveyResponseSchema, status_code=status.HTTP_201_CREATED)
def create_survey_for_experiment(
    experiment_id: str,
    payload: SurveyCreate,
    db: Session = Depends(get_db)
):
    """Create a new survey for an experiment."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    return SurveyService.create_survey(db, experiment_id, payload)


@router.get("/api/experiments/{experiment_id}/surveys", response_model=List[SurveyResponseSchema])
def get_surveys_for_experiment(
    experiment_id: str,
    db: Session = Depends(get_db)
):
    """List all surveys created for an experiment."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    return SurveyService.get_surveys_by_experiment(db, experiment_id)


@router.post("/api/surveys/{survey_id}/questions", response_model=QuestionResponseSchema, status_code=status.HTTP_201_CREATED)
def add_question_to_survey(
    survey_id: str,
    payload: QuestionCreate,
    db: Session = Depends(get_db)
):
    """Add a question to an existing survey."""
    survey = SurveyService.get_survey_by_id(db, survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID '{survey_id}' not found"
        )
    return SurveyService.add_question(db, survey_id, payload)


@router.post("/api/surveys/{survey_id}/run", response_model=SurveyRunResponse)
async def run_survey_for_personas(
    survey_id: str,
    db: Session = Depends(get_db)
):
    """
    Execute a survey for all synthetic personas in the experiment.
    Generates one response per persona per question using their persona attributes and memory.
    """
    survey = SurveyService.get_survey_by_id(db, survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID '{survey_id}' not found"
        )

    try:
        result = await SurveyService.run_survey(db, survey_id)
        
        # Validate and format responses
        resp_items = []
        for r in result["responses"]:
            resp_items.append(SurveyResponseItem(
                id=r.id,
                experiment_id=r.experiment_id,
                survey_id=r.survey_id,
                question_id=r.question_id,
                persona_id=r.persona_id,
                persona_name=r.persona.name if r.persona else "",
                answer=r.answer,
                rating_score=r.rating_score,
                reasoning=r.reasoning or "",
                created_at=r.created_at
            ))

        return SurveyRunResponse(
            survey_id=result["survey_id"],
            total_personas=result["total_personas"],
            total_responses_generated=result["total_responses_generated"],
            responses=resp_items
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.get("/api/surveys/{survey_id}/responses", response_model=SurveyResponsesGrouped)
def get_survey_responses_grouped(
    survey_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve survey responses grouped by question for side-by-side persona comparison.
    """
    survey = SurveyService.get_survey_by_id(db, survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with ID '{survey_id}' not found"
        )

    grouped_data = SurveyService.get_grouped_responses(db, survey_id)
    return SurveyResponsesGrouped.model_validate(grouped_data)
