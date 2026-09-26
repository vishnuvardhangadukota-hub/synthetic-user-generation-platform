from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

class UsageScoreRequest(BaseModel):
    custom_question: Optional[str] = Field(
        None,
        description="Optional custom product usage evaluation question. E.g., 'How likely are you to use this food delivery app weekly?'"
    )

class PersonaScoreItem(BaseModel):
    persona_id: str
    persona_name: str
    occupation: str
    age: int
    price_sensitivity: str
    would_use: bool
    score: float  # 1-10 scale
    category: str # 'Would Use', 'Unlikely', 'Maybe'
    reasoning: str

class UsageScoreResponse(BaseModel):
    id: str
    experiment_id: str
    overall_score: float  # Average 1-10 score
    would_use_percentage: float  # % personas who would use
    segmentation_breakdown: Dict[str, Any]
    persona_scores: List[Dict[str, Any]]
    calculation_method: str
    limitations: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
