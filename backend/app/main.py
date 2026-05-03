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
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded

from app.routers import resume, analysis, report, auth, jd_match, improve, history, feedback, admin
from app.database import create_tables, engine
from app.config import get_settings
from app.utils.logger import setup_logging
from app.middleware import RequestIDMiddleware, SecurityHeadersMiddleware

# ── Initialize logging ──────────────────────────────────────────────
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Allowed CORS origins — hardcoded + env var (wildcard excluded) ──
_CORS_ORIGINS = set([
    "https://ai-resume-analyzer-tawny-theta.vercel.app",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
] + [o for o in settings.cors_origins_list if o != "*"])


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.info("Database tables initialized")
    logger.info("CORS origins: %s", _CORS_ORIGINS)
    logger.info("AI Resume Analyzer v4.0.0 started successfully")
    yield
    logger.info("AI Resume Analyzer shutting down gracefully")


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Production SaaS — Auth + ATS + JD Match + Improvement",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Manual CORS middleware ────────────────────────────────────────────
# We use a raw @app.middleware("http") instead of CORSMiddleware because
# CORSMiddleware was not sending Access-Control-Allow-Origin headers on
# Render (due to CORS_ORIGINS="*" env var conflicting with credentials).
# This approach bypasses all middleware ordering issues.
@app.middleware("http")
async def cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin", "")

    # Handle CORS preflight (OPTIONS) — must respond before route handler
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        if origin in _CORS_ORIGINS:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
        return response

    # Handle actual requests
    response = await call_next(request)

    if origin in _CORS_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"

    return response


# ── Security + RequestID middleware ──────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)

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
app.include_router(admin.router,    prefix="/api/admin",    tags=["Admin"])


# ── Health check endpoints ──────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "AI Resume Analyzer v4.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    """Basic health check — is the process alive?"""
    return {"status": "healthy", "version": "4.0.1"}   # bumped to confirm deploy


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
