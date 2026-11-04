from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from datetime import datetime
from backend.app.db.session import Base

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(String(50), primary_key=True, index=True) # e.g. KVS-ID-001, KVS-KYC-001, KVS-INC-001
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=True, index=True)
    category = Column(String(50), nullable=False) # IDENTITY, KYC, INCOME, EDUCATION, RESIDENCE, BANKING
    title = Column(String(100), nullable=False) # Identity Credential, KYC Credential, Income Credential
    issuer = Column(String(120), nullable=False, default="KavachSetu Demo Issuer")
    status = Column(String(30), nullable=False, default="VALID") # VALID, EXPIRING_SOON, REVOKED
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    is_synthetic = Column(Boolean, default=True) # Strictly identify synthetic demo data
    verification_hash = Column(String(64), nullable=True) # SHA-256 integrity hash
    fabric_tx_id = Column(String(64), nullable=True) # On-chain transaction reference
    metadata_json = Column(Text, nullable=True) # JSON encoded safe attributes for zero-exposure proofing
    created_at = Column(DateTime, default=datetime.utcnow)
