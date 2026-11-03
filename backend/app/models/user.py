from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from backend.app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_code = Column(String(50), unique=True, index=True, nullable=False) # e.g. KVS-001
    full_name = Column(String(100), nullable=False) # e.g. Aarav Mehta
    email = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_masked = Column(String(20), default="+91 ••••• ••421")
    created_at = Column(DateTime, default=datetime.utcnow)

