from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import (
    create_access_token,
    get_current_user,
    issue_otp,
    normalize_phone,
    verify_otp,
)
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/send-otp", response_model=schemas.SendOTPResponse)
def send_otp(body: schemas.SendOTPRequest, db: Session = Depends(get_db)):
    """Step 1 of login. Students pass their registration number, owners /
    moderators pass their phone number. In DEBUG mode the demo OTP is echoed
    back so the frontend can show it."""
    identifier = body.identifier.strip()
    if body.role == "student":
        identifier = identifier.upper()
        if len(identifier) < 5:
            raise HTTPException(400, "Invalid registration number")
    else:
        identifier = normalize_phone(identifier)
        if len(identifier) < 10:
            raise HTTPException(400, "Invalid phone number")

    code = issue_otp(db, identifier)
    return schemas.SendOTPResponse(
        message=f"OTP sent to {identifier}" if not settings.DEBUG else f"Demo mode — use OTP {code}",
        identifier=identifier,
        expires_in_minutes=settings.OTP_EXPIRE_MINUTES,
        demo_otp=code if settings.DEBUG else None,
    )


def _login_response(user: models.User) -> schemas.TokenResponse:
    return schemas.TokenResponse(access_token=create_access_token(user), user=user)


@router.post("/student/login", response_model=schemas.TokenResponse)
def student_login(body: schemas.StudentLoginRequest, db: Session = Depends(get_db)):
    reg_no = body.reg_no.strip().upper()
    if not verify_otp(db, reg_no, body.otp.strip()):
        raise HTTPException(401, "Invalid or expired OTP")

    user = db.query(models.User).filter(models.User.reg_no == reg_no).first()
    if not user:
        user = models.User(role="student", reg_no=reg_no, name=body.name or f"Student {reg_no}")
        db.add(user)
        db.commit()
        db.refresh(user)
    elif body.name and not user.name:
        user.name = body.name
        db.commit()
    if user.role != "student":
        raise HTTPException(403, "This registration number is not a student account")
    return _login_response(user)


@router.post("/owner/login", response_model=schemas.TokenResponse)
def owner_login(body: schemas.PhoneLoginRequest, db: Session = Depends(get_db)):
    """Phone + OTP login for property owners. The demo moderator phone
    (+910000000000) also logs in here and gets the moderator role."""
    phone = normalize_phone(body.phone)
    if not verify_otp(db, phone, body.otp.strip()):
        raise HTTPException(401, "Invalid or expired OTP")

    user = db.query(models.User).filter(models.User.phone == phone).first()
    if not user:
        role = "moderator" if phone == settings.MODERATOR_PHONE else "owner"
        user = models.User(role=role, phone=phone, name=body.name or f"Owner {phone[-4:]}")
        db.add(user)
        db.commit()
        db.refresh(user)
    elif body.name and not user.name:
        user.name = body.name
        db.commit()
    if user.role == "student":
        raise HTTPException(403, "This phone belongs to a student account")
    return _login_response(user)


@router.post("/moderator/login", response_model=schemas.TokenResponse)
def moderator_login(body: schemas.PhoneLoginRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(body.phone)
    if not verify_otp(db, phone, body.otp.strip()):
        raise HTTPException(401, "Invalid or expired OTP")
    user = db.query(models.User).filter(models.User.phone == phone).first()
    if not user or user.role != "moderator":
        raise HTTPException(403, "Not a moderator account")
    return _login_response(user)


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/logout", response_model=schemas.Message)
def logout(_: models.User = Depends(get_current_user)):
    # Stateless JWT — the client simply discards the token.
    return schemas.Message(message="Logged out")
