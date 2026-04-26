from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.activity import Activity
from schemas.activity import ActivityCreate, ActivityResponse, ActivityListData
from typing import Optional, List
from datetime import datetime

class ActivityService:
    def __init__(self, db: Session):
        self.db = db

    def list_activities(
        self,
        tenant_id: str,
        page: int = 1,
        limit: int = 20,
        actor_id: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> dict:
        query = self.db.query(Activity).filter(Activity.tenant_id == tenant_id)
        if actor_id:
            query = query.filter(Activity.actor_id == actor_id)
        if action_type:
            query = query.filter(Activity.action_type == action_type)
        if entity_type:
            query = query.filter(Activity.entity_type == entity_type)

        total = query.count()
        items = query.order_by(desc(Activity.created_at)).offset((page - 1) * limit).limit(limit).all()
        pages = (total + limit - 1) // limit
        return {
            "items": [ActivityResponse.model_validate(a).model_dump() for a in items],
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    def create_activity(self, tenant_id: str, data: ActivityCreate) -> Activity:
        activity = Activity(tenant_id=tenant_id, **data.model_dump())
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_unread_count(self, tenant_id: str) -> int:
        """获取未读活动数量"""
        return self.db.query(Activity).filter(
            Activity.tenant_id == tenant_id,
            Activity.read_at.is_(None)
        ).count()

    def mark_as_read(self, tenant_id: str, activity_ids: Optional[List[str]] = None) -> int:
        """标记活动为已读。如果提供 activity_ids，则只标记指定的活动；否则标记所有未读活动"""
        query = self.db.query(Activity).filter(
            Activity.tenant_id == tenant_id,
            Activity.read_at.is_(None)
        )
        if activity_ids:
            query = query.filter(Activity.id.in_(activity_ids))

        now = datetime.utcnow()
        count = query.update({Activity.read_at: now}, synchronize_session=False)
        self.db.commit()
        return count