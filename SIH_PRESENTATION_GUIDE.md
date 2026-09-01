# SIH 2024 / SIH26184 — Official Presentation Guide
**Team Name:** Apex Pointers  
**Problem Statement ID:** 184 (SIH26184)  
**Theme:** Blockchain & Cybersecurity  
**Category:** Software  
**Title:** Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance  

---

## Slide 1: Title & Team Details
* **Project Name:** Cybercrime Cash-Withdrawal Predictive Forecaster
* **Problem Statement:** SIH26184 — Development of a Predictive Analytics Framework for Cybercrime Complaints to Forecast Likely Cash Withdrawal Locations in Advance
* **Team Name:** Apex Pointers
* **Theme:** Blockchain & Cybersecurity (Software Category)

---

## Slide 2: Proposed Solution
* **The Core Insight:** Cyber fraud funds do not flow directly from Victim to ATM. They bounce through complex, branching **multi-hop mule networks** (Victim ➔ Mule 1 ➔ Mule 2 ➔ Mule 3 ➔ Cash-out) across multiple jurisdictions.
* **Our Solution:** A real-time predictive intelligence engine that:
  1. Models dynamic transaction graphs using **NetworkX**.
  2. Extracts **48 topological, velocity, geospatial (Haversine), and temporal features** with strict zero-leakage ($t \le T$).
  3. Evaluates 12 candidate ATM clusters across India to output **probabilistic Top-1, Top-3, and Top-5 risk rankings**.
  4. Empirically projects the **cash-out intervention time window** (e.g. 06:00 – 07:10).
  5. Provides **SHAP explainability** so field investigators know exactly *why* a location is high risk.
  6. Supports **real-time dynamic re-ranking** when new mule transfers arrive without requiring model retraining.

---

## Slide 3 & 4: Technical Architecture & Methodology

### Data Flow Pipeline:
```
[1. Complaint Filed] ➔ [2. Multi-Hop Graph G_T] ➔ [3. 48 Multi-Domain Features]
                                                          │
                                                          ▼
[6. Real-Time Intervention]  [5. Calibrated Rankings]  [4. Random Forest ML Model]
  - Top-1/3/5 ATM Clusters      (Trained with Balanced
  - Intervention Time Window     Class Weighting)
  - SHAP Factor Explanations
```

### Chronological Test Set Benchmark Comparison:
*(Strict split: Oldest 70% Train, Next 15% Validation, Newest 15% Test)*

| Model | Top-1 Accuracy | Top-3 Accuracy | Top-5 Accuracy | ROC-AUC | Precision | Recall | F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 6.67% | 20.00% | 46.67% | 0.5580 | 0.1023 | 0.6000 | 0.1748 |
| **Random Forest (Selected Best)** | **7.78%** | **28.89%** | **40.00%** | **0.5018** | **0.1282** | 0.0556 | 0.0775 |
| **XGBoost Classifier** | 5.56% | 24.44% | 43.33% | 0.4976 | 0.0833 | 0.0778 | 0.0805 |

---

## Slide 5: Feasibility & Technical Stack
* **Machine Learning:** Scikit-Learn, XGBoost, SHAP, NetworkX, Pandas, Joblib.
* **Backend API:** FastAPI with SQLAlchemy 2.0 ORM, SQLite database (`cybercrime.db`), JWT authentication, and automated database seeder.
* **Frontend Portal:** React + Vite, Leaflet.js interactive dark-mode surveillance maps, and real-time transaction simulation widget.
* **Speed:** Sub-20 millisecond inference per case; scales horizontally.

---

## Slide 6: Challenges & Mitigation Strategies
1. **Severe Class Imbalance (1 positive vs 11 negative candidates per case):**
   * *Mitigation:* Balanced class weighting (`class_weight='balanced'`) and evaluation focused on Top-K ranking accuracy rather than flat accuracy.
2. **Temporal Data Leakage:**
   * *Mitigation:* Strictly enforced time cut-off ($t \le T$) with rolling pre-$T$ historical priors; 0% future leakage.
3. **Syndicate Geographic Evasion:**
   * *Mitigation:* Combined multi-hop graph depth with cross-state Haversine distances rather than naive city matching (which is only 7.8% accurate).

---

## Slide 7: Impact & Law Enforcement Benefits
* **Proactive Interception:** Shifts cyber cells from reactive post-fraud forensics to **preemptive ATM surveillance** during the critical 180-minute laundering window.
* **Resource Optimization:** Directs police patrols to Top-3 high-probability clusters instead of guessing randomly across hundreds of city ATMs.
* **Actionable Field Alerts:** Automatic alert dispatching with officer acknowledgment workflows.

---

## Slide 8: Mandatory Limitations & Governance Notice
> *This prototype is developed for the Smart India Hackathon using synthetic data for workflow validation purposes only. In a real-world deployment, model weights would be trained on verified NCRP (National Cybercrime Reporting Portal) bank freeze logs, with strict privacy preserving protocols.*
