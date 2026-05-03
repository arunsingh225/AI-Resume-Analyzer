"""
AI Resume Analyzer — FastAPI Application Entry Point.

Production-hardened with:
  - Custom pure ASGI CORS middleware (replaces broken CORSMiddleware)
  - Pure ASGI Request-ID and Security headers middleware
  - Rate limiting with per-user support
  - Health check endpoints (/health, /ready, /live)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from slowapi.errors import RateLimitExceeded

from app.routers import resume, analysis, report, auth, jd_match, improve, history, feedback, admin
from app.database import create_tables, engine
from app.config import get_settings
from app.utils.logger import setup_logging
from app.middleware import CORSMiddlewareManual, RequestIDMiddleware, SecurityHeadersMiddleware

# ── Initialize logging ──────────────────────────────────────────────
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

settings = get_settings()

# ── Extra CORS origins from env var (excluding wildcard) ─────────────
_extra_origins = {o for o in settings.cors_origins_list if o != "*"}


# ── Lifespan ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    logger.info("Database tables initialized")
    logger.info("AI Resume Analyzer v4.1.0 started")
    yield
    logger.info("AI Resume Analyzer shutting down gracefully")


app = FastAPI(
    title="AI Resume Analyzer API",
    description="Production SaaS — Auth + ATS + JD Match + Improvement",
    version="4.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware stack (LIFO — last added = outermost = first to run) ──
#
#  Request flow:
#    CORSMiddlewareManual → RequestIDMiddleware → SecurityHeadersMiddleware → routes
#
#  ALL middleware are pure ASGI (no BaseHTTPMiddleware).
#  CORSMiddlewareManual MUST be outermost to handle OPTIONS preflights
#  before any other middleware runs.
#
#  We do NOT use Starlette's CORSMiddleware — it fails to send CORS
#  headers on Render.com when combined with other middleware.

app.add_middleware(SecurityHeadersMiddleware)                          # innermost  (1st)
app.add_middleware(RequestIDMiddleware)                                # middle     (2nd)
app.add_middleware(CORSMiddlewareManual, extra_origins=_extra_origins) # outermost  (3rd)

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
    return {"status": "AI Resume Analyzer v4.1.0", "docs": "/docs"}


@app.get("/health")
def health():
    """Basic health check — is the process alive?"""
    return {"status": "healthy", "version": "4.1.0"}


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
