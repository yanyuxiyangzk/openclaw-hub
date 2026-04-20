from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=64)
    name: str = Field(..., min_length=1, max_length=64)
    avatar: str | None = Field(None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=64)


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    avatar: str | None = Field(None, max_length=255)


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    page: int
    page_size: int


class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=64)


class ToggleActive(BaseModel):
    is_active: bool