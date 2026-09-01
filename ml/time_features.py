"""
ml/time_features.py
Temporal feature extraction and empirical cash-out time window estimation.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


def extract_temporal_features(
    complaint_time: pd.Timestamp,
    case_tx: pd.DataFrame,
    t_prediction: Optional[pd.Timestamp] = None
) -> Dict[str, float]:
    """
    Extracts time-of-day, day-of-week, and latency features strictly prior to t_prediction.
    """
    if case_tx.empty:
        ref_time = complaint_time
        time_since_last_tx = 0.0
        avg_delay = 0.0
    else:
        sorted_tx = case_tx.sort_values("timestamp")
        ref_time = sorted_tx.iloc[-1]["timestamp"]
        if t_prediction is not None:
            time_since_last_tx = max(0.0, (t_prediction - ref_time).total_seconds() / 60.0)
        else:
            time_since_last_tx = 0.0

        if len(sorted_tx) > 1:
            avg_delay = float(sorted_tx["timestamp"].diff().dropna().dt.total_seconds().mean() / 60.0)
        else:
            avg_delay = 0.0

    eval_time = t_prediction if t_prediction is not None else ref_time
    time_since_complaint = max(0.0, (eval_time - complaint_time).total_seconds() / 60.0)

    # Cyclical hour encoding
    hour = float(ref_time.hour)
    minute_of_day = float(ref_time.hour * 60 + ref_time.minute)
    day_of_week = float(ref_time.weekday())
    is_night = 1.0 if (hour < 6 or hour >= 22) else 0.0

    return {
        "complaint_hour": float(complaint_time.hour),
        "complaint_day_of_week": float(complaint_time.weekday()),
        "tx_hour": hour,
        "tx_minute_of_day": minute_of_day,
        "tx_day_of_week": day_of_week,
        "is_night_transaction": is_night,
        "time_since_complaint_min": time_since_complaint,
        "time_since_last_tx_min": time_since_last_tx,
        "avg_transfer_interval_min": avg_delay,
    }


def estimate_cashout_time_window(
    case_tx: pd.DataFrame,
    median_latency_min: float = 67.5,
    iqr_spread_min: float = 35.0
) -> str:
    """
    Estimates the likely cash-out time window (e.g., '14:30 – 16:00')
    based on the latest observed transaction timestamp and empirical latency.
    Returns 'Insufficient temporal evidence' if evidence is lacking.
    """
    if case_tx.empty:
        return "Insufficient temporal evidence"

    sorted_tx = case_tx.sort_values("timestamp")
    last_tx_time = sorted_tx.iloc[-1]["timestamp"]

    if pd.isna(last_tx_time):
        return "Insufficient temporal evidence"

    # Predicted lower and upper bounds of cash withdrawal
    est_start = last_tx_time + pd.Timedelta(minutes=max(15.0, median_latency_min - iqr_spread_min))
    est_end = last_tx_time + pd.Timedelta(minutes=median_latency_min + iqr_spread_min)

    return f"{est_start.strftime('%H:%M')} - {est_end.strftime('%H:%M')}"



if __name__ == "__main__":
    from ml.data_loader import load_raw_data
    cases, _, txs, _, _ = load_raw_data()
    c1 = cases.iloc[0]
    c1_tx = txs[txs["case_id"] == c1["case_id"]]
    time_feats = extract_temporal_features(c1["complaint_time"], c1_tx)
    window = estimate_cashout_time_window(c1_tx)
    print("[STEP 3 - TIME SUCCESS] Time features:", time_feats)
    print("Estimated cash-out time window:", window)
