import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class SchedulerJob(Base):
    __tablename__ = "scheduler_jobs"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable=False)
    task_template_id = Column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    cron_expression = Column(String(64), nullable=False)
    agent_id = Column(UUID, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    enabled = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task_template = relationship("Task", back_populates="scheduler_jobs")
    agent = relationship("Agent", back_populates="scheduler_jobs")
