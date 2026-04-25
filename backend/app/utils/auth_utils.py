"""
JWT Auth Utilities — access + refresh token pattern.

Access token:  short-lived (15 min) — sent on every API request.
Refresh token: long-lived (7 days)  — used only to get a new access token.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db, User
from app.config import get_settings

import logging

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# ── Token lifetimes ─────────────────────────────────────────────────
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(user_id: str, email: Optional[str] = None) -> str:
    """Create a short-lived access token (15 min)."""
    s = get_settings()
    payload = {
        "sub":   user_id,
        "email": email,
        "type":  "access",
        "iat":   datetime.utcnow(),
        "exp":   datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived refresh token (7 days)."""
    s = get_settings()
    payload = {
        "sub":  user_id,
        "type": "refresh",
        "iat":  datetime.utcnow(),
        "exp":  datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT, checking the token type."""
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
    except JWTError:
        logger.warning("JWT decode failed for token type=%s", expected_type)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if payload.get("type") != expected_type:
        logger.warning("Token type mismatch: expected=%s got=%s", expected_type, payload.get("type"))
        raise HTTPException(status_code=401, detail="Invalid token type")

    return payload


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Extract current user from a valid access token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(credentials.credentials, expected_type="access")
    user_id = payload.get("sub")
    user    = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Returns user if token present, else None (for optional auth routes)."""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id = payload.get("sub")
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None
