from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)


class OrganizationUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)


class OrganizationResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberResponse(BaseModel):
    id: str
    org_id: str
    user_id: str
    role: str
    joined_at: datetime
    user_email: str | None = None
    user_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OrganizationMemberListResponse(BaseModel):
    items: list[OrganizationMemberResponse]
    total: int