import json
import logging
from typing import List, Dict, Any, Tuple
from app.services.llm_service import get_llm_provider, DeterministicFallbackGenerator
from app.utils.prompts import PERSONA_GENERATION_SYSTEM_PROMPT, PERSONA_GENERATION_USER_PROMPT
from app.utils.validators import validate_personas_list

logger = logging.getLogger(__name__)

class PersonaGenerationAgent:
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider or get_llm_provider()

    async def generate_personas(
        self,
        product_name: str,
        product_description: str,
        target_audience: str,
        research_objectives: List[str],
        number_of_personas: int = 5
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Generates realistic and diverse synthetic personas based on experiment requirements.
        Returns a tuple of (personas_data_list, is_synthetic_test_data).
        """
        objectives_formatted = "\n".join([f"- {obj}" for obj in research_objectives])
        user_prompt = PERSONA_GENERATION_USER_PROMPT.format(
            product_name=product_name,
            product_description=product_description,
            target_audience=target_audience,
            research_objectives_formatted=objectives_formatted,
            number_of_personas=number_of_personas
        )

        is_fallback = isinstance(self.llm_provider, DeterministicFallbackGenerator)

        try:
            raw_response = await self.llm_provider.generate_json(
                system_prompt=PERSONA_GENERATION_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
            
            personas_raw = raw_response.get("personas", [])
            if not personas_raw and isinstance(raw_response, list):
                personas_raw = raw_response

            validated_personas = validate_personas_list(personas_raw)
            return validated_personas, is_fallback

        except Exception as e:
            logger.warning(f"LLM persona generation failed or produced invalid JSON: {e}. Executing fallback generator.")
            fallback = DeterministicFallbackGenerator()
            raw_response = await fallback.generate_json(
                system_prompt=PERSONA_GENERATION_SYSTEM_PROMPT,
                user_prompt=user_prompt
            )
            personas_raw = raw_response.get("personas", [])
            validated_personas = validate_personas_list(personas_raw)
            return validated_personas, True
