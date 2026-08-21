"""Owner dashboard: manage own listings and tenants."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import require_owner
from ..database import get_db
from .properties import serialize_many, serialize_property

router = APIRouter(prefix="/owner", tags=["owner"])


def _own_property(db: Session, owner: models.User, property_id: int) -> models.Property:
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop or prop.owner_id != owner.id:
        raise HTTPException(404, "Property not found")
    return prop


@router.get("/dashboard")
def dashboard(owner: models.User = Depends(require_owner), db: Session = Depends(get_db)):
    props = db.query(models.Property).filter(models.Property.owner_id == owner.id).all()
    ids = [p.id for p in props]
    tenants = db.query(models.Tenant).filter(models.Tenant.property_id.in_(ids)).all() if ids else []
    slots = db.query(models.Slot).filter(models.Slot.property_id.in_(ids)).all() if ids else []
    return {
        "owner": schemas.UserOut.model_validate(owner).model_dump(),
        "stats": {
            "total_properties": len(props),
            "approved": sum(p.status == "approved" for p in props),
            "pending": sum(p.status == "pending" for p in props),
            "rejected": sum(p.status == "rejected" for p in props),
            "total_slots": len(slots),
            "occupied_slots": sum(s.is_occupied for s in slots),
            "active_tenants": sum(t.end_date is None for t in tenants),
            "monthly_revenue": sum((t.rent or 0) for t in tenants if t.end_date is None),
            "rent_due": sum((t.rent or 0) for t in tenants if t.end_date is None and t.rent_status != "paid"),
        },
    }


@router.get("/properties", response_model=List[schemas.PropertyOut])
def my_properties(owner: models.User = Depends(require_owner), db: Session = Depends(get_db)):
    props = db.query(models.Property).filter(models.Property.owner_id == owner.id).order_by(models.Property.id.desc()).all()
    return serialize_many(db, props)


@router.post("/properties", response_model=schemas.PropertyDetail, status_code=201)
def create_property(
    body: schemas.PropertyCreate,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    """New listing → goes to moderator queue (status=pending)."""
    prop = models.Property(owner_id=owner.id, status="pending", **body.model_dump())
    db.add(prop)
    db.flush()
    for i in range(max(1, body.total_slots)):
        db.add(models.Slot(property_id=prop.id, label=f"Bed {i + 1}", rent_per_slot=body.rent))
    db.commit()
    db.refresh(prop)
    return serialize_property(db, prop, detail=True)


@router.patch("/properties/{property_id}", response_model=schemas.PropertyDetail)
def update_property(
    property_id: int,
    body: schemas.PropertyUpdate,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    prop = _own_property(db, owner, property_id)
    changes = body.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(prop, k, v)
    # material edits go back to moderation
    if {"rent", "address", "name", "type"} & set(changes) and prop.status == "approved":
        prop.status = "pending"
    db.commit()
    db.refresh(prop)
    return serialize_property(db, prop, detail=True)


@router.delete("/properties/{property_id}", response_model=schemas.Message)
def delete_property(
    property_id: int, owner: models.User = Depends(require_owner), db: Session = Depends(get_db)
):
    prop = _own_property(db, owner, property_id)
    db.delete(prop)
    db.commit()
    return schemas.Message(message="Property deleted")


@router.patch("/properties/{property_id}/slots/{slot_id}", response_model=schemas.SlotOut)
def toggle_slot(
    property_id: int,
    slot_id: int,
    is_occupied: bool,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    _own_property(db, owner, property_id)
    slot = db.query(models.Slot).filter(models.Slot.id == slot_id, models.Slot.property_id == property_id).first()
    if not slot:
        raise HTTPException(404, "Slot not found")
    slot.is_occupied = is_occupied
    if not is_occupied:
        slot.occupied_by = None
    db.commit()
    db.refresh(slot)
    return slot


# ---------------------------------------------------------------- tenants ---
@router.get("/tenants", response_model=List[schemas.TenantOut])
def list_tenants(
    property_id: Optional[int] = None,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    ids = [p.id for p in db.query(models.Property.id).filter(models.Property.owner_id == owner.id)]
    if not ids:
        return []
    q = db.query(models.Tenant).filter(models.Tenant.property_id.in_(ids))
    if property_id:
        q = q.filter(models.Tenant.property_id == property_id)
    return q.order_by(models.Tenant.id.desc()).all()


@router.post("/tenants", response_model=schemas.TenantOut, status_code=201)
def add_tenant(
    body: schemas.TenantCreate,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    prop = _own_property(db, owner, body.property_id)
    data = body.model_dump(exclude_unset=True)
    if data.get("rent") is None:
        data["rent"] = prop.rent
    if data.get("start_date") is None:
        data.pop("start_date", None)
    # link to a registered student if the reg_no matches
    if body.reg_no:
        student = db.query(models.User).filter(models.User.reg_no == body.reg_no.upper()).first()
        if student:
            data["student_id"] = student.id
    tenant = models.Tenant(**data)
    db.add(tenant)
    # occupy the slot (explicit or first free)
    slot = None
    if body.slot_id:
        slot = db.query(models.Slot).filter(models.Slot.id == body.slot_id, models.Slot.property_id == prop.id).first()
    if slot is None:
        slot = db.query(models.Slot).filter(models.Slot.property_id == prop.id, models.Slot.is_occupied == False).first()  # noqa: E712
    if slot:
        slot.is_occupied = True
        slot.occupied_by = data.get("student_id")
        tenant.slot_id = slot.id
    db.commit()
    db.refresh(tenant)
    return tenant


@router.patch("/tenants/{tenant_id}", response_model=schemas.TenantOut)
def update_tenant(
    tenant_id: int,
    body: schemas.TenantUpdate,
    owner: models.User = Depends(require_owner),
    db: Session = Depends(get_db),
):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    _own_property(db, owner, tenant.property_id)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(tenant, k, v)
    if body.end_date and tenant.slot_id:
        slot = db.query(models.Slot).filter(models.Slot.id == tenant.slot_id).first()
        if slot:
            slot.is_occupied = False
            slot.occupied_by = None
    db.commit()
    db.refresh(tenant)
    return tenant


@router.delete("/tenants/{tenant_id}", response_model=schemas.Message)
def remove_tenant(
    tenant_id: int, owner: models.User = Depends(require_owner), db: Session = Depends(get_db)
):
    tenant = db.query(models.Tenant).filter(models.Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    _own_property(db, owner, tenant.property_id)
    if tenant.slot_id:
        slot = db.query(models.Slot).filter(models.Slot.id == tenant.slot_id).first()
        if slot:
            slot.is_occupied = False
            slot.occupied_by = None
    db.delete(tenant)
    db.commit()
    return schemas.Message(message="Tenant removed")
