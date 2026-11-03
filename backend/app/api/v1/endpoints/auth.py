from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.activity import Activity
from backend.app.schemas.schemas import LoginRequest, TokenResponse, UserSummary
from backend.app.core.security import verify_password, create_session_token
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    email = login_data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. For demo, use user@kavachsetu.demo / GhostProtocol@2026"
        )
    
    token = create_session_token({"sub": user.id, "email": user.email, "user_code": user.user_code})
    
    # Record Login Activity
    client_host = request.client.host if request.client else "127.0.0.1"
    activity = Activity(
        user_id=user.id,
        action_type="LOGIN",
        title="User Authentication Successful",
        description="Session started via secure credentials",
        ip_masked=f"{client_host} (Verified)",
        device_info="KavachSetu Secure Client",
        timestamp=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserSummary(
            user_code=user.user_code,
            full_name=user.full_name,
            email=user.email,
            phone_masked=user.phone_masked
        )
    )

@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    client_host = request.client.host if request.client else "127.0.0.1"
    activity = Activity(
        user_id=current_user.id,
        action_type="LOGOUT",
        title="User Signed Out",
        description="Active session gracefully terminated",
        ip_masked=f"{client_host} (Verified)",
        device_info="KavachSetu Secure Client",
        timestamp=datetime.utcnow()
    )
    db.add(activity)
    db.commit()
    return {"message": "Logged out successfully", "status": "TERMINATED"}

@router.get("/me", response_model=UserSummary)
def get_me(current_user: User = Depends(get_current_user)):
    return UserSummary(
        user_code=current_user.user_code,
        full_name=current_user.full_name,
        email=current_user.email,
        phone_masked=current_user.phone_masked
    )

