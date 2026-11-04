from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. KVS-001
    full_name = Column(String(100), nullable=False) # e.g. Aarav Mehta
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_masked = Column(String(30), default="+91 ••••• ••421")
    date_of_birth = Column(String(20), default="1998-05-14") # Stored securely
    address_masked = Column(String(100), default="Bandra West, Mumbai, MH - 400050")
    recovery_key_hash = Column(String(64), nullable=True) # SHA-256 of 12-word recovery mnemonic
    two_factor_enabled = Column(Boolean, default=False)
    privacy_auto_masking = Column(Boolean, default=True)
    session_timeout_minutes = Column(Integer, default=60)
    created_at = Column(DateTime, default=datetime.utcnow)
