from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.consent import ConsentRequest
from backend.app.models.notification import Notification
from backend.app.schemas.schemas import ConsentRequestItem, ConsentActionRequest
from backend.app.api.deps import get_current_user
from backend.app.core.fabric_ledger import FabricLedgerService

router = APIRouter(prefix="/consent", tags=["Consent & Permissions"])


@router.get("/requests", response_model=List[ConsentRequestItem])
def list_consent_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    requests = db.query(ConsentRequest).filter(
        ConsentRequest.user_id == current_user.id
    ).order_by(ConsentRequest.created_at.desc()).all()

    now = datetime.utcnow()
    # Check for expired requests
    for r in requests:
        if r.status == "ACTIVE" and r.expires_at and r.expires_at < now:
            r.status = "EXPIRED"
    db.commit()

    return [
        ConsentRequestItem(
            id=r.id,
            institution_name=r.institution_name,
            institution_category=r.institution_category or "FinTech Verifier",
            purpose=r.purpose,
            requested_credential_type=r.requested_credential_type,
            requested_claim=r.requested_claim,
            status=r.status,
            duration_hours=r.duration_hours,
            expires_at=r.expires_at.strftime("%d %b %Y, %I:%M %p") if r.expires_at else None,
            approved_at=r.approved_at.strftime("%d %b %Y, %I:%M %p") if r.approved_at else None,
            revoked_at=r.revoked_at.strftime("%d %b %Y, %I:%M %p") if r.revoked_at else None,
            created_at=r.created_at.strftime("%d %b %Y, %I:%M %p"),
            fabric_tx_id=r.fabric_tx_id
        )
        for r in requests
    ]


@router.post("/requests/{request_id}/action", response_model=ConsentRequestItem)
def handle_consent_action(
    request_id: str,
    action_data: ConsentActionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(ConsentRequest).filter(
        ConsentRequest.id == request_id,
        ConsentRequest.user_id == current_user.id
    ).first()

    if not req:
        raise HTTPException(status_code=404, detail="Consent request not found.")

    act = action_data.action.upper()
    now = datetime.utcnow()

    if act == "APPROVE":
        hours = action_data.duration_hours or 24
        req.status = "ACTIVE"
        req.duration_hours = hours
        req.approved_at = now
        req.expires_at = now + timedelta(hours=hours)

        fabric_tx = FabricLedgerService.record_event(
            db=db,
            user_id=current_user.id,
            action_type="CONSENT_APPROVED",
            title=f"Approved Consent for {req.institution_name}",
            description=f"Granted {hours}h zero-exposure access for predicate: '{req.requested_claim}'",
            institution=req.institution_name
        )
        req.fabric_tx_id = fabric_tx.get("tx_id")

        notif = Notification(
            user_id=current_user.id,
            title=f"Permission Granted: {req.institution_name}",
            message=f"Access granted for '{req.requested_claim}' valid for {hours} hours.",
            category="ACCESS_REQUEST",
            action_url="consent"
        )
        db.add(notif)

    elif act == "REJECT":
        req.status = "REJECTED"
        fabric_tx = FabricLedgerService.record_event(
            db=db,
            user_id=current_user.id,
            action_type="CONSENT_REJECTED",
            title=f"Rejected Consent Request: {req.institution_name}",
            description=f"User declined access request for purpose: '{req.purpose}'",
            institution=req.institution_name
        )
        req.fabric_tx_id = fabric_tx.get("tx_id")

    elif act == "REVOKE":
        req.status = "REVOKED"
        req.revoked_at = now
        fabric_tx = FabricLedgerService.record_event(
            db=db,
            user_id=current_user.id,
            action_type="PERMISSION_REVOKED",
            title=f"Revoked Access: {req.institution_name}",
            description=f"Immediate cryptographic revocation applied. Future verifier token access terminated.",
            institution=req.institution_name
        )
        req.fabric_tx_id = fabric_tx.get("tx_id")

        notif = Notification(
            user_id=current_user.id,
            title=f"Permission Revoked: {req.institution_name}",
            message=f"Access token for {req.institution_name} has been immediately revoked.",
            category="REVOCATION",
            action_url="consent"
        )
        db.add(notif)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid action: {act}. Use APPROVE, REJECT, or REVOKE.")

    db.commit()
    db.refresh(req)

    return ConsentRequestItem(
        id=req.id,
        institution_name=req.institution_name,
        institution_category=req.institution_category or "Verifier",
        purpose=req.purpose,
        requested_credential_type=req.requested_credential_type,
        requested_claim=req.requested_claim,
        status=req.status,
        duration_hours=req.duration_hours,
        expires_at=req.expires_at.strftime("%d %b %Y, %I:%M %p") if req.expires_at else None,
        approved_at=req.approved_at.strftime("%d %b %Y, %I:%M %p") if req.approved_at else None,
        revoked_at=req.revoked_at.strftime("%d %b %Y, %I:%M %p") if req.revoked_at else None,
        created_at=req.created_at.strftime("%d %b %Y, %I:%M %p"),
        fabric_tx_id=req.fabric_tx_id
    )


@router.post("/create-demo", response_model=ConsentRequestItem)
def create_demo_consent_request(
    institution: Optional[str] = "State Bank of India",
    claim: Optional[str] = "Monthly Income > ₹25,000",
    purpose: Optional[str] = "Credit Card Underwriting Assessment",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a sample incoming consent request for testing."""
    import secrets
    req_id = f"REQ-{secrets.token_hex(3).upper()}"
    new_req = ConsentRequest(
        id=req_id,
        user_id=current_user.id,
        institution_name=institution,
        institution_category="Financial Institution",
        purpose=purpose,
        requested_credential_type="INCOME",
        requested_claim=claim,
        status="PENDING",
        duration_hours=24,
        created_at=datetime.utcnow()
    )
    db.add(new_req)

    notif = Notification(
        user_id=current_user.id,
        title=f"New Access Request: {institution}",
        message=f"{institution} requested permission: {claim}",
        category="ACCESS_REQUEST",
        action_url="consent"
    )
    db.add(notif)
    db.commit()

    return ConsentRequestItem(
        id=new_req.id,
        institution_name=new_req.institution_name,
        institution_category=new_req.institution_category,
        purpose=new_req.purpose,
        requested_credential_type=new_req.requested_credential_type,
        requested_claim=new_req.requested_claim,
        status=new_req.status,
        duration_hours=new_req.duration_hours,
        expires_at=None,
        approved_at=None,
        revoked_at=None,
        created_at=new_req.created_at.strftime("%d %b %Y, %I:%M %p"),
        fabric_tx_id=None
    )
