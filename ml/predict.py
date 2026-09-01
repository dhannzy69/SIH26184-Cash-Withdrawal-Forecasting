"""
ml/predict.py
Inference Engine for SIH26184 Cash-Withdrawal Location Forecasting.
Evaluates active cases at cut-off time T and returns probabilistic rankings and time windows.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
import joblib

from ml.config import MODELS_DIR, RISK_THRESHOLDS
from ml.data_loader import load_raw_data
from ml.preprocessing import (
    filter_transactions_up_to_t, build_account_lookup, build_location_lookup
)
from ml.features import build_candidate_feature_vector
from ml.time_features import estimate_cashout_time_window


_MODEL = None
_FEATURE_COLS = None
_DATA_CACHE = None


def get_inference_resources():
    """Caches loaded model and lookup data in memory for sub-second inference."""
    global _MODEL, _FEATURE_COLS, _DATA_CACHE
    if _MODEL is None:
        model_path = MODELS_DIR / "best_model.joblib"
        cols_path = MODELS_DIR / "feature_columns.json"

        if not model_path.exists() or not cols_path.exists():
            raise FileNotFoundError("Model artifacts not found. Please run ml/train.py first.")

        _MODEL = joblib.load(model_path)
        with open(cols_path, "r") as f:
            _FEATURE_COLS = json.load(f)

        cases_df, accounts_df, transactions_df, locations_df, _ = load_raw_data()
        _DATA_CACHE = {
            "cases": cases_df,
            "accounts": accounts_df,
            "transactions": transactions_df,
            "locations": locations_df,
            "account_lookup": build_account_lookup(accounts_df),
            "city_coords": locations_df.set_index("city")[["latitude", "longitude"]].to_dict(orient="index"),
            "location_lookup": build_location_lookup(locations_df)
        }
    return _MODEL, _FEATURE_COLS, _DATA_CACHE


def assign_risk_level(score: float, rank: int) -> str:
    """Categorizes candidate into risk tiers based on model score and rank."""
    if rank == 1 or score >= RISK_THRESHOLDS["HIGH"]:
        return "HIGH"
    elif rank <= 3 or score >= RISK_THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "LOW"


def predict_locations(
    case_id: str,
    prediction_time: Optional[Union[str, pd.Timestamp]] = None,
    custom_transactions_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Given an active case_id and prediction cut-off time T:
    1. Loads case information and available transactions up to T.
    2. Builds the active mule network and extracts 48 features for each candidate location.
    3. Scores candidates using the selected ML model.
    4. Ranks locations descending by predicted model score.
    5. Returns Top-1, Top-3, Top-5 candidates, risk tiers, and predicted time window.
    """
    model, feature_cols, data = get_inference_resources()

    cases_df = data["cases"]
    transactions_df = custom_transactions_df if custom_transactions_df is not None else data["transactions"]
    locations_df = data["locations"]
    account_lookup = data["account_lookup"]
    city_coords = data["city_coords"]

    # 1. Fetch case record
    case_matches = cases_df[cases_df["case_id"] == case_id]
    if case_matches.empty:
        raise ValueError(f"Case ID '{case_id}' not found in cases dataset.")

    case_row = case_matches.iloc[0].to_dict()

    # 2. Filter transactions strictly up to prediction_time T
    if prediction_time is not None:
        t_cutoff = pd.to_datetime(prediction_time)
    else:
        # Default to latest known transaction for this case
        case_tx_all = transactions_df[transactions_df["case_id"] == case_id]
        t_cutoff = case_tx_all["timestamp"].max() if not case_tx_all.empty else case_row["complaint_time"]

    filtered_tx = filter_transactions_up_to_t(transactions_df, case_id, t_cutoff)

    # 3. Construct case-candidate evaluation pairs for all 12 locations
    candidates = [row.to_dict() for _, row in locations_df.iterrows()]
    feature_rows = []

    # Calculate rolling priors up to T
    # Terminal mule region
    if not filtered_tx.empty:
        terminal_acc = str(filtered_tx.iloc[-1]["receiver_account"])
        terminal_reg = account_lookup.get(terminal_acc, {}).get("region", str(case_row["victim_region"]))
    else:
        terminal_reg = str(case_row["victim_region"])

    for cand in candidates:
        feat_vec = build_candidate_feature_vector(
            case_info=case_row,
            case_tx=filtered_tx,
            candidate_loc=cand,
            account_lookup=account_lookup,
            city_coords_lookup=city_coords,
            t_prediction=t_cutoff,
            hist_location_freq=1.0 / 12.0,
            hist_network_association=1.0 / 12.0
        )
        # Ensure exact column order
        ordered_vec = [feat_vec.get(col, 0.0) for col in feature_cols]
        feature_rows.append(ordered_vec)

    X_infer = pd.DataFrame(feature_rows, columns=feature_cols)

    # 4. Predict likelihood / model score
    probs = model.predict_proba(X_infer)[:, 1]

    # Normalize scores across the 12 mutually exclusive candidates so sum approximates 1.0 (calibrated distribution)
    sum_probs = np.sum(probs)
    if sum_probs > 0:
        normalized_scores = probs / sum_probs
    else:
        normalized_scores = probs

    # 5. Build and sort rankings
    ranked_list = []
    for i, cand in enumerate(candidates):
        ranked_list.append({
            "location_id": str(cand["location_id"]),
            "city": str(cand["city"]),
            "district": str(cand["district"]),
            "state": str(cand["state"]),
            "latitude": float(cand["latitude"]),
            "longitude": float(cand["longitude"]),
            "atm_cluster_name": str(cand["atm_cluster_name"]),
            "score": round(float(normalized_scores[i]), 4),
            "raw_model_prob": round(float(probs[i]), 4),
        })

    # Sort descending by score
    ranked_list.sort(key=lambda x: x["score"], reverse=True)

    # Assign ranks and risk tiers
    for rank_idx, item in enumerate(ranked_list, start=1):
        item["rank"] = rank_idx
        item["risk"] = assign_risk_level(item["score"], rank_idx)

    # 6. Estimate predicted cash-out time window
    time_window = estimate_cashout_time_window(filtered_tx)

    result = {
        "case_id": case_id,
        "prediction_time": str(t_cutoff),
        "estimated_cashout_time_window": time_window,
        "observed_transactions_count": len(filtered_tx),
        "top_1": ranked_list[:1],
        "top_3": ranked_list[:3],
        "top_5": ranked_list[:5],
        "all_ranked_locations": ranked_list,
        "disclaimer": (
            "This prototype uses synthetic data. The resulting model performance demonstrates "
            "the technical workflow and controlled experimental behaviour only; it does not "
            "establish real-world predictive accuracy."
        )
    }

    return result


if __name__ == "__main__":
    test_case = "C0001"
    output = predict_locations(test_case)
    print(f"[STEP 10 SUCCESS] Prediction output for case {test_case}:")
    print(f"Prediction Time: {output['prediction_time']}")
    print(f"Estimated Time Window: {output['estimated_cashout_time_window']}")
    print("\nTop-3 Probable Locations:")
    for pred in output["top_3"]:
        print(f"  Rank {pred['rank']}: {pred['location_id']} ({pred['city']} - {pred['atm_cluster_name']}) | Score: {pred['score']} | Risk: {pred['risk']}")
