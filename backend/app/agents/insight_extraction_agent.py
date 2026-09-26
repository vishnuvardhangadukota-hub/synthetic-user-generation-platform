import json
import logging
from typing import Dict, Any, List
from app.services.llm_service import get_llm_provider, DeterministicFallbackGenerator
from app.utils.prompts import INSIGHT_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)

class InsightExtractionAgent:
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider or get_llm_provider()

    async def extract_insights(
        self,
        product_name: str,
        product_description: str,
        collected_data_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyzes survey responses and interview conversation logs to extract structured insights.
        Returns JSON report object.
        """
        # Format collected data text
        data_text_lines = []
        for item in collected_data_items:
            source = item.get("source_type", "survey")
            persona_name = item.get("persona_name", "Persona")
            text = item.get("content", "")
            ref_id = item.get("reference_id", "")
            data_text_lines.append(f"[{source.upper()} | Ref: {ref_id} | Persona: {persona_name}]: {text}")

        collected_text = "\n".join(data_text_lines) if data_text_lines else "No responses collected yet."

        user_prompt = INSIGHT_EXTRACTION_PROMPT.format(
            product_name=product_name,
            product_description=product_description,
            collected_data_text=collected_text
        )

        system_prompt = "You are an AI research analyst producing structured JSON user research insights."

        try:
            insight_json = await self.llm_provider.generate_json(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            return self._validate_and_sanitize_insights(insight_json, collected_data_items)

        except Exception as e:
            logger.warning(f"Error in LLM insight extraction: {e}. Running fallback generator.")
            fallback = DeterministicFallbackGenerator()
            insight_json = await fallback.generate_json(system_prompt=system_prompt, user_prompt=user_prompt)
            return self._validate_and_sanitize_insights(insight_json, collected_data_items)

    def _validate_and_sanitize_insights(
        self,
        raw_json: Dict[str, Any],
        collected_data_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ensures all required insight fields exist and are properly formatted."""
        recurring_themes = raw_json.get("recurring_themes", [])
        if not isinstance(recurring_themes, list):
            recurring_themes = []

        sentiment_dist = raw_json.get("sentiment_distribution", {})
        if not isinstance(sentiment_dist, dict):
            sentiment_dist = {
                "positive_percentage": 33.3,
                "neutral_percentage": 33.3,
                "negative_percentage": 33.4,
                "counts": {"positive": 1, "neutral": 1, "negative": 1}
            }

        agreement_patterns = raw_json.get("agreement_patterns", [])
        if not isinstance(agreement_patterns, list):
            agreement_patterns = []

        disagreements = raw_json.get("disagreements", [])
        if not isinstance(disagreements, list):
            disagreements = []

        behavioral_trends = raw_json.get("behavioral_trends", [])
        if not isinstance(behavioral_trends, list):
            behavioral_trends = []

        supporting_refs = raw_json.get("supporting_references", [])
        if not isinstance(supporting_refs, list) or len(supporting_refs) == 0:
            # Populate references from input items if empty
            supporting_refs = []
            for item in collected_data_items[:5]:
                supporting_refs.append({
                    "reference_id": item.get("reference_id", "ref_001"),
                    "source_type": item.get("source_type", "survey"),
                    "persona_id": item.get("persona_id", "p_001"),
                    "persona_name": item.get("persona_name", "Persona"),
                    "content_snippet": item.get("content", "")[:150]
                })

        limitations = raw_json.get(
            "limitations",
            "DISCLAIMER: These insights represent synthetic persona simulation models derived for exploratory research. They do not constitute population-level statistical evidence."
        )

        return {
            "recurring_themes": recurring_themes,
            "sentiment_distribution": sentiment_dist,
            "agreement_patterns": agreement_patterns,
            "disagreements": disagreements,
            "behavioral_trends": behavioral_trends,
            "supporting_references": supporting_refs,
            "limitations": limitations
        }
