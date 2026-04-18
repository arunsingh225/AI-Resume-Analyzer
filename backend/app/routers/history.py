"""
Analysis History — CRUD endpoints for saved resume analyses.
"""
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db, Analysis, User
from app.utils.auth_utils import get_current_user

router = APIRouter()


@router.get("/")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List user's past analyses (summary only, not full JSON)."""
    total = db.query(Analysis).filter(Analysis.user_id == current_user.id).count()
    analyses = (
        db.query(Analysis)
        .filter(Analysis.user_id == current_user.id)
        .order_by(Analysis.created_at.desc())
        .offset(offset).limit(limit)
        .all()
    )
    return {
        "analyses": [
            {
                "id": a.id,
                "filename": a.filename,
                "file_type": a.file_type,
                "detected_field": a.detected_field,
                "detected_subfield": a.detected_subfield,
                "ats_score": a.ats_score,
                "grade": a.grade,
                "experience_level": a.experience_level,
                "candidate_name": a.candidate_name,
                "created_at": str(a.created_at),
            }
            for a in analyses
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{analysis_id}")
def get_analysis_detail(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get full analysis result by ID."""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    try:
        return json.loads(analysis.result_json)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(500, "Stored analysis data is corrupted")


@router.delete("/{analysis_id}")
def delete_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific analysis."""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    if not analysis:
        raise HTTPException(404, "Analysis not found")
    db.delete(analysis)
    db.commit()
    return {"message": "Analysis deleted"}
