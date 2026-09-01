from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Case, Location
from backend.schemas import PredictionResponse, LocationResponse
from ml.predict import predict_locations
from ml.explain import explain_candidate_prediction

router = APIRouter(prefix="/api/predictions", tags=["ML Predictions & Intelligence"])


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
    Executes the ML inference engine for an active cybercrime complaint:
    1. Reconstructs the multi-hop mule graph.
    2. Extracts 48 non-leaking topological, velocity, geospatial, and temporal features.
    3. Returns calibrated Top-1, Top-3, and Top-5 candidate ATM clusters with risk tiers.
    4. Calculates the empirical cash-out time window.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' was not found.")

    try:
        forecast = predict_locations(case_id, prediction_time=t_cutoff)
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
    explaining the primary factors driving the model's risk score.
    """
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' was not found.")

    try:
        explanation = explain_candidate_prediction(case_id, target_rank=rank)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explainability error: {str(e)}")
