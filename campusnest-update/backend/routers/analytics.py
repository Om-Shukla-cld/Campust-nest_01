"""Rent trend analytics — powers the RentAnalyzer screen."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["analytics"])


@router.get("/rent-trends", response_model=List[schemas.RentTrendSeries])
def rent_trends(
    area: Optional[str] = None,
    property_type: Optional[str] = Query(None, alias="type"),
    months: int = Query(6, ge=1, le=24),
    db: Session = Depends(get_db),
):
    q = db.query(models.RentTrend)
    if area:
        q = q.filter(models.RentTrend.area.ilike(f"%{area}%"))
    if property_type:
        q = q.filter(models.RentTrend.property_type == property_type)
    rows = q.order_by(models.RentTrend.area, models.RentTrend.property_type, models.RentTrend.month).all()

    grouped: dict = {}
    for r in rows:
        grouped.setdefault((r.area, r.property_type), []).append(r)

    out = []
    for (a, t), pts in grouped.items():
        pts = pts[-months:]
        first, last = pts[0].avg_rent, pts[-1].avg_rent
        change = round((last - first) / first * 100, 1) if first else 0
        out.append(
            schemas.RentTrendSeries(
                area=a,
                property_type=t,
                points=[schemas.RentTrendPoint(month=p.month, avg_rent=p.avg_rent, listings=p.listings) for p in pts],
                change_pct=change,
            )
        )
    return out


@router.get("/rent-trends/areas", response_model=List[schemas.AreaSummary])
def area_summary(db: Session = Depends(get_db)):
    """Live aggregate of approved listings, per area."""
    rows = (
        db.query(
            models.Property.area,
            func.avg(models.Property.rent),
            func.min(models.Property.rent),
            func.max(models.Property.rent),
            func.count(models.Property.id),
            func.avg(models.Property.safety_score),
        )
        .filter(models.Property.status == "approved", models.Property.area.isnot(None))
        .group_by(models.Property.area)
        .all()
    )
    return [
        schemas.AreaSummary(
            area=a,
            avg_rent=int(avg or 0),
            min_rent=int(mn or 0),
            max_rent=int(mx or 0),
            listings=int(cnt),
            avg_safety=round(float(safety or 0), 1),
        )
        for a, avg, mn, mx, cnt, safety in rows
    ]


@router.get("/rent-trends/analyze", response_model=schemas.RentAnalysis)
def analyze_rent(
    rent: int = Query(..., ge=0),
    area: Optional[str] = None,
    property_type: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_db),
):
    """Is this rent fair? Compares against approved listings (and falls back
    to the trend table) for the given area / type."""
    q = db.query(models.Property.rent).filter(models.Property.status == "approved")
    if area:
        q = q.filter(models.Property.area.ilike(f"%{area}%"))
    if property_type:
        q = q.filter(models.Property.type == property_type)
    rents = sorted(r[0] for r in q.all())

    if len(rents) < 2:  # fallback to trend table
        tq = db.query(models.RentTrend.avg_rent)
        if area:
            tq = tq.filter(models.RentTrend.area.ilike(f"%{area}%"))
        if property_type:
            tq = tq.filter(models.RentTrend.property_type == property_type)
        rents = sorted(r[0] for r in tq.all())

    if not rents:
        return schemas.RentAnalysis(
            rent=rent, area=area, property_type=property_type, verdict="unknown",
            suggestion="Not enough data for this area yet — try a broader search.",
        )

    avg = round(sum(rents) / len(rents))
    diff_pct = round((rent - avg) / avg * 100, 1) if avg else 0
    percentile = int(round(sum(1 for r in rents if r <= rent) / len(rents) * 100))
    if diff_pct <= -15:
        verdict, suggestion = "great deal", "Well below market average — verify the listing is genuine and grab it."
    elif diff_pct <= 5:
        verdict, suggestion = "fair", "Priced around market average — reasonable to go ahead."
    elif diff_pct <= 20:
        verdict, suggestion = "slightly high", f"About {diff_pct}% above average — try negotiating ₹{int((rent-avg)/2)} off."
    else:
        verdict, suggestion = "overpriced", f"{diff_pct}% above market — compare alternatives in the same area first."
    return schemas.RentAnalysis(
        rent=rent, area=area, property_type=property_type, market_avg=avg,
        verdict=verdict, diff_pct=diff_pct, percentile=percentile, suggestion=suggestion,
    )
