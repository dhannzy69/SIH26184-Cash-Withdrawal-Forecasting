"""
backend/seed.py
Initializes database tables and seeds prototype records from CSV datasets.
Creates initial law enforcement officer accounts for authentication.
"""

from datetime import datetime
import pandas as pd
from sqlalchemy.orm import Session

from backend.database import engine, Base, SessionLocal
from backend.models import User, Case, Account, Transaction, Location, Alert
from backend.auth import hash_password
from ml.data_loader import load_raw_data


def seed_database():
    print("=" * 70)
    print("INITIALIZING AND SEEDING CYBERCRIME DATABASE")
    print("=" * 70)

    # 1. Create all schema tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # 2. Seed Default Users
        if db.query(User).count() == 0:
            print("[1/4] Seeding default law enforcement officer accounts...")
            users = [
                User(
                    username="admin",
                    hashed_password=hash_password("admin123"),
                    full_name="Central Cyber Operations Admin",
                    badge_number="ADMIN-001",
                    role="ADMIN"
                ),
                User(
                    username="officer_sharma",
                    hashed_password=hash_password("investigator123"),
                    full_name="Inspector Vikram Sharma",
                    badge_number="CYBER-108",
                    role="INVESTIGATOR"
                ),
                User(
                    username="field_unit_blr",
                    hashed_password=hash_password("patrol123"),
                    full_name="SI Rajesh Gowda (Bengaluru Tactical)",
                    badge_number="FIELD-501",
                    role="FIELD_OFFICER"
                )
            ]
            db.add_all(users)
            db.commit()
            print("  Created 3 default accounts: 'admin', 'officer_sharma', 'field_unit_blr'")
        else:
            print("[1/4] User accounts already present.")

        # 3. Check if cases/accounts/transactions/locations are already seeded
        case_count = db.query(Case).count()
        if case_count > 0:
            print(f"[2/4] Database already populated with {case_count} cases. Skipping CSV ingestion.")
            return

        print("[2/4] Loading CSV datasets...")
        cases_df, accounts_df, tx_df, locs_df, withs_df = load_raw_data()

        # Seed Locations
        print("[3/4] Seeding 12 Candidate ATM Clusters...")
        locations = []
        for _, row in locs_df.iterrows():
            locations.append(Location(
                location_id=str(row["location_id"]),
                city=str(row["city"]),
                district=str(row["district"]),
                state=str(row["state"]),
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                atm_cluster_name=str(row["atm_cluster_name"])
            ))
        db.add_all(locations)
        db.commit()

        # Seed Cases
        print(f"[4/4] Seeding {len(cases_df)} Cases, {len(accounts_df)} Accounts, and {len(tx_df)} Transactions...")
        investigator = db.query(User).filter(User.username == "officer_sharma").first()
        inv_id = investigator.id if investigator else None

        case_objs = []
        for _, row in cases_df.iterrows():
            case_objs.append(Case(
                case_id=str(row["case_id"]),
                fraud_type=str(row["fraud_type"]),
                complaint_time=pd.to_datetime(row["complaint_time"]).to_pydatetime(),
                amount=float(row["amount"]),
                victim_region=str(row["victim_region"]),
                status=str(row.get("status", "ACTIVE")),
                assigned_officer_id=inv_id
            ))
        db.add_all(case_objs)
        db.commit()

        # Bulk insert Accounts
        acc_objs = []
        for _, row in accounts_df.iterrows():
            acc_objs.append(Account(
                account_id=str(row["account_id"]),
                case_id=str(row["case_id"]),
                account_type=str(row["account_type"]),
                region=str(row["region"]),
                account_age_days=int(row.get("account_age_days", 0))
            ))
        db.bulk_save_objects(acc_objs)
        db.commit()

        # Bulk insert Transactions
        tx_objs = []
        for _, row in tx_df.iterrows():
            tx_objs.append(Transaction(
                transaction_id=str(row["transaction_id"]),
                case_id=str(row["case_id"]),
                sender_account=str(row["sender_account"]),
                receiver_account=str(row["receiver_account"]),
                amount=float(row["amount"]),
                timestamp=pd.to_datetime(row["timestamp"]).to_pydatetime(),
                transaction_type=str(row.get("transaction_type", "Transfer"))
            ))
        db.bulk_save_objects(tx_objs)
        db.commit()

        # Seed 2 Initial Sample Alerts for demo
        sample_alerts = [
            Alert(
                case_id="C0001",
                location_id="L001",
                city="Bengaluru",
                atm_cluster_name="Cluster A",
                risk_score=0.1173,
                risk_tier="HIGH",
                estimated_time_window="06:00 - 07:10",
                status="DISPATCHED",
                notes="High probability ATM cash-out predicted based on multi-hop transfer velocity."
            ),
            Alert(
                case_id="C0002",
                location_id="L005",
                city="Kochi",
                atm_cluster_name="Cluster E",
                risk_score=0.1042,
                risk_tier="HIGH",
                estimated_time_window="02:15 - 03:25",
                status="ACKNOWLEDGED",
                notes="Field unit notified for targeted surveillance."
            )
        ]
        db.add_all(sample_alerts)
        db.commit()

        print("\nDATABASE SEEDING COMPLETE!")
        print(f"  Cases:        {db.query(Case).count()}")
        print(f"  Accounts:     {db.query(Account).count()}")
        print(f"  Transactions: {db.query(Transaction).count()}")
        print(f"  Locations:    {db.query(Location).count()}")
        print(f"  Alerts:       {db.query(Alert).count()}")
        print(f"  Users:        {db.query(User).count()}")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
