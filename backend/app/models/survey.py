import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_survey_id():
    return f"srv_{uuid.uuid4().hex[:12]}"

def generate_question_id():
    return f"sq_{uuid.uuid4().hex[:12]}"

def generate_response_id():
    return f"sresp_{uuid.uuid4().hex[:12]}"

class Survey(Base):
    __tablename__ = "surveys"

    id = Column(String(50), primary_key=True, default=generate_survey_id)
    experiment_id = Column(String(50), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True, default="")
    status = Column(String(50), nullable=False, default="draft")  # 'draft', 'completed'
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    experiment = relationship("Experiment")
    questions = relationship("SurveyQuestion", back_populates="survey", cascade="all, delete-orphan", order_by="SurveyQuestion.order")
    responses = relationship("SurveyResponse", back_populates="survey", cascade="all, delete-orphan")


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    id = Column(String(50), primary_key=True, default=generate_question_id)
    survey_id = Column(String(50), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default="short_answer") # 'rating', 'yes_no', 'short_answer', 'opinion', 'open_ended'
    options = Column(JSON, nullable=True, default=list) # Optional choices for multiple choice / rating scale
    order = Column(Integer, nullable=False, default=1)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    survey = relationship("Survey", back_populates="questions")
    responses = relationship("SurveyResponse", back_populates="question", cascade="all, delete-orphan")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    id = Column(String(50), primary_key=True, default=generate_response_id)
    experiment_id = Column(String(50), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    survey_id = Column(String(50), ForeignKey("surveys.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(50), ForeignKey("survey_questions.id", ondelete="CASCADE"), nullable=False)
    persona_id = Column(String(50), ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    
    answer = Column(Text, nullable=False)
    rating_score = Column(Float, nullable=True) # Used for rating/numerical questions (e.g. 1-5 or 1-10)
    reasoning = Column(Text, nullable=True, default="")
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    survey = relationship("Survey", back_populates="responses")
    question = relationship("SurveyQuestion", back_populates="responses")
    persona = relationship("Persona")
