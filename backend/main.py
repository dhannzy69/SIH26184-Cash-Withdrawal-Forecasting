"""
backend/main.py
Master FastAPI Application for SIH26184 Cybercrime Cash-Withdrawal Location Forecasting.
Mounts all modular routers with CORS, OpenAPI documentation, and automated database startup.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import DATABASE_URL, HORIZON_MINUTES
from backend.database import engine, Base
from backend.seed import seed_database
from backend.routers import auth, cases, transactions, predictions, alerts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes database tables and seeds prototype records on startup."""
    print("[Backend Lifespan] Initializing database...")
    Base.metadata.create_all(bind=engine)
    seed_database()
    yield
    print("[Backend Lifespan] Shutting down backend...")


app = FastAPI(
    title="SIH26184: Cybercrime Cash-Withdrawal Location Forecasting Backend",
    description=(
        "Enterprise-grade predictive analytics platform for active cybercrime complaints. "
        "Models multi-hop mule networks, extracts 48 topological and geospatial features, "
        "forecasts Top-K candidate ATM cash-out clusters, and dispatches field surveillance alerts."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for all frontend origins (React, Vue, Flutter, Next.js, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Modular Routers
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(transactions.router)
app.include_router(predictions.router)
app.include_router(alerts.router)


@app.get("/", tags=["System Information"])
def root_service_info():
    return {
        "service": "SIH26184 Cybercrime Cash-Withdrawal Forecasting Backend",
        "status": "online",
        "version": "2.0.0",
        "api_documentation": "/docs",
        "redoc_documentation": "/redoc",
        "database_backend": "SQLite (SQLAlchemy 2.0)",
        "prediction_horizon_minutes": HORIZON_MINUTES,
        "features_count": 48,
        "selected_model": "Random Forest Classifier",
        "disclaimer": (
            "This system uses synthetic prototype data for hackathon demonstration. "
            "Model outputs are probabilistic risk tiers intended to guide authorized law enforcement investigators."
        )
    }


@app.get("/health", tags=["System Information"])
def health():
    return {
        "status": "healthy",
        "database": "connected",
        "ml_engine": "ready"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
