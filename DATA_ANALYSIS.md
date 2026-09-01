# SIH26184 — Dataset Analysis Report: Cybercrime Cash-Withdrawal Location Forecasting

## 1. Executive Summary & Dataset Integrity
Inspection was conducted across all 5 CSV files comprising the synthetic prototype dataset for Smart India Hackathon problem statement **SIH26184**.

> **Synthetic Data Disclaimer:**
> This prototype uses synthetic data. The resulting model performance demonstrates the technical workflow and controlled experimental behaviour only; it does not establish real-world predictive accuracy.

### Summary Metrics Across Tables
| Dataset File | Rows (Shape) | Columns | Duplicates | Missing Values | Primary Key / Identifier |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `cases.csv` | 600 | 6 | 0 | 0 (0.0%) | `case_id` |
| `accounts.csv` | 3,351 | 5 | 0 | 0 (0.0%) | `account_id` |
| `transactions.csv` | 2,751 | 7 | 0 | 0 (0.0%) | `transaction_id` |
| `locations.csv` | 12 | 7 | 0 | 0 (0.0%) | `location_id` |
| `withdrawals.csv` | 600 | 6 | 0 | 0 (0.0%) | `withdrawal_id` |

---

## 2. Table Schemas & Column Audit

### A. `cases.csv` (600 records)
* `case_id` (str): Unique complaint case identifier (`C0001` - `C0600`).
* `fraud_type` (str): Category of cybercrime (`Investment Fraud` [136], `Job Scam` [128], `Phishing` [124], `UPI Fraud` [110], `Online Shopping Fraud` [102]).
* `complaint_time` (datetime): Timestamp of initial cybercrime complaint (range: `2026-01-01 20:59:00` to `2026-08-29 14:13:00`).
* `amount` (int64): Total disputed amount in INR (min: 25,123, max: 499,842, mean: 228,683).
* `victim_region` (str): Geographic city/region of victim (8 distinct cities: Bengaluru, Chennai, Coimbatore, Delhi, Hyderabad, Kochi, Mumbai, Pune).
* `status` (str): Case disposition (`Closed` across all records).

### B. `accounts.csv` (3,351 records)
* `account_id` (str): Unique account identifier (`A{case}_{index}`).
* `case_id` (str): Foreign key to `cases.csv`.
* `account_type` (str): `Victim` (600 accounts, exactly 1 per case) or `Mule` (2,751 accounts, 2 to 6 mules per case).
* `region` (str): Account registered city (12 distinct cities matching `locations.csv`).
* `account_age_days` (int64): Account tenure in days (min: 15, max: 1,825).

### C. `transactions.csv` (2,751 records)
* `transaction_id` (str): Unique transaction identifier (`T{case}_{index}`).
* `case_id` (str): Foreign key to `cases.csv`.
* `sender_account` (str): Originating account.
* `receiver_account` (str): Beneficiary account.
* `amount` (int64): Transferred amount in INR (min: 5,012, max: 442,109).
* `timestamp` (datetime): Transaction timestamp (range: `2026-01-01 21:28:00` to `2026-08-29 15:34:00`).
* `transaction_type` (str): `Transfer`.

### D. `locations.csv` (12 candidate clusters)
* `location_id` (str): `L001` to `L012`.
* `city` (str): Bengaluru, Chennai, Hyderabad, Coimbatore, Kochi, Pune, Mumbai, Delhi, Ahmedabad, Jaipur, Lucknow, Bhubaneswar.
* `district` (str), `state` (str)
* `latitude` (float64), `longitude` (float64): Precise geo-coordinates for Haversine calculations.
* `atm_cluster_name` (str): `Cluster A` through `Cluster L`.

### E. `withdrawals.csv` (600 records)
* `withdrawal_id` (str): `W0001` to `W0600`.
* `case_id` (str): Exact 1-to-1 foreign key to `cases.csv`.
* `account_id` (str): Account from which cash was withdrawn (always the terminal mule account).
* `location_id` (str): Foreign key to `locations.csv` (the ground-truth cash-out cluster).
* `amount` (int64): Cash-out amount in INR (min: 3,110, max: 279,845).
* `timestamp` (datetime): Cash-out timestamp (range: `2026-01-02 00:02:00` to `2026-08-29 17:07:00`).

---

## 3. Relational & Topological Verification

```
[cases.csv] (case_id) 1 ─── N [accounts.csv] (account_id)
      │                               │
      │ 1                             │ (sender/receiver)
      ▼                               ▼
[transactions.csv] (case_id) N ─── N [accounts.csv]
      │
      │ 1
      ▼
[withdrawals.csv] (case_id) ─── 1 [locations.csv] (location_id)
                   (account_id) ─── 1 [accounts.csv]
```

