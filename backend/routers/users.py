from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session
from typing import Optional
from core.database import get_db
from core.security import get_current_user, get_current_superuser
from models.user import User
from schemas.user import UserResponse, UserListResponse, UserUpdate, PasswordUpdate, ToggleActive
from services.auth_service import AuthService

router = APIRouter(prefix="/api/users", tags=["users"])


def response(code: int = 0, message: str = "success", data=None):
    return {"code": code, "message": message, "data": data}


@router.get("", response_model=dict)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """GET /api/users - User list (paginated) - Superuser only"""
    total = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()
    return response(data={
        "items": [UserResponse.model_validate(u).model_dump() for u in users],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """GET /api/users/{id} - User detail"""
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": 40301, "message": "Access denied"}
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )
    return response(data=UserResponse.model_validate(user).model_dump())


@router.put("/{user_id}", response_model=dict)
def update_user(
    user_id: str,
    data: UserUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """PUT /api/users/{id} - Update user - Superuser only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )
    user.name = data.name
    if data.avatar is not None:
        user.avatar = data.avatar
    db.commit()
    db.refresh(user)
    return response(data=UserResponse.model_validate(user).model_dump())


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: str, current_user: User = Depends(get_current_superuser), db: Session = Depends(get_db)):
    """DELETE /api/users/{id} - Delete user - Superuser only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 42201, "message": "Cannot delete yourself"}
        )
    db.delete(user)
    db.commit()
    return response(message="User deleted successfully")


@router.put("/{user_id}/password", response_model=dict)
def change_password(
    user_id: str,
    data: PasswordUpdate,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """PUT /api/users/{id}/password - Change password - Superuser only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )
    service = AuthService(db)
    user.password_hash = service.hash_password(data.new_password)
    db.commit()
    return response(message="Password updated successfully")


@router.put("/{user_id}/toggle-active", response_model=dict)
def toggle_active(
    user_id: str,
    data: ToggleActive,
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db)
):
    """PUT /api/users/{id}/toggle-active - Enable/disable user - Superuser only"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": 40401, "message": "User not found"}
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": 42201, "message": "Cannot toggle yourself"}
        )
    user.is_active = data.is_active
    db.commit()
    return response(data={"id": user.id, "is_active": user.is_active})