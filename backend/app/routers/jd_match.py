from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.jd_matcher import match_resume_to_jd
from app.utils.auth_utils import get_current_user
from app.database import User

router = APIRouter()


class JDMatchRequest(BaseModel):
    resume_text: str
    jd_text:     str


@router.post("/match")
def match_jd(
    body: JDMatchRequest,
    current_user: User = Depends(get_current_user),
):
    if len(body.resume_text.strip()) < 50:
        raise HTTPException(400, "Resume text too short. Please upload and analyze a resume first.")
    if len(body.jd_text.strip()) < 30:
        raise HTTPException(400, "Job description too short. Please paste the full JD.")
    try:
        return match_resume_to_jd(body.resume_text, body.jd_text)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"Matching failed: {str(e)}")
