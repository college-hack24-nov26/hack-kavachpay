from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.credential import Credential
from backend.app.models.activity import Activity
from backend.app.models.consent import ConsentRequest
from backend.app.models.notification import Notification
from backend.app.schemas.schemas import (
    DashboardSummary, UserSummary, DocumentListItem, CredentialListItem,
    ActivityItem, ConsentRequestItem
)
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = date.today()
    thirty_days_later = today + timedelta(days=30)

    # 1. Real Document counts & Upcoming Expirations
    user_docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    total_docs = len(user_docs)
    pending_verifs = sum(1 for d in user_docs if d.verification_status == "PENDING_VERIFICATION")

    upcoming_exp = 0
    for d in user_docs:
        if d.expiry_date:
            exp_d = d.expiry_date.date()
            if today <= exp_d <= thirty_days_later:
                upcoming_exp += 1

    # 2. Real Credentials
    credentials = db.query(Credential).filter(Credential.user_id == current_user.id).all()
    total_creds = len(credentials)
    valid_creds = sum(1 for c in credentials if c.status == "VALID")

    # 3. Real Active Consent Permissions
    now = datetime.utcnow()
    active_consents = db.query(ConsentRequest).filter(
        ConsentRequest.user_id == current_user.id,
        ConsentRequest.status == "ACTIVE"
    ).all()
    active_permissions_count = len(active_consents)

    # 4. Unread Notifications Count
    unread_notifs = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    # 5. Recent Activity
    recent_acts = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.timestamp.desc()).limit(6).all()

    # 6. Profile Completion Percentage
    completion = 85
    if current_user.date_of_birth and current_user.phone_masked and current_user.two_factor_enabled:
        completion = 100

    return DashboardSummary(
        user=UserSummary(
            user_code=current_user.user_code,
            full_name=current_user.full_name,
            email=current_user.email,
            phone_masked=current_user.phone_masked,
            date_of_birth=current_user.date_of_birth,
            address_masked=current_user.address_masked,
            two_factor_enabled=current_user.two_factor_enabled,
            profile_completion_percentage=completion
        ),
        total_credentials=total_creds,
        valid_credentials=valid_creds,
        total_documents=total_docs,
        verified_credentials=valid_creds,
        pending_verifications=pending_verifs,
        active_permissions=active_permissions_count,
        upcoming_expirations=upcoming_exp,
        vault_status="ACTIVE & SECURE (AES-256-GCM)",
        encryption_status="Hardware-Isolated AES-GCM Encrypted",
        recent_documents=[
            DocumentListItem(
                id=d.id,
                category=d.category,
                title=d.title,
                holder_name=d.holder_name,
                document_number_masked=d.document_number_masked,
                issue_date=d.issue_date.strftime("%Y-%m-%d") if d.issue_date else None,
                expiry_date=d.expiry_date.strftime("%Y-%m-%d") if d.expiry_date else None,
                file_name=d.file_name,
                file_size=d.file_size,
                file_hash=d.file_hash,
                verification_status=d.verification_status,
                rejection_reason=d.rejection_reason,
                is_expired=d.expiry_date.date() < today if d.expiry_date else False,
                is_expiring_soon=(0 <= (d.expiry_date.date() - today).days <= 30) if d.expiry_date else False,
                created_at=d.created_at.strftime("%d %b %Y, %I:%M %p")
            )
            for d in user_docs[:3]
        ],
        recent_credentials=[
            CredentialListItem(
                id=c.id,
                category=c.category,
                title=c.title,
                issuer=c.issuer,
                status=c.status,
                issue_date=c.issue_date.strftime("%Y-%m-%d"),
                expiry_date=c.expiry_date.strftime("%Y-%m-%d"),
                is_synthetic=c.is_synthetic
            )
            for c in credentials[:3]
        ],
        recent_activities=[
            ActivityItem(
                id=a.id,
                action_type=a.action_type,
                title=a.title,
                description=a.description,
                ip_masked=a.ip_masked,
                device_info=a.device_info,
                fabric_tx_id=a.fabric_tx_id,
                timestamp=a.timestamp.strftime("%d %b, %I:%M %p")
            )
            for a in recent_acts
        ],
        active_consents=[
            ConsentRequestItem(
                id=c.id,
                institution_name=c.institution_name,
                institution_category=c.institution_category or "FinTech",
                purpose=c.purpose,
                requested_credential_type=c.requested_credential_type,
                requested_claim=c.requested_claim,
                status=c.status,
                duration_hours=c.duration_hours,
                expires_at=c.expires_at.strftime("%d %b, %I:%M %p") if c.expires_at else None,
                approved_at=c.approved_at.strftime("%d %b, %I:%M %p") if c.approved_at else None,
                revoked_at=c.revoked_at.strftime("%d %b, %I:%M %p") if c.revoked_at else None,
                created_at=c.created_at.strftime("%d %b, %I:%M %p"),
                fabric_tx_id=c.fabric_tx_id
            )
            for c in active_consents[:2]
        ],
        unread_notifications_count=unread_notifs,
        security_notice="Zero-knowledge privacy enabled. All documents encrypted at rest with AES-256-GCM."
    )
