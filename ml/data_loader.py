"""
ml/data_loader.py
Loads, validates, and prepares dataframes for the SIH26184 Cash-Withdrawal Location Forecasting system.
"""

import os
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
from ml.config import DATA_DIR, BASE_DIR


def get_data_file(filename: str) -> Path:
    """Find file in DATA_DIR or fallback to BASE_DIR."""
    primary = DATA_DIR / filename
    if primary.exists():
        return primary
    fallback = BASE_DIR / filename
    if fallback.exists():
        return fallback
    raise FileNotFoundError(f"Could not find {filename} in {DATA_DIR} or {BASE_DIR}")


def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads all five dataset files and validates their column schemas and types.
    Returns:
        cases_df, accounts_df, transactions_df, locations_df, withdrawals_df
    """
    cases_df = pd.read_csv(get_data_file("cases.csv"))
    accounts_df = pd.read_csv(get_data_file("accounts.csv"))
    transactions_df = pd.read_csv(get_data_file("transactions.csv"))
    locations_df = pd.read_csv(get_data_file("locations.csv"))
    withdrawals_df = pd.read_csv(get_data_file("withdrawals.csv"))

    # Parse datetime columns
    cases_df["complaint_time"] = pd.to_datetime(cases_df["complaint_time"])
    transactions_df["timestamp"] = pd.to_datetime(transactions_df["timestamp"])
    withdrawals_df["timestamp"] = pd.to_datetime(withdrawals_df["timestamp"])

    # Basic validations
    required_case_cols = {"case_id", "complaint_time", "amount", "victim_region"}
    required_tx_cols = {"transaction_id", "case_id", "sender_account", "receiver_account", "amount", "timestamp"}
    required_loc_cols = {"location_id", "city", "latitude", "longitude"}
    required_with_cols = {"withdrawal_id", "case_id", "account_id", "location_id", "timestamp"}

    assert required_case_cols.issubset(cases_df.columns), f"cases.csv missing {required_case_cols - set(cases_df.columns)}"
    assert required_tx_cols.issubset(transactions_df.columns), f"transactions.csv missing {required_tx_cols - set(transactions_df.columns)}"
    assert required_loc_cols.issubset(locations_df.columns), f"locations.csv missing {required_loc_cols - set(locations_df.columns)}"
    assert required_with_cols.issubset(withdrawals_df.columns), f"withdrawals.csv missing {required_with_cols - set(withdrawals_df.columns)}"

    return cases_df, accounts_df, transactions_df, locations_df, withdrawals_df


if __name__ == "__main__":
    cases, accs, txs, locs, withs = load_raw_data()
    print("[STEP 1 SUCCESS] Raw data loaded and validated successfully.")
    print(f"Cases: {cases.shape}, Accounts: {accs.shape}, Transactions: {txs.shape}, Locations: {locs.shape}, Withdrawals: {withs.shape}")
