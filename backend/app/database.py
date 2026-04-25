from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import datetime
import uuid
import os

from app.config import get_settings

_settings = get_settings()

# Support both SQLite (dev) and PostgreSQL (prod) via config
_connect_args = {"check_same_thread": False} if "sqlite" in _settings.database_url else {}

engine = create_engine(
    _settings.database_url,
    connect_args=_connect_args,
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Modern SQLAlchemy 2.x declarative base."""
    pass


# ── User model ──────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name       = Column(String, nullable=True)
    email      = Column(String, unique=True, nullable=True, index=True)
    phone      = Column(String, unique=True, nullable=True, index=True)
    password   = Column(String, nullable=True)          # hashed
    provider   = Column(String, default="email")        # email / google / phone
    avatar_url = Column(String, nullable=True)
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", lazy="dynamic")


# ── OTP store (in-memory is fine for mock; persisted for demo) ──────
class OTPRecord(Base):
    __tablename__ = "otp_records"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    phone      = Column(String, index=True)
    otp        = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    used       = Column(Boolean, default=False)


# ── Analysis History ────────────────────────────────────────────────
class Analysis(Base):
    __tablename__ = "analyses"

    id               = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id          = Column(String, ForeignKey("users.id"), index=True)
    filename         = Column(String, nullable=True)
    file_type        = Column(String, nullable=True)
    detected_field   = Column(String, nullable=True)
    detected_subfield = Column(String, nullable=True)
    ats_score        = Column(Float, nullable=True)
    grade            = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    candidate_name   = Column(String, nullable=True)
    result_json      = Column(Text, nullable=True)       # Full analysis JSON
    file_hash        = Column(String, nullable=True)      # SHA-256 for dedup
    created_at       = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="analyses")


# ── User Preferences ────────────────────────────────────────────────
class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id      = Column(String, ForeignKey("users.id"), primary_key=True)
    target_field = Column(String, nullable=True)
    target_role  = Column(String, nullable=True)
    theme        = Column(String, default="light")
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)


# ── Feedback System ─────────────────────────────────────────────────
class Feedback(Base):
    __tablename__ = "feedbacks"

    id           = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id      = Column(String, ForeignKey("users.id"), index=True, nullable=True)
    analysis_id  = Column(String, ForeignKey("analyses.id"), nullable=True)
    rating       = Column(Float, nullable=False)            # 1-5 stars
    category     = Column(String, default="general")        # general / accuracy / ui / feature
    comment      = Column(Text, nullable=True)
    page         = Column(String, nullable=True)            # which page the feedback came from
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", backref="feedbacks")


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency — yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

