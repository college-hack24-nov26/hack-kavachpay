import json
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.credential import Credential
from backend.app.models.activity import Activity
from backend.app.schemas.schemas import CredentialListItem, CredentialDetail
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/vault", tags=["Ghost-Vault"])

@router.get("/credentials", response_model=List[CredentialListItem])
def list_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    creds = db.query(Credential).filter(Credential.user_id == current_user.id).all()
    return [
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
        for c in creds
    ]

@router.get("/credentials/{credential_id}", response_model=CredentialDetail)
def get_credential_detail(
    credential_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cred = db.query(Credential).filter(
        Credential.id == credential_id,
        Credential.user_id == current_user.id
    ).first()
    
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential {credential_id} not found in your Ghost-Vault."
        )
    
    # Record actual VIEW_CREDENTIAL activity event
    client_host = request.client.host if request.client else "127.0.0.1"
    activity = Activity(
        user_id=current_user.id,
        action_type="VIEW_CREDENTIAL",
        title=f"Accessed {cred.title}",
        description=f"Inspected credential metadata for ID {cred.id}",
        ip_masked=f"{client_host} (Verified)",
        device_info="KavachSetu Secure Client",
        timestamp=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    
    safe_attrs = json.loads(cred.metadata_json) if cred.metadata_json else {}
    
    return CredentialDetail(
        id=cred.id,
        category=cred.category,
        title=cred.title,
        issuer=cred.issuer,
        status=cred.status,
        issue_date=cred.issue_date.strftime("%d %b %Y"),
        expiry_date=cred.expiry_date.strftime("%d %b %Y"),
        is_synthetic=cred.is_synthetic,
        verification_hash=cred.verification_hash,
        safe_attributes=safe_attrs,
        privacy_notice="SYNTHETIC DEMO CREDENTIAL: For testing and evaluation only. Not issued by government or commercial banking entities. Raw sensitive documents remain decoupled."
    )

