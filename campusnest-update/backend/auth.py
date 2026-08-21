"""
Authentication layer: OTP issuance/verification + JWT creation/validation
+ FastAPI dependencies for role-based access.
"""
import logging
import random
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from . import models
from .config import settings
from .database import get_db
from .models import utcnow

log = logging.getLogger("campusnest.auth")


# ------------------------------------------------------------------- OTP ---
def normalize_phone(phone: str) -> str:
    p = phone.strip().replace(" ", "").replace("-", "")
    if p and not p.startswith("+"):
        # assume Indian numbers when no country code supplied
        p = "+91" + p[-10:] if len(p) >= 10 else "+91" + p
    return p


def issue_otp(db: Session, identifier: str, purpose: str = "login") -> str:
    """Create a fresh OTP for `identifier`. In a real deployment you would
    hand the code to an SMS/email provider here; in DEBUG mode we just log it."""
    code = settings.DEMO_OTP if settings.DEBUG else f"{random.randint(0, 9999):04d}"
    db.add(
        models.OTPCode(
            identifier=identifier,
            code=code,
            purpose=purpose,
            expires_at=utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
        )
    )
    db.commit()
    log.info("OTP for %s: %s", identifier, code)
    return code


def verify_otp(db: Session, identifier: str, code: str) -> bool:
    # Demo/dev shortcut: DEMO_OTP always works while DEBUG=true
    if settings.DEBUG and code == settings.DEMO_OTP:
        return True
    otp = (
        db.query(models.OTPCode)
        .filter(
            models.OTPCode.identifier == identifier,
            models.OTPCode.code == code,
            models.OTPCode.used == False,  # noqa: E712
            models.OTPCode.expires_at >= utcnow(),
        )
        .order_by(models.OTPCode.id.desc())
        .first()
    )
    if not otp:
        return False
    otp.used = True
    db.commit()
    return True


# ------------------------------------------------------------------- JWT ---
def create_access_token(user: models.User) -> str:
    now = utcnow()
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "name": user.name,
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired, please log in again")
    except jwt.PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


# ---------------------------------------------------------- dependencies ---
def _extract_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def get_current_user(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> models.User:
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    payload = decode_token(token)
    user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> Optional[models.User]:
    token = _extract_bearer(authorization)
    if not token:
        return None
    try:
        payload = decode_token(token)
    except HTTPException:
        return None
    return db.query(models.User).filter(models.User.id == int(payload["sub"])).first()


def require_role(*roles: str):
    def _dep(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, f"This action requires role: {', '.join(roles)}"
            )
        return user

    return _dep


require_student = require_role("student")
require_owner = require_role("owner")
require_moderator = require_role("moderator")
require_owner_or_moderator = require_role("owner", "moderator")
