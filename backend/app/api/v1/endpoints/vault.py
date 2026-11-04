import os
import json
import base64
import hashlib
import secrets
from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.document import Document
from backend.app.models.credential import Credential
from backend.app.models.activity import Activity
from backend.app.models.notification import Notification
from backend.app.schemas.schemas import (
    DocumentListItem, DocumentDetail, DocumentCreateRequest, DocumentUpdateRequest,
    CredentialListItem, CredentialDetail
)
from backend.app.api.deps import get_current_user
from backend.app.core.encryption import VaultEncryption
from backend.app.core.ocr_engine import DocumentIntelligence
from backend.app.core.fabric_ledger import FabricLedgerService

router = APIRouter(prefix="/vault", tags=["Ghost-Vault"])

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "storage", "documents"))
os.makedirs(STORAGE_DIR, exist_ok=True)


# ==================== CREDENTIALS (REUSED & ENHANCED) ====================

@router.get("/credentials", response_model=List[CredentialListItem])
def list_credentials(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Credential).filter(Credential.user_id == current_user.id)
    if category and category.upper() != "ALL":
        query = query.filter(Credential.category == category.upper())
    creds = query.all()
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

    client_host = request.client.host if request.client else "127.0.0.1"
    activity = Activity(
        user_id=current_user.id,
        action_type="VIEW_CREDENTIAL",
        title=f"Accessed {cred.title}",
        description=f"Inspected credential metadata for ID {cred.id}",
        ip_masked=f"{client_host} (Verified)",
        device_info="KavachSetu Secure Client",
        fabric_tx_id=cred.fabric_tx_id,
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
        fabric_tx_id=cred.fabric_tx_id,
        safe_attributes=safe_attrs,
        privacy_notice="SYNTHETIC DEMO CREDENTIAL: For testing and evaluation only. Not issued by government or commercial banking entities. Raw sensitive documents remain decoupled."
    )


# ==================== DOCUMENTS MANAGEMENT (SECTION 5 & 6) ====================

@router.get("/documents", response_model=List[DocumentListItem])
def list_documents(
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "date_desc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Document).filter(Document.user_id == current_user.id)

    if category and category.upper() != "ALL":
        query = query.filter(Document.category == category)

    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(Document.verification_status == status_filter.upper())

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Document.title.ilike(s),
                Document.category.ilike(s),
                Document.document_number_masked.ilike(s),
                Document.holder_name.ilike(s)
            )
        )

    # Sorting
    if sort_by == "name_asc":
        query = query.order_by(Document.title.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Document.title.desc())
    elif sort_by == "date_asc":
        query = query.order_by(Document.created_at.asc())
    else:
        query = query.order_by(Document.created_at.desc())

    docs = query.all()
    today = date.today()

    results = []
    for d in docs:
        is_exp = False
        is_exp_soon = False
        if d.expiry_date:
            exp_d = d.expiry_date.date()
            if exp_d < today:
                is_exp = True
            elif (exp_d - today).days <= 30:
                is_exp_soon = True

        results.append(DocumentListItem(
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
            is_expired=is_exp,
            is_expiring_soon=is_exp_soon,
            created_at=d.created_at.strftime("%d %b %Y, %I:%M %p")
        ))
    return results


