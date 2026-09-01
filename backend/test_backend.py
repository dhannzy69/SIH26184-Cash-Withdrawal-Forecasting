"""
backend/test_backend.py
Automated end-to-end integration test suite for the FastAPI backend.
Tests Auth, Case CRUD, ML Prediction, SHAP Explainability, Transaction Stream, and Alerts.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_end_to_end_backend():
    print("=" * 70)
    print("RUNNING BACKEND INTEGRATION TEST SUITE")
    print("=" * 70)

    # 1. Health & Root Info
    print("\n[1] Testing Root & Health Check...")
    r_root = client.get("/")
    assert r_root.status_code == 200
    print("  Root Service Info:", r_root.json()["service"])

    r_health = client.get("/health")
    assert r_health.status_code == 200
    print("  Health Status:", r_health.json()["status"])

    # 2. Authentication Flow
    print("\n[2] Testing Authentication & JWT Flow...")
    # Register new investigator
    reg_payload = {
        "username": "officer_patel",
        "password": "securepassword123",
        "full_name": "Inspector Neha Patel",
        "badge_number": "CYBER-999",
        "role": "INVESTIGATOR"
    }
    r_reg = client.post("/api/auth/register", json=reg_payload)
    if r_reg.status_code == 201:
        print("  Officer Registered:", r_reg.json()["username"])
    else:
        print("  Officer already exists, proceeding to login...")

    # Login
    login_payload = {
        "username": "officer_patel",
        "password": "securepassword123"
    }
    r_login = client.post("/api/auth/login/json", json=login_payload)
    assert r_login.status_code == 200
    token_data = r_login.json()
    token = token_data["access_token"]
    print("  JWT Token Generated:", token[:30] + "...")

    # Test /api/auth/me with bearer token
    r_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r_me.status_code == 200
    print("  Authenticated Officer Profile:", r_me.json()["full_name"], f"({r_me.json()['role']})")

    # 3. Case Management
    print("\n[3] Testing Case Management Endpoints...")
    r_cases = client.get("/api/cases?limit=5")
    assert r_cases.status_code == 200
    cases_list = r_cases.json()
    print(f"  Retrieved {len(cases_list)} sample cases. First: {cases_list[0]['case_id']} ({cases_list[0]['fraud_type']})")

    # Detailed dossier
    r_dossier = client.get("/api/cases/C0001")
    assert r_dossier.status_code == 200
    dossier = r_dossier.json()
    print(f"  Case C0001 Dossier: {len(dossier['accounts'])} Accounts, {len(dossier['transactions'])} Transactions")

    # 4. ML Prediction Endpoint
    print("\n[4] Testing ML Location Forecasting Endpoint...")
    r_pred = client.get("/api/predictions/C0001")
    assert r_pred.status_code == 200
    pred = r_pred.json()
    print(f"  Forecast for C0001: Window = {pred['estimated_cashout_time_window']}")
    print(f"  Top Candidate: Rank {pred['top_1'][0]['rank']} - {pred['top_1'][0]['city']} ({pred['top_1'][0]['atm_cluster_name']}) | Score: {pred['top_1'][0]['score']} | Risk: {pred['top_1'][0]['risk']}")

    # 5. SHAP Explainability Endpoint
    print("\n[5] Testing SHAP Explainability Endpoint...")
    r_explain = client.get("/api/predictions/C0001/explain?rank=1")
    assert r_explain.status_code == 200
    expl = r_explain.json()
    print(f"  Explanation for {expl['city']}: Method = {expl['explanation_method']}")
    print("  Top Factor:", expl["contributing_factors"][0]["feature_description"], f"(Attribution: {expl['contributing_factors'][0]['attribution_score']})")

    # 6. Live Transaction Stream Ingestion & Auto-Alerting
    print("\n[6] Testing Real-Time Transaction Ingestion & Alerting...")
    tx_stream_payload = {
        "case_id": "C0001",
        "sender_account": "A0001_5",
        "receiver_account": "A0001_LIVE_MULE",
        "receiver_region": "Mumbai",
        "amount": 28500,
        "timestamp": "2026-06-13 05:48:00",
        "transaction_type": "Transfer"
    }
    r_tx = client.post("/api/transactions", json=tx_stream_payload)
    assert r_tx.status_code == 201
    tx_res = r_tx.json()
    print("  Transaction Stream Ingested:", tx_res["transaction_id"])
    print("  Live Updated Time Window:", tx_res["live_prediction_summary"]["estimated_cashout_time_window"])
    if tx_res.get("surveillance_alert"):
        print("  Surveillance Alert Generated:", tx_res["surveillance_alert"]["target_city"], f"(Risk Score: {tx_res['surveillance_alert']['risk_score']})")

    # 7. Surveillance Alerts Management
    print("\n[7] Testing Surveillance Alerts Management...")
    r_alerts = client.get("/api/alerts")
    assert r_alerts.status_code == 200
    alerts = r_alerts.json()
    print(f"  Total Active Alerts: {len(alerts)}")
    first_alert = alerts[0]
    print(f"  First Alert #{first_alert['id']}: Case {first_alert['case_id']} -> {first_alert['city']} ({first_alert['risk_tier']}) - Status: {first_alert['status']}")

    # Acknowledge alert
    r_ack = client.patch(f"/api/alerts/{first_alert['id']}/status", json={"status": "ACKNOWLEDGED", "notes": "Patrol dispatched to ATM cluster"})
    assert r_ack.status_code == 200
    print(f"  Alert #{first_alert['id']} Updated to: {r_ack.json()['status']}")

    print("\n" + "=" * 70)
    print("ALL 7 BACKEND INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    test_end_to_end_backend()
