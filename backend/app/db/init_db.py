import os
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.credential import Credential
from backend.app.models.zk_proof import ZkProof
from backend.app.models.consent import ConsentRequest
from backend.app.models.blockchain import BlockchainBlock, BlockchainTransaction
from backend.app.models.notification import Notification
from backend.app.models.activity import Activity
from backend.app.core.security import hash_password
from backend.app.core.encryption import VaultEncryption
from backend.app.core.fabric_ledger import FabricLedgerService

# Ensure documents storage directory exists
STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "documents")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _write_encrypted_demo_file(doc_id: str, sample_text: str):
    raw_bytes = sample_text.encode("utf-8")
    enc_bytes = VaultEncryption.encrypt_document(raw_bytes)
    file_path = os.path.join(STORAGE_DIR, f"{doc_id}.enc")
    with open(file_path, "wb") as f:
        f.write(enc_bytes)
    return file_path, hashlib.sha256(raw_bytes).hexdigest(), len(raw_bytes)


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
                phone_masked="+91 ••••• ••421",
                date_of_birth="1998-05-14",
                address_masked="Bandra West, Mumbai, MH - 400050",
                recovery_key_hash=hashlib.sha256(b"kavachsetu demo 12 word mnemonic recovery seed 2026").hexdigest(),
                two_factor_enabled=True,
                privacy_auto_masking=True,
                session_timeout_minutes=60
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)

        # Initialize Fabric Genesis Block if empty
        genesis = db.query(BlockchainBlock).filter(BlockchainBlock.block_number == 0).first()
        if not genesis:
            genesis = BlockchainBlock(
                block_number=0,
                previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
                block_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                merkle_root="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                channel_name="kavach-channel",
                chaincode_id="vault-audit-cc",
                tx_count=1,
                endorsing_peer="peer0.org1.kavachsetu.internal",
                timestamp=datetime.utcnow() - timedelta(days=20)
            )
            db.add(genesis)
            db.commit()

        # Seed Documents if empty
        existing_doc = db.query(Document).filter(Document.user_id == demo_user.id).first()
        if not existing_doc:
            # 1. Aadhaar Card
            f1_path, f1_hash, f1_size = _write_encrypted_demo_file("DOC-AADHAAR-001", "KAVACHSETU SYNTHETIC AADHAAR ID CARD - AARAV MEHTA - XXXX-XXXX-8921")
            d1 = Document(
                id="DOC-AADHAAR-001",
                user_id=demo_user.id,
                category="Aadhaar Card",
                title="National Identity Card (Aadhaar)",
                holder_name="Aarav Mehta",
                document_number_masked="XXXX-XXXX-8921",
                document_number_hash=hashlib.sha256(b"8921").hexdigest(),
                issue_date=datetime(2022, 4, 10),
                expiry_date=None,
                file_name="Aadhaar_Aarav_Mehta.pdf",
                file_path=f1_path,
                file_size=f1_size,
                file_hash=f1_hash,
                mime_type="application/pdf",
                verification_status="ISSUER_VERIFIED",
                verified_at=datetime(2022, 4, 11),
                verified_by="UIDAI Decoupled Trust Node",
                is_synthetic=True,
                ocr_extracted_json=json.dumps({
                    "holder_name": "Aarav Mehta",
                    "document_number": "XXXX-XXXX-8921",
                    "issuer": "Unique Identification Authority of India (UIDAI)",
                    "dob": "1998-05-14",
                    "gender": "Male"
                })
            )

            # 2. PAN Card
            f2_path, f2_hash, f2_size = _write_encrypted_demo_file("DOC-PAN-001", "KAVACHSETU SYNTHETIC PAN CARD - AARAV MEHTA - ABCDE1234F")
            d2 = Document(
                id="DOC-PAN-001",
                user_id=demo_user.id,
                category="PAN Card",
                title="Permanent Account Number (PAN)",
                holder_name="Aarav Mehta",
                document_number_masked="AB•••34F",
                document_number_hash=hashlib.sha256(b"ABCDE1234F").hexdigest(),
                issue_date=datetime(2021, 8, 19),
                expiry_date=None,
                file_name="PAN_Card_Aarav.pdf",
                file_path=f2_path,
                file_size=f2_size,
                file_hash=f2_hash,
                mime_type="application/pdf",
                verification_status="ISSUER_VERIFIED",
                verified_at=datetime(2021, 8, 20),
                verified_by="Income Tax Dept Gateway",
                is_synthetic=True,
                ocr_extracted_json=json.dumps({
                    "holder_name": "Aarav Mehta",
                    "document_number": "ABCDE1234F",
                    "issuer": "Income Tax Department of India",
                    "tax_status": "Individual Resident"
                })
            )

            # 3. Income Certificate
            f3_path, f3_hash, f3_size = _write_encrypted_demo_file("DOC-INC-001", "KAVACHSETU SYNTHETIC REVENUE INCOME CERTIFICATE - ₹35,000/MONTH")
            d3 = Document(
                id="DOC-INC-001",
                user_id=demo_user.id,
                category="Income Certificate",
                title="Annual Revenue Income Certificate",
                holder_name="Aarav Mehta",
                document_number_masked="INC/2026/••••",
                document_number_hash=hashlib.sha256(b"INC/2026/9012").hexdigest(),
                issue_date=datetime(2026, 1, 10),
                expiry_date=datetime(2027, 1, 9),
                file_name="Income_Certificate_2026.pdf",
                file_path=f3_path,
                file_size=f3_size,
                file_hash=f3_hash,
                mime_type="application/pdf",
                verification_status="ISSUER_VERIFIED",
                verified_at=datetime(2026, 1, 12),
                verified_by="State Revenue Department Node",
                is_synthetic=True,
                ocr_extracted_json=json.dumps({
                    "holder_name": "Aarav Mehta",
                    "annual_income": "₹4,20,000",
                    "monthly_income": "₹35,000",
                    "issuer": "Revenue Dept, Govt of Maharashtra"
                })
            )

            # 4. Driving Licence (Pending Demo Verification)
            f4_path, f4_hash, f4_size = _write_encrypted_demo_file("DOC-DL-001", "KAVACHSETU SYNTHETIC DRIVING LICENCE - MH02-20210049214")
            d4 = Document(
                id="DOC-DL-001",
                user_id=demo_user.id,
                category="Driving Licence",
                title="Motor Driving Licence (LMV)",
                holder_name="Aarav Mehta",
                document_number_masked="MH02••••••••214",
                document_number_hash=hashlib.sha256(b"MH02-20210049214").hexdigest(),
                issue_date=datetime(2021, 11, 5),
                expiry_date=datetime(2041, 11, 4),
                file_name="Driving_Licence_Scan.jpg",
                file_path=f4_path,
                file_size=f4_size,
                file_hash=f4_hash,
                mime_type="image/jpeg",
                verification_status="PENDING_VERIFICATION",
                is_synthetic=True,
                ocr_extracted_json=json.dumps({
                    "holder_name": "Aarav Mehta",
                    "vehicle_class": "LMV (Light Motor Vehicle)",
                    "issuer": "Regional Transport Office (RTO)"
                })
            )

            db.add_all([d1, d2, d3, d4])
            db.commit()

        # Seed Credentials if empty
        existing_creds = db.query(Credential).filter(Credential.user_id == demo_user.id).all()
        if not existing_creds:
            c1 = Credential(
                id="KVS-ID-001",
                user_id=demo_user.id,
                document_id="DOC-AADHAAR-001",
                category="IDENTITY",
                title="Identity Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 1, 15, 10, 0, 0),
                expiry_date=datetime(2031, 1, 14, 23, 59, 59),
                is_synthetic=True,
                verification_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                fabric_tx_id="TX-FABRIC-7A9B2C11",
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
                document_id="DOC-PAN-001",
                category="KYC",
                title="KYC Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 2, 10, 14, 30, 0),
                expiry_date=datetime(2027, 2, 9, 23, 59, 59),
                is_synthetic=True,
                verification_hash="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
                fabric_tx_id="TX-FABRIC-8F3C5E90",
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
                document_id="DOC-INC-001",
                category="INCOME",
                title="Income Credential",
                issuer="KavachSetu Demo Issuer",
                status="VALID",
                issue_date=datetime(2026, 3, 1, 9, 15, 0),
                expiry_date=datetime(2026, 9, 1, 23, 59, 59),
                is_synthetic=True,
                verification_hash="ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d",
                fabric_tx_id="TX-FABRIC-9E2A10D4",
                metadata_json=json.dumps({
                    "synthetic_monthly_income": "₹35,000",
                    "predicate_test_satisfied": "Monthly Income > ₹25,000",
                    "currency": "INR",
                    "raw_bank_statement_shared": "No (Decoupled proof model)",
                    "verification_cycle": "Q1 2026 Self-Custody Vault"
                })
            )
            db.add_all([c1, c2, c3])
            db.commit()

        # Seed Consent Requests
        existing_consents = db.query(ConsentRequest).filter(ConsentRequest.user_id == demo_user.id).all()
        if not existing_consents:
            req1 = ConsentRequest(
                id="REQ-8821",
                user_id=demo_user.id,
                institution_name="HDFC Bank Ltd",
                institution_category="Retail & Mortgage Banking",
                purpose="Home Loan Underwriting Predicate Verification",
                requested_credential_type="INCOME",
                requested_claim="Verify Monthly Income >= ₹25,000",
                status="PENDING",
                duration_hours=24,
                created_at=datetime.utcnow() - timedelta(hours=3)
            )

            req2 = ConsentRequest(
                id="REQ-7104",
                user_id=demo_user.id,
                institution_name="National Scholarship Portal",
                institution_category="Government Education Grants",
                purpose="Merit-cum-Means Scholarship Grant Eligibility",
                requested_credential_type="INCOME",
                requested_claim="Verify Annual Income <= ₹8,00,000",
                status="ACTIVE",
                duration_hours=168,
                expires_at=datetime.utcnow() + timedelta(days=6),
                approved_at=datetime.utcnow() - timedelta(hours=12),
                fabric_tx_id="TX-FABRIC-7104BFT",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
            db.add_all([req1, req2])
            db.commit()

        # Seed Notifications
        existing_notifs = db.query(Notification).filter(Notification.user_id == demo_user.id).all()
        if not existing_notifs:
            n1 = Notification(
                user_id=demo_user.id,
                title="New Consent Request: HDFC Bank Ltd",
                message="HDFC Bank has requested zero-knowledge verification for your Monthly Income predicate (> ₹25,000).",
                category="ACCESS_REQUEST",
                is_read=False,
                action_url="consent"
            )
            n2 = Notification(
                user_id=demo_user.id,
                title="Ghost-Vault Encryption Activated",
                message="AES-256-GCM hardware-isolated encryption key generated and sealed.",
                category="SECURITY",
                is_read=False,
                action_url="settings"
            )
            n3 = Notification(
                user_id=demo_user.id,
                title="Action Required: Driving Licence",
                message="Your uploaded Driving Licence (DOC-DL-001) is pending verification.",
                category="VERIFICATION",
                is_read=True,
                action_url="verification"
            )
            db.add_all([n1, n2, n3])
            db.commit()

        # Seed Activity if empty
        existing_acts = db.query(Activity).filter(Activity.user_id == demo_user.id).all()
        if not existing_acts:
            a1 = Activity(
                user_id=demo_user.id,
                action_type="VAULT_INITIALIZED",
                title="Ghost-Vault Initialized",
                description="AES-256-GCM secure vault initialized with 4 documents and 3 verified credentials.",
                fabric_tx_id="TX-FABRIC-INIT-001",
                timestamp=datetime.utcnow() - timedelta(days=2)
            )
            db.add(a1)
            db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized, schema migrated, and production demo state seeded.")
