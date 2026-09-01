"""
ml/preprocessing.py
Data preprocessing, leakage prevention filters, and transformation pipelines.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline


def filter_transactions_up_to_t(
    transactions_df: pd.DataFrame,
    case_id: str,
    t_cutoff: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    CRITICAL LEAKAGE PREVENTION:
    Extracts only transactions associated with case_id that occurred strictly at or before t_cutoff.
    If t_cutoff is None, returns all transactions up to the latest known transaction for that case.
    """
    case_tx = transactions_df[transactions_df["case_id"] == case_id].copy()
    if case_tx.empty:
        return case_tx

    case_tx = case_tx.sort_values("timestamp")
    if t_cutoff is not None:
        case_tx = case_tx[case_tx["timestamp"] <= t_cutoff]

    return case_tx


def build_account_lookup(accounts_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Builds a fast in-memory dictionary of account attributes:
    account_id -> {account_type, region, account_age_days}
    """
    return accounts_df.set_index("account_id")[["case_id", "account_type", "region", "account_age_days"]].to_dict(orient="index")


def build_location_lookup(locations_df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Builds a fast in-memory dictionary of candidate locations:
    location_id -> {city, district, state, latitude, longitude, atm_cluster_name}
    """
    return locations_df.set_index("location_id").to_dict(orient="index")


def create_numeric_preprocessor() -> Pipeline:
    """
    Standard imputation and scaling pipeline for tabular features.
    """
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
