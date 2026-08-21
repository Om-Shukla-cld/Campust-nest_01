from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user, get_current_user_optional
from ..database import get_db
from ..models import utcnow

router = APIRouter(prefix="/transport", tags=["transport"])


def _ride_out(r: models.TransportRide, user: Optional[models.User]) -> dict:
    d = schemas.RideOut.model_validate(r).model_dump()
    d["host"] = schemas.AuthorBrief.model_validate(r.host).model_dump() if r.host else None
    d["seats_left"] = max(0, r.seats_total - r.seats_taken)
    d["is_joined"] = bool(user and any(p.user_id == user.id for p in r.passengers))
    return d


@router.get("/rides", response_model=List[schemas.RideOut])
def list_rides(
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    mode: Optional[str] = None,
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    include_past: bool = False,
    db: Session = Depends(get_db),
    user: Optional[models.User] = Depends(get_current_user_optional),
):
    q = db.query(models.TransportRide).filter(models.TransportRide.status.in_(["open", "full"]))
    if origin:
        q = q.filter(models.TransportRide.origin.ilike(f"%{origin}%"))
    if destination:
        q = q.filter(models.TransportRide.destination.ilike(f"%{destination}%"))
    if mode:
        q = q.filter(models.TransportRide.mode == mode)
    if not include_past:
        q = q.filter(models.TransportRide.depart_at >= utcnow())
    rides = q.order_by(models.TransportRide.depart_at.asc()).all()
    if date:
        rides = [r for r in rides if r.depart_at.strftime("%Y-%m-%d") == date]
    return [_ride_out(r, user) for r in rides]


@router.get("/rides/mine", response_model=List[schemas.RideOut])
def my_rides(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    hosted = db.query(models.TransportRide).filter(models.TransportRide.host_id == user.id).all()
    joined_ids = [p.ride_id for p in db.query(models.RidePassenger).filter(models.RidePassenger.user_id == user.id)]
    joined = db.query(models.TransportRide).filter(models.TransportRide.id.in_(joined_ids)).all() if joined_ids else []
    seen, out = set(), []
    for r in hosted + joined:
        if r.id not in seen:
            seen.add(r.id)
            out.append(_ride_out(r, user))
    return out


@router.post("/rides", response_model=schemas.RideOut, status_code=201)
def create_ride(
    body: schemas.RideCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ride = models.TransportRide(host_id=user.id, **body.model_dump())
    db.add(ride)
    db.commit()
    db.refresh(ride)
    return _ride_out(ride, user)


@router.post("/rides/{ride_id}/join", response_model=schemas.RideOut)
def join_ride(
    ride_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    ride = db.query(models.TransportRide).filter(models.TransportRide.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")
    if ride.host_id == user.id:
        raise HTTPException(400, "You are the host of this ride")
    if any(p.user_id == user.id for p in ride.passengers):
        raise HTTPException(400, "Already joined")
    if ride.seats_taken >= ride.seats_total or ride.status != "open":
        raise HTTPException(409, "Ride is full")
    db.add(models.RidePassenger(ride_id=ride.id, user_id=user.id))
    ride.seats_taken += 1
    if ride.seats_taken >= ride.seats_total:
        ride.status = "full"
    db.commit()
    db.refresh(ride)
    return _ride_out(ride, user)


@router.post("/rides/{ride_id}/leave", response_model=schemas.RideOut)
def leave_ride(
    ride_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    ride = db.query(models.TransportRide).filter(models.TransportRide.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")
    p = (
        db.query(models.RidePassenger)
        .filter(models.RidePassenger.ride_id == ride_id, models.RidePassenger.user_id == user.id)
        .first()
    )
    if not p:
        raise HTTPException(400, "You have not joined this ride")
    db.delete(p)
    ride.seats_taken = max(0, ride.seats_taken - 1)
    if ride.status == "full":
        ride.status = "open"
    db.commit()
    db.refresh(ride)
    return _ride_out(ride, user)


@router.delete("/rides/{ride_id}", response_model=schemas.Message)
def cancel_ride(
    ride_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    ride = db.query(models.TransportRide).filter(models.TransportRide.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")
    if ride.host_id != user.id and user.role != "moderator":
        raise HTTPException(403, "Only the host can cancel")
    ride.status = "cancelled"
    db.commit()
    return schemas.Message(message="Ride cancelled")
