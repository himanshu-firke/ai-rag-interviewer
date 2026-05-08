"""
Interview router — handles the interactive interview flow.
- Supports coding, MCQ, conceptual, scenario, debugging, applied question types
- Allows editing previous answers
- Evaluates ALL answers only on final submission
"""

import json
import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import InterviewSession, QuestionAnswer, SessionStatus
from backend.services.rag_pipeline import get_context_for_question
from backend.services.question_generator import generate_question
from backend.services.answer_evaluator import evaluate_answer
from backend.src import rag_logger

router = APIRouter()


class AnswerRequest(BaseModel):
    answer_text: str


class UpdateAnswerRequest(BaseModel):
    answer_text: str


def _serialize_question(qa) -> dict:
    """Serialize a QuestionAnswer to a dict for API response."""
    data = {
        "id": qa.id, "number": qa.order,
        "text": qa.question_text, "topic": qa.question_topic,
        "type": qa.question_type, "difficulty": qa.difficulty,
        "answer": qa.answer_text,
    }
    # Coding question fields
    if qa.question_type == "coding":
        data["code_template"] = qa.code_template or ""
        data["expected_language"] = qa.expected_language or "python"
    # MCQ question fields
    if qa.question_type == "mcq":
        data["options"] = json.loads(qa.options) if qa.options else []
    return data


def _store_question(session_id, order, question) -> QuestionAnswer:
    """Create a QuestionAnswer ORM object from generated question."""
    return QuestionAnswer(
        session_id=session_id,
        order=order,
        question_text=question.question_text,
        question_topic=question.topic,
        question_type=question.question_type,
        difficulty=question.difficulty,
        context_used=question.context_used,
        code_template=question.code_template or None,
        expected_language=question.expected_language or None,
        options=json.dumps(question.options) if question.options else None,
        correct_option=question.correct_option if question.correct_option >= 0 else None,
    )


@router.post("/{session_id}/start")
async def start_interview(session_id: int, db: Session = Depends(get_db)):
    """Start the interview and generate the first question."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="This interview session is already completed")

    if session.status == SessionStatus.IN_PROGRESS.value:
        all_qa = db.query(QuestionAnswer).filter(
            QuestionAnswer.session_id == session_id,
        ).order_by(QuestionAnswer.order).all()
        return {
            "session_id": session.id,
            "status": "in_progress",
            "questions": [_serialize_question(qa) for qa in all_qa],
            "total_questions": session.total_questions,
        }

    session.status = SessionStatus.IN_PROGRESS.value
    db.flush()

    candidate = session.candidate
    skills = candidate.get_skills_list()
    technologies = candidate.get_technologies_list()

    rag_logger.log_session_start(
        candidate_name=candidate.name, role=session.role,
        skills=skills, technologies=technologies,
        experience=candidate.experience_level or "unknown",
    )

    rag_logger.log_separator("RAG RETRIEVAL - QUESTION 1")
    context = get_context_for_question(
        skills=skills, technologies=technologies, role=session.role,
        experience_level=candidate.experience_level or "unknown",
    )

    question = generate_question(
        context=context.combined_text, role=session.role,
        skills=skills, technologies=technologies,
        experience_level=candidate.experience_level or "unknown",
        question_index=0, total_questions=session.total_questions,
    )

    qa = _store_question(session.id, 1, question)
    db.add(qa)
    session.current_question_index = 1
    db.commit()
    db.refresh(qa)

    return {
        "session_id": session.id,
        "status": "in_progress",
        "questions": [_serialize_question(qa)],
        "total_questions": session.total_questions,
    }


@router.post("/{session_id}/answer")
async def submit_answer(session_id: int, request: AnswerRequest, db: Session = Depends(get_db)):
    """Submit an answer — stores it and generates the next question (no evaluation)."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != SessionStatus.IN_PROGRESS.value:
        raise HTTPException(status_code=400, detail="Interview is not in progress")

    current_qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
        QuestionAnswer.answer_text.is_(None),
    ).order_by(QuestionAnswer.order.desc()).first()

    if not current_qa:
        raise HTTPException(status_code=400, detail="No pending question found")

    current_qa.answer_text = request.answer_text
    current_qa.answered_at = datetime.datetime.utcnow()
    rag_logger.log_answer_received(request.answer_text)
    db.flush()

    answered_count = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
        QuestionAnswer.answer_text.isnot(None),
    ).count()

    if answered_count >= session.total_questions:
        db.commit()
        return {
            "session_id": session.id,
            "status": "ready_to_submit",
            "message": "All questions answered! Review and submit.",
            "answered_questions": answered_count,
            "total_questions": session.total_questions,
        }

    # Generate next question
    candidate = session.candidate
    skills = candidate.get_skills_list()
    technologies = candidate.get_technologies_list()

    previous_qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
        QuestionAnswer.answer_text.isnot(None),
    ).order_by(QuestionAnswer.order).all()

    prev_qa_list = [
        {"question": qa.question_text, "answer": qa.answer_text, "topic": qa.question_topic}
        for qa in previous_qa
    ]
    covered_topics = [qa.question_topic for qa in previous_qa if qa.question_topic]

    rag_logger.log_separator(f"RAG RETRIEVAL - QUESTION {answered_count + 1}")
    context = get_context_for_question(
        skills=skills, technologies=technologies, role=session.role,
        experience_level=candidate.experience_level or "unknown",
        previous_topics=covered_topics,
    )

    next_question = generate_question(
        context=context.combined_text, role=session.role,
        skills=skills, technologies=technologies,
        experience_level=candidate.experience_level or "unknown",
        question_index=answered_count, total_questions=session.total_questions,
        previous_qa=prev_qa_list,
    )

    next_qa = _store_question(session.id, answered_count + 1, next_question)
    db.add(next_qa)
    session.current_question_index = answered_count + 1
    db.commit()
    db.refresh(next_qa)

    return {
        "session_id": session.id,
        "status": "in_progress",
        "next_question": _serialize_question(next_qa),
        "answered_questions": answered_count,
        "total_questions": session.total_questions,
    }


@router.put("/{session_id}/update-answer/{question_id}")
async def update_answer(session_id: int, question_id: int, request: UpdateAnswerRequest, db: Session = Depends(get_db)):
    """Edit a previously answered question."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Cannot edit — interview already submitted")

    qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.id == question_id, QuestionAnswer.session_id == session_id,
    ).first()
    if not qa:
        raise HTTPException(status_code=404, detail="Question not found")

    qa.answer_text = request.answer_text
    qa.answered_at = datetime.datetime.utcnow()
    qa.correctness_score = None
    qa.depth_score = None
    qa.clarity_score = None
    qa.overall_score = None
    qa.feedback = None
    db.commit()

    return {
        "session_id": session.id, "question_id": qa.id,
        "question_number": qa.order, "answer": qa.answer_text,
        "message": "Answer updated successfully",
    }


@router.get("/{session_id}/questions")
async def get_all_questions(session_id: int, db: Session = Depends(get_db)):
    """Get all questions and answers for review before final submission."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    all_qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
    ).order_by(QuestionAnswer.order).all()

    return {
        "session_id": session.id, "status": session.status,
        "role": session.role, "total_questions": session.total_questions,
        "questions": [_serialize_question(qa) for qa in all_qa],
    }


@router.post("/{session_id}/submit-all")
async def submit_all_answers(session_id: int, db: Session = Depends(get_db)):
    """Final submission — evaluates ALL answers at once."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Already submitted")

    all_qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
    ).order_by(QuestionAnswer.order).all()

    answered = [qa for qa in all_qa if qa.answer_text]
    if not answered:
        raise HTTPException(status_code=400, detail="No answers to evaluate")

    rag_logger.log_separator("FINAL EVALUATION - ALL ANSWERS")

    for qa in answered:
        evaluation = evaluate_answer(
            question=qa.question_text, answer=qa.answer_text,
            context=qa.context_used or "", role=session.role,
            difficulty=qa.difficulty or "medium",
            question_type=qa.question_type or "conceptual",
        )
        qa.correctness_score = evaluation.correctness_score
        qa.depth_score = evaluation.depth_score
        qa.clarity_score = evaluation.clarity_score
        qa.overall_score = evaluation.overall_score
        qa.feedback = evaluation.feedback

    session.status = SessionStatus.COMPLETED.value
    session.completed_at = datetime.datetime.utcnow()
    db.commit()

    scores = [qa.overall_score for qa in answered if qa.overall_score]
    avg = round(sum(scores) / len(scores), 1) if scores else 0
    rec = "strong_hire" if avg >= 8 else "hire" if avg >= 6.5 else "maybe" if avg >= 4.5 else "no_hire"
    rag_logger.log_session_complete(session.id, len(answered), avg, rec)

    return {
        "session_id": session.id, "status": "completed",
        "message": "Interview submitted and evaluated!",
        "answered_questions": len(answered),
        "total_questions": session.total_questions,
        "average_score": avg,
    }


@router.post("/{session_id}/end")
async def end_interview(session_id: int, db: Session = Depends(get_db)):
    """End the interview early and evaluate what was answered."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answered = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session_id,
        QuestionAnswer.answer_text.isnot(None),
        QuestionAnswer.overall_score.is_(None),
    ).all()

    if answered:
        rag_logger.log_separator("EARLY END - EVALUATING ANSWERS")
        for qa in answered:
            evaluation = evaluate_answer(
                question=qa.question_text, answer=qa.answer_text,
                context=qa.context_used or "", role=session.role,
                difficulty=qa.difficulty or "medium",
                question_type=qa.question_type or "conceptual",
            )
            qa.correctness_score = evaluation.correctness_score
            qa.depth_score = evaluation.depth_score
            qa.clarity_score = evaluation.clarity_score
            qa.overall_score = evaluation.overall_score
            qa.feedback = evaluation.feedback

    session.status = SessionStatus.COMPLETED.value
    session.completed_at = datetime.datetime.utcnow()
    db.commit()

    return {"session_id": session.id, "status": "completed", "message": "Interview ended and evaluated."}
