from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, BigInteger
from datetime import datetime
from backend.app.db.session import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(50), primary_key=True, index=True) # e.g. DOC-AADHAAR-001
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    category = Column(String(60), nullable=False, index=True) # Aadhaar Card, PAN Card, etc.
    title = Column(String(120), nullable=False)
    holder_name = Column(String(120), nullable=False)
    document_number_masked = Column(String(50), nullable=False) # e.g. XXXX-XXXX-8921
    document_number_hash = Column(String(64), nullable=True, index=True) # SHA-256 for duplicate detection
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True) # Nullable for non-expiring docs like Aadhaar/PAN
    file_name = Column(String(200), nullable=False)
    file_path = Column(String(300), nullable=False) # Encrypted file location on server
    file_size = Column(BigInteger, default=0)
    file_hash = Column(String(64), nullable=False, index=True) # SHA-256 of encrypted file
    mime_type = Column(String(50), default="application/pdf")
    verification_status = Column(String(40), nullable=False, default="UNVERIFIED") # UNVERIFIED, PENDING_VERIFICATION, DEMO_VERIFIED, ISSUER_VERIFIED, REJECTED
    rejection_reason = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(120), nullable=True)
    ocr_extracted_json = Column(Text, nullable=True)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
