from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.resume_improver import improve_resume
from app.utils.auth_utils import get_current_user
from app.database import User

router = APIRouter()


class ImproveRequest(BaseModel):
    resume_text: str


@router.post("/improve")
def improve(
    body: ImproveRequest,
    current_user: User = Depends(get_current_user),
):
    if len(body.resume_text.strip()) < 50:
        raise HTTPException(400, "Resume text too short.")
    try:
        return improve_resume(body.resume_text)
    except Exception as e:
        raise HTTPException(500, f"Improvement failed: {str(e)}")
