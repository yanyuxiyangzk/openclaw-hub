from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class InvitationCreate(BaseModel):
    email: EmailStr = Field(..., max_length=64)
    role: str = Field(default="member", pattern="^(owner|admin|member)$")


class InvitationResponse(BaseModel):
    id: str
    org_id: str
    email: str
    role: str
    token: str
    expires_at: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvitationValidateResponse(BaseModel):
    valid: bool
    invitation: InvitationResponse | None = None
    organization_name: str | None = None


class InvitationAcceptResponse(BaseModel):
    success: bool
    message: str
    organization_id: str | None = None
    organization_name: str | None = None