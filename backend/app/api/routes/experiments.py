from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.experiment import ExperimentCreate, ExperimentUpdate, ExperimentResponse
from app.schemas.persona import PersonaGenerateRequest, PersonaGenerateResponse, PersonaResponse
from app.services.experiment_service import ExperimentService
from app.services.persona_service import PersonaService
from app.agents.persona_generation_agent import PersonaGenerationAgent

router = APIRouter(prefix="/api/experiments", tags=["Experiments"])

@router.post("", response_model=ExperimentResponse, status_code=status.HTTP_201_CREATED)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    """Create a new research experiment workspace."""
    return ExperimentService.create_experiment(db, payload)

@router.get("", response_model=List[ExperimentResponse])
def get_all_experiments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of all research experiments."""
    return ExperimentService.get_all_experiments(db, skip=skip, limit=limit)

@router.get("/{experiment_id}", response_model=ExperimentResponse)
def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Get a specific experiment by ID."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    return exp

@router.put("/{experiment_id}", response_model=ExperimentResponse)
def update_experiment(experiment_id: str, payload: ExperimentUpdate, db: Session = Depends(get_db)):
    """Update an existing experiment."""
    updated = ExperimentService.update_experiment(db, experiment_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    return updated

@router.delete("/{experiment_id}", status_code=status.HTTP_200_OK)
def delete_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Delete an experiment and all associated personas."""
    success = ExperimentService.delete_experiment(db, experiment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    return {"detail": f"Experiment '{experiment_id}' and all associated personas successfully deleted"}

@router.post("/{experiment_id}/personas/generate", response_model=PersonaGenerateResponse, status_code=status.HTTP_201_CREATED)
async def generate_personas_for_experiment(
    experiment_id: str,
    payload: Optional[PersonaGenerateRequest] = None,
    db: Session = Depends(get_db)
):
    """
    Generate synthetic personas for an experiment using the Persona Generation Agent.
    """
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )

    num_personas = payload.number_of_personas if (payload and payload.number_of_personas) else exp.number_of_personas

    agent = PersonaGenerationAgent()
    personas_data, is_synthetic_test_data = await agent.generate_personas(
        product_name=exp.product_name,
        product_description=exp.product_description,
        target_audience=exp.target_audience,
        research_objectives=exp.research_objectives,
        number_of_personas=num_personas
    )

    created_personas = PersonaService.save_personas_bulk(
        db=db,
        experiment_id=exp.id,
        personas_data=personas_data,
        is_synthetic_test_data=is_synthetic_test_data
    )

    return PersonaGenerateResponse(
        experiment_id=exp.id,
        personas=[PersonaResponse.model_validate(p) for p in created_personas]
    )

@router.get("/{experiment_id}/personas", response_model=List[PersonaResponse])
def get_personas_for_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Get all personas generated for an experiment."""
    exp = ExperimentService.get_experiment_by_id(db, experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment with ID '{experiment_id}' not found"
        )
    
    personas = PersonaService.get_personas_by_experiment(db, experiment_id)
    return [PersonaResponse.model_validate(p) for p in personas]
