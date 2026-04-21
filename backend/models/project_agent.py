import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class ProjectAgent(Base):
    __tablename__ = "project_agents"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(UUID, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="project_agents")
    agent = relationship("Agent", back_populates="project_agents")

    __table_args__ = (
        UniqueConstraint("project_id", "agent_id", name="uq_project_agent"),
    )