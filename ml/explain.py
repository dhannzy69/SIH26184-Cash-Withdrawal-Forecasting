"""
ml/explain.py
Explainability module using SHAP (SHapley Additive exPlanations) with feature-importance fallback.
Translates mathematical feature attributions into actionable investigative insights.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
import shap

from ml.config import MODELS_DIR
from ml.predict import get_inference_resources, predict_locations
from ml.preprocessing import filter_transactions_up_to_t
from ml.features import build_candidate_feature_vector


FEATURE_LABELS = {
    "dist_candidate_to_current_mule_km": "Short geographic distance to active mule",
    "min_dist_candidate_to_network_km": "Proximity to cybercrime mule network",
    "mean_dist_candidate_to_network_km": "Central geographic position relative to all mules",
    "dist_candidate_to_victim_km": "Distance from complainant/victim origin",
    "is_same_city_as_current_mule": "Direct city concordance with terminal mule account",
    "is_same_city_as_victim": "Victim city proximity",
    "current_hop_number": "Mule chain hop depth",
    "max_hop_depth": "Extended multi-hop graph structure",
    "num_mule_to_mule_transfers": "High volume of intermediate mule transfers",
    "transaction_velocity": "Rapid transaction flow velocity",
    "incoming_velocity": "High rate of incoming capital movement",
    "outgoing_velocity": "High rate of downstream capital distribution",
    "amount_ratio": "Proportion of funds retained at terminal node",
    "avg_transfer_delay_between_hops_min": "Hop-to-hop transfer pacing",
    "pagerank_terminal": "Graph centrality of active recipient account",
    "tx_hour": "Time-of-day transaction pattern",
    "is_night_transaction": "Off-hours nocturnal transaction activity",
    "candidate_location_num": "Historical cluster baseline risk",
    "hist_location_freq_prior": "Historical cash-out frequency at this ATM cluster",
    "hist_network_association_prior": "Past association between this mule region and ATM cluster",
}


def explain_candidate_prediction(
    case_id: str,
    target_rank: int = 1,
    top_n_factors: int = 4
) -> Dict[str, Any]:
    """
    Computes SHAP values or feature importance attributions for a given case and candidate rank.
    """
    model, feature_cols, data = get_inference_resources()
    pred_res = predict_locations(case_id)

    if not pred_res["all_ranked_locations"]:
        raise ValueError("No predictions available to explain.")

    # Find the target candidate (rank 1 by default)
    selected_cand = pred_res["all_ranked_locations"][target_rank - 1]
    loc_id = selected_cand["location_id"]

    # Reconstruct feature vector for this candidate
    case_row = data["cases"][data["cases"]["case_id"] == case_id].iloc[0].to_dict()
    case_tx = filter_transactions_up_to_t(data["transactions"], case_id, pd.to_datetime(pred_res["prediction_time"]))
    cand_row = data["locations"][data["locations"]["location_id"] == loc_id].iloc[0].to_dict()

    feat_vec = build_candidate_feature_vector(
        case_info=case_row,
        case_tx=case_tx,
        candidate_loc=cand_row,
        account_lookup=data["account_lookup"],
        city_coords_lookup=data["city_coords"],
        t_prediction=pd.to_datetime(pred_res["prediction_time"])
    )

    X_sample = pd.DataFrame([[feat_vec.get(col, 0.0) for col in feature_cols]], columns=feature_cols)

    explanation_method = "SHAP TreeExplainer"
    contributing_factors = []

    try:
        # Use TreeExplainer for tree-based models
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)

        # Handle binary classification shap output format
        if isinstance(shap_values, list) and len(shap_values) == 2:
            # Positive class (1)
            raw_vals = shap_values[1][0]
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 3:
            raw_vals = shap_values[0, :, 1]
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) == 2:
            raw_vals = shap_values[0]
        else:
            raw_vals = np.array(shap_values).flatten()

        # Sort by impact
        impact_order = np.argsort(-np.abs(raw_vals))

        for idx in impact_order[:top_n_factors]:
            col_name = feature_cols[idx]
            val = float(X_sample.iloc[0, idx])
            shap_val = float(raw_vals[idx])
            desc = FEATURE_LABELS.get(col_name, col_name.replace("_", " ").title())
            contributing_factors.append({
                "feature": col_name,
                "feature_description": desc,
                "feature_value": round(val, 2),
                "attribution_score": round(shap_val, 4),
                "direction": "INCREASES_RISK" if shap_val >= 0 else "DECREASES_RISK"
            })

    except Exception as e:
        # Fallback to feature importance
        explanation_method = f"Model Feature Importance Fallback (Prototype Explanation: {str(e)})"
        importances = getattr(model, "feature_importances_", None)
        if importances is not None:
            top_indices = np.argsort(-importances)[:top_n_factors]
            for idx in top_indices:
                col_name = feature_cols[idx]
                val = float(X_sample.iloc[0, idx])
                desc = FEATURE_LABELS.get(col_name, col_name.replace("_", " ").title())
                contributing_factors.append({
                    "feature": col_name,
                    "feature_description": desc,
                    "feature_value": round(val, 2),
                    "attribution_score": round(float(importances[idx]), 4),
                    "direction": "HIGH_IMPORTANCE"
                })

    return {
        "case_id": case_id,
        "rank": target_rank,
        "location_id": loc_id,
        "city": selected_cand["city"],
        "atm_cluster_name": selected_cand["atm_cluster_name"],
        "model_score": selected_cand["score"],
        "risk_tier": selected_cand["risk"],
        "explanation_method": explanation_method,
        "contributing_factors": contributing_factors,
        "clarification_note": (
            "SHAP and feature attribution metrics explain statistical model contributions. "
            "They illustrate which variables influenced the ranking, but do not prove physical causality."
        )
    }


if __name__ == "__main__":
    explanation = explain_candidate_prediction("C0001", target_rank=1)
    print(f"[STEP 11 SUCCESS] SHAP Explanation for Case {explanation['case_id']} (Rank 1):")
    print(f"Location: {explanation['city']} ({explanation['location_id']}) | Score: {explanation['model_score']} | Risk: {explanation['risk_tier']}")
    print(f"Method: {explanation['explanation_method']}")
    print("Contributing Factors:")
    for f in explanation["contributing_factors"]:
        print(f"  * {f['feature_description']} (Val: {f['feature_value']}, Impact: {f['attribution_score']} -> {f['direction']})")
