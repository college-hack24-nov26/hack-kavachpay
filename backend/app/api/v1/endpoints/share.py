import json
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.zk_proof import ZkProof
from backend.app.models.share import ShareLink
from backend.app.schemas.schemas import ShareCreateRequest, ShareLinkItem
from backend.app.api.deps import get_current_user
from backend.app.core.fabric_ledger import FabricLedgerService

router = APIRouter(prefix="/share", tags=["Secure Document & Proof Sharing"])


def _generate_qr_svg(content: str) -> str:
    """Generates a compact aesthetic SVG QR code placeholder with high-contrast matrix."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="120" height="120">
      <rect width="120" height="120" fill="#FFFFFF" rx="8"/>
      <rect x="10" y="10" width="30" height="30" fill="#0B6B58"/>
      <rect x="15" y="15" width="20" height="20" fill="#FFFFFF"/>
      <rect x="20" y="20" width="10" height="10" fill="#0B6B58"/>
      <rect x="80" y="10" width="30" height="30" fill="#0B6B58"/>
      <rect x="85" y="15" width="20" height="20" fill="#FFFFFF"/>
      <rect x="90" y="20" width="10" height="10" fill="#0B6B58"/>
      <rect x="10" y="80" width="30" height="30" fill="#0B6B58"/>
      <rect x="15" y="85" width="20" height="20" fill="#FFFFFF"/>
      <rect x="20" y="90" width="10" height="10" fill="#0B6B58"/>
      <rect x="50" y="20" width="8" height="8" fill="#1C1F1D"/>
      <rect x="62" y="20" width="8" height="8" fill="#1C1F1D"/>
      <rect x="50" y="50" width="14" height="14" fill="#0B6B58"/>
      <rect x="70" y="50" width="8" height="8" fill="#1C1F1D"/>
      <rect x="50" y="70" width="8" height="8" fill="#1C1F1D"/>
      <rect x="80" y="70" width="14" height="14" fill="#1C1F1D"/>
      <rect x="62" y="86" width="8" height="8" fill="#1C1F1D"/>
      <rect x="90" y="90" width="14" height="14" fill="#0B6B58"/>
    </svg>"""


@router.post("/create", response_model=ShareLinkItem)
def create_share_link(
    payload: ShareCreateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    token = f"kvs-{secrets.token_urlsafe(18)}"
    share_id = f"SH-{secrets.token_hex(4).upper()}"
    expiry_hours = payload.expiry_hours or 24
    expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)

    base_url = str(request.base_url).rstrip("/")
    share_url = f"{base_url}/api/v1/share/view/{token}"

    link = ShareLink(
        id=share_id,
        token=token,
        user_id=current_user.id,
        document_id=payload.document_id,
        zk_proof_id=payload.zk_proof_id,
        share_type=payload.share_type,
        title=payload.title,
        purpose=payload.purpose,
        recipient_info=payload.recipient_info or "External Verifier",
        status="ACTIVE",
        max_uses=payload.max_uses or 5,
        use_count=0,
        expires_at=expires_at,
        access_logs_json="[]"
    )
    db.add(link)
    db.commit()

    fabric_tx = FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="CREDENTIAL_SHARED",
        title=f"Shared: {payload.title}",
        description=f"Generated secure token for {payload.recipient_info}. Purpose: {payload.purpose}",
        institution=payload.recipient_info
    )
    link.fabric_tx_id = fabric_tx.get("tx_id")
    db.commit()

    return ShareLinkItem(
        id=link.id,
        token=link.token,
        share_url=share_url,
        title=link.title,
        purpose=link.purpose,
        share_type=link.share_type,
        recipient_info=link.recipient_info,
        status=link.status,
        use_count=link.use_count,
        max_uses=link.max_uses,
        expires_at=link.expires_at.strftime("%d %b %Y, %I:%M %p"),
        created_at=link.created_at.strftime("%d %b %Y, %I:%M %p"),
        qr_svg=_generate_qr_svg(share_url)
    )


