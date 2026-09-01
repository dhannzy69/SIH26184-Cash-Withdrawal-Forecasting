from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# --- Authentication Schemas ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str
    badge_number: Optional[str] = None
    role: str = Field(default="INVESTIGATOR")


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    badge_number: Optional[str] = None
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


# --- Account & Transaction Schemas ---
class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    account_id: str
    account_type: str
    region: str
    account_age_days: int


class TransactionCreate(BaseModel):
    case_id: str
    sender_account: str
    receiver_account: str
    amount: float = Field(..., gt=0)
    timestamp: datetime
    transaction_type: str = "Transfer"
    # Optional dynamic mule attributes
    receiver_region: Optional[str] = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    case_id: str
    sender_account: str
    receiver_account: str
    amount: float
    timestamp: datetime
    transaction_type: str


# --- Case Schemas ---
class CaseCreate(BaseModel):
    case_id: str
    fraud_type: str
    complaint_time: datetime
    amount: float = Field(..., gt=0)
    victim_region: str
    status: str = "ACTIVE"
    victim_account_id: Optional[str] = None


class CaseUpdate(BaseModel):
    status: Optional[str] = None
    assigned_officer_id: Optional[int] = None


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    case_id: str
    fraud_type: str
    complaint_time: datetime
    amount: float
    victim_region: str
    status: str
    created_at: datetime
    assigned_officer_id: Optional[int] = None


class CaseDetailResponse(CaseResponse):
    accounts: List[AccountResponse] = []
    transactions: List[TransactionResponse] = []


# --- Location Schemas ---
class LocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: str
    city: str
    district: str
    state: str
    latitude: float
    longitude: float
    atm_cluster_name: str


# --- Alert Schemas ---
class AlertCreate(BaseModel):
    case_id: str
    location_id: str
    city: str
    atm_cluster_name: str
    risk_score: float
    risk_tier: str = "HIGH"
    estimated_time_window: str
    notes: Optional[str] = None


class AlertUpdate(BaseModel):
    status: str  # DISPATCHED, ACKNOWLEDGED, INTERCEPTED, EXPIRED
    notes: Optional[str] = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    case_id: str
    location_id: str
    city: str
    atm_cluster_name: str
    risk_score: float
    risk_tier: str
    estimated_time_window: str
    status: str
    dispatched_at: datetime
    notes: Optional[str] = None


# --- Prediction Schemas ---
class PredictionCandidate(BaseModel):
    rank: int
    location_id: str
    city: str
    atm_cluster_name: str
    latitude: float
    longitude: float
    score: float
    risk: str


class PredictionResponse(BaseModel):
    case_id: str
    prediction_time: str
    estimated_cashout_time_window: str
    observed_transactions_count: int
    top_1: List[PredictionCandidate]
    top_3: List[PredictionCandidate]
    top_5: List[PredictionCandidate]
    all_ranked_locations: List[PredictionCandidate]
    disclaimer: str
