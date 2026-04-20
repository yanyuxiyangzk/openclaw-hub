from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr = Field(..., max_length=64)
    password: str = Field(..., min_length=6, max_length=64)
    name: str = Field(..., min_length=1, max_length=64)


class UserLogin(BaseModel):
    email: EmailStr = Field(..., max_length=64)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    avatar: str | None = Field(None, max_length=255)


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6, max_length=64)