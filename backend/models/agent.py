import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(32), nullable=False)
    config = Column(Text, nullable=True)
    org_id = Column(UUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="offline")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="agents")
    project_agents = relationship("ProjectAgent", back_populates="agent", cascade="all, delete-orphan")