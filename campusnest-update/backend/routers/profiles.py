from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=schemas.UserOut)
def get_my_profile(user: models.User = Depends(get_current_user)):
    return user


@router.put("/me", response_model=schemas.UserOut)
def update_my_profile(
    body: schemas.ProfileUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_public_profile(user_id: int, db: Session = Depends(get_db)):
    """Lets a prospective roommate view someone's lifestyle profile."""
    profile = db.query(models.User).filter(models.User.id == user_id).first()
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile
