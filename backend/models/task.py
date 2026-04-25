import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Float, Enum as SQLEnum
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class TaskStatus(str, enum.Enum):
    todo = "todo"
    in_progress = "in_progress"
    in_review = "in_review"
    done = "done"
    blocked = "blocked"


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default=TaskStatus.todo.value)
    priority = Column(String(20), nullable=False, default=TaskPriority.medium.value)

    # Hierarchy
    parent_id = Column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    root_id = Column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)

    # Position for kanban ordering
    position = Column(Integer, default=0)

    # Estimates
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)

    # Tags stored as JSON string
    tags = Column(Text, nullable=True)

    # Dates
    due_date = Column(DateTime, nullable=True)
    reminder_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # References
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    assignee_id = Column(UUID, ForeignKey("users.id"), nullable=True)
    created_by = Column(UUID, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id])
    creator = relationship("User", foreign_keys=[created_by])
    parent = relationship("Task", remote_side=[id], foreign_keys=[parent_id], back_populates="subtasks")
    root = relationship("Task", remote_side=[id], foreign_keys=[root_id])
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("TaskAttachment", back_populates="task", cascade="all, delete-orphan")
    subtasks = relationship("Task", back_populates="parent", foreign_keys=[parent_id])
    executions = relationship("Execution", back_populates="task", cascade="all, delete-orphan")
