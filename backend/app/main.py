from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.routers import resume, analysis, report, auth, jd_match, improve
from app.database import create_tables
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Resume Analyzer API",
    description="SaaS Resume Analyzer — Auth + ATS + JD Match + Improvement",
    version="3.1.0"
)

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup
create_tables()

app.include_router(auth.router,     prefix="/auth",         tags=["Auth"])
app.include_router(resume.router,   prefix="/api/resume",   tags=["Resume"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(report.router,   prefix="/api/report",   tags=["Report"])
app.include_router(jd_match.router, prefix="/api/jd",       tags=["JD Match"])
app.include_router(improve.router,  prefix="/api/improve",  tags=["Improve"])

# Import history router if available
try:
    from app.routers import history
    app.include_router(history.router, prefix="/api/history", tags=["History"])
except ImportError:
    pass

# Import feedback router
try:
    from app.routers import feedback
    app.include_router(feedback.router, prefix="/api/feedback", tags=["Feedback"])
except ImportError:
    pass

@app.get("/")
def root():
    return {"status": "AI Resume Analyzer v3.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0"}

