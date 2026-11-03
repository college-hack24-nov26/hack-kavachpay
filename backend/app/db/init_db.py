import json
from datetime import datetime, timedelta
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.models.user import User
from backend.app.models.credential import Credential
from backend.app.models.activity import Activity
from backend.app.core.security import hash_password

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if user already exists
        demo_user = db.query(User).filter(User.email == "user@kavachsetu.demo").first()
        if not demo_user:
            demo_user = User(
                user_code="KVS-001",
                full_name="Aarav Mehta",
                email="user@kavachsetu.demo",
                hashed_password=hash_password("GhostProtocol@2026"),
                phone_masked="+91 ••••• ••421"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

            # Seed the 3 required synthetic credentials
            c1 = Credential(
                id="KVS-ID-001",
                user_id=demo_user.id,
                category="IDENTITY",
                title="Identity Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 1, 15, 10, 0, 0),
                expiry_date=datetime(2031, 1, 14, 23, 59, 59),
                is_synthetic=True,
                verification_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                metadata_json=json.dumps({
                    "document_type": "Synthetic National Digital ID",
                    "holder_pseudonym": "AARAV-M-***4",
                    "issuing_jurisdiction": "IN-Demo-Trust-Framework",
                    "privacy_mode": "Decoupled Identifier",
                    "tamper_evidence": "SHA-256 Digest Verified"
                })
            )

            c2 = Credential(
                id="KVS-KYC-001",
                user_id=demo_user.id,
                category="KYC",
                title="KYC Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 2, 10, 14, 30, 0),
                expiry_date=datetime(2027, 2, 9, 23, 59, 59),
                is_synthetic=True,
                verification_hash="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
                metadata_json=json.dumps({
                    "compliance_standard": "KYC Equivalent (Synthetic Sandbox)",
                    "jurisdiction_region": "Western Region (India)",
                    "verification_method": "Biometric Hash Attestation",
                    "pii_leakage_risk": "0% (Raw documents never stored on server)"
                })
            )

            c3 = Credential(
                id="KVS-INC-001",
                user_id=demo_user.id,
                category="INCOME",
                title="Income Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 3, 1, 9, 15, 0),
                expiry_date=datetime(2026, 9, 1, 23, 59, 59),
                is_synthetic=True,
                verification_hash="ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
                metadata_json=json.dumps({
                    "synthetic_monthly_income": "₹35,000",
                    "predicate_test_satisfied": "Monthly Income > ₹25,000",
                    "currency": "INR",
                    "raw_bank_statement_shared": "No (Decoupled proof model)",
                    "verification_cycle": "Q1 2026 Self-Custody Vault"
                })
            )

            db.add_all([c1, c2, c3])

            # Seed initial activity
            a1 = Activity(
                user_id=demo_user.id,
                action_type="VAULT_INITIALIZED",
                title="Ghost-Vault Initialized",
                description="Secure vault created with 3 synthetic credentials",
                timestamp=datetime.utcnow() - timedelta(hours=2)
            )
            db.add(a1)
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized and demo data seeded successfully.")

