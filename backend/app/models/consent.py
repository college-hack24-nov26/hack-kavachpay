from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from backend.app.db.session import Base

class ConsentRequest(Base):
    __tablename__ = "consent_requests"

    id = Column(String(50), primary_key=True, index=True) # e.g. REQ-8821
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    institution_name = Column(String(120), nullable=False) # e.g. HDFC Bank Ltd, National Scholarship Portal
    institution_category = Column(String(50), default="Banking & Lending")
    purpose = Column(Text, nullable=False) # e.g. "Home Loan Underwriting Predicate Verification"
    requested_credential_type = Column(String(60), nullable=False) # e.g. INCOME, IDENTITY, KYC
    requested_claim = Column(String(200), nullable=False) # e.g. "Monthly Income > ₹25,000"
    status = Column(String(30), nullable=False, default="PENDING") # PENDING, ACTIVE, REJECTED, REVOKED, EXPIRED
    duration_hours = Column(Integer, default=24)
    expires_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    fabric_tx_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
