import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(UUID, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(256), nullable=False)
    file_url = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(UUID, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    task = relationship("Task", back_populates="attachments")
    uploader = relationship("User")
