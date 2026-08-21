"""Roommate compatibility matching based on lifestyle profile fields."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/roommates", tags=["roommates"])

# field -> weight (sums to 100)
WEIGHTS = {
    "sleep": 25,
    "cleanliness": 20,
    "smoker": 20,
    "veg": 15,
    "study": 10,
    "budget": 10,
}


def compatibility(a: models.User, b: models.User):
    score = 0.0
    matched, differs = [], []
    for field, weight in WEIGHTS.items():
        va, vb = getattr(a, field), getattr(b, field)
        if va is None or vb is None:
            score += weight * 0.5  # unknown → neutral
            continue
        if field == "budget":
            diff = abs(int(va) - int(vb))
            ratio = max(0.0, 1 - diff / max(int(va), int(vb), 1))
            score += weight * ratio
            (matched if ratio > 0.8 else differs).append("budget")
        elif str(va).lower() == str(vb).lower() or "flexible" in (str(va).lower(), str(vb).lower()):
            score += weight
            matched.append(field)
        elif field == "smoker" and {str(va).lower(), str(vb).lower()} == {"no", "occasionally"}:
            score += weight * 0.5
            differs.append(field)
        else:
            differs.append(field)
    return int(round(score)), matched, differs


@router.get("/matches", response_model=List[schemas.RoommateMatch])
def my_matches(
    min_score: int = Query(0, ge=0, le=100),
    limit: int = Query(20, le=100),
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    candidates = (
        db.query(models.User)
        .filter(
            models.User.role == "student",
            models.User.id != user.id,
            models.User.is_active == True,  # noqa: E712
            models.User.looking_for_roommate == True,  # noqa: E712
        )
        .all()
    )
    results = []
    for c in candidates:
        score, matched, differs = compatibility(user, c)
        if score >= min_score:
            results.append(
                schemas.RoommateMatch(user=c, score=score, matched_on=matched, differs_on=differs)
            )
    results.sort(key=lambda r: -r.score)
    return results[:limit]


@router.get("/score/{other_id}", response_model=schemas.RoommateMatch)
def score_with(
    other_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    other = db.query(models.User).filter(models.User.id == other_id).first()
    if not other:
        from fastapi import HTTPException

        raise HTTPException(404, "User not found")
    score, matched, differs = compatibility(user, other)
    return schemas.RoommateMatch(user=other, score=score, matched_on=matched, differs_on=differs)


@router.get("/browse", response_model=List[schemas.UserOut])
def browse(
    veg: Optional[str] = None,
    sleep: Optional[str] = None,
    smoker: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Public browse of students looking for a roommate (no login needed)."""
    q = db.query(models.User).filter(
        models.User.role == "student", models.User.looking_for_roommate == True  # noqa: E712
    )
    if veg:
        q = q.filter(models.User.veg == veg)
    if sleep:
        q = q.filter(models.User.sleep == sleep)
    if smoker:
        q = q.filter(models.User.smoker == smoker)
    return q.limit(50).all()
