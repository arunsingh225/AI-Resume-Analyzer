import random
import string
import datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import User, OTPRecord

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)


# ── User CRUD ───────────────────────────────────────────────────────
def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> User | None:
    return db.query(User).filter(User.phone == phone).first()


def create_user_email(db: Session, name: str, email: str, password: str) -> User:
    user = User(
        name=name,
        email=email,
        password=hash_password(password),
        provider="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_google(db: Session, name: str, email: str, avatar_url: str = "") -> User:
    """Create or fetch user via Google OAuth mock."""
    existing = get_user_by_email(db, email)
    if existing:
        return existing
    user = User(name=name, email=email, provider="google", avatar_url=avatar_url)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user_phone(db: Session, phone: str, name: str = "") -> User:
    """Create user after OTP verified."""
    user = User(name=name or f"User-{phone[-4:]}", phone=phone, provider="phone")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── OTP helpers ─────────────────────────────────────────────────────
OTP_VALID_MINUTES = 10


def generate_otp(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def save_otp(db: Session, phone: str, otp: str):
    # Invalidate old OTPs for this phone
    old = db.query(OTPRecord).filter(OTPRecord.phone == phone, OTPRecord.used == False).all()
    for rec in old:
        rec.used = True
    db.commit()

    record = OTPRecord(phone=phone, otp=otp)
    db.add(record)
    db.commit()


def verify_otp(db: Session, phone: str, otp: str) -> bool:
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=OTP_VALID_MINUTES)
    record = (
        db.query(OTPRecord)
        .filter(
            OTPRecord.phone == phone,
            OTPRecord.otp   == otp,
            OTPRecord.used  == False,
            OTPRecord.created_at >= cutoff,
        )
        .order_by(OTPRecord.created_at.desc())
        .first()
    )
    if not record:
        return False
    record.used = True
    db.commit()
    return True
