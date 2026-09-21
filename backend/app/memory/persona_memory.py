import json
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.persona import Persona
from app.services.memory_service import MemoryService
from app.services.llm_service import get_llm_provider
from app.utils.prompts import MEMORY_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class PersonaMemoryManager:
    """
    Manages 3 memory types:
    1. Core Memory (Permanent demographics, personality traits)
    2. Behavioral Memory (Habits, decision patterns, preferences)
    3. Opinion Memory (Opinions developed during conversations)
    """

    @staticmethod
    def get_core_memory(persona: Persona) -> Dict[str, Any]:
        return {
            "name": persona.name,
            "age": persona.age,
            "occupation": persona.occupation,
            "location": persona.location,
            "demographics": persona.demographics or {},
            "personality_traits": persona.personality_traits or [],
            "psychological_profile": persona.psychological_profile or {}
        }

    @staticmethod
    def get_behavioral_memory(db: Session, persona: Persona) -> List[Dict[str, Any]]:
        # Retrieve explicit behavior memories stored in DB
        db_mems = MemoryService.get_memories_by_persona(db, persona.id, memory_type="behavior")
        mems = [{"topic": m.topic, "content": m.content, "importance": m.importance} for m in db_mems]
        
        # Combine with initial behavioral patterns if present
        if persona.behavioral_patterns:
            for pattern in persona.behavioral_patterns:
                mems.append({"topic": "habit", "content": pattern, "importance": 1.0})
        return mems

    @staticmethod
    def get_opinion_memory(persona: Persona) -> Dict[str, Any]:
        return persona.opinions or {}

    @staticmethod
    def format_memories_and_opinions_text(db: Session, persona: Persona) -> str:
        lines = []
        # Stated Opinions
        opinions = PersonaMemoryManager.get_opinion_memory(persona)
        if opinions:
            lines.append("Established Opinions:")
            for topic, data in opinions.items():
                if isinstance(data, dict):
                    op = data.get('opinion', '')
                    reason = data.get('reason', '')
                    lines.append(f" - [{topic}]: {op} (Reason: {reason})")
                else:
                    lines.append(f" - [{topic}]: {data}")

        # Behavioral patterns
        behaviors = PersonaMemoryManager.get_behavioral_memory(db, persona)
        if behaviors:
            lines.append("Behavioral Habits & Constraints:")
            for b in behaviors:
                lines.append(f" - {b.get('content')}")

        if not lines:
            return "No prior opinions or interactions stored."
        return "\n".join(lines)

    @staticmethod
    async def extract_and_store_new_memories(
        db: Session,
        persona: Persona,
        user_message: str,
        persona_response: str,
        llm_provider=None
    ) -> bool:
        """
        Uses LLM (or fallback) to extract new opinions/memories from the conversation turn and updates DB.
        """
        provider = llm_provider or get_llm_provider()
        prompt = MEMORY_EXTRACTION_PROMPT.format(
            name=persona.name,
            age=persona.age,
            occupation=persona.occupation,
            user_message=user_message,
            persona_response=persona_response
        )

        try:
            raw_result = await provider.generate_text(
                system_prompt="You extract structured memory opinions from conversations.",
                user_prompt=prompt
            )
            
            # Clean json fences if present
            cleaned = raw_result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            extracted_items = json.loads(cleaned)
            if isinstance(extracted_items, list) and len(extracted_items) > 0:
                # Save into DB memory table & update persona opinion map
                for item in extracted_items:
                    MemoryService.add_memory(
                        db=db,
                        persona_id=persona.id,
                        memory_type="opinion",
                        topic=item.get("topic", "general"),
                        content=f"Opinion: {item.get('opinion')} | Reason: {item.get('reason')}",
                        importance=float(item.get("importance", 1.0))
                    )
                MemoryService.update_persona_opinions_and_summary(db, persona, extracted_items)
                return True
        except Exception as e:
            logger.warning(f"Error extracting memory from turn: {e}")
            
        return False
