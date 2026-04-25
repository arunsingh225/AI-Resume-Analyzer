"""
AI Resume Analyzer — FastAPI Application Entry Point.

Production-hardened with:
  - Modern lifespan context manager (no deprecated on_event)
  - Structured JSON logging
  - Request-ID tracing middleware
  - Security headers middleware
  - Rate limiting with per-user support
  - Health check endpoints (/health, /ready, /live)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded

from app.routers import resume, analysis, report, auth, jd_match, improve, history, feedback
from app.database import create_tables, engine
from app.config import get_settings
from app.utils.logger import setup_logging
from app.middleware import RequestIDMiddleware, SecurityHeadersMiddleware

# ── Initialize logging ──────────────────────────────────────────────
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

settings = get_settings()


# ── Lifespan — modern replacement for on_event("startup"/"shutdown") ─
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for the application."""
    # ── Startup ──
    create_tables()
    logger.info("Database tables initialized")
    logger.info("CORS origins: %s", settings.cors_origins_list)
    logger.info("AI Resume Analyzer v4.0.0 started successfully")
    yield
    # ── Shutdown ──
    logger.info("AI Resume Analyzer shutting down gracefully")


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Production SaaS — Auth + ATS + JD Match + Improvement",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware (order matters — outermost first) ────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limit error handler ────────────────────────────────────────
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning("Rate limit exceeded: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

# ── Register routers ────────────────────────────────────────────────
app.include_router(auth.router,     prefix="/auth",         tags=["Auth"])
app.include_router(resume.router,   prefix="/api/resume",   tags=["Resume"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(report.router,   prefix="/api/report",   tags=["Report"])
app.include_router(jd_match.router, prefix="/api/jd",       tags=["JD Match"])
app.include_router(improve.router,  prefix="/api/improve",  tags=["Improve"])
app.include_router(history.router,  prefix="/api/history",  tags=["History"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])


# ── Health check endpoints ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AI Resume Analyzer v4.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    """Basic health check — is the process alive?"""
    return {"status": "healthy", "version": "4.0.0"}


@app.get("/ready")
def readiness():
    """Readiness check — can we serve traffic? Tests DB connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error("Readiness check failed: %s", str(e))
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "database": "disconnected", "error": str(e)}
        )


@app.get("/live")
def liveness():
    """Liveness check — is the process running?"""
    return {"status": "alive"}
