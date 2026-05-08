"""
Report router — generates, retrieves, and exports interview reports.
Supports JSON and PDF export formats.
"""

import io
import json
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import InterviewSession, QuestionAnswer, SessionReport, SessionStatus
from backend.services.answer_evaluator import generate_session_report

router = APIRouter()


def _build_report_data(session, db):
    """Build report data from session."""
    all_qa = db.query(QuestionAnswer).filter(
        QuestionAnswer.session_id == session.id,
    ).order_by(QuestionAnswer.order).all()

    qa_pairs = [
        {
            "question": qa.question_text,
            "answer": qa.answer_text or "Not answered",
            "topic": qa.question_topic,
            "score": qa.overall_score or 0,
        }
        for qa in all_qa
    ]

    # Generate report using LLM
    report_data = generate_session_report(
        role=session.role,
        candidate_name=session.candidate.name,
        qa_pairs=qa_pairs,
    )

    # Save to DB
    existing = db.query(SessionReport).filter(SessionReport.session_id == session.id).first()
    if existing:
        existing.overall_score = report_data.get("overall_score", 0)
        existing.recommendation = report_data.get("recommendation", "maybe")
        existing.strengths = json.dumps(report_data.get("strengths", []))
        existing.weaknesses = json.dumps(report_data.get("weaknesses", []))
        existing.summary = report_data.get("summary", "")
        existing.detailed_analysis = report_data.get("detailed_analysis", "")
    else:
        report = SessionReport(
            session_id=session.id,
            overall_score=report_data.get("overall_score", 0),
            recommendation=report_data.get("recommendation", "maybe"),
            strengths=json.dumps(report_data.get("strengths", [])),
            weaknesses=json.dumps(report_data.get("weaknesses", [])),
            summary=report_data.get("summary", ""),
            detailed_analysis=report_data.get("detailed_analysis", ""),
        )
        db.add(report)
    db.commit()

    return {
        "session_id": session.id,
        "role": session.role,
        "candidate": {
            "name": session.candidate.name,
            "email": session.candidate.email,
        },
        "total_questions": session.total_questions,
        "answered_questions": len([qa for qa in all_qa if qa.answer_text]),
        "report": report_data,
        "questions": [
            {
                "number": qa.order,
                "question": qa.question_text,
                "answer": qa.answer_text,
                "topic": qa.question_topic,
                "difficulty": qa.difficulty,
                "scores": {
                    "correctness": qa.correctness_score,
                    "depth": qa.depth_score,
                    "clarity": qa.clarity_score,
                    "overall": qa.overall_score,
                },
                "feedback": qa.feedback,
            }
            for qa in all_qa
        ],
    }


@router.get("/{session_id}")
async def get_report(session_id: int, db: Session = Depends(get_db)):
    """Get or generate the session report."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    return _build_report_data(session, db)


@router.get("/{session_id}/export")
async def export_report_json(session_id: int, db: Session = Depends(get_db)):
    """Export report as downloadable JSON."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return _build_report_data(session, db)


@router.get("/{session_id}/export-pdf")
async def export_report_pdf(session_id: int, db: Session = Depends(get_db)):
    """Export report as downloadable PDF."""
    session = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != SessionStatus.COMPLETED.value:
        raise HTTPException(status_code=400, detail="Interview not yet completed")

    data = _build_report_data(session, db)

    # Generate PDF
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import mm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=20, spaceAfter=6)
    heading_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceAfter=8, textColor=colors.HexColor("#4f46e5"))
    body_style = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=10, spaceAfter=4, leading=14)
    small_style = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    elements = []

    # Title
    elements.append(Paragraph("AI Interview Screening Report", title_style))
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4f46e5")))
    elements.append(Spacer(1, 6*mm))

    # Candidate info
    elements.append(Paragraph("Candidate Information", heading_style))
    info_data = [
        ["Name", data["candidate"]["name"]],
        ["Role", data["role"]],
        ["Questions", f'{data["answered_questions"]}/{data["total_questions"]}'],
        ["Overall Score", f'{data["report"].get("overall_score", 0)}/10'],
        ["Recommendation", data["report"].get("recommendation", "N/A").replace("_", " ").upper()],
        ["Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")],
    ]
    info_table = Table(info_data, colWidths=[120, 350])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#4f46e5")),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8*mm))

    # Summary
    if data["report"].get("summary"):
        elements.append(Paragraph("Summary", heading_style))
        elements.append(Paragraph(data["report"]["summary"], body_style))
        elements.append(Spacer(1, 6*mm))

    # Strengths
    strengths = data["report"].get("strengths", [])
    if strengths:
        elements.append(Paragraph("Strengths", heading_style))
        for s in strengths:
            elements.append(Paragraph(f"+ {s}", body_style))
        elements.append(Spacer(1, 4*mm))

    # Weaknesses
    weaknesses = data["report"].get("weaknesses", [])
    if weaknesses:
        elements.append(Paragraph("Areas for Improvement", heading_style))
        for w in weaknesses:
            elements.append(Paragraph(f"- {w}", body_style))
        elements.append(Spacer(1, 6*mm))

    # Question breakdown
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph("Question-by-Question Breakdown", heading_style))
    elements.append(Spacer(1, 2*mm))

    for q in data.get("questions", []):
        scores = q.get("scores", {})
        score_text = f'Score: {scores.get("overall", 0)}/10 (C:{scores.get("correctness", 0)} D:{scores.get("depth", 0)} Cl:{scores.get("clarity", 0)})'

        elements.append(Paragraph(
            f'<b>Q{q["number"]}</b> [{q.get("topic", "General")}] [{q.get("difficulty", "medium")}] — {score_text}',
            ParagraphStyle("QHead", parent=body_style, fontSize=10, textColor=colors.HexColor("#1e293b")),
        ))
        elements.append(Paragraph(f'<i>{q["question"]}</i>', small_style))
        elements.append(Paragraph(f'<b>Answer:</b> {(q.get("answer") or "Not answered")[:500]}', body_style))
        if q.get("feedback"):
            elements.append(Paragraph(f'<b>Feedback:</b> {q["feedback"]}', small_style))
        elements.append(Spacer(1, 4*mm))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    candidate_name = data["candidate"]["name"].replace(" ", "_")
    filename = f"Interview_Report_{candidate_name}_{session_id}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
