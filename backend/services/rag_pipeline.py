"""
RAG Pipeline service — thin wrapper around src/retriever.
Kept for backward compatibility with routers.
"""

from backend.src.retriever import retrieve, RetrievedContext


def get_context_for_question(
    skills: list[str], technologies: list[str], role: str,
    experience_level: str = "unknown", previous_topics: list[str] = None,
) -> RetrievedContext:
    """Full RAG retrieval pipeline."""
    return retrieve(
        skills=skills, technologies=technologies, role=role,
        previous_topics=previous_topics,
    )
