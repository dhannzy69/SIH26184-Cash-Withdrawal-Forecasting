"""
ml/dataset_builder.py
Constructs the full ML dataset by pairing cases with all 12 candidate locations at cut-off time T.
Implements chronological train/val/test splitting and leakage-free rolling historical priors.
"""

from typing import Dict, Any, Tuple, List, Optional
import os
from collections import defaultdict
import pandas as pd
import numpy as np

from ml.config import (
    HORIZON_MINUTES, TRAIN_RATIO, VAL_RATIO, TEST_RATIO, DATA_DIR, RESULTS_DIR
)
from ml.data_loader import load_raw_data
from ml.preprocessing import (
    filter_transactions_up_to_t, build_account_lookup, build_location_lookup
)
from ml.features import build_candidate_feature_vector


class RollingHistoricalTracker:
    """
    Maintains strictly chronological historical statistics prior to time T.
    Guarantees that no future events or withdrawals leak into earlier predictions.
    """
    def __init__(self):
        self.location_counts: Dict[str, int] = defaultdict(int)
        self.region_location_matrix: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.total_completed_cases: int = 0

    def get_location_prior(self, location_id: str) -> float:
        if self.total_completed_cases == 0:
            return 1.0 / 12.0
        return self.location_counts[location_id] / self.total_completed_cases

    def get_network_region_prior(self, terminal_region: str, location_id: str) -> float:
        region_dict = self.region_location_matrix[terminal_region]
        region_total = sum(region_dict.values())
        if region_total == 0:
            return self.get_location_prior(location_id)
        return region_dict[location_id] / region_total

    def update(self, terminal_region: str, true_location_id: str):
        self.location_counts[true_location_id] += 1
        self.region_location_matrix[terminal_region][true_location_id] += 1
        self.total_completed_cases += 1


