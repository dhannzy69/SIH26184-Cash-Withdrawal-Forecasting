# SIH26184 — Cybercrime Cash-Withdrawal Location Forecasting ML Framework

**Problem Statement ID:** SIH26184  
**Problem Statement Title:** Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance, Enabling Generation of Actionable Intelligence for Timely and Proactive Cybercrime Intervention.  
**Theme:** Blockchain & Cybersecurity (Category: Software)

---

## 1. Executive Summary & Core Formulation

Traditional anti-fraud systems often treat financial flows as a simplistic `Victim -> Mule -> ATM` pipeline. In reality, cybercrime syndicates employ complex, branching, multi-hop mule networks (`Victim -> Mule A -> Mule B -> Mule C -> ATM`) across varying geographical jurisdictions.

This project delivers an **end-to-end, leakage-free Machine Learning framework** that ingests active complaint records and transaction flows up to cut-off time $T$, constructs dynamic directed graphs using NetworkX, extracts 48 multi-domain features, and outputs a calibrated probabilistic ranking of Top-1, Top-3, and Top-5 candidate ATM clusters alongside an estimated cash-out time window, SHAP explainability, and real-time transaction simulation.

> ### ⚠️ Synthetic Data Limitation & Operational Governance
> **"This prototype uses synthetic data. The resulting model performance demonstrates the technical workflow and controlled experimental behaviour only; it does not establish real-world predictive accuracy."**
> 
> * **Probabilistic Ranking vs. Certainty:** The system produces risk scores, not guarantees. A high score flags a high-priority area for surveillance, not definitive guilt.
> * **False Positives:** Multi-candidate scoring inherently carries a trade-off between surveillance coverage (Top-5 recall) and precision.
> * **Concept Drift & Adversarial Adaptation:** Real-world syndicates actively modify laundering patterns in response to law enforcement countermeasures.
> * **Geographic Variation:** Urban ATM densities vary greatly across metropolitan clusters and rural centers.
> * **Authorized Real-World Data:** Production deployment requires authorized access to live financial intelligence channels (e.g., I4C, CFCFRMS, NPCI, and core banking feeds).
> * **Human-in-the-Loop Validation:** All model outputs must be validated by authorized investigative officers before field dispatch or account freezing.

---

## 2. Project Architecture & Codebase Structure

```
.
├── data/                       # Prototype dataset CSVs
│   ├── cases.csv               # 600 cybercrime complaint records
│   ├── accounts.csv            # 3,351 victim and mule accounts
│   ├── transactions.csv        # 2,751 fund transfers (78.2% mule-to-mule)
│   ├── locations.csv           # 12 candidate ATM clusters with geo-coordinates
│   └── withdrawals.csv         # 600 ground-truth cash-out outcome records
│
├── ml/                         # Modular Machine Learning Pipeline
│   ├── config.py               # Central configuration (HORIZON_MINUTES=180, paths)
│   ├── data_loader.py          # Data ingestion, schema validation, and datetime parsing
│   ├── preprocessing.py        # Strict leakage-prevention filters (timestamp <= T)
│   ├── network_features.py     # NetworkX directed graph metrics & multi-hop depths
│   ├── time_features.py        # Cyclical temporal metrics & empirical time-window estimator
│   ├── geo_features.py         # Haversine distance computations & spatial relationships
│   ├── features.py             # Feature consolidation (48 multi-domain features)
│   ├── dataset_builder.py      # Case-location evaluation pair builder with rolling priors
│   ├── train.py                # Baseline (Logistic Regression), Random Forest, XGBoost
│   ├── evaluate.py             # Top-1/3/5 ranking accuracy, ROC-AUC, report generation
│   ├── predict.py              # Inference engine (Top-K probabilistic rankings)
│   ├── explain.py              # SHAP TreeExplainer & feature attribution insights
│   └── simulate.py             # Dynamic transaction simulation without retraining
│
├── models/                     # Persisted Artifacts
│   ├── best_model.joblib       # Serialized trained model (Random Forest)
│   ├── feature_columns.json    # Exact ordered feature list
│   └── model_metadata.json     # Hyperparameters and evaluation scores
│
├── results/                    # Validation & Test Evaluation Outputs
│   ├── model_comparison.csv    # Real test metrics comparison
│   └── evaluation_report.txt   # Detailed interpretive report
│
├── requirements.txt            # Python dependencies
└── DATA_ANALYSIS.md            # In-depth dataset audit report
```

---

## 3. Machine Learning Formulation & Leakage Prevention