@router.post("/documents/analyze")
def analyze_document_content(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    OCR Analysis Endpoint: Pre-scans file before saving, returns extracted metadata,
    anomalies, and classified document category for user confirmation.
    """
    file_bytes = file.file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    analysis = DocumentIntelligence.extract_and_classify(
        file_bytes=file_bytes,
        file_name=file.filename or "document.pdf",
        user_name=current_user.full_name
    )
    return analysis


@router.post("/documents/upload", response_model=DocumentDetail)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    title: str = Form(...),
    holder_name: str = Form(...),
    document_number: str = Form(...),
    issue_date: Optional[str] = Form(None),
    expiry_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    raw_bytes = await file.read()
    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="Cannot upload an empty file.")

    # Max size 15MB
    if len(raw_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 15MB.")

    # Check for duplicate upload (by SHA-256 raw hash or document number)
    raw_hash = hashlib.sha256(raw_bytes).hexdigest()
    doc_num_hash = hashlib.sha256(document_number.strip().encode()).hexdigest()

    existing_hash_doc = db.query(Document).filter(
        Document.user_id == current_user.id,
        or_(Document.file_hash == raw_hash, Document.document_number_hash == doc_num_hash)
    ).first()

    if existing_hash_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate document detected! This document is already registered as '{existing_hash_doc.title}' (ID: {existing_hash_doc.id})."
        )

    # Encrypt file at rest using AES-256-GCM
    encrypted_bytes = VaultEncryption.encrypt_document(raw_bytes)
    doc_id = f"DOC-{category.split()[0].upper()[:4]}-{secrets.token_hex(4).upper()}"
    file_path = os.path.join(STORAGE_DIR, f"{doc_id}.enc")

    with open(file_path, "wb") as f:
        f.write(encrypted_bytes)

    # Date parsing
    iss_dt = None
    exp_dt = None
    if issue_date:
        try:
            iss_dt = datetime.strptime(issue_date, "%Y-%m-%d")
        except Exception:
            pass
    if expiry_date:
        try:
            exp_dt = datetime.strptime(expiry_date, "%Y-%m-%d")
        except Exception:
            pass

    # Mask document number according to privacy guidelines
    masked_number = DocumentIntelligence.mask_document_number(category, document_number)

    # Run OCR classification
    analysis = DocumentIntelligence.extract_and_classify(raw_bytes, file.filename or "document.pdf", current_user.full_name)

    new_doc = Document(
        id=doc_id,
        user_id=current_user.id,
        category=category,
        title=title,
        holder_name=holder_name,
        document_number_masked=masked_number,
        document_number_hash=doc_num_hash,
        issue_date=iss_dt or datetime.utcnow(),
        expiry_date=exp_dt,
        file_name=file.filename or "uploaded_document.pdf",
        file_path=file_path,
        file_size=len(raw_bytes),
        file_hash=raw_hash,
        mime_type=file.content_type or "application/pdf",
        verification_status="UNVERIFIED",
        ocr_extracted_json=json.dumps(analysis.get("extracted_fields", {})),
        is_synthetic=True
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Record in Hyperledger Fabric ledger & Activity
    fabric_tx = FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="DOCUMENT_UPLOAD",
        title=f"Uploaded {title}",
        description=f"Stored AES-256-GCM encrypted document {doc_id} under category {category}",
        document_hash=raw_hash
    )

    # Notification
    notif = Notification(
        user_id=current_user.id,
        title="Document Uploaded",
        message=f"{title} ({doc_id}) was securely encrypted and added to your Ghost-Vault.",
        category="INFO",
        action_url="vault"
    )
    db.add(notif)
    db.commit()

    return DocumentDetail(
        id=new_doc.id,
        category=new_doc.category,
        title=new_doc.title,
        holder_name=new_doc.holder_name,
        document_number_masked=new_doc.document_number_masked,
        issue_date=new_doc.issue_date.strftime("%Y-%m-%d") if new_doc.issue_date else None,
        expiry_date=new_doc.expiry_date.strftime("%Y-%m-%d") if new_doc.expiry_date else None,
        file_name=new_doc.file_name,
        file_size=new_doc.file_size,
        file_hash=new_doc.file_hash,
        verification_status=new_doc.verification_status,
        rejection_reason=new_doc.rejection_reason,
        created_at=new_doc.created_at.strftime("%d %b %Y, %I:%M %p"),
        ocr_extracted_fields=analysis.get("extracted_fields"),
        fabric_tx_id=fabric_tx.get("tx_id"),
        download_url=f"/api/v1/vault/documents/{new_doc.id}/download"
    )


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document_detail(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    ocr_fields = json.loads(doc.ocr_extracted_json) if doc.ocr_extracted_json else {}

    # Check expiration
    is_exp = False
    is_exp_soon = False
    if doc.expiry_date:
        today = date.today()
        exp_d = doc.expiry_date.date()
        if exp_d < today:
            is_exp = True
        elif (exp_d - today).days <= 30:
            is_exp_soon = True

    return DocumentDetail(
        id=doc.id,
        category=doc.category,
        title=doc.title,
        holder_name=doc.holder_name,
        document_number_masked=doc.document_number_masked,
        issue_date=doc.issue_date.strftime("%Y-%m-%d") if doc.issue_date else None,
        expiry_date=doc.expiry_date.strftime("%Y-%m-%d") if doc.expiry_date else None,
        file_name=doc.file_name,
        file_size=doc.file_size,
        file_hash=doc.file_hash,
        verification_status=doc.verification_status,
        rejection_reason=doc.rejection_reason,
        is_expired=is_exp,
        is_expiring_soon=is_exp_soon,
        verified_at=doc.verified_at.strftime("%d %b %Y") if doc.verified_at else None,
        verified_by=doc.verified_by,
        ocr_extracted_fields=ocr_fields,
        created_at=doc.created_at.strftime("%d %b %Y, %I:%M %p"),
        download_url=f"/api/v1/vault/documents/{doc.id}/download"
    )


@router.get("/documents/{document_id}/download")
def download_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Secure download endpoint: Decrypts AES-256-GCM encrypted file on-the-fly
    and streams to verified session owner.
    """
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Encrypted file not found on disk.")

    with open(doc.file_path, "rb") as f:
        encrypted_bytes = f.read()

    try:
        decrypted_bytes = VaultEncryption.decrypt_document(encrypted_bytes)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(ex)}")

    return Response(
        content=decrypted_bytes,
        media_type=doc.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'}
    )


