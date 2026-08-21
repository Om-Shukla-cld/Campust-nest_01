"""
Optional Razorpay integration for booking a slot. The router is always
mounted; if RAZORPAY keys are not configured every endpoint returns 503 so the
rest of the API keeps working without payment credentials.
"""
import hashlib
import hmac

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..config import settings
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])

_client = None
if settings.payments_enabled:
    try:
        import razorpay  # type: ignore

        _client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    except Exception:  # pragma: no cover
        _client = None


def _require_payments():
    if not _client:
        raise HTTPException(503, "Payments are not configured on this server (set RAZORPAY_KEY_ID / SECRET)")


@router.get("/status")
def payments_status():
    return {"enabled": bool(_client), "key_id": settings.RAZORPAY_KEY_ID if _client else None}


@router.post("/create-order", response_model=schemas.CreateOrderResponse)
def create_order(
    body: schemas.CreateOrderRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_payments()
    slot = db.query(models.Slot).filter(models.Slot.id == body.slot_id).first()
    if not slot:
        raise HTTPException(404, "Slot not found")
    if slot.is_occupied:
        raise HTTPException(409, "This slot is already taken")

    amount_paise = int(slot.rent_per_slot or slot.property.rent) * 100
    order = _client.order.create(
        {
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"slot_{slot.id}_user_{user.id}",
            "notes": {"slot_id": str(slot.id), "user_id": str(user.id)},
        }
    )
    db.add(
        models.Payment(
            slot_id=slot.id,
            user_id=user.id,
            razorpay_order_id=order["id"],
            amount=amount_paise // 100,
            status="created",
        )
    )
    db.commit()
    return schemas.CreateOrderResponse(
        order_id=order["id"], amount=amount_paise, currency="INR", key_id=settings.RAZORPAY_KEY_ID
    )


@router.post("/verify")
def verify_payment(
    body: schemas.VerifyPaymentRequest,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_payments()
    generated = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{body.razorpay_order_id}|{body.razorpay_payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()

    payment = (
        db.query(models.Payment)
        .filter(models.Payment.razorpay_order_id == body.razorpay_order_id, models.Payment.user_id == user.id)
        .first()
    )
    if not payment:
        raise HTTPException(404, "Payment record not found")

    if not hmac.compare_digest(generated, body.razorpay_signature):
        payment.status = "failed"
        db.commit()
        raise HTTPException(400, "Payment signature verification failed")

    payment.status = "paid"
    payment.razorpay_payment_id = body.razorpay_payment_id
    slot = db.query(models.Slot).filter(models.Slot.id == payment.slot_id).first()
    if slot:
        slot.is_occupied = True
        slot.occupied_by = user.id
    db.commit()
    return {"status": "paid", "slot_id": payment.slot_id}
