from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
)
from sqlalchemy.orm import relationship
from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    badge_number = Column(String(50), unique=True, nullable=True)
    role = Column(String(50), default="INVESTIGATOR", nullable=False)  # ADMIN, INVESTIGATOR, FIELD_OFFICER
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assigned_cases = relationship("Case", back_populates="assigned_officer")


class Case(Base):
    __tablename__ = "cases"

    case_id = Column(String(50), primary_key=True, index=True)
    fraud_type = Column(String(100), index=True, nullable=False)
    complaint_time = Column(DateTime, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    victim_region = Column(String(100), index=True, nullable=False)
    status = Column(String(50), default="ACTIVE", index=True)  # ACTIVE, INVESTIGATING, ALERTED, CLOSED
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assigned_officer = relationship("User", back_populates="assigned_cases")
    accounts = relationship("Account", back_populates="case", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="case", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="case", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.case_id"), index=True, nullable=False)
    account_type = Column(String(50), nullable=False)  # Victim, Mule
    region = Column(String(100), nullable=False)
    account_age_days = Column(Integer, default=0)

    # Relationships
    case = relationship("Case", back_populates="accounts")


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(String(50), primary_key=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.case_id"), index=True, nullable=False)
    sender_account = Column(String(50), index=True, nullable=False)
    receiver_account = Column(String(50), index=True, nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    transaction_type = Column(String(50), default="Transfer")

    # Relationships
    case = relationship("Case", back_populates="transactions")


class Location(Base):
    __tablename__ = "locations"

    location_id = Column(String(50), primary_key=True, index=True)
    city = Column(String(100), index=True, nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    atm_cluster_name = Column(String(100), nullable=False)

    # Relationships
    alerts = relationship("Alert", back_populates="location")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    case_id = Column(String(50), ForeignKey("cases.case_id"), index=True, nullable=False)
    location_id = Column(String(50), ForeignKey("locations.location_id"), index=True, nullable=False)
    city = Column(String(100), nullable=False)
    atm_cluster_name = Column(String(100), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_tier = Column(String(20), default="HIGH")  # HIGH, MEDIUM, LOW
    estimated_time_window = Column(String(50), nullable=False)
    status = Column(String(50), default="DISPATCHED", index=True)  # DISPATCHED, ACKNOWLEDGED, INTERCEPTED, EXPIRED
    dispatched_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    # Relationships
    case = relationship("Case", back_populates="alerts")
    location = relationship("Location", back_populates="alerts")
