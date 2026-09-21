from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class PersonaCreate(BaseModel):
    name: str
    age: int
    occupation: str
    location: str = "Hyderabad"
    demographics: Dict[str, Any] = Field(default_factory=dict)
    personality_traits: List[str] = Field(default_factory=list)
    behavioral_patterns: List[str] = Field(default_factory=list)
    psychological_profile: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    opinions: Dict[str, Any] = Field(default_factory=dict)
    memory_summary: str = ""
    is_synthetic_test_data: bool = False

class PersonaResponse(BaseModel):
    id: str
    experiment_id: str
    name: str
    age: int
    occupation: str
    location: str
    demographics: Dict[str, Any]
    personality_traits: List[str]
    behavioral_patterns: List[str]
    psychological_profile: Dict[str, Any]
    preferences: Dict[str, Any]
    opinions: Dict[str, Any]
    memory_summary: str
    is_synthetic_test_data: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonaGenerateRequest(BaseModel):
    number_of_personas: Optional[int] = Field(None, ge=1, le=20, description="Override number of personas to generate (1-20)")

class PersonaGenerateResponse(BaseModel):
    experiment_id: str
    personas: List[PersonaResponse]
