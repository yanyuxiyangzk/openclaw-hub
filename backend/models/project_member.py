import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class ProjectMember(Base):
    __tablename__ = "project_members"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")