### A. Candidate-Pair Formulation
Every sample represents:
$$\text{Sample} = (\text{Case } C_i, \text{Cut-off Time } T, \text{Candidate Location } L_k) \quad \text{for } k \in \{L001, \dots, L012\}$$
* **Target $Y = 1$:** Actual cash withdrawal occurs at $L_k$ within $T \le t_{\text{withdrawal}} \le T + 180\text{ minutes}$.
* **Target $Y = 0$:** No cash-out at $L_k$ within the prediction horizon.
* **Class Imbalance:** 1 positive per 11 negatives (~8.33% positive class prevalence).

### B. Strict Data Leakage Safeguards
1. **Timestamp Cut-off:** Only transactions where `timestamp <= T` are visible during feature extraction.
2. **Quarantined Target:** `withdrawals.csv` is strictly isolated and used exclusively to assign target labels during training.
3. **Rolling Historical Priors:** Location cash-out frequencies and mule-region co-occurrences are computed strictly from cases concluded before time $T$.

---

## 4. Multi-Domain Feature Engineering (48 Features)

| Domain | Key Features | Analytical Objective |
| :--- | :--- | :--- |
| **Network Graph (NetworkX)** | `network_num_accounts`, `network_num_mules`, `network_num_edges`, `terminal_in_degree`, `terminal_out_degree`, `current_hop_number`, `max_hop_depth`, `num_mule_to_mule_transfers`, `amount_retained_ratio`, `pagerank_terminal`, `betweenness_terminal` | Captures mule network topology, branching depth, intermediary laundering layers, and centrality of the active account. |
| **Transaction Dynamics** | `total_incoming_amount`, `total_outgoing_amount`, `transaction_count`, `recent_transaction_count`, `avg_transaction_amount`, `max_transaction_amount`, `transaction_velocity`, `incoming_velocity`, `outgoing_velocity`, `amount_ratio` | Measures fund flow velocity, splitting behavior, commission retention, and recent transaction acceleration. |
| **Temporal Dynamics** | `tx_hour`, `tx_minute_of_day`, `tx_day_of_week`, `complaint_hour`, `is_night_transaction`, `time_since_complaint_min`, `time_since_last_tx_min`, `avg_transfer_interval_min` | Encodes circadian rhythms of laundering networks, time elapsed since initial fraud alert, and hop delays. |
| **Spatial / Geospatial** | `dist_candidate_to_victim_km`, `dist_candidate_to_current_mule_km`, `min_dist_candidate_to_network_km`, `mean_dist_candidate_to_network_km`, `max_dist_candidate_to_network_km`, `is_same_city_as_current_mule`, `is_same_city_as_victim` | Haversine great-circle distances between candidate ATM clusters and case network nodes. |
| **Historical Priors** | `hist_location_freq_prior`, `hist_network_association_prior`, `candidate_location_num` | Leakage-free Bayesian prior indicators based on historical regional cash-out tendencies prior to $T$. |

---

## 5. Experimental Results & Model Benchmark

Evaluated on a strictly **chronological test partition** (newest 15% of cases: July 26 to August 29, 2026; 1,080 candidate evaluations across 90 cases):

| Model | Precision | Recall | F1-Score | ROC-AUC | Top-1 Accuracy | Top-3 Accuracy | Top-5 Accuracy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 0.1023 | 0.6000 | 0.1748 | 0.5580 | 6.67% | 20.00% | 46.67% |
| **Random Forest Classifier (Selected)** | **0.1282** | 0.0556 | 0.0775 | 0.5018 | **7.78%** | **28.89%** | 40.00% |
| **XGBoost Classifier** | 0.0833 | 0.0778 | 0.0805 | 0.4976 | 5.56% | 24.44% | **43.33%** |

* **Selected Model:** **Random Forest Classifier** achieved the highest validation Top-3 ranking accuracy (32.22%) and was persisted to `models/best_model.joblib`.
* **Benchmark Takeaway:** While the simple baseline achieves moderate recall by predicting indiscriminately, Random Forest achieves superior precision and Top-3 candidate ranking.

---

## 6. How to Run the System

### Prerequisites
```bash
python -m pip install -r requirements.txt
```

### 1. Train Models & Generate Benchmarks
```bash
python -m ml.train
```

### 2. Predict Probable Cash-Out Locations for an Active Case
```bash
python -m ml.predict
```
Example programmatic usage:
```python
from ml.predict import predict_locations

result = predict_locations(case_id="C0001")
print("Top Probable Location:", result["top_1"])
print("Estimated Cash-Out Window:", result["estimated_cashout_time_window"])
```

### 3. Generate SHAP Explainability for Investigators
```bash
python -m ml.explain
```

### 4. Run Real-Time Transaction Simulation (Dynamic Re-ranking)
```bash
python -m ml.simulate
```
Demonstrates how incoming multi-hop transfers update candidate risk rankings on the fly without model retraining.
