from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserSummary"

class UserSummary(BaseModel):
    user_code: str
    full_name: str
    email: str
    phone_masked: str

class CredentialDetail(BaseModel):
    id: str
    category: str
    title: str
    issuer: str
    status: str
    issue_date: str
    expiry_date: str
    is_synthetic: bool
    verification_hash: Optional[str] = None
    safe_attributes: Dict[str, Any]
    privacy_notice: str

class CredentialListItem(BaseModel):
    id: str
    category: str
    title: str
    issuer: str
    status: str
    issue_date: str
    expiry_date: str
    is_synthetic: bool

class ActivityItem(BaseModel):
    id: int
    action_type: str
    title: str
    description: Optional[str]
    ip_masked: str
    device_info: str
    timestamp: str

class DashboardSummary(BaseModel):
    user: UserSummary
    total_credentials: int
    valid_credentials: int
    vault_status: str
    recent_credentials: List[CredentialListItem]
    recent_activities: List[ActivityItem]
    security_notice: str

class SecurityOverview(BaseModel):
    session_valid: bool
    password_hashing: str
    vault_storage_type: str
    encryption_algorithm: str
    active_tokens: int
    data_protection_mode: str
