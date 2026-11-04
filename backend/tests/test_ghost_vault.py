import io
import json
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.init_db import init_db

# Ensure clean DB setup
init_db()
client = TestClient(app)

def test_full_ghost_vault_lifecycle():
    print("\n--- 1. Testing Health & Public Static Client ---")
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

    resp = client.get("/")
    assert resp.status_code == 200

    print("--- 2. Testing Authentication ---")
    login_resp = client.post("/api/v1/auth/login", json={
        "email": "user@kavachsetu.demo",
        "password": "GhostProtocol@2026"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("--- 3. Testing Dashboard Overview ---")
    dash_resp = client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()
    assert dash_data["total_documents"] >= 4
    assert dash_data["verified_credentials"] >= 3
    assert dash_data["vault_status"].startswith("ACTIVE")

    print("--- 4. Testing Document Listing & Filtering ---")
    docs_resp = client.get("/api/v1/vault/documents", headers=headers)
    assert docs_resp.status_code == 200
    docs = docs_resp.json()
    assert len(docs) >= 4
    categories = [d["category"] for d in docs]
    assert "Aadhaar Card" in categories
    assert "PAN Card" in categories
    assert "Income Certificate" in categories

    print("--- 5. Testing Document OCR Pre-Analysis ---")
    sample_file = io.BytesIO(b"INCOME TAX DEPARTMENT - PERMANENT ACCOUNT NUMBER ABCDE1234F - AARAV MEHTA")
    analyze_resp = client.post(
        "/api/v1/vault/documents/analyze",
        headers=headers,
        files={"file": ("pan_scan.pdf", sample_file, "application/pdf")}
    )
    assert analyze_resp.status_code == 200
    an_data = analyze_resp.json()
    assert an_data["classified_category"] == "PAN Card"

    print("--- 6. Testing Document Upload with Encryption at Rest ---")
    import secrets
    test_passport_num = f"Z{secrets.token_hex(4).upper()}"
    new_doc_bytes = io.BytesIO(f"%PDF-1.4 SAMPLE PASSPORT SCAN FOR AARAV MEHTA - {test_passport_num}".encode())
    upload_resp = client.post(
        "/api/v1/vault/documents/upload",
        headers=headers,
        data={
            "category": "Passport",
            "title": "Republic of India Passport",
            "holder_name": "Aarav Mehta",
            "document_number": test_passport_num,
            "issue_date": "2020-03-12",
            "expiry_date": "2030-03-11"
        },
        files={"file": ("Aarav_Passport.pdf", new_doc_bytes, "application/pdf")}
    )
    assert upload_resp.status_code == 200
    uploaded_doc = upload_resp.json()
    doc_id = uploaded_doc["id"]
    assert "Passport" in uploaded_doc["title"]

    print("--- 7. Testing Duplicate Document Detection (409 Conflict) ---")
    dup_file = io.BytesIO(f"%PDF-1.4 SAMPLE PASSPORT SCAN FOR AARAV MEHTA - {test_passport_num}".encode())
    dup_resp = client.post(
        "/api/v1/vault/documents/upload",
        headers=headers,
        data={
            "category": "Passport",
            "title": "Duplicate Passport",
            "holder_name": "Aarav Mehta",
            "document_number": test_passport_num
        },
        files={"file": ("Aarav_Passport_dup.pdf", dup_file, "application/pdf")}
    )
    assert dup_resp.status_code == 409

    print("--- 8. Testing Secure Decrypted Document Download ---")
    dl_resp = client.get(f"/api/v1/vault/documents/{doc_id}/download", headers=headers)
    assert dl_resp.status_code == 200
    assert b"SAMPLE PASSPORT SCAN" in dl_resp.content

    print("--- 9. Testing Document Verification Simulation Workflow ---")
    # Verify the uploaded passport
    verif_resp = client.post(f"/api/v1/vault/documents/{doc_id}/verify-simulation", headers=headers)
    assert verif_resp.status_code == 200
    v_data = verif_resp.json()
    assert v_data["status"] == "VERIFIED"
    assert "credential_id" in v_data

    print("--- 10. Testing ZK Proof Studio: Age Range Proof Generation & Verification ---")
    zk_age_resp = client.post(
        "/api/v1/zk/generate",
        headers=headers,
        json={
            "credential_id": "KVS-ID-001",
            "claim_type": "AGE_RANGE_PROOF",
            "threshold_value": 18
        }
    )
    assert zk_age_resp.status_code == 200
    age_proof = zk_age_resp.json()
    proof_id = age_proof["id"]
    assert "Citizen age is at least 18 years" in age_proof["claim_statement"]

    # Verify proof via verification endpoint
    verify_resp = client.post(
        "/api/v1/zk/verify",
        headers=headers,
        json={"proof_id": proof_id}
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["is_valid"] is True
    assert "VERIFIED" in verify_resp.json()["explanation"]

    print("--- 11. Testing ZK Proof Studio: Income Predicate Proof ---")
    zk_inc_resp = client.post(
        "/api/v1/zk/generate",
        headers=headers,
        json={
            "credential_id": "KVS-INC-001",
            "claim_type": "INCOME_PREDICATE_PROOF",
            "threshold_value": 25000,
            "condition": "GREATER_THAN"
        }
    )
    assert zk_inc_resp.status_code == 200
    inc_proof = zk_inc_resp.json()
    inc_proof_id = inc_proof["id"]

    verify_inc = client.post(
        "/api/v1/zk/verify",
        headers=headers,
        json={"proof_id": inc_proof_id}
    )
    assert verify_inc.status_code == 200
    assert verify_inc.json()["is_valid"] is True

    print("--- 12. Testing Consent & Permission Management (Approve & Revoke) ---")
    consents_resp = client.get("/api/v1/consent/requests", headers=headers)
    assert consents_resp.status_code == 200
    consents = consents_resp.json()
    assert len(consents) >= 1

    pending_req = next((c for c in consents if c["status"] == "PENDING"), None)
    if not pending_req:
        create_req = client.post("/api/v1/consent/create-demo", headers=headers)
        assert create_req.status_code == 200
        pending_req = create_req.json()
    assert pending_req is not None
    req_id = pending_req["id"]

    # Approve consent
    appr_resp = client.post(
        f"/api/v1/consent/requests/{req_id}/action",
        headers=headers,
        json={"action": "APPROVE", "duration_hours": 48}
    )
    assert appr_resp.status_code == 200
    assert appr_resp.json()["status"] == "ACTIVE"

    # Revoke consent
    rev_resp = client.post(
        f"/api/v1/consent/requests/{req_id}/action",
        headers=headers,
        json={"action": "REVOKE"}
    )
    assert rev_resp.status_code == 200
    assert rev_resp.json()["status"] == "REVOKED"

    print("--- 13. Testing Secure Document Sharing & Verifier Public View ---")
    share_create = client.post(
        "/api/v1/share/create",
        headers=headers,
        json={
            "zk_proof_id": proof_id,
            "share_type": "ZK_PROOF",
            "title": "Proof of Age Verification",
            "purpose": "KYC Onboarding",
            "recipient_info": "Axis Bank",
            "expiry_hours": 24,
            "max_uses": 3
        }
    )
    assert share_create.status_code == 200
    share_data = share_create.json()
    share_token = share_data["token"]
    share_id = share_data["id"]

    # External verifier accesses the public view endpoint
    verifier_resp = client.get(f"/api/v1/share/view/{share_token}")
    assert verifier_resp.status_code == 200
    assert verifier_resp.json()["status"] == "AUTHORIZED_ACCESS"
    assert "proof_id" in verifier_resp.json()["payload"]

    # Revoke share link
    revoke_resp = client.post(f"/api/v1/share/links/{share_id}/revoke", headers=headers)
    assert revoke_resp.status_code == 200

    # Subsequent access should be blocked (403 Forbidden)
    blocked_resp = client.get(f"/api/v1/share/view/{share_token}")
    assert blocked_resp.status_code == 403

    print("--- 14. Testing Hyperledger Fabric Explorer & Cryptographic Hash Chain ---")
    exp_resp = client.get("/api/v1/blockchain/explorer", headers=headers)
    assert exp_resp.status_code == 200
    explorer = exp_resp.json()
    assert explorer["network"]["channel"] == "kavach-channel"
    assert len(explorer["recent_blocks"]) >= 1
    assert len(explorer["recent_transactions"]) >= 1

    chain_val = client.get("/api/v1/blockchain/verify-chain", headers=headers)
    assert chain_val.status_code == 200
    assert chain_val.json()["valid"] is True

    print("--- 15. Testing Notifications System ---")
    notif_resp = client.get("/api/v1/notifications", headers=headers)
    assert notif_resp.status_code == 200
    notifs = notif_resp.json()
    assert len(notifs) >= 1

    # Mark all read
    read_all_resp = client.post("/api/v1/notifications/read-all", headers=headers)
    assert read_all_resp.status_code == 200

    print("--- 16. Testing Encrypted Backup & Restore ---")
    backup_resp = client.post(
        "/api/v1/settings/backup/export",
        headers=headers,
        params={"passphrase": "GhostProtocol@2026"}
    )
    assert backup_resp.status_code == 200
    backup_data = backup_resp.json()
    assert "backup_archive" in backup_data
    archive = backup_data["backup_archive"]
    assert archive["cipher"] == "AES-256-GCM"

    # Restore from archive
    restore_resp = client.post(
        "/api/v1/settings/backup/restore",
        headers=headers,
        json={"backup_archive": archive, "passphrase": "GhostProtocol@2026"}
    )
    assert restore_resp.status_code == 200
    assert restore_resp.json()["status"] == "RESTORED_SUCCESSFULLY"

    print("\n>>> ALL 16 GHOST-VAULT PRODUCTION LIFECYCLE TESTS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    test_full_ghost_vault_lifecycle()