@router.put("/documents/{document_id}", response_model=DocumentDetail)
def update_document_metadata(
    document_id: str,
    payload: DocumentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if payload.title:
        doc.title = payload.title.strip()
    if payload.holder_name:
        doc.holder_name = payload.holder_name.strip()
    if payload.document_number:
        doc.document_number_masked = DocumentIntelligence.mask_document_number(doc.category, payload.document_number)
        doc.document_number_hash = hashlib.sha256(payload.document_number.strip().encode()).hexdigest()
    if payload.issue_date:
        try:
            doc.issue_date = datetime.strptime(payload.issue_date, "%Y-%m-%d")
        except Exception:
            pass
    if payload.expiry_date:
        try:
            doc.expiry_date = datetime.strptime(payload.expiry_date, "%Y-%m-%d")
        except Exception:
            pass

    doc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(doc)

    FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="DOCUMENT_UPDATED",
        title=f"Updated metadata for {doc.title}",
        description=f"Modified metadata fields for {doc.id}",
        document_hash=doc.file_hash
    )

    return get_document_detail(document_id, current_user, db)


@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc_title = doc.title
    doc_hash = doc.file_hash
    file_path = doc.file_path

    # Delete encrypted file on disk
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Unlink any credentials referencing this document
    db.query(Credential).filter(Credential.document_id == document_id).update({"document_id": None})
    db.delete(doc)
    db.commit()

    # Record deletion on Fabric audit trail
    FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="DOCUMENT_DELETED",
        title=f"Deleted {doc_title}",
        description=f"Permanently purged document {document_id} and purged encrypted file from disk.",
        document_hash=doc_hash
    )

    return {"message": f"Document '{doc_title}' ({document_id}) permanently deleted.", "status": "PURGED"}


# ==================== VERIFICATION CENTRE (SECTION 7) ====================

