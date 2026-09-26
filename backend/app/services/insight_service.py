import logging
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from app.models.insight import InsightReport
from app.models.experiment import Experiment
from app.models.survey import SurveyResponse, SurveyQuestion
from app.models.conversation import Conversation
from app.models.persona import Persona
from app.agents.insight_extraction_agent import InsightExtractionAgent
from app.services.experiment_service import ExperimentService

logger = logging.getLogger(__name__)

class InsightService:
    @staticmethod
    async def generate_insights_for_experiment(db: Session, experiment_id: str, llm_provider=None) -> InsightReport:
        exp = ExperimentService.get_experiment_by_id(db, experiment_id)
        if not exp:
            raise ValueError(f"Experiment with ID '{experiment_id}' not found")

        # Gather survey responses for this experiment
        survey_responses = (
            db.query(SurveyResponse)
            .filter(SurveyResponse.experiment_id == experiment_id)
            .all()
        )

        # Gather interview conversations for personas in this experiment
        personas = db.query(Persona).filter(Persona.experiment_id == experiment_id).all()
        persona_ids = [p.id for p in personas]
        
        conversations = []
        if persona_ids:
            conversations = (
                db.query(Conversation)
                .filter(Conversation.persona_id.in_(persona_ids))
                .all()
            )

        if not survey_responses and not conversations:
            raise ValueError(
                f"No survey responses or interview conversations found for experiment '{experiment_id}'. "
                "Please run a survey or converse with personas before generating insights."
            )

        # Prepare collected items with metadata and snippets
        collected_items = []
        for sr in survey_responses:
            p_name = sr.persona.name if sr.persona else "Persona"
            q_text = sr.question.question_text if sr.question else "Question"
            collected_items.append({
                "reference_id": sr.id,
                "source_type": "survey",
                "persona_id": sr.persona_id,
                "persona_name": p_name,
                "content": f"Question: '{q_text}' -> Answer: {sr.answer} (Reasoning: {sr.reasoning})"
            })

        for conv in conversations:
            p_name = conv.persona.name if conv.persona else "Persona"
            collected_items.append({
                "reference_id": conv.id,
                "source_type": "interview",
                "persona_id": conv.persona_id,
                "persona_name": p_name,
                "content": f"User: '{conv.user_message}' -> Persona: {conv.persona_response}"
            })

        agent = InsightExtractionAgent(llm_provider=llm_provider)
        insights_data = await agent.extract_insights(
            product_name=exp.product_name,
            product_description=exp.product_description,
            collected_data_items=collected_items
        )

        db_report = InsightReport(
            experiment_id=exp.id,
            recurring_themes=insights_data["recurring_themes"],
            sentiment_distribution=insights_data["sentiment_distribution"],
            agreement_patterns=insights_data["agreement_patterns"],
            disagreements=insights_data["disagreements"],
            behavioral_trends=insights_data["behavioral_trends"],
            supporting_references=insights_data["supporting_references"],
            limitations=insights_data["limitations"]
        )

        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def get_latest_insight(db: Session, experiment_id: str) -> Optional[InsightReport]:
        return (
            db.query(InsightReport)
            .filter(InsightReport.experiment_id == experiment_id)
            .order_by(InsightReport.created_at.desc())
            .first()
        )
