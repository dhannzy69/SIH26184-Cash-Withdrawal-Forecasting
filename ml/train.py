"""
ml/train.py
Model training pipeline:
1. Logistic Regression Baseline (benchmark with limited features)
2. Random Forest Classifier (balanced weights, tree ensemble)
3. XGBoost Classifier (positive class weighting, gradient boosting)
Evaluates on chronological validation & test sets, selects superior model, and persists artifacts.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
import joblib

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier

from ml.config import MODELS_DIR, RESULTS_DIR, RANDOM_SEED
from ml.dataset_builder import build_ml_dataset
from ml.evaluate import (
    evaluate_model_performance, save_comparison_csv, generate_evaluation_report
)

# Baseline limited feature subset (Section 13)
BASELINE_FEATURES = [
    "avg_transaction_amount",
    "transaction_count",
    "dist_candidate_to_victim_km",
    "dist_candidate_to_current_mule_km",
    "tx_hour",
    "tx_day_of_week"
]


def train_and_evaluate_all():
    print("=" * 80)
    print("SIH26184: TRAINING & EVALUATING CASH-WITHDRAWAL FORECASTING MODELS")
    print("=" * 80)

    # 1. Load chronological datasets
    print("\n[1/5] Building chronological datasets...")
    train_data, val_data, test_data = build_ml_dataset()
    X_train, y_train, meta_train = train_data
    X_val, y_val, meta_val = val_data
    X_test, y_test, meta_test = test_data

    feature_cols = list(X_train.columns)
    print(f"Features available ({len(feature_cols)}): {feature_cols[:5]} ...")

    val_results = {}
    test_results = {}
    trained_models = {}

    # -------------------------------------------------------------
    # STEP 5: Logistic Regression Baseline (Limited Features)
    # -------------------------------------------------------------
    print("\n[2/5] Training Baseline (Logistic Regression)...")
    baseline_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced", random_state=RANDOM_SEED, max_iter=1000))
    ])
    baseline_pipeline.fit(X_train[BASELINE_FEATURES], y_train)
    trained_models["LogisticRegression"] = baseline_pipeline

    # Validation evaluation
    val_probs_lr = baseline_pipeline.predict_proba(X_val[BASELINE_FEATURES])[:, 1]
    val_preds_lr = (val_probs_lr >= 0.5).astype(int)
    val_results["LogisticRegression"] = evaluate_model_performance(y_val, val_preds_lr, val_probs_lr, meta_val)

    # Test evaluation
    test_probs_lr = baseline_pipeline.predict_proba(X_test[BASELINE_FEATURES])[:, 1]
    test_preds_lr = (test_probs_lr >= 0.5).astype(int)
    test_results["LogisticRegression"] = evaluate_model_performance(y_test, test_preds_lr, test_probs_lr, meta_test)

    print(f"  Baseline Test Metrics: ROC-AUC={test_results['LogisticRegression']['roc_auc']}, "
          f"Top-1={test_results['LogisticRegression']['top1']}, "
          f"Top-3={test_results['LogisticRegression']['top3']}, "
          f"Top-5={test_results['LogisticRegression']['top5']}")

    # -------------------------------------------------------------
    # STEP 6: Random Forest Classifier (Full Features)
    # -------------------------------------------------------------
    print("\n[3/5] Training Model 1: Random Forest Classifier...")
    rf_clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_SEED,
        n_jobs=-1
    )
    rf_clf.fit(X_train, y_train)
    trained_models["RandomForest"] = rf_clf

    # Validation evaluation
    val_probs_rf = rf_clf.predict_proba(X_val)[:, 1]
    val_preds_rf = (val_probs_rf >= 0.5).astype(int)
    val_results["RandomForest"] = evaluate_model_performance(y_val, val_preds_rf, val_probs_rf, meta_val)

    # Test evaluation
    test_probs_rf = rf_clf.predict_proba(X_test)[:, 1]
    test_preds_rf = (test_probs_rf >= 0.5).astype(int)
    test_results["RandomForest"] = evaluate_model_performance(y_test, test_preds_rf, test_probs_rf, meta_test)

    print(f"  Random Forest Test Metrics: ROC-AUC={test_results['RandomForest']['roc_auc']}, "
          f"Top-1={test_results['RandomForest']['top1']}, "
          f"Top-3={test_results['RandomForest']['top3']}, "
          f"Top-5={test_results['RandomForest']['top5']}")

    # -------------------------------------------------------------
    # STEP 7: XGBoost Classifier (Full Features)
    # -------------------------------------------------------------
    print("\n[4/5] Training Model 2: XGBoost Classifier...")
    xgb_clf = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=11.0,  # 1 positive per 11 negative candidates
        random_state=RANDOM_SEED,
        eval_metric="logloss"
    )
    xgb_clf.fit(X_train, y_train)
    trained_models["XGBoost"] = xgb_clf

    # Validation evaluation
    val_probs_xgb = xgb_clf.predict_proba(X_val)[:, 1]
    val_preds_xgb = (val_probs_xgb >= 0.5).astype(int)
    val_results["XGBoost"] = evaluate_model_performance(y_val, val_preds_xgb, val_probs_xgb, meta_val)

    # Test evaluation
    test_probs_xgb = xgb_clf.predict_proba(X_test)[:, 1]
    test_preds_xgb = (test_probs_xgb >= 0.5).astype(int)
    test_results["XGBoost"] = evaluate_model_performance(y_test, test_preds_xgb, test_probs_xgb, meta_test)

    print(f"  XGBoost Test Metrics: ROC-AUC={test_results['XGBoost']['roc_auc']}, "
          f"Top-1={test_results['XGBoost']['top1']}, "
          f"Top-3={test_results['XGBoost']['top3']}, "
          f"Top-5={test_results['XGBoost']['top5']}")

    # -------------------------------------------------------------
    # STEP 8 & 9: Model Selection & Persistence
    # -------------------------------------------------------------
    print("\n[5/5] Comparing models on Validation Set and selecting best model...")
    # Selection criteria: Primary = Top-3 Accuracy on validation set, Secondary = ROC-AUC
    candidates = ["RandomForest", "XGBoost"]
    best_model_name = max(
        candidates,
        key=lambda m: (val_results[m]["top3"], val_results[m]["roc_auc"])
    )

    print(f"\nSelection Decision: {best_model_name} selected as the Best Model!")
    print(f"  Validation Top-3 Accuracy: {val_results[best_model_name]['top3']}")
    print(f"  Validation ROC-AUC:        {val_results[best_model_name]['roc_auc']}")

    best_model = trained_models[best_model_name]

    # Save model and artifacts
    joblib.dump(best_model, MODELS_DIR / "best_model.joblib")
    with open(MODELS_DIR / "feature_columns.json", "w") as f:
        json.dump(feature_cols, f, indent=2)

    metadata = {
        "best_model_name": best_model_name,
        "feature_count": len(feature_cols),
        "validation_metrics": val_results[best_model_name],
        "test_metrics": test_results[best_model_name],
        "baseline_test_metrics": test_results["LogisticRegression"]
    }
    with open(MODELS_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Save comparison CSV and evaluation report
    comp_df = save_comparison_csv(test_results, RESULTS_DIR / "model_comparison.csv")
    report_str = generate_evaluation_report(test_results, best_model_name, RESULTS_DIR / "evaluation_report.txt")

    print(f"\nModel Comparison Saved to: {RESULTS_DIR / 'model_comparison.csv'}")
    print(comp_df.to_string(index=False))

    print(f"\nEvaluation Report Saved to: {RESULTS_DIR / 'evaluation_report.txt'}")
    print("\n" + report_str)

    return best_model, feature_cols, test_results


if __name__ == "__main__":
    train_and_evaluate_all()
