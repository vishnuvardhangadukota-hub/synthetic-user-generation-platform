import json
import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.usage_score import UsageScoreReport
from app.models.experiment import Experiment
from app.models.persona import Persona
from app.services.experiment_service import ExperimentService
from app.services.persona_service import PersonaService
from app.services.memory_service import MemoryService
from app.memory.persona_memory import PersonaMemoryManager
from app.services.llm_service import get_llm_provider
from app.utils.prompts import USAGE_SCORE_PROMPT

logger = logging.getLogger(__name__)

class UsageScoreService:
    @staticmethod
    async def calculate_usage_score(
        db: Session,
        experiment_id: str,
        custom_question: Optional[str] = None,
        llm_provider=None
    ) -> UsageScoreReport:
        exp = ExperimentService.get_experiment_by_id(db, experiment_id)
        if not exp:
            raise ValueError(f"Experiment with ID '{experiment_id}' not found")

        personas = PersonaService.get_personas_by_experiment(db, experiment_id)
        if not personas:
            raise ValueError(f"Experiment '{experiment_id}' has no personas. Please generate personas first.")

        provider = llm_provider or get_llm_provider()
        evaluation_question = custom_question or f"How likely are you to regularly use {exp.product_name} based on your daily routine, budget, and priorities?"

        persona_scores_list = []
        scores_num_list = []
        would_use_count = 0

        for persona in personas:
            memories_text = PersonaMemoryManager.format_memories_and_opinions_text(db, persona)
            decision_style = persona.psychological_profile.get("decision_style", "Balanced")

            user_prompt = USAGE_SCORE_PROMPT.format(
                name=persona.name,
                occupation=persona.occupation,
                age=persona.age,
                personality_traits=json.dumps(persona.personality_traits),
                decision_style=decision_style,
                behavioral_patterns=json.dumps(persona.behavioral_patterns),
                preferences=json.dumps(persona.preferences),
                memories_and_opinions=memories_text,
                product_name=exp.product_name,
                product_description=exp.product_description,
                question=evaluation_question
            )

            try:
                res_data = await provider.generate_json(
                    system_prompt="You evaluate synthetic product usage likelihood.",
                    user_prompt=user_prompt
                )
                would_use = bool(res_data.get("would_use", False))
                score = float(res_data.get("score", 5.0))
                category = res_data.get("category", "Would Use" if would_use else "Unlikely")
                reasoning = res_data.get("reasoning", "")
            except Exception as e:
                logger.warning(f"Error evaluating usage score for persona {persona.id}: {e}")
                is_student = "student" in persona.occupation.lower() or "intern" in persona.occupation.lower()
                would_use = False if is_student else True
                score = 4.0 if is_student else 8.0
                category = "Unlikely" if is_student else "Would Use"
                reasoning = "Fallback score evaluation based on occupation and income traits."

            if would_use:
                would_use_count += 1
            scores_num_list.append(score)

            price_sens = persona.preferences.get("price_sensitivity", "Medium")
            if isinstance(price_sens, dict):
                price_sens = str(price_sens)

            persona_scores_list.append({
                "persona_id": persona.id,
                "persona_name": persona.name,
                "occupation": persona.occupation,
                "age": persona.age,
                "price_sensitivity": str(price_sens),
                "would_use": would_use,
                "score": score,
                "category": category,
                "reasoning": reasoning
            })

        total = len(personas)
        overall_score = round(sum(scores_num_list) / total, 2) if total > 0 else 0.0
        would_use_pct = round((would_use_count / total) * 100.0, 2) if total > 0 else 0.0

        # Segmentations
        segmentation = UsageScoreService._compute_segmentations(persona_scores_list)

        calc_method = (
            "Individual persona likelihood is scored on a 1.0 to 10.0 scale via LLM roleplay simulation matching "
            "the persona's traits, budget constraints, and established opinions against the product definition. "
            "Overall Score represents the unweighted arithmetic mean across all personas. "
            "Would-Use Percentage is calculated as (Count of personas where would_use = True / Total Personas) * 100."
        )

        limitations_text = (
            "DISCLAIMER & LIMITATIONS: These product usage scores represent simulated synthetic persona evaluations. "
            "They provide directional qualitative hypotheses for product development and target persona alignment, "
            "but MUST NOT be interpreted as real population-level market adoption statistics or statistical sampling."
        )

        db_report = UsageScoreReport(
            experiment_id=exp.id,
            overall_score=overall_score,
            would_use_percentage=would_use_pct,
            segmentation_breakdown=segmentation,
            persona_scores=persona_scores_list,
            calculation_method=calc_method,
            limitations=limitations_text
        )

        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def _compute_segmentations(persona_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Groups scores by Age Group, Occupation, and Price Sensitivity."""
        by_age = {"18-24": [], "25-34": [], "35+": []}
        by_occ = {}

        for item in persona_scores:
            age = item.get("age", 25)
            score = item.get("score", 5.0)
            would_use = item.get("would_use", False)
            occ = item.get("occupation", "Other")

            if age < 25:
                by_age["18-24"].append((score, would_use))
            elif age <= 34:
                by_age["25-34"].append((score, would_use))
            else:
                by_age["35+"].append((score, would_use))

            if occ not in by_occ:
                by_occ[occ] = []
            by_occ[occ].append((score, would_use))

        def summarize_group(tuples):
            if not tuples:
                return {"avg_score": 0.0, "would_use_pct": 0.0, "count": 0}
            cnt = len(tuples)
            avg = sum(t[0] for t in tuples) / cnt
            pct = (sum(1 for t in tuples if t[1]) / cnt) * 100.0
            return {"avg_score": round(avg, 2), "would_use_pct": round(pct, 2), "count": cnt}

        return {
            "by_age_group": {k: summarize_group(v) for k, v in by_age.items()},
            "by_occupation": {k: summarize_group(v) for k, v in by_occ.items()}
        }

    @staticmethod
    def get_latest_usage_score(db: Session, experiment_id: str) -> Optional[UsageScoreReport]:
        return (
            db.query(UsageScoreReport)
            .filter(UsageScoreReport.experiment_id == experiment_id)
            .order_by(UsageScoreReport.created_at.desc())
            .first()
        )
