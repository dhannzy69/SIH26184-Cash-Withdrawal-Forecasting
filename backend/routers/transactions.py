from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Case, Account, Transaction, Alert
from backend.schemas import TransactionCreate, TransactionResponse
from backend.config import ALERT_SCORE_THRESHOLD
from ml.predict import predict_locations

router = APIRouter(prefix="/api/transactions", tags=["Transaction Stream & Ingestion"])


@router.get("/{case_id}", response_model=List[TransactionResponse])
def get_case_transactions(case_id: str, db: Session = Depends(get_db)):
    """Retrieves all transactions recorded for a given case in chronological order."""
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    txs = db.query(Transaction).filter(Transaction.case_id == case_id).order_by(Transaction.timestamp.asc()).all()
    return txs


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def ingest_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    """
    Ingests an active fund transfer in real-time:
    1. Records transaction to the database.
    2. Registers the beneficiary account as a new active mule node if not already present.
    3. Triggers ML location forecasting for the updated case.
    4. Automatically dispatches an actionable surveillance alert if top risk exceeds threshold.
    """
    case = db.query(Case).filter(Case.case_id == payload.case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{payload.case_id}' not found.")

    # 1. Register Receiver Account if new
    receiver_acc = db.query(Account).filter(Account.account_id == payload.receiver_account).first()
    if not receiver_acc:
        receiver_region = payload.receiver_region or case.victim_region
        new_mule = Account(
            account_id=payload.receiver_account,
            case_id=payload.case_id,
            account_type="Mule",
            region=receiver_region,
            account_age_days=180
        )
        db.add(new_mule)
        db.commit()

    # 2. Record Transaction
    tx_count = db.query(Transaction).filter(Transaction.case_id == payload.case_id).count()
    tx_id = f"T_{payload.case_id}_{tx_count + 1:02d}"

    new_tx = Transaction(
        transaction_id=tx_id,
        case_id=payload.case_id,
        sender_account=payload.sender_account,
        receiver_account=payload.receiver_account,
        amount=payload.amount,
        timestamp=payload.timestamp,
        transaction_type=payload.transaction_type
    )
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)

    # 3. Trigger Real-Time ML Re-scoring
    ml_forecast = predict_locations(
        case_id=payload.case_id,
        prediction_time=payload.timestamp
    )

    # 4. Auto-Alert Generation if Top Candidate Exceeds Risk Threshold
    alert_created = None
    if ml_forecast["top_1"]:
        top_cand = ml_forecast["top_1"][0]
        if top_cand["score"] >= ALERT_SCORE_THRESHOLD:
            new_alert = Alert(
                case_id=payload.case_id,
                location_id=top_cand["location_id"],
                city=top_cand["city"],
                atm_cluster_name=top_cand["atm_cluster_name"],
                risk_score=top_cand["score"],
                risk_tier=top_cand["risk"],
                estimated_time_window=ml_forecast["estimated_cashout_time_window"],
                status="DISPATCHED",
                notes=f"Auto-dispatched via transaction stream {tx_id} (Transfer: INR {payload.amount})"
            )
            db.add(new_alert)
            case.status = "ALERTED"
            db.commit()
            db.refresh(new_alert)
            alert_created = {
                "alert_id": new_alert.id,
                "target_city": new_alert.city,
                "cluster": new_alert.atm_cluster_name,
                "risk_score": new_alert.risk_score,
                "window": new_alert.estimated_time_window
            }

    return {
        "message": "Transaction ingested successfully",
        "transaction_id": tx_id,
        "live_prediction_summary": {
            "prediction_time": ml_forecast["prediction_time"],
            "estimated_cashout_time_window": ml_forecast["estimated_cashout_time_window"],
            "top_3_locations": ml_forecast["top_3"]
        },
        "surveillance_alert": alert_created
    }