### Relational Integrity Check Results
1. **Case Consistency:** All 600 cases exist in `cases.csv`, `accounts.csv`, `transactions.csv`, and `withdrawals.csv`. Exactly 0 orphans or dangling foreign keys.
2. **Account Consistency:** All 2,751 transaction sender/receiver accounts and all 600 withdrawal accounts exist in `accounts.csv`.
3. **Location Consistency:** All 600 withdrawal records point to valid `location_id`s in `locations.csv`.

---

## 4. Mule-to-Mule Flow Verification

### Transaction Types Breakdown
* **Victim → Mule (Hop 1):** 600 transactions (21.8%)
* **Mule → Mule (Hop 2+):** 2,151 transactions (78.2%)
* **Multi-hop chains are confirmed to exist across 100% of cases.**

### Sample Transaction Chain (Case C0255)
* **Complaint:** `2026-04-14 04:11:00` | Victim Region: `Mumbai` | Disputed Amount: `₹103,958`
  1. `A0255_1 (Victim)` ➔ `A0255_2 (Mule, Hyderabad)` | ₹63,305 | `04:53:00` (delay +42m)
  2. `A0255_2 (Mule, Hyderabad)` ➔ `A0255_3 (Mule, Pune)` | ₹37,553 | `05:11:00` (delay +18m)
  3. `A0255_3 (Mule, Pune)` ➔ `A0255_4 (Mule, Ahmedabad)` | ₹28,004 | `05:27:00` (delay +16m)
  4. `A0255_4 (Mule, Ahmedabad)` ➔ `A0255_5 (Mule, Delhi)` | ₹22,440 | `05:37:00` (delay +10m)
  5. `A0255_5 (Mule, Delhi)` ➔ `A0255_6 (Mule, Jaipur)` | ₹12,608 | `05:42:00` (delay +5m)
  6. `A0255_6 (Mule, Jaipur)` ➔ `A0255_7 (Mule, Mumbai)` | ₹11,121 | `06:15:00` (delay +33m)
* **Withdrawal (Ground Truth Target):**
  * Account: `A0255_7` | Amount: `₹10,749` | Location: `L007 (Mumbai - Cluster G)` | Timestamp: `07:28:00` (+73m after last transfer).

### Key Temporal & Routing Characteristics
* **Transactions per case:** min = 3, median = 5, max = 6 (mean: 4.58).
* **Complaint to 1st transfer:** median = 30.0 min (min 6 min, max 55 min).
* **Last transfer to withdrawal:** median = 67.5 min (min 10 min, max 197 min).
* **Geographic Disconnect:** Withdrawal city matches the final mule account region in only 7.8% of cases, and victim region in only 8.3% of cases. Simple heuristic lookups will fail; non-linear machine learning combining topological, geographic, and temporal features is strictly required.

---

## 5. Potential Data Leakage Risks & Safeguards

| Leakage Risk | How it Occurs | Prevention Safeguard in ML Pipeline |
| :--- | :--- | :--- |
| **Future Transactions** | Using transfers timestamped after prediction cut-off $T$. | Filter transactions strictly where `timestamp <= T`. |
| **Ground Truth Withdrawal** | Feeding withdrawal amount, withdrawal timestamp, or terminal account to model features. | `withdrawals.csv` is quarantined and ONLY used to label binary targets ($Y=1$ if candidate location matches actual withdrawal location within prediction horizon). |
| **Lookahead Historical Stats** | Calculating location or network frequencies over the entire 8-month dataset. | Calculate historical aggregates dynamically or cumulatively based strictly on events prior to $T$. |
| **Target in Training Pairs** | Including the true location as an explicit feature. | Candidate location is purely an evaluation subject paired with case context; features represent spatial distance from candidate to current known case nodes. |

---

## 6. Target Formulation & Class Balance
For each case $C_i$ evaluated at time $T$, we construct 12 candidate pairs: $(C_i, T, L_k)$ for $k \in \{1, \dots, 12\}$.
* Target $y_{i, k} = 1$ if cash-out occurs at $L_k$ within horizon $T + \Delta H$ (where $\Delta H = 180$ minutes).
* Target $y_{i, k} = 0$ otherwise.
* **Class Ratio:** Exactly 1 positive per 11 negatives per case (1:11 ratio, ~8.33% positive prevalence). Handled via `class_weight='balanced'` in Random Forest and `scale_pos_weight=11.0` in XGBoost.
