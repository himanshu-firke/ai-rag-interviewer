"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type safety.
"""

import os
import sys
from pathlib import Path

# Fix Windows encoding for emoji/unicode in print statements
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Settings(BaseSettings):
    """Application settings with environment variable binding."""

    # LLM Provider: "groq" or "gemini"
    LLM_PROVIDER: str = "groq"

    # Groq (free, recommended)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # Gemini (fallback)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"
    EMBEDDING_MODEL: str = "text-embedding-004"

    # Database
    DATABASE_URL: str = "sqlite:///./backend/interview.db"

    # ChromaDB
    CHROMA_PATH: str = "./backend/chroma_db"

    # Knowledge Base
    KNOWLEDGE_BASE_PATH: str = "./knowledge"

    # Interview Settings
    MAX_QUESTIONS_PER_SESSION: int = 7
    MIN_QUESTIONS_PER_SESSION: int = 5
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5

    # Server
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # JWT Authentication
    JWT_SECRET: str = "ai-interview-secret-key-change-in-production-2024"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
