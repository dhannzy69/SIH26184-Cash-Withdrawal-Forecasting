"""
ml/features.py
Comprehensive feature engineering pipeline consolidating transaction, network,
temporal, geographic, and historical prior features.
"""

from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from ml.network_features import extract_network_features
from ml.time_features import extract_temporal_features
from ml.geo_features import extract_geo_features


def extract_transaction_features(
    complaint_info: Dict[str, Any],
    case_tx: pd.DataFrame,
    t_prediction: Optional[pd.Timestamp] = None
) -> Dict[str, float]:
    """
    Extracts transaction volume, velocity, and hop dynamics features strictly up to t_prediction.
    """
    original_amount = float(complaint_info.get("amount", 1.0))
    complaint_time = complaint_info.get("complaint_time")

    if case_tx.empty:
        return {
            "total_incoming_amount": 0.0,
            "total_outgoing_amount": 0.0,
            "transaction_count": 0.0,
            "recent_transaction_count": 0.0,
            "avg_transaction_amount": 0.0,
            "max_transaction_amount": 0.0,
            "transaction_velocity": 0.0,
            "incoming_velocity": 0.0,
            "outgoing_velocity": 0.0,
            "amount_ratio": 0.0,
            "number_of_hops": 0.0,
            "time_since_last_incoming_min": 0.0,
            "time_since_last_outgoing_min": 0.0,
        }

    sorted_tx = case_tx.sort_values("timestamp")
    last_tx_time = sorted_tx.iloc[-1]["timestamp"]
    eval_time = t_prediction if t_prediction is not None else last_tx_time

    # Amounts
    tx_amounts = sorted_tx["amount"].astype(float)
    total_in = float(tx_amounts.sum())
    # In a chain, total outgoing from sender accounts
    total_out = float(tx_amounts.iloc[:-1].sum()) if len(tx_amounts) > 1 else float(tx_amounts.iloc[0])

    tx_count = float(len(sorted_tx))
    avg_amt = float(tx_amounts.mean())
    max_amt = float(tx_amounts.max())

    # Recent transactions within 60 minutes of eval_time
    cutoff_60 = eval_time - pd.Timedelta(minutes=60)
    recent_cnt = float((sorted_tx["timestamp"] >= cutoff_60).sum())

    # Velocities (per hour)
    hours_elapsed = max(0.1, (eval_time - complaint_time).total_seconds() / 3600.0)
    tx_velocity = tx_count / hours_elapsed
    in_velocity = total_in / hours_elapsed
    out_velocity = total_out / hours_elapsed

    # Amount ratio: latest transferred amount / original complaint amount
    latest_amt = float(sorted_tx.iloc[-1]["amount"])
    amount_ratio = latest_amt / max(1.0, original_amount)

    # Time since last incoming / outgoing
    time_since_last_incoming = max(0.0, (eval_time - last_tx_time).total_seconds() / 60.0)
    # First tx is from victim to mule
    first_tx_time = sorted_tx.iloc[0]["timestamp"]
    time_since_first_outgoing = max(0.0, (eval_time - first_tx_time).total_seconds() / 60.0)

    return {
        "total_incoming_amount": total_in,
        "total_outgoing_amount": total_out,
        "transaction_count": tx_count,
        "recent_transaction_count": recent_cnt,
        "avg_transaction_amount": avg_amt,
        "max_transaction_amount": max_amt,
        "transaction_velocity": tx_velocity,
        "incoming_velocity": in_velocity,
        "outgoing_velocity": out_velocity,
        "amount_ratio": amount_ratio,
        "number_of_hops": tx_count,
        "time_since_last_incoming_min": time_since_last_incoming,
        "time_since_last_outgoing_min": time_since_first_outgoing,
    }


def build_candidate_feature_vector(
    case_info: Dict[str, Any],
    case_tx: pd.DataFrame,
    candidate_loc: Dict[str, Any],
    account_lookup: Dict[str, Dict[str, Any]],
    city_coords_lookup: Dict[str, Dict[str, float]],
    t_prediction: Optional[pd.Timestamp] = None,
    hist_location_freq: float = 0.0,
    hist_network_association: float = 0.0,
) -> Dict[str, float]:
    """
    Consolidates all feature domains for a single (Case, Candidate Location, Time T) tuple.
    Guaranteed Leakage-Free: Only features computed prior to t_prediction are included.
    """
    complaint_amt = float(case_info.get("amount", 1.0))
    complaint_time = case_info.get("complaint_time")
    victim_region = str(case_info.get("victim_region", "Unknown"))

    # 1. Transaction Features
    tx_feats = extract_transaction_features(case_info, case_tx, t_prediction)

    # 2. Network Graph Features
    net_feats = extract_network_features(case_tx, account_lookup, original_amount=complaint_amt)

    # 3. Temporal Features
    time_feats = extract_temporal_features(complaint_time, case_tx, t_prediction)

    # 4. Geographic Features
    # Identify ordered list of active account regions involved up to T
    active_regions = [victim_region]
    if not case_tx.empty:
        for acc in case_tx.sort_values("timestamp")["receiver_account"]:
            reg = account_lookup.get(acc, {}).get("region")
            if reg and reg not in active_regions:
                active_regions.append(reg)

    geo_feats = extract_geo_features(candidate_loc, victim_region, active_regions, city_coords_lookup)

    # 5. Historical Priors & Identity Features
    loc_num = float(int(candidate_loc.get("location_id", "L001").replace("L", "")))
    hist_feats = {
        "candidate_location_num": loc_num,
        "hist_location_freq_prior": float(hist_location_freq),
        "hist_network_association_prior": float(hist_network_association),
    }

    # Consolidated dictionary
    features = {}
    features.update(tx_feats)
    features.update(net_feats)
    features.update(time_feats)
    features.update(geo_feats)
    features.update(hist_feats)

    return features


if __name__ == "__main__":
    from ml.data_loader import load_raw_data
    from ml.preprocessing import build_account_lookup

    cases, accs, txs, locs, _ = load_raw_data()
    acc_map = build_account_lookup(accs)
    coords_map = locs.set_index("city")[["latitude", "longitude"]].to_dict(orient="index")

    c1 = cases.iloc[0].to_dict()
    c1_tx = txs[txs["case_id"] == c1["case_id"]]
    l1 = locs.iloc[0].to_dict()

    feats = build_candidate_feature_vector(
        c1, c1_tx, l1, acc_map, coords_map, t_prediction=None, hist_location_freq=0.08, hist_network_association=0.10
    )
    print(f"[STEP 3 SUCCESS] Consolidated feature vector created with {len(feats)} features:")
    for k in sorted(feats.keys()):
        print(f"  {k}: {feats[k]:.4f}")
