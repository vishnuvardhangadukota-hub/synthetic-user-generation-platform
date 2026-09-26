import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_usage_score_id():
    return f"uscore_{uuid.uuid4().hex[:12]}"

class UsageScoreReport(Base):
    __tablename__ = "usage_score_reports"

    id = Column(String(50), primary_key=True, default=generate_usage_score_id)
    experiment_id = Column(String(50), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    overall_score = Column(Float, nullable=False)
    would_use_percentage = Column(Float, nullable=False)
    segmentation_breakdown = Column(JSON, nullable=False, default=dict)
    persona_scores = Column(JSON, nullable=False, default=list)
    calculation_method = Column(Text, nullable=False)
    limitations = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    experiment = relationship("Experiment")
