from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.activity import Activity
from schemas.activity import ActivityResponse, ActivityCreate, ActivityListResponse
from services.activity_service import ActivityService
from typing import Optional, List

router = APIRouter(prefix="/api/activities", tags=["activities"])

def api_response(code=0, message="success", data=None):
    return {"code": code, "message": message, "data": data}

@router.get("", response_model=dict)
def list_activities(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    actor_id: Optional[str] = None,
    action_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActivityService(db)
    result = service.list_activities(
        tenant_id=current_user.tenant_id,
        page=page,
        limit=limit,
        actor_id=actor_id,
        action_type=action_type,
        entity_type=entity_type,
    )
    return api_response(data=result)

@router.post("", response_model=dict)
def create_activity(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ActivityService(db)
    activity = service.create_activity(tenant_id=current_user.tenant_id, data=data)
    return api_response(data=ActivityResponse.model_validate(activity).model_dump())

@router.get("/unread", response_model=dict)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取未读活动数量"""
    service = ActivityService(db)
    count = service.get_unread_count(tenant_id=current_user.tenant_id)
    return api_response(data={"unread_count": count})

@router.post("/mark-read", response_model=dict)
def mark_as_read(
    activity_ids: Optional[List[str]] = Query(None, description="要标记为已读的活动ID列表，空列表或None表示标记全部"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记活动为已读"""
    service = ActivityService(db)
    count = service.mark_as_read(tenant_id=current_user.tenant_id, activity_ids=activity_ids)
    return api_response(data={"marked_count": count})