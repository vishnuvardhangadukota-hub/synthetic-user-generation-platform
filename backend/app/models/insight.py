import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_insight_id():
    return f"ins_{uuid.uuid4().hex[:12]}"

class InsightReport(Base):
    __tablename__ = "insight_reports"

    id = Column(String(50), primary_key=True, default=generate_insight_id)
    experiment_id = Column(String(50), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    recurring_themes = Column(JSON, nullable=False, default=list)
    sentiment_distribution = Column(JSON, nullable=False, default=dict)
    agreement_patterns = Column(JSON, nullable=False, default=list)
    disagreements = Column(JSON, nullable=False, default=list)
    behavioral_trends = Column(JSON, nullable=False, default=list)
    supporting_references = Column(JSON, nullable=False, default=list)
    limitations = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    experiment = relationship("Experiment")
