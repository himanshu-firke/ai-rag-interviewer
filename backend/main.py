"""
Main FastAPI application entry point.
Sets up CORS, lifespan events, and mounts all routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — runs on startup and shutdown."""
    # Startup
    print("[*] Starting AI Interview Screening System...")
    init_db()
    print("[+] System ready.")
    yield
    # Shutdown
    print("[!] Shutting down...")


app = FastAPI(
    title="AI Interview Screening System",
    description="AI-powered role-based candidate screening with RAG pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
from backend.routers import auth, session, interview, report  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(session.router, prefix="/api/session", tags=["Session"])
app.include_router(interview.router, prefix="/api/interview", tags=["Interview"])
app.include_router(report.router, prefix="/api/report", tags=["Report"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Interview Screening System",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    from backend.src.vector_store import get_collection_stats
    vs = get_collection_stats()
    return {
        "status": "healthy",
        "database": "connected",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.GROQ_MODEL if settings.LLM_PROVIDER == "groq" else settings.GEMINI_MODEL,
        "vector_store_chunks": vs["count"],
        "embedding": "all-MiniLM-L6-v2 (local)",
    }
