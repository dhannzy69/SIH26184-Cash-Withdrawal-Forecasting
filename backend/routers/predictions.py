from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Case, Location, Transaction, Account
from backend.schemas import PredictionResponse, LocationResponse
from ml.predict import predict_locations
from ml.explain import explain_candidate_prediction

router = APIRouter(prefix="/api/predictions", tags=["ML Predictions & Intelligence"])


def _get_case_data_from_db(case_id: str, db: Session):
    """Fetches dynamic transactions and accounts from SQLite DB to ensure live ML re-scoring."""
    tx_records = db.query(Transaction).filter(Transaction.case_id == case_id).all()
    if tx_records:
        df_tx = pd.DataFrame([{
            "transaction_id": t.transaction_id,
            "case_id": t.case_id,
            "sender_account": t.sender_account,
            "receiver_account": t.receiver_account,
            "amount": float(t.amount),
            "timestamp": pd.to_datetime(t.timestamp),
            "transaction_type": t.transaction_type
        } for t in tx_records])
    else:
        df_tx = None

    acc_records = db.query(Account).filter(Account.case_id == case_id).all()
    custom_acc_lookup = {
        a.account_id: {
            "account_type": a.account_type,
            "region": a.region,
            "account_age_days": a.account_age_days
        }
        for a in acc_records
    } if acc_records else None

    return df_tx, custom_acc_lookup


@router.get("/locations", response_model=List[LocationResponse])
def get_candidate_locations(db: Session = Depends(get_db)):
    """Retrieves all 12 candidate ATM clusters with geographic coordinates."""
    locations = db.query(Location).all()
    return locations


@router.get("/{case_id}", response_model=PredictionResponse)
def get_case_prediction(
    case_id: str,
    t_cutoff: Optional[str] = Query(None, description="Optional prediction cut-off timestamp (YYYY-MM-DD HH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Executes the ML inference engine for an active cybercrime complaint using live database state:
    1. Fetches current transaction chain and registered mule accounts from SQLite.
    2. Reconstructs the multi-hop mule graph dynamically.
    3. Extracts 48 non-leaking topological, velocity, geospatial, and temporal features.
    4. Returns calibrated Top-1, Top-3, and Top-5 candidate ATM clusters with risk tiers.
    5. Calculates the empirical cash-out time window.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' was not found.")

    try:
        df_tx, custom_acc_lookup = _get_case_data_from_db(case_id, db)
        forecast = predict_locations(
            case_id,
            prediction_time=t_cutoff,
            custom_transactions_df=df_tx,
            custom_accounts_lookup=custom_acc_lookup
        )
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


@router.get("/{case_id}/explain")
def get_case_explanation(
    case_id: str,
    rank: int = Query(default=1, ge=1, le=12, description="Candidate rank to explain (1 for highest risk candidate)"),
    db: Session = Depends(get_db)
):
    """
    Computes SHAP (SHapley Additive exPlanations) feature attributions
    explaining the primary factors driving the model's risk score based on live database state.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' was not found.")

    try:
        df_tx, custom_acc_lookup = _get_case_data_from_db(case_id, db)
        explanation = explain_candidate_prediction(
            case_id,
            target_rank=rank,
            custom_transactions_df=df_tx,
            custom_accounts_lookup=custom_acc_lookup
        )
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explainability error: {str(e)}")
