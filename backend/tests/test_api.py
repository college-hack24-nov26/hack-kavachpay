from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db

# Ensure clean DB setup
init_db()
client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_static_index_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "KavachSetu – The Ghost Protocol" in response.text
    assert "Prove, Don't Share." in response.text

def test_login_invalid():
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@kavachsetu.demo",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_full_user_journey():
    # 1. Login with demo user
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user@kavachsetu.demo",
        "password": "GhostProtocol@2026"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    token = login_data["access_token"]
    assert token is not None
    assert login_data["user"]["user_code"] == "KVS-001"
    assert login_data["user"]["full_name"] == "Aarav Mehta"

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Me
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "user@kavachsetu.demo"

    # 3. Dashboard Summary
    dash_resp = client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_credentials"] == 3
    assert dash_data["valid_credentials"] == 3
    assert len(dash_data["recent_credentials"]) == 3

    # 4. Ghost-Vault Listing
    vault_resp = client.get("/api/v1/vault/credentials", headers=headers)
    assert vault_resp.status_code == 200
    creds = vault_resp.json()
    assert len(creds) == 3
    cred_ids = [c["id"] for c in creds]
    assert "KVS-ID-001" in cred_ids
    assert "KVS-KYC-001" in cred_ids
    assert "KVS-INC-001" in cred_ids

    # 5. Tap Income Credential (KVS-INC-001)
    inc_resp = client.get("/api/v1/vault/credentials/KVS-INC-001", headers=headers)
    assert inc_resp.status_code == 200
    inc_data = inc_resp.json()
    assert inc_data["id"] == "KVS-INC-001"
    assert inc_data["category"] == "INCOME"
    assert inc_data["issuer"] == "KavachSetu Demo Issuer"
    assert inc_data["is_synthetic"] is True
    assert "₹35,000" in str(inc_data["safe_attributes"])

    # 6. Check Activity Log
    # Should contain USER_LOGIN and VIEW_CREDENTIAL
    act_resp = client.get("/api/v1/activity", headers=headers)
    assert act_resp.status_code == 200
    acts = act_resp.json()
    assert len(acts) >= 2
    action_types = [a["action_type"] for a in acts]
    assert "LOGIN" in action_types
    assert "VIEW_CREDENTIAL" in action_types

    # 7. Check Security Overview
    sec_resp = client.get("/api/v1/settings/security-overview", headers=headers)
    assert sec_resp.status_code == 200
    sec_data = sec_resp.json()
    assert sec_data["session_valid"] is True
    assert "Bcrypt" in sec_data["password_hashing"]

    # 8. Logout
    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

if __name__ == "__main__":
    test_health_check()
    test_static_index_html()
    test_login_invalid()
    test_full_user_journey()
    print("All backend tests PASSED successfully!")
