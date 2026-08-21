from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user_optional
from ..database import get_db

router = APIRouter(prefix="/properties", tags=["properties"])


# ---------------------------------------------------------------- helpers ---
def _rating_map(db: Session, ids: List[int]) -> dict:
    if not ids:
        return {}
    rows = (
        db.query(
            models.Review.property_id,
            func.avg(models.Review.stars),
            func.count(models.Review.id),
        )
        .filter(models.Review.property_id.in_(ids), models.Review.is_hidden == False)  # noqa: E712
        .group_by(models.Review.property_id)
        .all()
    )
    return {pid: (round(float(avg or 0), 1), int(cnt)) for pid, avg, cnt in rows}


def _slot_map(db: Session, ids: List[int]) -> dict:
    if not ids:
        return {}
    rows = (
        db.query(models.Slot.property_id, func.count(models.Slot.id))
        .filter(models.Slot.property_id.in_(ids), models.Slot.is_occupied == False)  # noqa: E712
        .group_by(models.Slot.property_id)
        .all()
    )
    return {pid: int(cnt) for pid, cnt in rows}


def serialize_property(db: Session, prop: models.Property, detail: bool = False) -> dict:
    """Shared by several routers — turns a Property ORM object into the
    PropertyOut / PropertyDetail payload with computed fields filled in."""
    ratings = _rating_map(db, [prop.id])
    slots = _slot_map(db, [prop.id])
    avg, cnt = ratings.get(prop.id, (0.0, 0))
    data = schemas.PropertyOut.model_validate(prop).model_dump()
    data.update(
        avg_rating=avg,
        review_count=cnt,
        available_slots=slots.get(prop.id, 0),
        is_approved=prop.status == "approved",
    )
    if detail:
        data["slots"] = [schemas.SlotOut.model_validate(s).model_dump() for s in prop.slots]
        data["reviews"] = [
            _review_dict(r) for r in prop.reviews if not r.is_hidden
        ]
    return data


def _review_dict(r: models.Review) -> dict:
    d = schemas.ReviewOut.model_validate(r).model_dump()
    d["author_name"] = "Anonymous" if r.is_anonymous else (r.user.name if r.user else "Student")
    return d


def serialize_many(db: Session, props: List[models.Property]) -> List[dict]:
    ids = [p.id for p in props]
    ratings = _rating_map(db, ids)
    slots = _slot_map(db, ids)
    out = []
    for p in props:
        avg, cnt = ratings.get(p.id, (0.0, 0))
        d = schemas.PropertyOut.model_validate(p).model_dump()
        d.update(
            avg_rating=avg,
            review_count=cnt,
            available_slots=slots.get(p.id, 0),
            is_approved=p.status == "approved",
        )
        out.append(d)
    return out


