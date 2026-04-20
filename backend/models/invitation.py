import uuid
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.sqlite import TEXT as UUID
from sqlalchemy.orm import relationship
from core.database import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id = Column(UUID, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(64), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")
    token = Column(String(64), unique=True, nullable=False, default=lambda: secrets.token_urlsafe(32))
    expires_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc) + timedelta(days=7))
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    organization = relationship("Organization", back_populates="invitations")