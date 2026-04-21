from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_current_user
from models.user import User
from schemas.auth import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserUpdate
from schemas.user import UserResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def api_response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


@router.post("/register", response_model=dict)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """POST /api/auth/register - User registration (returns user + tokens)"""
    service = AuthService(db)
    user = service.register(data)
    access_token = service.create_tokens(user)
    return api_response(data={
        "user": UserResponse.model_validate(user).model_dump(),
        **access_token,
    })


@router.post("/login", response_model=dict)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """POST /api/auth/login - Login (returns user + tokens)"""
    service = AuthService(db)
    user = service.authenticate(data)
    tokens = service.create_tokens(user)
    return api_response(data={
        "user": UserResponse.model_validate(user).model_dump(),
        **tokens,
    })


@router.post("/refresh", response_model=dict)
def refresh(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """POST /api/auth/refresh - Refresh token"""
    service = AuthService(db)
    tokens = service.refresh_tokens(data.refresh_token)
    return api_response(data=tokens)


@router.get("/me", response_model=dict)
def get_me(current_user: User = Depends(get_current_user)):
    """GET /api/auth/me - Current user"""
    return api_response(data=UserResponse.model_validate(current_user).model_dump())


@router.put("/me", response_model=dict)
def update_me(data: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PUT /api/auth/me - Update current user"""
    service = AuthService(db)
    user = service.update_user(current_user, data)
    return api_response(data=UserResponse.model_validate(user).model_dump())


@router.post("/logout", response_model=dict)
def logout():
    """POST /api/auth/logout - Logout"""
    return api_response(message="Logged out successfully")
