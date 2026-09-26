from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict

class ThemeItem(BaseModel):
    theme: str
    description: str
    supporting_quotes: List[str] = []

class SentimentDistribution(BaseModel):
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    counts: Dict[str, int]

class SupportingReference(BaseModel):
    reference_id: str
    source_type: str  # 'survey' or 'interview'
    persona_id: str
    persona_name: str
    content_snippet: str

class InsightReportResponse(BaseModel):
    id: str
    experiment_id: str
    recurring_themes: List[Dict[str, Any]]
    sentiment_distribution: Dict[str, Any]
    agreement_patterns: List[str]
    disagreements: List[str]
    behavioral_trends: List[str]
    supporting_references: List[Dict[str, Any]]
    limitations: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
