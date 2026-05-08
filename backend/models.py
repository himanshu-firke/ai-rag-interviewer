"""
SQLAlchemy ORM models for the interview screening system.
Stores candidates, sessions, questions/answers, and reports.
"""

import datetime
import json
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class SessionStatus(str, enum.Enum):
    """Interview session status."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    """Authenticated user accounts."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="user")


class Candidate(Base):
    """Stores candidate information and parsed resume data."""
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    resume_text = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # JSON string of extracted skills
    technologies = Column(Text, nullable=True)  # JSON string of technologies
    experience_level = Column(String(50), nullable=True)  # junior/mid/senior
    domain_exposure = Column(Text, nullable=True)  # JSON string of domains
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    sessions = relationship("InterviewSession", back_populates="candidate")

    def get_skills_list(self) -> list:
        """Return skills as a Python list."""
        if self.skills:
            return json.loads(self.skills)
        return []

    def get_technologies_list(self) -> list:
        """Return technologies as a Python list."""
        if self.technologies:
            return json.loads(self.technologies)
        return []


class InterviewSession(Base):
    """Tracks a single interview session."""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    role = Column(String(100), nullable=False)
    status = Column(String(20), default=SessionStatus.CREATED.value)
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    candidate = relationship("Candidate", back_populates="sessions")
    user = relationship("User", back_populates="sessions")
    question_answers = relationship("QuestionAnswer", back_populates="session", order_by="QuestionAnswer.order")
    report = relationship("SessionReport", back_populates="session", uselist=False)


class QuestionAnswer(Base):
    """Stores each question-answer pair within a session."""
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Question number in the session

    # Question details
    question_text = Column(Text, nullable=False)
    question_topic = Column(String(200), nullable=True)
    question_type = Column(String(50), nullable=True)  # conceptual, applied, scenario, debugging, coding, mcq
    difficulty = Column(String(20), nullable=True)  # easy, medium, hard
    context_used = Column(Text, nullable=True)  # Retrieved context that generated this question

    # Coding question fields
    code_template = Column(Text, nullable=True)  # Starter code for coding questions
    expected_language = Column(String(50), nullable=True)  # e.g., "python"

    # MCQ question fields
    options = Column(Text, nullable=True)  # JSON array of 4 options
    correct_option = Column(Integer, nullable=True)  # Index 0-3 of correct answer

    # Answer details
    answer_text = Column(Text, nullable=True)

    # Evaluation
    correctness_score = Column(Float, nullable=True)  # 1-10
    depth_score = Column(Float, nullable=True)  # 1-10
    clarity_score = Column(Float, nullable=True)  # 1-10
    overall_score = Column(Float, nullable=True)  # Average
    feedback = Column(Text, nullable=True)  # LLM-generated feedback

    answered_at = Column(DateTime, nullable=True)

    # Relationships
    session = relationship("InterviewSession", back_populates="question_answers")


class SessionReport(Base):
    """Final summary report for a completed interview session."""
    __tablename__ = "session_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("interview_sessions.id"), unique=True, nullable=False)

    overall_score = Column(Float, nullable=True)
    strengths = Column(Text, nullable=True)  # JSON array of strengths
    weaknesses = Column(Text, nullable=True)  # JSON array of weaknesses
    summary = Column(Text, nullable=True)
    recommendation = Column(String(100), nullable=True)  # strong_hire, hire, maybe, no_hire
    detailed_analysis = Column(Text, nullable=True)

    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    session = relationship("InterviewSession", back_populates="report")
