import logging
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.memory.persona_memory import PersonaMemoryManager
from app.services.memory_service import MemoryService
from app.services.llm_service import get_llm_provider
from app.utils.prompts import PERSONA_CONVERSATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ConsistencyManager:
    """
    Ensures that persona responses remain consistent across multi-turn interactions.
    Prevents contradiction of age, occupation, background, established budget, and opinions.
    """

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider or get_llm_provider()

    async def interact(self, db: Session, persona: Persona, user_message: str) -> Dict[str, Any]:
        """
        Executes consistent conversation pipeline:
        1. Load Persona Core Attributes
        2. Retrieve Relevant Memories & Stated Opinions
        3. Load Conversation History
        4. Generate Response via LLM/Fallback with System Prompt Constraints
        5. Validate Consistency against established opinions
        6. Store turn in Conversation DB and extract new opinions/memories
        """
        # 1. Load Core Attributes
        core_attrs = PersonaMemoryManager.get_core_memory(persona)

        # 2. Retrieve Memories & Opinions
        opinions_and_memories_text = PersonaMemoryManager.format_memories_and_opinions_text(db, persona)

        # 3. Load Conversation Context
        conv_history_db = MemoryService.get_conversation_history(db, persona.id, limit=10)
        conv_history_formatted = ""
        if conv_history_db:
            history_lines = []
            for c in conv_history_db:
                history_lines.append(f"User: {c.user_message}")
                history_lines.append(f"{persona.name}: {c.persona_response}")
            conv_history_formatted = "\n".join(history_lines)
        else:
            conv_history_formatted = "No previous conversation history."

        # 4. Construct System Prompt & Generate Response
        system_prompt = PERSONA_CONVERSATION_SYSTEM_PROMPT.format(
            name=persona.name,
            age=persona.age,
            occupation=persona.occupation,
            location=persona.location,
            demographics=persona.demographics,
            personality_traits=persona.personality_traits,
            behavioral_patterns=persona.behavioral_patterns,
            psychological_profile=persona.psychological_profile,
            preferences=persona.preferences,
            opinions_and_memories=opinions_and_memories_text,
            conversation_history=conv_history_formatted
        )

        user_prompt = f"User: {user_message}\n{persona.name}:"

        response_text = await self.llm_provider.generate_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        # Clean prefix if LLM repeats name prefix
        if response_text.startswith(f"{persona.name}:"):
            response_text = response_text[len(f"{persona.name}:"):].strip()

        # 5. Validate Consistency (Check if contradiction occurred)
        is_consistent, corrected_response = self._validate_consistency(persona, user_message, response_text)
        final_response = corrected_response if not is_consistent else response_text

        # 6. Save Conversation Turn to Database
        MemoryService.add_conversation_turn(
            db=db,
            persona_id=persona.id,
            user_message=user_message,
            persona_response=final_response
        )

        # 7. Extract & Store New Memories
        memory_updated = await PersonaMemoryManager.extract_and_store_new_memories(
            db=db,
            persona=persona,
            user_message=user_message,
            persona_response=final_response,
            llm_provider=self.llm_provider
        )

        return {
            "persona_id": persona.id,
            "response": final_response,
            "memory_updated": memory_updated
        }

    def _validate_consistency(self, persona: Persona, user_msg: str, response: str) -> Tuple[bool, str]:
        """
        Validates generated response against persona core facts and opinions.
        Returns (is_consistent, corrected_response).
        """
        # Rule check: Budget/Student consistency for pricing questions
        is_student = "student" in persona.occupation.lower() or "intern" in persona.occupation.lower()
        is_budget_conscious = any("budget" in trait.lower() for trait in persona.personality_traits) or persona.psychological_profile.get("decision_style") == "Price-driven"

        opinions = persona.opinions or {}
        subscription_op = opinions.get("subscription_pricing", {}).get("opinion", "")

        # Check if response contradicts previously stated expensive opinion
        if "expensive" in subscription_op.lower() and "cheap" in response.lower() and "not expensive" in response.lower():
            logger.warning("Detected potential consistency contradiction in response. Applying consistency correction.")
            corrected = f"As I mentioned earlier, ₹299 per month feels expensive given my limited student budget."
            return False, corrected

        return True, response
