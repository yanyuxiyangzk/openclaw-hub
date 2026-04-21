from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    description: str | None = None
    org_id: str


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    description: str | None = None
    status: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    org_id: str
    status: str
    settings: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: str
    joined_at: datetime
    user_email: str | None = None
    user_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberListResponse(BaseModel):
    items: list[ProjectMemberResponse]
    total: int


class ProjectWithMembersResponse(BaseModel):
    id: str
    name: str
    description: str | None
    org_id: str
    status: str
    settings: str | None
    created_by: str
    created_at: datetime
    updated_at: datetime
    members: list[ProjectMemberResponse]

    model_config = ConfigDict(from_attributes=True)