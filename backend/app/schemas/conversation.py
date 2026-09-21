from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    message: str = Field(..., min_length=1, description="Message from the user to the persona")

class ConversationResponse(BaseModel):
    persona_id: str
    response: str
    memory_updated: bool = True
