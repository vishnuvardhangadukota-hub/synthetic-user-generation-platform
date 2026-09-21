from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.persona import PersonaResponse
from app.schemas.memory import PersonaFullMemoryResponse
from app.services.persona_service import PersonaService
from app.services.memory_service import MemoryService

router = APIRouter(prefix="/api/personas", tags=["Personas"])

@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona(persona_id: str, db: Session = Depends(get_db)):
    """Get specific persona profile by ID."""
    persona = PersonaService.get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona with ID '{persona_id}' not found"
        )
    return PersonaResponse.model_validate(persona)

@router.delete("/{persona_id}", status_code=status.HTTP_200_OK)
def delete_persona(persona_id: str, db: Session = Depends(get_db)):
    """Delete a persona by ID."""
    success = PersonaService.delete_persona(db, persona_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona with ID '{persona_id}' not found"
        )
    return {"detail": f"Persona '{persona_id}' successfully deleted"}

@router.get("/{persona_id}/memory", response_model=PersonaFullMemoryResponse)
def get_persona_memory(persona_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full persona memory, including core attributes, behavioral memories,
    established opinions, conversation history, and memory summary.
    """
    persona = PersonaService.get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona with ID '{persona_id}' not found"
        )
    
    full_memory = MemoryService.get_full_persona_memory(db, persona)
    return PersonaFullMemoryResponse.model_validate(full_memory)
