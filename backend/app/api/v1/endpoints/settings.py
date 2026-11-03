from fastapi import APIRouter, Depends
from backend.app.models.user import User
from backend.app.schemas.schemas import SecurityOverview
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["Settings & Security"])

@router.get("/security-overview", response_model=SecurityOverview)
def get_security_overview(current_user: User = Depends(get_current_user)):
    return SecurityOverview(
        session_valid=True,
        password_hashing="Bcrypt (12 Rounds Adaptive Cost)",
        vault_storage_type="Decoupled Local Metadata Store",
        encryption_algorithm="HMAC-SHA256 Session Signing",
        active_tokens=1,
        data_protection_mode="Zero-Raw-Data Exposure"
    )

