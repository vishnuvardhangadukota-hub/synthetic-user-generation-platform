from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.persona_service import PersonaService
from app.memory.consistency_manager import ConsistencyManager

router = APIRouter(prefix="/api/personas", tags=["Conversations"])

@router.post("/{persona_id}/conversation", response_model=ConversationResponse)
async def converse_with_persona(
    persona_id: str,
    payload: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Interact with a synthetic persona in a conversation.
    Uses the Persona Consistency Manager to retrieve core attributes & memories,
    generate persona responses, enforce consistency, and store new memories.
    """
    persona = PersonaService.get_persona_by_id(db, persona_id)
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona with ID '{persona_id}' not found"
        )

    consistency_manager = ConsistencyManager()
    result = await consistency_manager.interact(
        db=db,
        persona=persona,
        user_message=payload.message
    )

    return ConversationResponse.model_validate(result)
