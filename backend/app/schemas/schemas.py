from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Auth & User ---
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
    date_of_birth: Optional[str] = "1998-05-14"
    address_masked: Optional[str] = "Bandra West, Mumbai, MH - 400050"
    two_factor_enabled: Optional[bool] = False
    profile_completion_percentage: Optional[int] = 85

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone_masked: Optional[str] = None
    date_of_birth: Optional[str] = None
    address_masked: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

# --- Documents ---
class DocumentCreateRequest(BaseModel):
    category: str
    title: str
    holder_name: str
    document_number: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    issuer: Optional[str] = "Authorized Issuer"
    file_content_b64: Optional[str] = None # Base64 encoded file payload
    file_name: Optional[str] = "document.pdf"
    mime_type: Optional[str] = "application/pdf"

class DocumentUpdateRequest(BaseModel):
    title: Optional[str] = None
    holder_name: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None

class DocumentListItem(BaseModel):
    id: str
    category: str
    title: str
    holder_name: str
    document_number_masked: str
    issue_date: Optional[str]
    expiry_date: Optional[str]
    file_name: str
    file_size: int
    file_hash: str
    verification_status: str # UNVERIFIED, PENDING_VERIFICATION, DEMO_VERIFIED, ISSUER_VERIFIED, REJECTED
    rejection_reason: Optional[str] = None
    is_expired: bool = False
    is_expiring_soon: bool = False
    created_at: str

class DocumentDetail(DocumentListItem):
    verified_at: Optional[str] = None
    verified_by: Optional[str] = None
    ocr_extracted_fields: Optional[Dict[str, Any]] = None
    fabric_tx_id: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None

# --- Credentials ---
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
    fabric_tx_id: Optional[str] = None
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

# --- ZK Proof Studio ---
class ZkProofGenerateRequest(BaseModel):
    credential_id: str
    claim_type: str # AGE_RANGE_PROOF, INCOME_PREDICATE_PROOF, CREDENTIAL_POSSESSION
    threshold_value: Optional[int] = None
    condition: Optional[str] = "GREATER_THAN" # GREATER_THAN or LESS_THAN

class ZkProofVerifyRequest(BaseModel):
    proof_id: Optional[str] = None
    proof_object: Optional[Dict[str, Any]] = None

class ZkProofItem(BaseModel):
    id: str
    credential_id: Optional[str]
    claim_type: str
    claim_statement: str
    commitment: str
    verification_status: str
    verified_at: str
    created_at: str
    fabric_tx_id: Optional[str] = None

class ZkProofDetail(ZkProofItem):
    public_inputs: Dict[str, Any]
    proof_data: Dict[str, Any]

# --- Consent & Permissions ---
class ConsentRequestItem(BaseModel):
    id: str
    institution_name: str
    institution_category: str
    purpose: str
    requested_credential_type: str
    requested_claim: str
    status: str # PENDING, ACTIVE, REJECTED, REVOKED, EXPIRED
    duration_hours: int
    expires_at: Optional[str]
    approved_at: Optional[str]
    revoked_at: Optional[str]
    created_at: str
    fabric_tx_id: Optional[str]

class ConsentActionRequest(BaseModel):
    action: str # APPROVE, REJECT, REVOKE
    duration_hours: Optional[int] = 24

# --- Secure Sharing ---
class ShareCreateRequest(BaseModel):
    document_id: Optional[str] = None
    zk_proof_id: Optional[str] = None
    share_type: str # DOCUMENT, ZK_PROOF, SELECTIVE_DISCLOSURE
    title: str
    purpose: str
    recipient_info: Optional[str] = "Financial Institution"
    expiry_hours: Optional[int] = 24
    max_uses: Optional[int] = 5

class ShareLinkItem(BaseModel):
    id: str
    token: str
    share_url: str
    title: str
    purpose: str
    share_type: str
    recipient_info: str
    status: str
    use_count: int
    max_uses: int
    expires_at: str
    created_at: str
    qr_svg: Optional[str] = None

# --- Blockchain Audit Explorer ---
class BlockItem(BaseModel):
    block_number: int
    block_hash: str
    previous_hash: str
    merkle_root: str
    tx_count: int
    channel_name: str
    chaincode_id: str
    endorsing_peer: str
    timestamp: str

class TransactionItem(BaseModel):
    tx_id: str
    block_number: int
    action_type: str
    document_hash: str
    title: str
    institution: str
    status: str
    timestamp: str

class BlockchainOverviewResponse(BaseModel):
    network: Dict[str, Any]
    recent_blocks: List[BlockItem]
    recent_transactions: List[TransactionItem]

# --- Notifications ---
class NotificationItem(BaseModel):
    id: int
    title: str
    message: str
    category: str
    is_read: bool
    action_url: Optional[str]
    created_at: str

# --- Activity & Dashboard ---
class ActivityItem(BaseModel):
    id: int
    action_type: str
    title: str
    description: Optional[str]
    ip_masked: str
    device_info: str
    fabric_tx_id: Optional[str] = None
    timestamp: str

class DashboardSummary(BaseModel):
    user: UserSummary
    total_credentials: int
    valid_credentials: int
    total_documents: int
    verified_credentials: int
    pending_verifications: int
    active_permissions: int
    upcoming_expirations: int
    vault_status: str
    encryption_status: str
    recent_documents: List[DocumentListItem]
    recent_credentials: List[CredentialListItem]
    recent_activities: List[ActivityItem]
    active_consents: List[ConsentRequestItem]
    unread_notifications_count: int
    security_notice: str

class SecurityOverview(BaseModel):
    session_valid: bool
    password_hashing: str
    vault_storage_type: str
    encryption_algorithm: str
    active_tokens: int
    data_protection_mode: str
    zk_snark_engine: str
    fabric_channel_status: str

# --- Backup & Recovery ---
class BackupExportResponse(BaseModel):
    backup_archive: Dict[str, Any]
    checksum: str
    exported_at: str
    total_records: int

class BackupRestoreRequest(BaseModel):
    backup_archive: Dict[str, Any]
    passphrase: str
