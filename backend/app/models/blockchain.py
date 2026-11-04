from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from backend.app.db.session import Base

class BlockchainBlock(Base):
    __tablename__ = "blockchain_blocks"

    block_number = Column(Integer, primary_key=True)
    previous_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), nullable=False, unique=True, index=True)
    merkle_root = Column(String(64), nullable=False)
    channel_name = Column(String(50), default="kavach-channel")
    chaincode_id = Column(String(50), default="vault-audit-cc")
    tx_count = Column(Integer, default=0)
    endorsing_peer = Column(String(100), default="peer0.org1.kavachsetu.internal")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class BlockchainTransaction(Base):
    __tablename__ = "blockchain_transactions"

    tx_id = Column(String(64), primary_key=True, index=True) # e.g. TX-FABRIC-7B9A2F...
    block_number = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    action_type = Column(String(60), nullable=False, index=True)
    document_hash = Column(String(64), nullable=False, index=True)
    payload_summary = Column(Text, nullable=True) # JSON metadata
    status = Column(String(30), default="CONFIRMED")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
