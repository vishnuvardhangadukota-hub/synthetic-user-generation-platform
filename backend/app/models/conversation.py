import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_conversation_id():
    return f"conv_{uuid.uuid4().hex[:12]}"

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(50), primary_key=True, default=generate_conversation_id)
    persona_id = Column(String(50), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    
    user_message = Column(Text, nullable=False)
    persona_response = Column(Text, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    persona = relationship("Persona", back_populates="conversations")
