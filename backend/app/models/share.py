from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from backend.app.db.session import Base

class ShareLink(Base):
    __tablename__ = "share_links"

    id = Column(String(50), primary_key=True, index=True) # e.g. SH-78210
    token = Column(String(80), unique=True, index=True, nullable=False) # random URL token
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String(50), ForeignKey("documents.id"), nullable=True)
    zk_proof_id = Column(String(60), ForeignKey("zk_proofs.id"), nullable=True)
    share_type = Column(String(40), nullable=False) # DOCUMENT, ZK_PROOF, SELECTIVE_DISCLOSURE
    title = Column(String(120), nullable=False)
    purpose = Column(String(200), nullable=False) # e.g. "Rental Verification"
    recipient_info = Column(String(150), default="Authorized Verifier")
    status = Column(String(30), default="ACTIVE") # ACTIVE, EXPIRED, REVOKED
    max_uses = Column(Integer, default=5)
    use_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=False)
    access_logs_json = Column(Text, default="[]") # List of access timestamps and IP addresses
    fabric_tx_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
