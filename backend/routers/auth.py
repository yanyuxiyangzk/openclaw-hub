from fastapi import APIRouter, Depends, HTTPException, status, Response
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
    """POST /api/auth/register - User registration"""
    service = AuthService(db)
    user = service.register(data)
    return api_response(data=UserResponse.model_validate(user).model_dump())


@router.post("/login", response_model=dict)
def login(data: UserLogin, res: Response, db: Session = Depends(get_db)):
    """POST /api/auth/login - Login (returns access_token + refresh_token)"""
    service = AuthService(db)
    tokens = service.login(data)
    res.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax"
    )
    res.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        samesite="lax"
    )
    return api_response(data=tokens)


@router.post("/refresh", response_model=dict)
def refresh(data: RefreshTokenRequest, res: Response, db: Session = Depends(get_db)):
    """POST /api/auth/refresh - Refresh token"""
    service = AuthService(db)
    tokens = service.refresh_tokens(data.refresh_token)
    res.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax"
    )
    res.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=30 * 24 * 60 * 60,
        samesite="lax"
    )
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
def logout(res: Response):
    """POST /api/auth/logout - Logout"""
    res.delete_cookie(key="access_token")
    res.delete_cookie(key="refresh_token")
    return api_response(message="Logged out successfully")
