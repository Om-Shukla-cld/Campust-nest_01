from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from .properties import _review_dict

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=schemas.ReviewOut, status_code=201)
def create_review(
    body: schemas.ReviewCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prop = db.query(models.Property).filter(models.Property.id == body.property_id).first()
    if not prop or prop.status != "approved":
        raise HTTPException(404, "Property not found")
    if prop.owner_id == user.id:
        raise HTTPException(400, "You cannot review your own property")

    existing = (
        db.query(models.Review)
        .filter(models.Review.property_id == prop.id, models.Review.user_id == user.id)
        .first()
    )
    if existing:
        existing.stars = body.stars
        existing.comment = body.comment
        existing.is_anonymous = body.is_anonymous
        db.commit()
        db.refresh(existing)
        return _review_dict(existing)

    review = models.Review(
        property_id=prop.id,
        user_id=user.id,
        stars=body.stars,
        comment=body.comment,
        is_anonymous=body.is_anonymous,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _review_dict(review)


@router.get("/mine", response_model=List[schemas.ReviewOut])
def my_reviews(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(models.Review).filter(models.Review.user_id == user.id).all()
    return [_review_dict(r) for r in rows]


@router.delete("/{review_id}", response_model=schemas.Message)
def delete_review(
    review_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    if review.user_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Not allowed")
    db.delete(review)
    db.commit()
    return schemas.Message(message="Review deleted")


@router.post("/{review_id}/flag", response_model=schemas.Message)
def flag_review(
    review_id: int,
    _: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    review.is_flagged = True
    db.commit()
    return schemas.Message(message="Review reported to moderators")
