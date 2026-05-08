"""
Session router — handles session creation, resume upload, and session management.
Now requires authentication and includes resume-role compatibility scoring.
"""

import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import Candidate, InterviewSession, SessionStatus, User
from backend.services.resume_parser import parse_resume
from backend.services.knowledge_ingestion import ingest_knowledge_base
from backend.src.vector_store import get_collection_stats
from backend.routers.auth import get_current_user, get_optional_user

router = APIRouter()

# Role-specific expected skills for compatibility scoring
ROLE_SKILL_KEYWORDS = {
    "AI/ML Engineer": [
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "neural network", "nlp", "computer vision", "scikit-learn", "keras",
        "pandas", "numpy", "data science", "ai", "artificial intelligence",
        "regression", "classification", "clustering", "cnn", "rnn", "lstm",
        "transformer", "bert", "gpt", "reinforcement learning", "opencv",
    ],
    "Backend Engineer": [
        "python", "java", "node", "javascript", "api", "rest", "graphql",
        "database", "sql", "postgresql", "mongodb", "redis", "docker",
        "kubernetes", "microservices", "aws", "cloud", "fastapi", "django",
        "flask", "express", "spring", "git", "ci/cd", "linux", "backend",
    ],
    "Data Scientist": [
        "python", "statistics", "machine learning", "data analysis", "pandas",
        "numpy", "visualization", "matplotlib", "seaborn", "sql", "r",
        "tableau", "power bi", "hypothesis testing", "regression", "jupyter",
        "data mining", "feature engineering", "a/b testing", "scipy",
    ],
    "Full Stack Engineer": [
        "javascript", "typescript", "react", "angular", "vue", "next.js",
        "node", "express", "html", "css", "tailwind", "bootstrap",
        "python", "django", "flask", "fastapi", "java", "spring",
        "sql", "postgresql", "mongodb", "redis", "docker", "aws",
        "rest", "graphql", "api", "git", "ci/cd", "webpack", "vite",
        "authentication", "deployment", "testing", "jest", "frontend", "backend",
    ],
}


def compute_role_compatibility(skills: list, technologies: list, role: str) -> dict:
    """Compute how well a candidate's resume matches the selected role."""
    role_keywords = ROLE_SKILL_KEYWORDS.get(role, [])
    if not role_keywords:
        return {"score": 100, "matched": [], "missing": [], "verdict": "compatible"}

    candidate_tokens = set()
    for item in skills + technologies:
        candidate_tokens.update(item.lower().split())

    matched = []
    for keyword in role_keywords:
        kw_parts = keyword.lower().split()
        if any(part in candidate_tokens for part in kw_parts):
            matched.append(keyword)

    score = round((len(matched) / len(role_keywords)) * 100)
    missing = [k for k in role_keywords[:10] if k not in matched][:5]

    if score >= 40:
        verdict = "compatible"
    elif score >= 15:
        verdict = "partial_match"
    else:
        verdict = "low_match"

    return {
        "score": score,
        "matched": matched[:10],
        "missing": missing,
        "verdict": verdict,
        "message": {
            "compatible": "Good match! Your resume aligns well with this role.",
            "partial_match": "Partial match. You may face challenging questions outside your expertise.",
            "low_match": "Low match. Your resume doesn't align well with this role. You can still proceed, but questions may be difficult.",
        }.get(verdict, ""),
    }


@router.post("/create")
async def create_session(
    role: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new interview session (requires login).
    Name and email auto-filled from user account.
    Returns resume-role compatibility score.
    """
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    valid_roles = ["AI/ML Engineer", "Backend Engineer", "Data Scientist", "Full Stack Engineer"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Choose from: {valid_roles}")

    try:
        pdf_bytes = await resume.read()
        profile = parse_resume(pdf_bytes)

        candidate = Candidate(
            name=user.name,
            email=user.email,
            resume_text=profile.raw_text[:10000],
            skills=json.dumps(profile.skills),
            technologies=json.dumps(profile.technologies),
            experience_level=profile.experience_level,
            domain_exposure=json.dumps(profile.domain_exposure),
        )
        db.add(candidate)
        db.flush()

        session = InterviewSession(
            candidate_id=candidate.id,
            user_id=user.id,
            role=role,
            status=SessionStatus.CREATED.value,
            total_questions=7,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        db.refresh(candidate)

        return {
            "session_id": session.id,
            "candidate_id": candidate.id,
            "role": role,
            "status": session.status,
            "profile": {
                "name": user.name,
                "email": user.email,
                "skills": profile.skills,
                "technologies": profile.technologies,
                "experience_level": profile.experience_level,
                "domain_exposure": profile.domain_exposure,
                "summary": profile.summary,
            },
            "message": "Session created. Interview starting...",
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get session details."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    candidate = session.candidate
    answered_count = len([qa for qa in session.question_answers if qa.answer_text])

    return {
        "session_id": session.id,
        "role": session.role,
        "status": session.status,
        "current_question": session.current_question_index,
        "total_questions": session.total_questions,
        "answered_questions": answered_count,
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "candidate": {
            "name": candidate.name,
            "email": candidate.email,
            "skills": candidate.get_skills_list(),
            "technologies": candidate.get_technologies_list(),
            "experience_level": candidate.experience_level,
        },
    }


@router.get("/{session_id}/status")
async def get_session_status(session_id: int, db: Session = Depends(get_db)):
    """Get concise session status."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    answered_count = len([qa for qa in session.question_answers if qa.answer_text])
    return {
        "session_id": session.id,
        "status": session.status,
        "current_question": session.current_question_index,
        "total_questions": session.total_questions,
        "answered_questions": answered_count,
        "progress_percent": round((answered_count / session.total_questions) * 100, 1),
    }


@router.post("/ingest-knowledge")
async def trigger_knowledge_ingestion():
    """Trigger knowledge base ingestion."""
    try:
        stats = ingest_knowledge_base()
        return {"status": "success", "message": "Knowledge base ingested", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/knowledge/status")
async def knowledge_status():
    """Check knowledge base status."""
    try:
        stats = get_collection_stats()
        return {
            "status": "ready" if stats["count"] > 0 else "empty",
            "document_count": stats["count"],
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/history/all")
async def get_all_sessions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get interview history for the logged-in user only."""
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user.id,
    ).order_by(InterviewSession.created_at.desc()).all()

    results = []
    for session in sessions:
        candidate = session.candidate
        qa_list = session.question_answers
        answered = [qa for qa in qa_list if qa.answer_text]
        scores = [qa.overall_score for qa in answered if qa.overall_score]
        avg_score = round(sum(scores) / len(scores), 1) if scores else None

        rec = None
        if avg_score is not None:
            if avg_score >= 8: rec = "strong_hire"
            elif avg_score >= 6.5: rec = "hire"
            elif avg_score >= 4.5: rec = "maybe"
            else: rec = "no_hire"

        results.append({
            "session_id": session.id,
            "candidate_name": candidate.name if candidate else "Unknown",
            "candidate_email": candidate.email if candidate else "",
            "role": session.role,
            "status": session.status,
            "total_questions": session.total_questions,
            "answered_questions": len(answered),
            "average_score": avg_score,
            "recommendation": rec,
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
        })

    return {"sessions": results, "total": len(results)}
