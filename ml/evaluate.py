"""
ml/evaluate.py
Comprehensive evaluation suite for Cash-Withdrawal Location Forecasting.
Computes Precision, Recall, F1, ROC-AUC, Confusion Matrix, and custom Top-1, Top-3, Top-5 Accuracies.
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
)
from ml.config import RESULTS_DIR


def compute_top_k_accuracy(
    meta_df: pd.DataFrame,
    predicted_scores: np.ndarray,
    k_list: List[int] = [1, 3, 5]
) -> Dict[str, float]:
    """
    Computes Top-K ranking accuracy across all unique cases in meta_df.
    For each case, candidate locations are ranked by predicted_scores descending.
    A hit occurs if the ground truth cash-out location is within the Top-K candidates.
    """
    df = meta_df.copy()
    df["score"] = predicted_scores

    hits = {k: 0 for k in k_list}
    unique_cases = df["case_id"].unique()
    total_cases = len(unique_cases)

    if total_cases == 0:
        return {f"top{k}": 0.0 for k in k_list}

    for case_id in unique_cases:
        case_group = df[df["case_id"] == case_id].sort_values("score", ascending=False)

        # Identify actual location
        actual_rows = case_group[case_group["actual_location_id"] == case_group["candidate_location_id"]]
        if actual_rows.empty:
            continue

        actual_loc = actual_rows.iloc[0]["actual_location_id"]
        ranked_locs = case_group["candidate_location_id"].tolist()

        for k in k_list:
            top_k_candidates = ranked_locs[:k]
            if actual_loc in top_k_candidates:
                hits[k] += 1

    return {f"top{k}": round(hits[k] / total_cases, 4) for k in k_list}


def evaluate_model_performance(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_prob: np.ndarray,
    meta_df: pd.DataFrame,
    k_list: List[int] = [1, 3, 5]
) -> Dict[str, Any]:
    """
    Computes both binary classification metrics and ranking Top-K accuracies.
    """
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    try:
        auc = roc_auc_score(y_true, y_prob)
    except ValueError:
        auc = 0.5

    cm = confusion_matrix(y_true, y_pred)
    top_k = compute_top_k_accuracy(meta_df, y_prob, k_list)

    metrics = {
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "confusion_matrix": cm.tolist(),
        **top_k
    }
    return metrics


def save_comparison_csv(
    results: Dict[str, Dict[str, Any]],
    output_path: Path = RESULTS_DIR / "model_comparison.csv"
) -> pd.DataFrame:
    """
    Saves model performance metrics to results/model_comparison.csv
    Format: model,precision,recall,f1,roc_auc,top1,top3,top5
    """
    rows = []
    for model_name, metrics in results.items():
        rows.append({
            "model": model_name,
            "precision": metrics.get("precision", 0.0),
            "recall": metrics.get("recall", 0.0),
            "f1": metrics.get("f1", 0.0),
            "roc_auc": metrics.get("roc_auc", 0.0),
            "top1": metrics.get("top1", 0.0),
            "top3": metrics.get("top3", 0.0),
            "top5": metrics.get("top5", 0.0),
        })

    comp_df = pd.DataFrame(rows)
    comp_df.to_csv(output_path, index=False)
    return comp_df


def generate_evaluation_report(
    results: Dict[str, Dict[str, Any]],
    best_model_name: str,
    output_path: Path = RESULTS_DIR / "evaluation_report.txt"
) -> str:
    """
    Generates human-readable evaluation report explaining model comparison,
    ranking efficacy, and synthetic data limitations.
    """
    lines = [
        "=" * 80,
        "SIH26184: CYBERCRIME CASH-WITHDRAWAL LOCATION FORECASTING - EVALUATION REPORT",
        "=" * 80,
        "",
        "1. SYNTHETIC DATA LIMITATION & ETHICAL DISCLAIMER:",
        "--------------------------------------------------",
        "This prototype uses synthetic data. The resulting model performance demonstrates",
        "the technical workflow and controlled experimental behaviour only; it does not establish",
        "real-world predictive accuracy.",
        "",
        "Operational Considerations for Real-World Deployment:",
        "- False Positives: Candidate rankings represent probabilistic risk; not definitive certainty.",
        "- Concept Drift & Changing Criminal Behaviour: Mule networks actively morph routing topologies.",
        "- Geographic Heterogeneity: Localized ATM cluster densities vary heavily by state.",
        "- Data Governance: Real-world deployment requires authorized law-enforcement (I4C/CFCFRMS) integration.",
        "- Human-in-the-Loop: Model output must serve as actionable leads for authorized human investigators.",
        "",
        "2. BENCHMARK PERFORMANCE COMPARISON (TEST SET EVALUATION):",
        "---------------------------------------------------------"
    ]

    header = f"{'Model':<24} | {'Precision':<9} | {'Recall':<8} | {'F1':<6} | {'ROC-AUC':<7} | {'Top-1':<6} | {'Top-3':<6} | {'Top-5':<6}"
    lines.append(header)
    lines.append("-" * len(header))

    for model_name, m in results.items():
        row = f"{model_name:<24} | {m['precision']:<9.4f} | {m['recall']:<8.4f} | {m['f1']:<6.4f} | {m['roc_auc']:<7.4f} | {m['top1']:<6.4f} | {m['top3']:<6.4f} | {m['top5']:<6.4f}"
        lines.append(row)

    lines.extend([
        "",
        f"3. SELECTED MODEL: {best_model_name}",
        "---------------------------------------------------------",
        f"The {best_model_name} model was selected based on superior validation Top-K ranking accuracy",
        "and balanced discrimination under severe class imbalance (1:11 ratio).",
        "",
        "4. RANKING METRICS INTERPRETATION:",
        "---------------------------------",
        "- Top-1 Accuracy: Proportion of cases where the single highest scored candidate is the actual cash-out location.",
        "- Top-3 Accuracy: Proportion of cases where the actual cash-out location is within the top 3 recommendations.",
        "- Top-5 Accuracy: Proportion of cases where field teams dispatching to the top 5 clusters intercept the withdrawal.",
        "=" * 80
    ])

    report_text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    return report_text
