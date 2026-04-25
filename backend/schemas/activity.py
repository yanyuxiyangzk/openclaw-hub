from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from datetime import datetime

class ActivityCreate(BaseModel):
    actor_id: str
    actor_name: str
    actor_avatar: Optional[str] = None
    action_type: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str] = None
    extra_data: Optional[Any] = None

class ActivityResponse(BaseModel):
    id: str
    tenant_id: str
    actor_id: str
    actor_name: str
    actor_avatar: Optional[str]
    action_type: str
    entity_type: str
    entity_id: str
    entity_name: Optional[str]
    extra_data: Optional[Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityListData(BaseModel):
    items: list[ActivityResponse]
    total: int
    page: int
    limit: int
    pages: int

class ActivityListResponse(BaseModel):
    items: list[ActivityResponse]
    total: int
    page: int
    limit: int
    pages: int