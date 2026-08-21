"""Moderator console: approve owners, listings, moderate reviews & posts."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_moderator
from ..database import get_db
from .community import _post_out
from .properties import _review_dict, serialize_many, serialize_property

router = APIRouter(prefix="/moderator", tags=["moderator"])


@router.get("/dashboard")
def dashboard(_: models.User = Depends(require_moderator), db: Session = Depends(get_db)):
    P, U, R, C = models.Property, models.User, models.Review, models.CommunityPost
    return {
        "properties": {
            "pending": db.query(P).filter(P.status == "pending").count(),
            "approved": db.query(P).filter(P.status == "approved").count(),
            "rejected": db.query(P).filter(P.status == "rejected").count(),
        },
        "owners": {
            "pending": db.query(U).filter(U.role == "owner", U.is_verified == False).count(),  # noqa: E712
            "verified": db.query(U).filter(U.role == "owner", U.is_verified == True).count(),  # noqa: E712
        },
        "students": db.query(U).filter(U.role == "student").count(),
        "flagged_reviews": db.query(R).filter(R.is_flagged == True, R.is_hidden == False).count(),  # noqa: E712
        "flagged_posts": db.query(C).filter(C.is_flagged == True, C.is_hidden == False).count(),  # noqa: E712
    }


# ------------------------------------------------------------- properties ---
@router.get("/properties", response_model=List[schemas.PropertyOut])
def list_for_moderation(
    status: Optional[str] = Query("pending", pattern="^(pending|approved|rejected|all)$"),
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    q = db.query(models.Property)
    if status and status != "all":
        q = q.filter(models.Property.status == status)
    return serialize_many(db, q.order_by(models.Property.created_at.desc()).all())


@router.get("/properties/{property_id}", response_model=schemas.PropertyDetail)
def property_detail(
    property_id: int, _: models.User = Depends(require_moderator), db: Session = Depends(get_db)
):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(404, "Property not found")
    return serialize_property(db, prop, detail=True)


@router.patch("/properties/{property_id}", response_model=schemas.PropertyOut)
def moderate_property(
    property_id: int,
    body: schemas.ModerationAction,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    """Approve / reject a listing. `status` = approved | rejected | pending."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(404, "Property not found")
    prop.status = body.status
    prop.rejection_reason = body.reason if body.status == "rejected" else None
    db.commit()
    db.refresh(prop)
    return serialize_property(db, prop)


@router.patch("/properties/{property_id}/feature", response_model=schemas.PropertyOut)
def toggle_featured(
    property_id: int, _: models.User = Depends(require_moderator), db: Session = Depends(get_db)
):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(404, "Property not found")
    prop.is_featured = not prop.is_featured
    db.commit()
    return serialize_property(db, prop)


# ----------------------------------------------------------------- owners ---
@router.get("/owners", response_model=List[schemas.UserOut])
def list_owners(
    verified: Optional[bool] = None,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    q = db.query(models.User).filter(models.User.role == "owner")
    if verified is not None:
        q = q.filter(models.User.is_verified == verified)
    return q.order_by(models.User.id.desc()).all()


@router.patch("/owners/{owner_id}", response_model=schemas.UserOut)
def verify_owner(
    owner_id: int,
    is_verified: bool = True,
    is_active: Optional[bool] = None,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    owner = db.query(models.User).filter(models.User.id == owner_id, models.User.role == "owner").first()
    if not owner:
        raise HTTPException(404, "Owner not found")
    owner.is_verified = is_verified
    if is_active is not None:
        owner.is_active = is_active
    db.commit()
    db.refresh(owner)
    return owner


# ---------------------------------------------------------------- reviews ---
@router.get("/reviews", response_model=List[schemas.ReviewOut])
def list_reviews(
    flagged_only: bool = True,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    q = db.query(models.Review)
    if flagged_only:
        q = q.filter(models.Review.is_flagged == True)  # noqa: E712
    return [_review_dict(r) for r in q.order_by(models.Review.created_at.desc()).all()]


@router.patch("/reviews/{review_id}", response_model=schemas.ReviewOut)
def moderate_review(
    review_id: int,
    body: schemas.ReviewModeration,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    review = db.query(models.Review).filter(models.Review.id == review_id).first()
    if not review:
        raise HTTPException(404, "Review not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(review, k, v)
    db.commit()
    db.refresh(review)
    return _review_dict(review)


# ------------------------------------------------------------------ posts ---
@router.get("/posts", response_model=List[schemas.PostOut])
def flagged_posts(_: models.User = Depends(require_moderator), db: Session = Depends(get_db)):
    posts = db.query(models.CommunityPost).filter(models.CommunityPost.is_flagged == True).all()  # noqa: E712
    return [_post_out(p) for p in posts]


@router.patch("/posts/{post_id}", response_model=schemas.PostOut)
def moderate_post(
    post_id: int,
    is_hidden: Optional[bool] = None,
    is_flagged: Optional[bool] = None,
    _: models.User = Depends(require_moderator),
    db: Session = Depends(get_db),
):
    post = db.query(models.CommunityPost).filter(models.CommunityPost.id == post_id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    if is_hidden is not None:
        post.is_hidden = is_hidden
    if is_flagged is not None:
        post.is_flagged = is_flagged
    db.commit()
    db.refresh(post)
    return _post_out(post)
