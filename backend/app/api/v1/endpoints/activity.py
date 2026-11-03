from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.activity import Activity
from backend.app.schemas.schemas import ActivityItem
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/activity", tags=["Activity History"])

@router.get("", response_model=List[ActivityItem])
def get_activity_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    activities = db.query(Activity).filter(
        Activity.user_id == current_user.id
    ).order_by(Activity.timestamp.desc()).limit(50).all()
    
    return [
        ActivityItem(
            id=a.id,
            action_type=a.action_type,
            title=a.title,
            description=a.description,
            ip_masked=a.ip_masked,
            device_info=a.device_info,
            timestamp=a.timestamp.strftime("%d %b %Y, %I:%M %p")
        )
        for a in activities
    ]