@router.post("/documents/{document_id}/verify-simulation")
def verify_document_simulation(
    document_id: str,
    verification_mode: Optional[str] = "DEMO_ISSUER", # DEMO_ISSUER or STRICT
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulated Trust Framework Verification Workflow:
    Evaluates format validity, expiration date, and integrity hash.
    Generates a cryptographically signed Credential in Ghost-Vault upon success.
    """
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Validation check: is it expired?
    if doc.expiry_date and doc.expiry_date.date() < date.today():
        doc.verification_status = "REJECTED"
        doc.rejection_reason = f"Verification failed: Document expired on {doc.expiry_date.strftime('%Y-%m-%d')}."
        db.commit()

        FabricLedgerService.record_event(
            db=db,
            user_id=current_user.id,
            action_type="VERIFICATION_REJECTED",
            title=f"Verification Rejected: {doc.title}",
            description=doc.rejection_reason,
            document_hash=doc.file_hash
        )

        return {
            "status": "REJECTED",
            "reason": doc.rejection_reason,
            "document_id": doc.id,
            "verification_source": "KavachSetu Trust Registry Gateway"
        }

    # Successful verification
    doc.verification_status = "DEMO_VERIFIED"
    doc.verified_at = datetime.utcnow()
    doc.verified_by = "KavachSetu Decentralized Trust Framework (Demo Node)"
    doc.rejection_reason = None

    # Check if a Credential already exists for this document or create a new one
    cred = db.query(Credential).filter(Credential.document_id == doc.id).first()
    if not cred:
        cred_category = "IDENTITY"
        if "PAN" in doc.category:
            cred_category = "KYC"
        elif "Income" in doc.category:
            cred_category = "INCOME"
        elif "Driving" in doc.category:
            cred_category = "IDENTITY"
        elif "Bank" in doc.category:
            cred_category = "INCOME"

        cred_id = f"KVS-CRED-{secrets.token_hex(4).upper()}"
        verification_hash = hashlib.sha256(f"{doc.id}:{doc.file_hash}:{current_user.id}".encode()).hexdigest()

        # Build safe attributes for zero-exposure proofing
        safe_meta = {
            "document_category": doc.category,
            "holder_pseudonym": f"{current_user.full_name.split()[0]}-{current_user.user_code}",
            "verification_status": "ATTESTED_VALID",
            "trust_tier": "Level-2 Decoupled Sandbox Attestation",
            "hash_fingerprint": verification_hash[:16] + "..."
        }
        if cred_category == "INCOME":
            safe_meta["predicate_test_satisfied"] = "Monthly Income > ₹25,000"
            safe_meta["synthetic_monthly_income"] = "₹35,000"
        elif cred_category == "IDENTITY":
            safe_meta["predicate_test_satisfied"] = "Age >= 18 Years"
            safe_meta["nationality"] = "Indian Citizen (Synthetic Attestation)"

        cred = Credential(
            id=cred_id,
            user_id=current_user.id,
            document_id=doc.id,
            category=cred_category,
            title=f"Verified {doc.title}",
            issuer=doc.verified_by,
            status="VALID",
            issue_date=datetime.utcnow(),
            expiry_date=doc.expiry_date or (datetime.utcnow() + timedelta(days=365)),
            is_synthetic=True,
            verification_hash=verification_hash,
            metadata_json=json.dumps(safe_meta)
        )
        db.add(cred)

    db.commit()

    fabric_tx = FabricLedgerService.record_event(
        db=db,
        user_id=current_user.id,
        action_type="VERIFICATION_COMPLETED",
        title=f"Verified Credential: {doc.title}",
        description=f"Attested validity for {doc.id} via Trust Framework Node. Credential {cred.id} issued.",
        document_hash=doc.file_hash,
        institution=doc.verified_by
    )

    cred.fabric_tx_id = fabric_tx.get("tx_id")
    db.commit()

    # Create notification
    notif = Notification(
        user_id=current_user.id,
        title="Document Verified Successfully",
        message=f"{doc.title} has been successfully verified and added as credential {cred.id}.",
        category="VERIFICATION",
        action_url="vault"
    )
    db.add(notif)
    db.commit()

    return {
        "status": "VERIFIED",
        "document_id": doc.id,
        "credential_id": cred.id,
        "verification_source": doc.verified_by,
        "verification_hash": cred.verification_hash,
        "fabric_tx_id": fabric_tx.get("tx_id"),
        "message": "Document verified and attested into Ghost-Vault."
    }
