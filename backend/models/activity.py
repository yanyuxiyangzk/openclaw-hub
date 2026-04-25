from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base
import uuid


class Activity(Base):
    """活动动态模型"""
    __tablename__ = "activities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)
    actor_name = Column(String(128), nullable=False)
    actor_avatar = Column(String(512), nullable=True)
    action_type = Column(String(32), nullable=False, index=True)  # created/updated/deleted/completed/assigned
    entity_type = Column(String(32), nullable=False, index=True)   # task/project/agent/workflow
    entity_id = Column(String(36), nullable=False, index=True)
    entity_name = Column(String(256), nullable=True)
    extra_data = Column(JSON, nullable=True)  # 额外上下文数据
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
