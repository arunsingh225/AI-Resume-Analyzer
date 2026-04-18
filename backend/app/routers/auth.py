from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
import re as _re
import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db, User
from app.services.auth_service import (
    get_user_by_email, get_user_by_phone,
    create_user_email, create_user_google, create_user_phone,
    verify_password, generate_otp, save_otp, verify_otp,
)
from app.utils.auth_utils import create_access_token, get_current_user

router = APIRouter()
limiter = Limiter(
    key_func=get_remote_address,
    enabled=os.getenv("TESTING", "").lower() != "true",
)


def _validate_password(pw: str):
    """Enforce: 8+ chars, 1 upper, 1 lower, 1 digit."""
    errs = []
    if len(pw) < 8:              errs.append("at least 8 characters")
    if not _re.search(r'[A-Z]', pw): errs.append("one uppercase letter")
    if not _re.search(r'[a-z]', pw): errs.append("one lowercase letter")
    if not _re.search(r'\d', pw):    errs.append("one digit")
    if errs:
        raise HTTPException(400, f"Password must contain: {', '.join(errs)}")


# ── Pydantic schemas ────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class GoogleLoginRequest(BaseModel):
    name:       str
    email:      EmailStr
    avatar_url: Optional[str] = ""

class SendOTPRequest(BaseModel):
    phone: str          # e.g. "+919876543210"

class VerifyOTPRequest(BaseModel):
    phone: str
    otp:   str
    name:  Optional[str] = ""


def user_response(user: User, token: str) -> dict:
    return {
        "token": token,
        "user": {
            "id":         user.id,
            "name":       user.name or "",
            "email":      user.email or "",
            "phone":      user.phone or "",
            "provider":   user.provider,
            "avatar_url": user.avatar_url or "",
        }
    }


# ── Email Signup ─────────────────────────────────────────────────────
@router.post("/signup")
@limiter.limit("3/minute")
def signup(request: Request, body: SignupRequest, db: Session = Depends(get_db)):
    if get_user_by_email(db, body.email):
        raise HTTPException(400, "Email already registered. Please log in.")
    _validate_password(body.password)
    user  = create_user_email(db, body.name, body.email, body.password)
    token = create_access_token(user.id, user.email)
    return user_response(user, token)


# ── Email Login ──────────────────────────────────────────────────────
@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user or not user.password:
        raise HTTPException(401, "No account found with this email.")
    if not verify_password(body.password, user.password):
        raise HTTPException(401, "Incorrect password.")
    token = create_access_token(user.id, user.email)
    return user_response(user, token)


# ── Google Login (mock — no OAuth server needed) ─────────────────────
@router.post("/google")
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Frontend passes name + email from Google's ID token (or mock data).
    We create/fetch the user and return our own JWT.
    """
    user  = create_user_google(db, body.name, body.email, body.avatar_url or "")
    token = create_access_token(user.id, user.email)
    return user_response(user, token)


# ── Send OTP ─────────────────────────────────────────────────────────
@router.post("/send-otp")
def send_otp(body: SendOTPRequest, db: Session = Depends(get_db)):
    phone = body.phone.strip()
    if len(phone) < 10:
        raise HTTPException(400, "Invalid phone number.")
    otp = generate_otp()
    save_otp(db, phone, otp)
    # In production: send via Twilio / MSG91
    # For mock/demo: return OTP in response (remove in prod)
    return {
        "message": f"OTP sent to {phone}",
        "otp_demo": otp,          # ← remove this line in production
    }


# ── Verify OTP ───────────────────────────────────────────────────────
@router.post("/verify-otp")
def verify_otp_endpoint(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    phone = body.phone.strip()
    if not verify_otp(db, phone, body.otp.strip()):
        raise HTTPException(401, "Invalid or expired OTP.")

    user = get_user_by_phone(db, phone)
    if not user:
        user = create_user_phone(db, phone, body.name)

    token = create_access_token(user.id, user.email)
    return user_response(user, token)


# ── Get Current User ─────────────────────────────────────────────────
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id":         current_user.id,
        "name":       current_user.name or "",
        "email":      current_user.email or "",
        "phone":      current_user.phone or "",
        "provider":   current_user.provider,
        "avatar_url": current_user.avatar_url or "",
        "created_at": str(current_user.created_at),
    }


# ── Logout ───────────────────────────────────────────────────────────
@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # JWT is stateless — client just deletes the token
    return {"message": "Logged out successfully"}
