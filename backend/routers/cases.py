from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Case, Account, User
from backend.schemas import CaseResponse, CaseDetailResponse, CaseCreate, CaseUpdate
from backend.auth import get_current_user

router = APIRouter(prefix="/api/cases", tags=["Case Management"])


@router.get("", response_model=List[CaseResponse])
def list_cases(
    status: Optional[str] = Query(None, description="Filter by case status (ACTIVE, CLOSED, etc.)"),
    fraud_type: Optional[str] = Query(None, description="Filter by fraud type"),
    victim_region: Optional[str] = Query(None, description="Filter by victim city/region"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=600),
    db: Session = Depends(get_db)
):
    """Lists cybercrime complaint cases with optional multi-parameter filtering."""
    query = db.query(Case)

    if status:
        query = query.filter(Case.status == status)
    if fraud_type:
        query = query.filter(Case.fraud_type == fraud_type)
    if victim_region:
        query = query.filter(Case.victim_region == victim_region)

    cases = query.order_by(Case.complaint_time.desc()).offset(skip).limit(limit).all()
    return cases


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new cybercrime complaint case."""
    existing = db.query(Case).filter(Case.case_id == payload.case_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Case ID '{payload.case_id}' already exists."
        )

    new_case = Case(
        case_id=payload.case_id,
        fraud_type=payload.fraud_type,
        complaint_time=payload.complaint_time,
        amount=payload.amount,
        victim_region=payload.victim_region,
        status=payload.status,
        assigned_officer_id=current_user.id
    )
    db.add(new_case)
    db.commit()

    # Automatically register victim account if provided
    if payload.victim_account_id:
        v_acc = Account(
            account_id=payload.victim_account_id,
            case_id=payload.case_id,
            account_type="Victim",
            region=payload.victim_region,
            account_age_days=365
        )
        db.add(v_acc)
        db.commit()

    db.refresh(new_case)
    return new_case


@router.get("/{case_id}", response_model=CaseDetailResponse)
def get_case_dossier(case_id: str, db: Session = Depends(get_db)):
    """Retrieves full case dossier including mule accounts and transaction chain."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case ID '{case_id}' was not found."
        )
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
def update_case_status(
    case_id: str,
    payload: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Updates case status or reassigns investigating officer."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case '{case_id}' not found.")

    if payload.status:
        case.status = payload.status
    if payload.assigned_officer_id is not None:
        case.assigned_officer_id = payload.assigned_officer_id

    db.commit()
    db.refresh(case)
    return case
