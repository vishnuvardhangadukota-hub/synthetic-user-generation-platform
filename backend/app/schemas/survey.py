from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

class QuestionCreate(BaseModel):
    question_text: str = Field(..., description="The survey question text")
    question_type: str = Field(
        "short_answer",
        description="Type of question: 'rating', 'yes_no', 'short_answer', 'opinion', 'open_ended'"
    )
    options: Optional[List[str]] = Field(default_factory=list, description="Optional choices or scale labels")
    order: int = Field(1, ge=1, description="Display order of question")

    @field_validator("question_text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question text cannot be empty or whitespace only")
        return v.strip()

    @field_validator("question_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        valid_types = {"rating", "yes_no", "short_answer", "opinion", "open_ended"}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid question type '{v}'. Must be one of {valid_types}")
        return v.lower()


class QuestionResponseSchema(BaseModel):
    id: str
    survey_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = []
    order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyCreate(BaseModel):
    title: str = Field(..., description="Survey title")
    description: Optional[str] = Field("", description="Survey description")

    @field_validator("title")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Survey title cannot be empty")
        return v.strip()


class SurveyResponseSchema(BaseModel):
    id: str
    experiment_id: str
    title: str
    description: Optional[str]
    status: str
    questions: List[QuestionResponseSchema] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyResponseItem(BaseModel):
    id: str
    experiment_id: str
    survey_id: str
    question_id: str
    persona_id: str
    persona_name: Optional[str] = ""
    answer: str
    rating_score: Optional[float] = None
    reasoning: Optional[str] = ""
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SurveyRunResponse(BaseModel):
    survey_id: str
    total_personas: int
    total_responses_generated: int
    responses: List[SurveyResponseItem]


class QuestionGroupedResponses(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    responses: List[SurveyResponseItem]


class SurveyResponsesGrouped(BaseModel):
    survey_id: str
    experiment_id: str
    grouped_by_question: List[QuestionGroupedResponses]
