import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_memory_id():
    return f"mem_{uuid.uuid4().hex[:12]}"

class PersonaMemory(Base):
    __tablename__ = "persona_memories"

    id = Column(String(50), primary_key=True, default=generate_memory_id)
    persona_id = Column(String(50), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    
    memory_type = Column(String(50), nullable=False) # 'core', 'behavior', 'opinion', 'conversation'
    topic = Column(String(255), nullable=False, default="general")
    content = Column(Text, nullable=False)
    importance = Column(Float, nullable=False, default=1.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    persona = relationship("Persona", back_populates="memories")
