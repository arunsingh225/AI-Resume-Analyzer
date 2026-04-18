"""
Feedback System — allows users to rate and comment on analyses and the product.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db, Feedback, User
from app.utils.auth_utils import get_current_user, get_optional_user

router = APIRouter()


class FeedbackCreate(BaseModel):
    rating: float = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    category: str = Field(default="general", pattern="^(general|accuracy|ui|feature|bug)$")
    comment: Optional[str] = Field(None, max_length=1000)
    analysis_id: Optional[str] = None
    page: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    rating: float
    category: str
    comment: Optional[str]
    analysis_id: Optional[str]
    page: Optional[str]
    created_at: str


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(
    body: FeedbackCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Submit feedback — works for both authenticated and anonymous users."""
    feedback = Feedback(
        user_id=current_user.id if current_user else None,
        analysis_id=body.analysis_id,
        rating=body.rating,
        category=body.category,
        comment=body.comment,
        page=body.page,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return FeedbackResponse(
        id=feedback.id,
        rating=feedback.rating,
        category=feedback.category,
        comment=feedback.comment,
        analysis_id=feedback.analysis_id,
        page=feedback.page,
        created_at=str(feedback.created_at),
    )


@router.get("/")
def get_feedback(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get user's own feedback history."""
    total = db.query(Feedback).filter(Feedback.user_id == current_user.id).count()
    feedbacks = (
        db.query(Feedback)
        .filter(Feedback.user_id == current_user.id)
        .order_by(Feedback.created_at.desc())
        .offset(offset).limit(limit)
        .all()
    )
    return {
        "feedbacks": [
            {
                "id": f.id,
                "rating": f.rating,
                "category": f.category,
                "comment": f.comment,
                "analysis_id": f.analysis_id,
                "page": f.page,
                "created_at": str(f.created_at),
            }
            for f in feedbacks
        ],
        "total": total,
    }


@router.get("/stats")
def get_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get aggregate feedback stats (for admin/analytics)."""
    from sqlalchemy import func
    total = db.query(Feedback).count()
    avg_rating = db.query(func.avg(Feedback.rating)).scalar() or 0

    by_category = (
        db.query(Feedback.category, func.count(Feedback.id), func.avg(Feedback.rating))
        .group_by(Feedback.category)
        .all()
    )

    return {
        "total_feedback": total,
        "avg_rating": round(float(avg_rating), 2),
        "by_category": {
            cat: {"count": count, "avg_rating": round(float(avg), 2)}
            for cat, count, avg in by_category
        },
    }
