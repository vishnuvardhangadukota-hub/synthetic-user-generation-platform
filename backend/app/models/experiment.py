import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_exp_id():
    return f"exp_{uuid.uuid4().hex[:12]}"

class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(50), primary_key=True, default=generate_exp_id)
    name = Column(String(255), nullable=False)
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=False)
    target_audience = Column(Text, nullable=False)
    research_objectives = Column(JSON, nullable=False)
    number_of_personas = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    personas = relationship("Persona", back_populates="experiment", cascade="all, delete-orphan")
