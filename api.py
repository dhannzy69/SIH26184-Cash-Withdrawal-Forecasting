"""
api.py
Headless FastAPI REST API for SIH26184 Cash-Withdrawal Location Forecasting.
Exposes clean JSON endpoints with CORS enabled for seamless future frontend integration.
Interactive API Documentation available at /docs (Swagger) and /redoc (ReDoc).
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ml.config import RESULTS_DIR, HORIZON_MINUTES
from ml.predict import predict_locations, get_inference_resources
from ml.explain import explain_candidate_prediction
from ml.simulate import simulate_transaction

app = FastAPI(
    title="SIH26184: Cybercrime Cash-Withdrawal Location Forecasting API",
    description="Headless ML Backend for Active Cybercrime Case Tracking & ATM Cluster Risk Forecasting.",
    version="1.0.0"
)

# Enable CORS for future frontend integration (React, Vue, Angular, Spring Boot, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-warm model and data cache
_, _, data_cache = get_inference_resources()


class SimulationPayload(BaseModel):
    case_id: str = Field(..., description="Active complaint case identifier (e.g. 'C0001')")
    sender_account: str = Field(..., description="Originating account ID")
    receiver_account: str = Field(..., description="Beneficiary account ID")
    receiver_region: str = Field(..., description="City/region of beneficiary account")
    amount: float = Field(..., description="Transaction amount in INR")
    timestamp: str = Field(..., description="Transaction timestamp (YYYY-MM-DD HH:MM:SS)")
    transaction_type: str = Field(default="Transfer", description="Type of transaction")


@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint confirming model status and horizon configuration."""
    return {
        "status": "online",
        "service": "SIH26184 Headless Location Forecasting Engine",
        "model": "Random Forest Classifier",
        "prediction_horizon_minutes": HORIZON_MINUTES
    }


@app.get("/api/cases", tags=["Cases"])
def get_cases(limit: int = Query(default=50, ge=1, le=600)):
    """Retrieves list of cybercrime complaint cases."""
    cases_df = data_cache["cases"]
    cols = ["case_id", "fraud_type", "complaint_time", "amount", "victim_region", "status"]
    return cases_df[cols].head(limit).to_dict(orient="records")


@app.get("/api/cases/{case_id}", tags=["Cases"])
def get_case_by_id(case_id: str):
    """Retrieves metadata and full transaction chain for a specific case."""
    cases_df = data_cache["cases"]
    tx_df = data_cache["transactions"]

    match = cases_df[cases_df["case_id"] == case_id]
    if match.empty:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found.")

    case_info = match.iloc[0].to_dict()
    case_tx = tx_df[tx_df["case_id"] == case_id].sort_values("timestamp").to_dict(orient="records")

    return {
        "case_details": case_info,
        "transaction_history": case_tx
    }


@app.get("/api/locations", tags=["Locations"])
def get_candidate_locations():
    """Returns all 12 candidate ATM clusters with geographic coordinates."""
    locations_df = data_cache["locations"]
    return locations_df.to_dict(orient="records")


@app.get("/api/predict/{case_id}", tags=["Inference"])
def forecast_locations(case_id: str, t_cutoff: Optional[str] = Query(None, description="Prediction cut-off timestamp")):
    """
    Evaluates active case up to time T and returns probabilistic Top-1, Top-3, Top-5
    ATM clusters, risk levels, and predicted cash-out time window.
    """
    try:
        return predict_locations(case_id, prediction_time=t_cutoff)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/explain/{case_id}", tags=["Explainability"])
def explain_prediction(case_id: str, rank: int = Query(default=1, ge=1, le=12)):
    """
    Computes SHAP feature attributions explaining the primary factors
    driving the model's risk score for the specified candidate rank.
    """
    try:
        return explain_candidate_prediction(case_id, target_rank=rank)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/simulate", tags=["Simulation"])
def simulate_new_evidence(payload: SimulationPayload):
    """
    Simulates the arrival of a new downstream mule transfer and returns
    updated rankings and rank shifts in real-time WITHOUT model retraining.
    """
    try:
        return simulate_transaction(payload.case_id, payload.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/metrics", tags=["System"])
def get_benchmark_metrics():
    """Returns chronological test set benchmark metrics for all evaluated models."""
    comp_file = RESULTS_DIR / "model_comparison.csv"
    if comp_file.exists():
        df = pd.read_csv(comp_file)
        return df.to_dict(orient="records")
    return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
