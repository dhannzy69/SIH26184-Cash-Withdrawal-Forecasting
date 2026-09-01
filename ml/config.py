import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
RESULTS_DIR = BASE_DIR / "results"

# Ensure runtime directories exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Prediction Horizon Configuration (Section 5)
HORIZON_MINUTES = 180  # Cash withdrawal occurring within the next 180 minutes

# Temporal Splitting Ratios (Section 16: Oldest 70%, Next 15%, Newest 15%)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

# Evaluation & Ranking
TOP_K_LIST = [1, 3, 5]
RANDOM_SEED = 42

# Risk Thresholds for Prediction Engine
RISK_THRESHOLDS = {
    "HIGH": 0.50,
    "MEDIUM": 0.20,
    "LOW": 0.00
}
