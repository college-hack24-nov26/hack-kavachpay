from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime
from backend.app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    message = Column(String(255), nullable=False)
    category = Column(String(50), default="INFO") # ACCESS_REQUEST, VERIFICATION, EXPIRATION, SECURITY, REVOCATION
    is_read = Column(Boolean, default=False)
    action_url = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
