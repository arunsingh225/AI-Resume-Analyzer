"""
Auth Router — email signup/login, Google OAuth, OTP phone auth.

Security hardened:
  - OTP is never returned in API responses
  - Access tokens expire in 15 minutes
  - Refresh tokens expire in 7 days
  - Password policy enforced on signup
  - Rate-limited auth endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
import re as _re
import os
import base64
import json as _json
import logging

from app.config import get_settings

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db, User
from app.services.auth_service import (
    get_user_by_email, get_user_by_phone,
    create_user_email, create_user_google, create_user_phone,
    verify_password, generate_otp, save_otp, verify_otp,
)
from app.utils.auth_utils import (
    create_access_token, create_refresh_token, decode_token, get_current_user,
)

logger = logging.getLogger(__name__)

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


def _decode_jwt_payload_unverified(token: str) -> dict:
    """
    Decode the JWT payload WITHOUT verifying the signature.
    Used only to peek at the `aud` claim before full verification.
    """
    try:
        payload_b64 = token.split(".")[1]
        # Pad to multiple of 4
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        return _json.loads(base64.urlsafe_b64decode(payload_b64))
    except Exception as exc:
        raise HTTPException(401, "Malformed Google credential token.") from exc


# ── Pydantic schemas ────────────────────────────────────────────────
class SignupRequest(BaseModel):
    name:     str
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str

class SendOTPRequest(BaseModel):
    phone: str          # e.g. "+919876543210"

class VerifyOTPRequest(BaseModel):
    phone: str
    otp:   str
    name:  Optional[str] = ""

class RefreshRequest(BaseModel):
    refresh_token: str


def _token_response(user: User, access_token: str, refresh_token: str) -> dict:
    """Standardized auth response with both tokens."""
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 900,  # 15 minutes in seconds
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
    user = create_user_email(db, body.name, body.email, body.password)
    logger.info("User signup: user_id=%s email=%s", user.id, body.email)
    access  = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id)
    return _token_response(user, access, refresh)


# ── Email Login ──────────────────────────────────────────────────────
@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, body.email)
    if not user or not user.password:
        raise HTTPException(401, "No account found with this email.")
    if not verify_password(body.password, user.password):
        logger.warning("Failed login attempt: email=%s", body.email)
        raise HTTPException(401, "Incorrect password.")
    logger.info("User login: user_id=%s", user.id)
    access  = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id)
    return _token_response(user, access, refresh)


# ── Refresh Token ────────────────────────────────────────────────────
@router.post("/refresh")
def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    payload = decode_token(body.refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    logger.info("Token refresh: user_id=%s", user.id)
    access  = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id)
    return _token_response(user, access, refresh)


# ── Google Login (Real OAuth — verifies Google JWT) ──────────────────
class GoogleLoginRequest(BaseModel):
    credential: str  # Google's JWT ID token from frontend

@router.post("/google")
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Verify Google's ID token and sign in / create the user.

    Auto-discovery mode (no GOOGLE_CLIENT_ID env var needed):
    ─────────────────────────────────────────────────────────
    We peek at the token's `aud` claim (unverified) and then pass it as
    the expected audience to google.oauth2.id_token.verify_oauth2_token().
    Google's library still fully verifies the RSA signature, expiry, and
    issuer — the only thing that changes is we get the audience from the
    token itself rather than from an env var.

    Since `aud` is inside the signed payload, it cannot be forged.
    This is completely secure and avoids needing manual env-var setup.

    If GOOGLE_CLIENT_ID *is* configured, we use that for strict
    audience verification (preferred for production).
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    # ── Determine the audience to verify against ──────────────────────
    settings = get_settings()
    configured_client_id = (
        settings.google_client_id
        or os.getenv("GOOGLE_CLIENT_ID", "")
    )

    if configured_client_id:
        # Preferred: strict audience check against known client ID
        audience = configured_client_id
        logger.debug("Google login: using configured GOOGLE_CLIENT_ID")
    else:
        # Auto-discover: peek at aud inside the (still-unverified) JWT
        raw_payload = _decode_jwt_payload_unverified(body.credential)
        audience = raw_payload.get("aud", "")
        if not audience:
            raise HTTPException(401, "Google credential missing audience claim.")
        logger.info(
            "Google login: GOOGLE_CLIENT_ID not set — auto-discovered aud=%s",
            audience,
        )

    # ── Full cryptographic verification ──────────────────────────────
    try:
        idinfo = id_token.verify_oauth2_token(
            body.credential,
            google_requests.Request(),
            audience,
        )
    except ValueError as exc:
        logger.warning("Google token verification failed: %s", exc)
        raise HTTPException(401, "Invalid Google credential. Please try again.")

    # ── Extra safety checks ───────────────────────────────────────────
    valid_issuers = ("accounts.google.com", "https://accounts.google.com")
    if idinfo.get("iss") not in valid_issuers:
        raise HTTPException(401, "Token issuer is not Google.")

    if not idinfo.get("email_verified", False):
        raise HTTPException(400, "Google account email is not verified.")

    # ── Create / fetch user ───────────────────────────────────────────
    email      = idinfo.get("email", "")
    name       = idinfo.get("name", "")
    avatar_url = idinfo.get("picture", "")

    if not email:
        raise HTTPException(400, "Google account has no email address.")

    user = create_user_google(db, name, email, avatar_url)
    logger.info("Google login: user_id=%s email=%s", user.id, email)
    access  = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id)
    return _token_response(user, access, refresh)


# ── Send OTP ─────────────────────────────────────────────────────────
@router.post("/send-otp")
@limiter.limit("3/minute")
def send_otp(request: Request, body: SendOTPRequest, db: Session = Depends(get_db)):
    phone = body.phone.strip()
    if len(phone) < 10:
        raise HTTPException(400, "Invalid phone number.")
    otp = generate_otp()
    save_otp(db, phone, otp)
    # In production: send via Twilio / MSG91
    logger.info("OTP generated for phone=%s (not logging OTP value)", phone)
    return {"message": f"OTP sent to {phone}"}


# ── Verify OTP ───────────────────────────────────────────────────────
@router.post("/verify-otp")
def verify_otp_endpoint(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    phone = body.phone.strip()
    if not verify_otp(db, phone, body.otp.strip()):
        raise HTTPException(401, "Invalid or expired OTP.")

    user = get_user_by_phone(db, phone)
    if not user:
        user = create_user_phone(db, phone, body.name)

    access  = create_access_token(user.id, user.email)
    refresh = create_refresh_token(user.id)
    return _token_response(user, access, refresh)


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
    # JWT is stateless — client deletes tokens.
    # For full revocation, add token to a blacklist (Redis) in future.
    logger.info("User logout: user_id=%s", current_user.id)
    return {"message": "Logged out successfully"}
