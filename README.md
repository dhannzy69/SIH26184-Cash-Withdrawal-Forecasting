# SIH26184 — Cybercrime Cash-Withdrawal Location Forecasting Platform

**Smart India Hackathon Prototype**  
*Problem Statement ID:* **184 (SIH26184)**  
*Theme:* **Blockchain & Cybersecurity**  
*Team Name:* **Apex Pointers**  

---

> [!WARNING]
> **Mandatory Disclaimer on Synthetic Data:**  
> *This prototype uses synthetic data. The resulting model performance demonstrates the technical workflow and controlled experimental behaviour only; it does not establish real-world predictive accuracy.*

---

## 1. System Overview

A full-stack, end-to-end predictive analytics framework designed for law enforcement cyber cells to forecast likely ATM cash-withdrawal locations and intervention time windows in advance of physical cash-out.

```
┌─────────────────────────────────────────────────────────────┐
│                 React + Vite Frontend (Port 5173)           │
│  - Interactive Leaflet Geospatial Surveillance Map          │
│  - Multi-Hop Mule Timeline & Graph Visualizer               │
│  - Top-K Candidate ATM Cluster Rankings                     │
│  - SHAP Explainable AI Feature Attribution Bars             │
│  - Real-Time Transaction Injection & Re-Ranking Simulator   │
└──────────────────────────────┬──────────────────────────────┘
                               │ JSON REST API
┌──────────────────────────────▼──────────────────────────────┐
│                 FastAPI Backend (Port 8000)                 │
│  - SQLite / SQLAlchemy 2.0 ORM Engine (600 Cases Seeded)     │
│  - JWT Authentication & Officer RBAC                        │
│  - Case Management CRUD & Dossier APIs                      │
│  - Live Transaction Stream Ingestion & Auto-Alert Engine    │
│  - Swagger UI Documentation (/docs)                         │
└──────────────────────────────┬──────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                     ML Intelligence Core                    │
│  - 48 Multi-Domain Features (Topological, Geo, Diurnal)     │
│  - NetworkX Directed Mule Network Graph                     │
│  - Random Forest Classifier (Balanced Class Weights)        │
│  - Empirical Cash-Out Time Window Estimator                 │
│  - TreeExplainer SHAP Feature Attributions                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Test Set Benchmark Results

Strict chronological evaluation (Oldest 70% Train, Next 15% Validation, Newest 15% Test):

| Model | Top-1 Accuracy | Top-3 Accuracy | Top-5 Accuracy | ROC-AUC | Precision | Recall | F1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Baseline)** | 6.67% | 20.00% | 46.67% | 0.5580 | 0.1023 | 0.6000 | 0.1748 |
| **Random Forest (Selected Best)** | **7.78%** | **28.89%** | **40.00%** | **0.5018** | **0.1282** | 0.0556 | 0.0775 |
| **XGBoost Classifier** | 5.56% | 24.44% | 43.33% | 0.4976 | 0.0833 | 0.0778 | 0.0805 |

---

## 3. Quick Start Guide

### Step 1: Start the FastAPI Backend
```powershell
# In project root:
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
* **API Documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Default Accounts:**
  * Investigator: `officer_sharma` / `investigator123`
  * Admin: `admin` / `admin123`
  * Field Patrol: `field_unit_blr` / `patrol123`

### Step 2: Start the React + Vite Frontend
```powershell
cd frontend
npm install
npm run dev
```
* Open **[http://127.0.0.1:5173](http://127.0.0.1:5173)** in your browser.

---

## 4. Repository Structure

* **`ml/`**: Feature engineering, NetworkX graph modeling, training, inference, explainability, and simulation.
* **`backend/`**: FastAPI REST API, SQLAlchemy ORM, JWT auth, and field alert dispatching.
* **`frontend/`**: React + Vite cyber surveillance portal with Leaflet.js maps.
* **`models/`**: Serialized Random Forest model (`best_model.joblib`).
* **`results/`**: Benchmark metrics (`model_comparison.csv`) and evaluation reports.
* **`DATA_ANALYSIS.md`**: In-depth dataset audit and multi-hop mule chain analysis.
* **`SIH_PRESENTATION_GUIDE.md`**: Slide-by-slide presentation guide for team Apex Pointers.
