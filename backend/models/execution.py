import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base
import enum


class ExecutionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class Execution(Base):
    __tablename__ = "executions"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default=ExecutionStatus.pending.value)
    input_data = Column(Text, nullable=True)
    output_data = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    task = relationship("Task", back_populates="executions")
    agent = relationship("Agent", back_populates="executions")
