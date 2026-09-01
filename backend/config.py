import os
from pathlib import Path

# Paths
BACKEND_DIR = Path(__file__).resolve().parent
BASE_DIR = BACKEND_DIR.parent
DATA_DIR = BASE_DIR / "data"

# Database Configuration (SQLite default with zero-config, PostgreSQL compatible)
SQLITE_DB_PATH = BACKEND_DIR / "cybercrime.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{SQLITE_DB_PATH}")

# Security & JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "sih26184_cybercrime_investigation_jwt_secret_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Surveillance & Alert Thresholds
ALERT_SCORE_THRESHOLD = 0.10  # Score >= 10% generates a surveillance alert
HORIZON_MINUTES = 180  # Default prediction horizon in minutes

