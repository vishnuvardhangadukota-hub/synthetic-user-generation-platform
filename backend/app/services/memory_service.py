from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.persona import Persona
from app.models.memory import PersonaMemory
from app.models.conversation import Conversation
from app.schemas.memory import MemoryCreate

class MemoryService:
    @staticmethod
    def add_memory(
        db: Session,
        persona_id: str,
        memory_type: str,
        topic: str,
        content: str,
        importance: float = 1.0
    ) -> PersonaMemory:
        mem = PersonaMemory(
            persona_id=persona_id,
            memory_type=memory_type,
            topic=topic,
            content=content,
            importance=importance
        )
        db.add(mem)
        db.commit()
        db.refresh(mem)
        return mem

    @staticmethod
    def add_conversation_turn(
        db: Session,
        persona_id: str,
        user_message: str,
        persona_response: str
    ) -> Conversation:
        conv = Conversation(
            persona_id=persona_id,
            user_message=user_message,
            persona_response=persona_response
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    @staticmethod
    def get_memories_by_persona(
        db: Session,
        persona_id: str,
        memory_type: Optional[str] = None
    ) -> List[PersonaMemory]:
        query = db.query(PersonaMemory).filter(PersonaMemory.persona_id == persona_id)
        if memory_type:
            query = query.filter(PersonaMemory.memory_type == memory_type)
        return query.order_by(PersonaMemory.created_at.asc()).all()

    @staticmethod
    def get_conversation_history(
        db: Session,
        persona_id: str,
        limit: int = 20
    ) -> List[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.persona_id == persona_id)
            .order_by(Conversation.created_at.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def update_persona_opinions_and_summary(
        db: Session,
        persona: Persona,
        new_opinions: List[Dict[str, Any]]
    ):
        """Updates the structured opinions dict and memory_summary text on the Persona model."""
        opinions_map = dict(persona.opinions or {})
        summary_lines = []

        for item in new_opinions:
            topic = item.get("topic", "general")
            opinions_map[topic] = {
                "opinion": item.get("opinion"),
                "reason": item.get("reason"),
                "importance": item.get("importance", 1.0)
            }
            summary_lines.append(f"Topic '{topic}': {item.get('opinion')} ({item.get('reason')})")

        persona.opinions = opinions_map
        if summary_lines:
            existing_summary = persona.memory_summary or ""
            new_text = "; ".join(summary_lines)
            persona.memory_summary = f"{existing_summary}\n{new_text}".strip()

        db.commit()
        db.refresh(persona)

    @staticmethod
    def get_full_persona_memory(db: Session, persona: Persona) -> Dict[str, Any]:
        """Returns structured full memory payload for persona memory API."""
        memories = MemoryService.get_memories_by_persona(db, persona.id)
        conversations = MemoryService.get_conversation_history(db, persona.id)

        behavioral_mems = [
            {"id": m.id, "topic": m.topic, "content": m.content, "importance": m.importance}
            for m in memories if m.memory_type == "behavior"
        ]
        
        opinions_list = []
        if persona.opinions:
            for topic, details in persona.opinions.items():
                if isinstance(details, dict):
                    opinions_list.append({
                        "topic": topic,
                        "opinion": details.get("opinion"),
                        "reason": details.get("reason"),
                        "importance": details.get("importance", 1.0)
                    })
                else:
                    opinions_list.append({"topic": topic, "opinion": str(details)})

        core_attributes = {
            "name": persona.name,
            "age": persona.age,
            "occupation": persona.occupation,
            "location": persona.location,
            "demographics": persona.demographics,
            "personality_traits": persona.personality_traits
        }

        return {
            "persona_id": persona.id,
            "core_attributes": core_attributes,
            "behavioral_memories": behavioral_mems,
            "opinions": opinions_list,
            "conversation_history": conversations,
            "memory_summary": persona.memory_summary or ""
        }
