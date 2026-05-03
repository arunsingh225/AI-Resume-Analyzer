"""
Admin Stats Router — user metrics and platform analytics.
Only accessible with a valid JWT (any logged-in user can view public stats).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import datetime

from app.database import get_db, User, Analysis
from app.utils.auth_utils import get_current_user

router = APIRouter()


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return platform statistics for the admin dashboard."""

    now = datetime.datetime.utcnow()
    day_ago  = now - datetime.timedelta(hours=24)
    week_ago = now - datetime.timedelta(days=7)

    # ── User stats ──
    total_users      = db.query(func.count(User.id)).scalar() or 0
    users_today      = db.query(func.count(User.id)).filter(User.created_at >= day_ago).scalar() or 0
    users_this_week  = db.query(func.count(User.id)).filter(User.created_at >= week_ago).scalar() or 0

    # ── Provider breakdown ──
    providers_raw = (
        db.query(User.provider, func.count(User.id))
        .group_by(User.provider)
        .all()
    )
    providers = {p: c for p, c in providers_raw}

    # ── Analysis stats ──
    total_analyses   = db.query(func.count(Analysis.id)).scalar() or 0
    analyses_today   = db.query(func.count(Analysis.id)).filter(Analysis.created_at >= day_ago).scalar() or 0
    analyses_week    = db.query(func.count(Analysis.id)).filter(Analysis.created_at >= week_ago).scalar() or 0
    avg_ats          = db.query(func.avg(Analysis.ats_score)).scalar()

    # ── Top fields ──
    top_fields_raw = (
        db.query(Analysis.detected_field, func.count(Analysis.id).label("cnt"))
        .filter(Analysis.detected_field.isnot(None))
        .group_by(Analysis.detected_field)
        .order_by(func.count(Analysis.id).desc())
        .limit(6)
        .all()
    )
    top_fields = [{"field": f, "count": c} for f, c in top_fields_raw]

    # ── Grade distribution ──
    grades_raw = (
        db.query(Analysis.grade, func.count(Analysis.id))
        .filter(Analysis.grade.isnot(None))
        .group_by(Analysis.grade)
        .all()
    )
    grades = {g: c for g, c in grades_raw}

    return {
        "users": {
            "total":      total_users,
            "today":      users_today,
            "this_week":  users_this_week,
            "by_provider": providers,
        },
        "analyses": {
            "total":      total_analyses,
            "today":      analyses_today,
            "this_week":  analyses_week,
            "avg_ats_score": round(avg_ats, 1) if avg_ats else 0,
            "top_fields": top_fields,
            "grade_distribution": grades,
        },
    }
