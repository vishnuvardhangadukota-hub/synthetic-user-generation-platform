from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class MemoryCreate(BaseModel):
    memory_type: str = Field(..., description="Type of memory: core, behavior, opinion, conversation")
    topic: str = "general"
    content: str
    importance: float = 1.0

class MemoryResponse(BaseModel):
    id: str
    persona_id: str
    memory_type: str
    topic: str
    content: str
    importance: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationHistoryItem(BaseModel):
    id: str
    user_message: str
    persona_response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonaFullMemoryResponse(BaseModel):
    persona_id: str
    core_attributes: Dict[str, Any]
    behavioral_memories: List[Dict[str, Any]]
    opinions: List[Dict[str, Any]]
    conversation_history: List[ConversationHistoryItem]
    memory_summary: str
