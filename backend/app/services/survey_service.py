import json
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.survey import Survey, SurveyQuestion, SurveyResponse
from app.models.persona import Persona
from app.models.experiment import Experiment
from app.schemas.survey import SurveyCreate, QuestionCreate, SurveyResponseItem
from app.services.persona_service import PersonaService
from app.services.memory_service import MemoryService
from app.services.llm_service import get_llm_provider
from app.memory.persona_memory import PersonaMemoryManager
from app.utils.prompts import SURVEY_QUESTION_ANSWER_PROMPT

logger = logging.getLogger(__name__)

class SurveyService:
    @staticmethod
    def create_survey(db: Session, experiment_id: str, schema: SurveyCreate) -> Survey:
        survey = Survey(
            experiment_id=experiment_id,
            title=schema.title,
            description=schema.description or "",
            status="draft"
        )
        db.add(survey)
        db.commit()
        db.refresh(survey)
        return survey

    @staticmethod
    def get_surveys_by_experiment(db: Session, experiment_id: str) -> List[Survey]:
        return db.query(Survey).filter(Survey.experiment_id == experiment_id).order_by(Survey.created_at.desc()).all()

    @staticmethod
    def get_survey_by_id(db: Session, survey_id: str) -> Optional[Survey]:
        return db.query(Survey).filter(Survey.id == survey_id).first()

    @staticmethod
    def add_question(db: Session, survey_id: str, schema: QuestionCreate) -> SurveyQuestion:
        # Determine next order integer if not specified
        existing_count = db.query(SurveyQuestion).filter(SurveyQuestion.survey_id == survey_id).count()
        question_order = schema.order if schema.order > 1 else (existing_count + 1)

        question = SurveyQuestion(
            survey_id=survey_id,
            question_text=schema.question_text,
            question_type=schema.question_type,
            options=schema.options or [],
            order=question_order
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question

    @staticmethod
    def get_survey_questions(db: Session, survey_id: str) -> List[SurveyQuestion]:
        return db.query(SurveyQuestion).filter(SurveyQuestion.survey_id == survey_id).order_by(SurveyQuestion.order.asc()).all()

    @staticmethod
    async def run_survey(db: Session, survey_id: str, llm_provider=None) -> Dict[str, Any]:
        """
        Runs a survey across all personas in the experiment.
        Generates tailored responses for each persona per question based on their attributes and memory.
        Prevents duplicate execution if responses already exist for the survey.
        """
        survey = SurveyService.get_survey_by_id(db, survey_id)
        if not survey:
            raise ValueError(f"Survey with ID '{survey_id}' not found")

        # Check if survey already ran
        existing_responses_count = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).count()
        if existing_responses_count > 0:
            logger.info(f"Survey '{survey_id}' already has responses. Returning existing survey responses.")
            responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).all()
            return {
                "survey_id": survey.id,
                "total_personas": len(set(r.persona_id for r in responses)),
                "total_responses_generated": len(responses),
                "responses": responses
            }

        questions = SurveyService.get_survey_questions(db, survey_id)
        if not questions:
            raise ValueError(f"Survey '{survey_id}' has no questions. Please add questions before running.")

        personas = PersonaService.get_personas_by_experiment(db, survey.experiment_id)
        if not personas:
            raise ValueError(f"Experiment '{survey.experiment_id}' has no personas. Please generate personas first.")

        provider = llm_provider or get_llm_provider()
        created_responses = []

        for persona in personas:
            memories_text = PersonaMemoryManager.format_memories_and_opinions_text(db, persona)
            decision_style = persona.psychological_profile.get("decision_style", "Balanced")

            for question in questions:
                options_str = ", ".join(question.options) if question.options else "None"
                user_prompt = SURVEY_QUESTION_ANSWER_PROMPT.format(
                    name=persona.name,
                    occupation=persona.occupation,
                    age=persona.age,
                    demographics=json.dumps(persona.demographics),
                    personality_traits=json.dumps(persona.personality_traits),
                    behavioral_patterns=json.dumps(persona.behavioral_patterns),
                    decision_style=decision_style,
                    memories_and_opinions=memories_text,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    options=options_str
                )

                try:
                    resp_data = await provider.generate_json(
                        system_prompt=f"You roleplay as persona {persona.name} answering a survey.",
                        user_prompt=user_prompt
                    )
                    answer_text = resp_data.get("answer", "No response provided")
                    rating_score = resp_data.get("rating_score")
                    reasoning_text = resp_data.get("reasoning", "")
                    
                    if rating_score is not None:
                        try:
                            rating_score = float(rating_score)
                        except (ValueError, TypeError):
                            rating_score = None
                except Exception as e:
                    logger.warning(f"Error generating survey response for persona {persona.id}, question {question.id}: {e}")
                    answer_text = f"As {persona.name}, I evaluate this based on my daily routine."
                    rating_score = 3.0 if question.question_type == "rating" else None
                    reasoning_text = "Generated fallback answer due to response processing error."

                s_resp = SurveyResponse(
                    experiment_id=survey.experiment_id,
                    survey_id=survey.id,
                    question_id=question.id,
                    persona_id=persona.id,
                    answer=answer_text,
                    rating_score=rating_score,
                    reasoning=reasoning_text
                )
                db.add(s_resp)
                created_responses.append(s_resp)

        survey.status = "completed"
        db.commit()
        for r in created_responses:
            db.refresh(r)

        return {
            "survey_id": survey.id,
            "total_personas": len(personas),
            "total_responses_generated": len(created_responses),
            "responses": created_responses
        }

    @staticmethod
    def get_grouped_responses(db: Session, survey_id: str) -> Dict[str, Any]:
        """
        Retrieves responses for a survey grouped by question, with persona name and answer details
        for side-by-side comparison.
        """
        survey = SurveyService.get_survey_by_id(db, survey_id)
        if not survey:
            raise ValueError(f"Survey with ID '{survey_id}' not found")

        questions = SurveyService.get_survey_questions(db, survey_id)
        grouped_list = []

        for q in questions:
            responses = (
                db.query(SurveyResponse)
                .filter(SurveyResponse.question_id == q.id)
                .order_by(SurveyResponse.created_at.asc())
                .all()
            )
            
            resp_items = []
            for r in responses:
                item_dict = {
                    "id": r.id,
                    "experiment_id": r.experiment_id,
                    "survey_id": r.survey_id,
                    "question_id": r.question_id,
                    "persona_id": r.persona_id,
                    "persona_name": r.persona.name if r.persona else "Unknown",
                    "answer": r.answer,
                    "rating_score": r.rating_score,
                    "reasoning": r.reasoning,
                    "created_at": r.created_at
                }
                resp_items.append(item_dict)

            grouped_list.append({
                "question_id": q.id,
                "question_text": q.question_text,
                "question_type": q.question_type,
                "responses": resp_items
            })

        return {
            "survey_id": survey.id,
            "experiment_id": survey.experiment_id,
            "grouped_by_question": grouped_list
        }
