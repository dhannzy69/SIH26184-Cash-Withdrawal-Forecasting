from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Alert, Case, Location
from backend.schemas import AlertResponse, AlertCreate, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["Actionable Surveillance Alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    status: Optional[str] = Query(None, description="Filter by status (DISPATCHED, ACKNOWLEDGED, INTERCEPTED)"),
    risk_tier: Optional[str] = Query(None, description="Filter by risk tier (HIGH, MEDIUM, LOW)"),
    city: Optional[str] = Query(None, description="Filter by city"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieves surveillance alerts with optional multi-parameter filtering."""
    query = db.query(Alert)

    if status:
        query = query.filter(Alert.status == status)
    if risk_tier:
        query = query.filter(Alert.risk_tier == risk_tier)
    if city:
        query = query.filter(Alert.city == city)

    alerts = query.order_by(Alert.dispatched_at.desc()).offset(skip).limit(limit).all()
    return alerts


@router.post("/dispatch", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def dispatch_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Manually dispatches a targeted surveillance alert to field units."""
    case = db.query(Case).filter(Case.case_id == payload.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{payload.case_id}' not found.")

    new_alert = Alert(
        case_id=payload.case_id,
        location_id=payload.location_id,
        city=payload.city,
        atm_cluster_name=payload.atm_cluster_name,
        risk_score=payload.risk_score,
        risk_tier=payload.risk_tier,
        estimated_time_window=payload.estimated_time_window,
        status="DISPATCHED",
        notes=payload.notes
    )
    db.add(new_alert)
    case.status = "ALERTED"
    db.commit()
    db.refresh(new_alert)
    return new_alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
def update_alert_status(alert_id: int, payload: AlertUpdate, db: Session = Depends(get_db)):
    """Field unit acknowledges alert or logs an interception outcome."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} was not found.")

    alert.status = payload.status
    if payload.notes:
        timestamp_note = f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {payload.notes}"
        alert.notes = (alert.notes or "") + timestamp_note

    db.commit()
    db.refresh(alert)
    return alert


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert_detail(alert_id: int, db: Session = Depends(get_db)):
    """Retrieves detailed information for a specific alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert #{alert_id} was not found.")
    return alert
