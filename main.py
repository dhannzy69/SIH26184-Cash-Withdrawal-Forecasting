"""
main.py
SIH26184 Cash-Withdrawal Location Forecasting - Unified Demonstration Entry Point.
Executes the full pipeline: Data check, Model inference, SHAP explanation, and Dynamic simulation.
"""

import sys
import pandas as pd
from ml.config import RESULTS_DIR
from ml.predict import predict_locations
from ml.explain import explain_candidate_prediction
from ml.simulate import demo_simulation


def main():
    print("=" * 80)
    print("SIH26184: CYBERCRIME CASH-WITHDRAWAL LOCATION FORECASTING PIPELINE")
    print("Theme: Blockchain & Cybersecurity | Hackathon Prototype")
    print("=" * 80)

    # 1. Display Model Evaluation Summary
    comp_file = RESULTS_DIR / "model_comparison.csv"
    if comp_file.exists():
        print("\n[1] TEST SET BENCHMARK METRICS (results/model_comparison.csv):")
        df = pd.read_csv(comp_file)
        print(df.to_string(index=False))
    else:
        print("\n[1] Model comparison not yet run. Run 'python -m ml.train' first.")

    # 2. Run Probabilistic Location Forecasting on Sample Active Case
    sample_case = "C0001"
    print(f"\n[2] ACTIVE CASE INFERENCE: Running prediction engine for case '{sample_case}'...")
    pred = predict_locations(sample_case)

    print(f"  Prediction Time Cut-Off (T): {pred['prediction_time']}")
    print(f"  Estimated Cash-Out Window:   {pred['estimated_cashout_time_window']}")
    print(f"  Observed Transactions at T:  {pred['observed_transactions_count']}")
    print("\n  Top-3 Ranked Cash-Out Locations:")
    for loc in pred["top_3"]:
        print(f"    Rank {loc['rank']}: {loc['city']:<12} ({loc['location_id']}) [{loc['atm_cluster_name']}] | Score: {loc['score']} | Risk: {loc['risk']}")

    # 3. Explainability with SHAP
    print(f"\n[3] EXPLAINABILITY: Computing SHAP feature attribution for Rank 1 location...")
    explanation = explain_candidate_prediction(sample_case, target_rank=1)
    print(f"  Location: {explanation['city']} ({explanation['location_id']}) | Method: {explanation['explanation_method']}")
    print("  Key Contributing Factors:")
    for f in explanation["contributing_factors"]:
        print(f"    - {f['feature_description']} (Value: {f['feature_value']}, Attribution: {f['attribution_score']} -> {f['direction']})")

    # 4. Multi-Hop Simulation Demo
    print("\n[4] DYNAMIC TRANSACTION SIMULATION:")
    demo_simulation()

    print("\n" + "=" * 80)
    print("PROTOTYPE EXECUTION COMPLETE.")
    print("Disclaimer: This prototype uses synthetic data for workflow validation purposes only.")
    print("=" * 80)


if __name__ == "__main__":
    main()
