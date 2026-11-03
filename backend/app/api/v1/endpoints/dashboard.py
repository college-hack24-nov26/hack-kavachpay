from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.credential import Credential
from backend.app.models.activity import Activity
from backend.app.schemas.schemas import DashboardSummary, UserSummary, CredentialListItem, ActivityItem
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    credentials = db.query(Credential).filter(Credential.user_id == current_user.id).all()
    total_creds = len(credentials)
    valid_creds = sum(1 for c in credentials if c.status == "VALID")
    
    recent_acts = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.timestamp.desc()).limit(5).all()
    
    return DashboardSummary(
        user=UserSummary(
            user_code=current_user.user_code,
            full_name=current_user.full_name,
            email=current_user.email,
            phone_masked=current_user.phone_masked
        ),
        total_credentials=total_creds,
        valid_credentials=valid_creds,
        vault_status="ACTIVE & SECURE",
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
                timestamp=a.timestamp.strftime("%d %b, %I:%M %p")
            )
            for a in recent_acts
        ],
        security_notice="Decoupled storage enabled. Zero PII shared with network nodes."
    )

