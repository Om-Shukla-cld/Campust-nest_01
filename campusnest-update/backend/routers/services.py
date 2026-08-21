from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/services", tags=["services"])


@router.get("", response_model=List[schemas.ServiceOut])
def list_services(
    category: Optional[str] = None,
    area: Optional[str] = None,
    q: Optional[str] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    query = db.query(models.Service)
    if category:
        query = query.filter(models.Service.category == category)
    if area:
        query = query.filter(models.Service.area.ilike(f"%{area}%"))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Service.name.ilike(like), models.Service.description.ilike(like)))
    if min_rating is not None:
        query = query.filter(models.Service.rating >= min_rating)
    return query.order_by(models.Service.rating.desc()).all()


@router.get("/categories", response_model=List[dict])
def categories(db: Session = Depends(get_db)):
    rows = db.query(models.Service.category, models.Service.id).all()
    counts: dict = {}
    for cat, _ in rows:
        counts[cat] = counts.get(cat, 0) + 1
    return [{"category": c, "count": n} for c, n in sorted(counts.items())]