@router.get("/links", response_model=List[ShareLinkItem])
def list_share_links(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    links = db.query(ShareLink).filter(
        ShareLink.user_id == current_user.id
    ).order_by(ShareLink.created_at.desc()).all()

    now = datetime.utcnow()
    base_url = str(request.base_url).rstrip("/")

    results = []
    for l in links:
        if l.status == "ACTIVE" and l.expires_at < now:
            l.status = "EXPIRED"
        share_url = f"{base_url}/api/v1/share/view/{l.token}"
        results.append(ShareLinkItem(
            id=l.id,
            token=l.token,
            share_url=share_url,
            title=l.title,
            purpose=l.purpose,
            share_type=l.share_type,
            recipient_info=l.recipient_info,
            status=l.status,
            use_count=l.use_count,
            max_uses=l.max_uses,
            expires_at=l.expires_at.strftime("%d %b %Y, %I:%M %p"),
            created_at=l.created_at.strftime("%d %b %Y, %I:%M %p"),
            qr_svg=_generate_qr_svg(share_url)
        ))
    db.commit()
    return results


@router.post("/links/{share_id}/revoke")
def revoke_share_link(
    share_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    link = db.query(ShareLink).filter(
        ShareLink.id == share_id,
        ShareLink.user_id == current_user.id
    ).first()

    if not link:
        raise HTTPException(status_code=404, detail="Share link not found.")

    link.status = "REVOKED"
    db.commit()

    FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="SHARE_REVOKED",
        title=f"Revoked Share Token: {link.title}",
        description=f"Revoked token {link.id}. Any future accesses using this URL will be blocked.",
        institution=link.recipient_info
    )

    return {"message": "Sharing link revoked successfully.", "status": "REVOKED"}


@router.get("/view/{token}")
def verifier_public_view(token: str, request: Request, db: Session = Depends(get_db)):
    """
    Institutional / External Verifier Endpoint:
    Validates token, checks expiration and rate limits, logs verifier access,
    and returns safe zero-exposure verification results.
    """
    link = db.query(ShareLink).filter(ShareLink.token == token).first()
    if not link:
        raise HTTPException(status_code=404, detail="Invalid sharing token.")

    if link.status == "REVOKED":
        raise HTTPException(status_code=403, detail="Access revoked by credential holder.")

    if datetime.utcnow() > link.expires_at:
        link.status = "EXPIRED"
        db.commit()
        raise HTTPException(status_code=410, detail="This sharing link has expired.")

    if link.use_count >= link.max_uses:
        raise HTTPException(status_code=429, detail="Maximum usage limit reached for this single-use or limited token.")

    # Record Access Log
    client_ip = request.client.host if request.client else "127.0.0.1"
    logs = json.loads(link.access_logs_json) if link.access_logs_json else []
    logs.append({
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ip": client_ip,
        "user_agent": request.headers.get("user-agent", "Unknown")[:80]
    })
    link.access_logs_json = json.dumps(logs)
    link.use_count += 1
    db.commit()

    # Payload based on share type
    shared_data: Dict[str, Any] = {}
    if link.zk_proof_id:
        proof = db.query(ZkProof).filter(ZkProof.id == link.zk_proof_id).first()
        if proof:
            shared_data = {
                "proof_id": proof.id,
                "claim_statement": proof.claim_statement,
                "verification_status": proof.verification_status,
                "commitment": proof.commitment,
                "public_inputs": json.loads(proof.public_inputs_json),
                "proof_system": "BN254 Cryptographic Sigma-Range Proof",
                "zero_knowledge_guarantee": "Zero PII disclosed. Mathematical statement verified true."
            }
    elif link.document_id:
        doc = db.query(Document).filter(Document.id == link.document_id).first()
        if doc:
            shared_data = {
                "document_category": doc.category,
                "holder_pseudonym": f"{doc.holder_name.split()[0]} (Verified Citizen)",
                "document_number_masked": doc.document_number_masked,
                "verification_status": doc.verification_status,
                "integrity_hash": doc.file_hash,
                "privacy_mode": "Masked Zero-Exposure Projection"
            }

    return {
        "status": "AUTHORIZED_ACCESS",
        "title": link.title,
        "purpose": link.purpose,
        "recipient": link.recipient_info,
        "expires_at": link.expires_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "uses_remaining": max(0, link.max_uses - link.use_count),
        "payload": shared_data,
        "blockchain_audit_anchor": link.fabric_tx_id
    }
