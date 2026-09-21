import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, JSON, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_persona_id():
    return f"persona_{uuid.uuid4().hex[:12]}"

class Persona(Base):
    __tablename__ = "personas"

    id = Column(String(50), primary_key=True, default=generate_persona_id)
    experiment_id = Column(String(50), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False, default="Hyderabad")

    demographics = Column(JSON, nullable=False, default=dict)
    personality_traits = Column(JSON, nullable=False, default=list)
    behavioral_patterns = Column(JSON, nullable=False, default=list)
    psychological_profile = Column(JSON, nullable=False, default=dict)
    preferences = Column(JSON, nullable=False, default=dict)
    opinions = Column(JSON, nullable=False, default=dict)
    
    memory_summary = Column(Text, nullable=False, default="")
    is_synthetic_test_data = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    experiment = relationship("Experiment", back_populates="personas")
    memories = relationship("PersonaMemory", back_populates="persona", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="persona", cascade="all, delete-orphan")
