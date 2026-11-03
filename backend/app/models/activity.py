from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from backend.app.db.session import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(String(50), nullable=False) # LOGIN, VIEW_CREDENTIAL, LOGOUT, VAULT_ACCESS
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    ip_masked = Column(String(50), default="127.0.0.1 (Local Session)")
    device_info = Column(String(100), default="KavachSetu Secure Client")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