def build_ml_dataset(
    cases_df: Optional[pd.DataFrame] = None,
    accounts_df: Optional[pd.DataFrame] = None,
    transactions_df: Optional[pd.DataFrame] = None,
    locations_df: Optional[pd.DataFrame] = None,
    withdrawals_df: Optional[pd.DataFrame] = None,
    horizon_minutes: int = HORIZON_MINUTES
) -> Tuple[
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame],
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame],
    Tuple[pd.DataFrame, pd.Series, pd.DataFrame]
]:
    """
    Builds the complete case-location-time dataset and performs chronological splitting.
    Returns:
        (X_train, y_train, meta_train), (X_val, y_val, meta_val), (X_test, y_test, meta_test)
    """
    if cases_df is None:
        cases_df, accounts_df, transactions_df, locations_df, withdrawals_df = load_raw_data()

    # Pre-build lookup dictionaries
    account_lookup = build_account_lookup(accounts_df)
    city_coords_lookup = locations_df.set_index("city")[["latitude", "longitude"]].to_dict(orient="index")
    withdrawal_lookup = withdrawals_df.set_index("case_id").to_dict(orient="index")

    # Sort cases strictly chronologically by complaint_time
    sorted_cases = cases_df.sort_values("complaint_time").reset_index(drop=True)
    all_candidate_locs = [row.to_dict() for _, row in locations_df.iterrows()]

    feature_rows = []
    target_rows = []
    metadata_rows = []

    rolling_tracker = RollingHistoricalTracker()

    for _, case in sorted_cases.iterrows():
        case_id = str(case["case_id"])
        case_dict = case.to_dict()

        # Extract all transactions for the case
        c_tx = transactions_df[transactions_df["case_id"] == case_id].sort_values("timestamp")
        if c_tx.empty:
            continue

        # In active case monitoring, prediction cut-off T is set at the latest observed transaction
        t_cutoff = c_tx.iloc[-1]["timestamp"]
        filtered_tx = filter_transactions_up_to_t(c_tx, case_id, t_cutoff)

        # Ground truth withdrawal outcome (used ONLY to construct training target)
        w_info = withdrawal_lookup.get(case_id, {})
        actual_loc = str(w_info.get("location_id", ""))
        actual_time = w_info.get("timestamp")

        # Check if actual cash-out occurs within the prediction horizon [T, T + horizon_minutes]
        within_horizon = False
        if actual_time is not None:
            time_to_cashout_min = (actual_time - t_cutoff).total_seconds() / 60.0
            within_horizon = (0 <= time_to_cashout_min <= horizon_minutes)

        # Terminal mule region for historical tracker
        terminal_acc = str(filtered_tx.iloc[-1]["receiver_account"])
        terminal_reg = account_lookup.get(terminal_acc, {}).get("region", str(case["victim_region"]))

        # Generate 12 case-location evaluation pairs
        for candidate in all_candidate_locs:
            loc_id = str(candidate["location_id"])

            # Target definition
            y_target = 1 if (loc_id == actual_loc and within_horizon) else 0

            # Rolling leakage-free priors prior to T
            loc_prior = rolling_tracker.get_location_prior(loc_id)
            net_prior = rolling_tracker.get_network_region_prior(terminal_reg, loc_id)

            feat_vec = build_candidate_feature_vector(
                case_info=case_dict,
                case_tx=filtered_tx,
                candidate_loc=candidate,
                account_lookup=account_lookup,
                city_coords_lookup=city_coords_lookup,
                t_prediction=t_cutoff,
                hist_location_freq=loc_prior,
                hist_network_association=net_prior
            )

            feature_rows.append(feat_vec)
            target_rows.append(y_target)
            metadata_rows.append({
                "case_id": case_id,
                "complaint_time": case["complaint_time"],
                "prediction_time": t_cutoff,
                "candidate_location_id": loc_id,
                "candidate_city": candidate["city"],
                "actual_location_id": actual_loc,
                "is_actual_location": int(loc_id == actual_loc),
                "within_horizon": int(within_horizon),
            })

        # Update historical tracker AFTER generating samples for this case
        rolling_tracker.update(terminal_reg, actual_loc)

    X_all = pd.DataFrame(feature_rows)
    y_all = pd.Series(target_rows, name="target")
    meta_all = pd.DataFrame(metadata_rows)

    # Chronological Split (by unique cases)
    unique_cases = sorted_cases["case_id"].tolist()
    n_cases = len(unique_cases)
    n_train = int(n_cases * TRAIN_RATIO)
    n_val = int(n_cases * VAL_RATIO)

    train_cases = set(unique_cases[:n_train])
    val_cases = set(unique_cases[n_train:n_train + n_val])
    test_cases = set(unique_cases[n_train + n_val:])

    train_mask = meta_all["case_id"].isin(train_cases)
    val_mask = meta_all["case_id"].isin(val_cases)
    test_mask = meta_all["case_id"].isin(test_cases)

    train_data = (X_all[train_mask].reset_index(drop=True), y_all[train_mask].reset_index(drop=True), meta_all[train_mask].reset_index(drop=True))
    val_data = (X_all[val_mask].reset_index(drop=True), y_all[val_mask].reset_index(drop=True), meta_all[val_mask].reset_index(drop=True))
    test_data = (X_all[test_mask].reset_index(drop=True), y_all[test_mask].reset_index(drop=True), meta_all[test_mask].reset_index(drop=True))

    return train_data, val_data, test_data


if __name__ == "__main__":
    train_data, val_data, test_data = build_ml_dataset()
    X_tr, y_tr, meta_tr = train_data
    X_va, y_va, meta_va = val_data
    X_te, y_te, meta_te = test_data

    print("[STEP 4 SUCCESS] Dataset built successfully!")
    print(f"Train Set: {X_tr.shape[0]} samples across {meta_tr['case_id'].nunique()} cases (Positives: {y_tr.sum()})")
    print(f"Val Set:   {X_va.shape[0]} samples across {meta_va['case_id'].nunique()} cases (Positives: {y_va.sum()})")
    print(f"Test Set:  {X_te.shape[0]} samples across {meta_te['case_id'].nunique()} cases (Positives: {y_te.sum()})")
    print(f"Total Features per sample: {X_tr.shape[1]}")
    print(f"Date Ranges - Train: {meta_tr['complaint_time'].min()} to {meta_tr['complaint_time'].max()}")
    print(f"Date Ranges - Val:   {meta_va['complaint_time'].min()} to {meta_va['complaint_time'].max()}")
    print(f"Date Ranges - Test:  {meta_te['complaint_time'].min()} to {meta_te['complaint_time'].max()}")
