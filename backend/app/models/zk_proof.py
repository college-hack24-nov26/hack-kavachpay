from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from datetime import datetime
from backend.app.db.session import Base

class ZkProof(Base):
    __tablename__ = "zk_proofs"

    id = Column(String(60), primary_key=True, index=True) # e.g. ZKP-AGE-XXXXX
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    credential_id = Column(String(50), ForeignKey("credentials.id"), nullable=True, index=True)
    claim_type = Column(String(60), nullable=False) # AGE_RANGE_PROOF, INCOME_PREDICATE_PROOF, CREDENTIAL_POSSESSION
    claim_statement = Column(String(200), nullable=False)
    commitment = Column(Text, nullable=False)
    public_inputs_json = Column(Text, nullable=False)
    proof_data_json = Column(Text, nullable=False)
    verification_status = Column(String(30), default="VERIFIED_VALID") # VERIFIED_VALID, FAILED
    verified_at = Column(DateTime, default=datetime.utcnow)
    fabric_tx_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
