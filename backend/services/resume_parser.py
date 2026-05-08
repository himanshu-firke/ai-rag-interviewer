"""
Resume parsing service.
Uses src/data_loader for PDF extraction and LLM for structured parsing.
"""

from pydantic import BaseModel
from backend.src.data_loader import extract_text_from_pdf_bytes
from backend.services.llm_client import get_json_response
from backend.src import rag_logger


class ResumeProfile(BaseModel):
    raw_text: str
    name: str = ""
    email: str = ""
    skills: list[str] = []
    technologies: list[str] = []
    experience_level: str = "unknown"
    domain_exposure: list[str] = []
    education: list[str] = []
    summary: str = ""


def parse_resume(pdf_bytes: bytes) -> ResumeProfile:
    """Parse a resume PDF and extract structured profile data."""
    raw_text = extract_text_from_pdf_bytes(pdf_bytes)

    if not raw_text.strip():
        return ResumeProfile(raw_text="", summary="Empty or unreadable resume")

    prompt = f"""Analyze the following resume text and extract structured information.
Return a valid JSON object with these exact keys:
- "name": candidate's full name (string)
- "email": email address if found (string, empty if not found)
- "skills": list of technical and soft skills (array of strings)
- "technologies": list of specific technologies, frameworks, tools, languages (array of strings)
- "experience_level": one of "junior", "mid", "senior" (string)
- "domain_exposure": list of domains/industries (array of strings)
- "education": list of educational qualifications (array of strings)
- "summary": a brief 2-3 sentence professional summary (string)

IMPORTANT: Return ONLY the JSON object, no markdown formatting.

Resume text:
{raw_text[:8000]}"""

    try:
        data = get_json_response(prompt)
        if "error" in data:
            raise ValueError(data.get("raw", "Parse failed"))

        profile = ResumeProfile(
            raw_text=raw_text,
            name=data.get("name", ""),
            email=data.get("email", ""),
            skills=data.get("skills", []),
            technologies=data.get("technologies", []),
            experience_level=data.get("experience_level", "unknown"),
            domain_exposure=data.get("domain_exposure", []),
            education=data.get("education", []),
            summary=data.get("summary", ""),
        )

        # Log parsed resume to terminal
        rag_logger.log_resume_parsed(
            profile.name, profile.skills, profile.technologies,
            profile.experience_level, profile.summary,
        )
        return profile

    except Exception as e:
        print(f"[WARN] LLM parsing failed: {e}")
        return ResumeProfile(
            raw_text=raw_text,
            summary="Resume parsed (basic extraction - AI unavailable)",
        )
