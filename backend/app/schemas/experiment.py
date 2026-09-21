from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class ExperimentCreate(BaseModel):
    name: str = Field(..., description="Experiment name")
    product_name: str = Field(..., description="Product name")
    product_description: str = Field(..., description="Detailed description of the product")
    target_audience: str = Field(..., description="Target audience definition")
    research_objectives: List[str] = Field(..., description="List of research objectives")
    number_of_personas: int = Field(5, ge=1, le=20, description="Number of personas to generate (1-20)")

    @field_validator("name", "product_name", "product_description", "target_audience")

    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip()

    @field_validator("research_objectives")

    @classmethod
    def validate_objectives(cls, v: List[str]) -> List[str]:
        cleaned = [obj.strip() for obj in v if obj and obj.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty research objective is required")
        return cleaned

class ExperimentUpdate(BaseModel):
    name: Optional[str] = None
    product_name: Optional[str] = None
    product_description: Optional[str] = None
    target_audience: Optional[str] = None
    research_objectives: Optional[List[str]] = None
    number_of_personas: Optional[int] = Field(None, ge=1, le=20)

class ExperimentResponse(BaseModel):
    id: str
    name: str
    product_name: str
    product_description: str
    target_audience: str
    research_objectives: List[str]
    number_of_personas: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