# -------------------------------------------------------------- endpoints ---
@router.get("", response_model=schemas.PropertyList)
def list_properties(
    q: Optional[str] = Query(None, description="Free-text search on name/area/address"),
    type: Optional[str] = None,
    area: Optional[str] = None,
    gender: Optional[str] = None,
    min_rent: Optional[int] = None,
    max_rent: Optional[int] = None,
    max_distance: Optional[float] = None,
    amenities: Optional[str] = Query(None, description="Comma separated, e.g. wifi,ac"),
    min_rating: Optional[float] = None,
    sort: str = Query("recommended", pattern="^(recommended|rent_asc|rent_desc|distance|rating|newest)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_lat: Optional[float] = None,
    max_lat: Optional[float] = None,
    min_lng: Optional[float] = None,
    max_lng: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Public listing — only moderator-approved properties are returned."""
    query = db.query(models.Property).filter(models.Property.status == "approved")

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Property.name.ilike(like),
                models.Property.area.ilike(like),
                models.Property.address.ilike(like),
                models.Property.description.ilike(like),
            )
        )
    if type:
        query = query.filter(models.Property.type == type)
    if area:
        query = query.filter(models.Property.area.ilike(f"%{area}%"))
    if gender:
        query = query.filter(or_(models.Property.gender == gender, models.Property.gender == "any"))
    if min_rent is not None:
        query = query.filter(models.Property.rent >= min_rent)
    if max_rent is not None:
        query = query.filter(models.Property.rent <= max_rent)
    if max_distance is not None:
        query = query.filter(models.Property.distance_km <= max_distance)
    if None not in (min_lat, max_lat, min_lng, max_lng):
        query = query.filter(
            models.Property.lat.between(min_lat, max_lat),
            models.Property.lng.between(min_lng, max_lng),
        )

    props = query.all()

    # amenities / rating filters are applied in Python (JSON column portability)
    if amenities:
        wanted = {a.strip().lower() for a in amenities.split(",") if a.strip()}
        props = [p for p in props if wanted.issubset({a.lower() for a in (p.amenities or [])})]

    items = serialize_many(db, props)
    if min_rating is not None:
        items = [i for i in items if i["avg_rating"] >= min_rating]

    key = {
        "rent_asc": lambda i: i["rent"],
        "rent_desc": lambda i: -i["rent"],
        "distance": lambda i: i["distance_km"] or 0,
        "rating": lambda i: (-i["avg_rating"], -i["review_count"]),
        "newest": lambda i: -(i["id"]),
        # recommended: featured first, then rating, then closeness
        "recommended": lambda i: (not i["is_featured"], -i["avg_rating"], i["distance_km"] or 0),
    }[sort]
    items.sort(key=key)

    total = len(items)
    start = (page - 1) * page_size
    return schemas.PropertyList(total=total, items=items[start : start + page_size])


@router.get("/areas", response_model=List[str])
def list_areas(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Property.area)
        .filter(models.Property.status == "approved", models.Property.area.isnot(None))
        .distinct()
        .all()
    )
    return sorted({r[0] for r in rows})


@router.get("/featured", response_model=List[schemas.PropertyOut])
def featured(db: Session = Depends(get_db)):
    props = (
        db.query(models.Property)
        .filter(models.Property.status == "approved", models.Property.is_featured == True)  # noqa: E712
        .limit(6)
        .all()
    )
    return serialize_many(db, props)


@router.post("/compare", response_model=schemas.CompareResponse)
def compare_properties(body: schemas.CompareRequest, db: Session = Depends(get_db)):
    props = (
        db.query(models.Property)
        .filter(models.Property.id.in_(body.property_ids), models.Property.status == "approved")
        .all()
    )
    if len(props) < 2:
        raise HTTPException(404, "Need at least two approved properties to compare")

    items = serialize_many(db, props)
    cheapest = min(items, key=lambda i: i["rent"] + (i["other_price"] or 0))
    closest = min(items, key=lambda i: i["distance_km"] or 9e9)
    safest = max(items, key=lambda i: i["safety_score"] or 0)
    top_rated = max(items, key=lambda i: (i["avg_rating"], i["review_count"]))

    # best value: normalised score across rent (lower better), rating, safety, amenities
    max_rent = max(i["rent"] for i in items) or 1
    scored = []
    for i in items:
        score = (
            (1 - i["rent"] / max_rent) * 40
            + (i["avg_rating"] / 5) * 25
            + ((i["safety_score"] or 0) / 5) * 20
            + min(len(i["amenities"] or []), 8) / 8 * 15
        )
        scored.append((score, i))
    best = max(scored, key=lambda s: s[0])[1]

    return schemas.CompareResponse(
        properties=items,
        best_value_id=best["id"],
        cheapest_id=cheapest["id"],
        closest_id=closest["id"],
        safest_id=safest["id"],
        top_rated_id=top_rated["id"],
        summary={
            "rent_range": [min(i["rent"] for i in items), max(i["rent"] for i in items)],
            "avg_rent": round(sum(i["rent"] for i in items) / len(items)),
            "common_amenities": sorted(
                set.intersection(*[set(i["amenities"] or []) for i in items]) if items else set()
            ),
        },
    )


@router.get("/{property_id}", response_model=schemas.PropertyDetail)
def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_optional),
):
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(404, "Property not found")
    # unapproved listings are visible only to their owner and moderators
    if prop.status != "approved":
        if not user or (user.role != "moderator" and user.id != prop.owner_id):
            raise HTTPException(404, "Property not found")
    return serialize_property(db, prop, detail=True)


@router.get("/{property_id}/slots", response_model=List[schemas.SlotOut])
def get_property_slots(property_id: int, db: Session = Depends(get_db)):
    return db.query(models.Slot).filter(models.Slot.property_id == property_id).all()


@router.get("/{property_id}/reviews", response_model=List[schemas.ReviewOut])
def get_property_reviews(property_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(models.Review)
        .filter(models.Review.property_id == property_id, models.Review.is_hidden == False)  # noqa: E712
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return [_review_dict(r) for r in reviews]
