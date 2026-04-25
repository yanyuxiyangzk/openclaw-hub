from sqlalchemy.orm import Session
from models.user import User
from schemas.auth import UserRegister, UserLogin, UserUpdate
from core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from core.exceptions import (
    EmailAlreadyRegisteredException, InvalidCredentialsException,
    InvalidRefreshTokenException, UserInactiveException
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: UserRegister) -> User:
        existing = self.db.query(User).filter(User.email == data.email).first()
        if existing:
            raise EmailAlreadyRegisteredException()

        user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            name=data.name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, data: UserLogin) -> User:
        user = self.db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UserInactiveException()

        return user

    def create_tokens(self, user: User) -> dict:
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def refresh_tokens(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenException()

        user_id = payload.get("sub")
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise InvalidRefreshTokenException()

        return self.create_tokens(user)

    def update_user(self, user: User, data: UserUpdate) -> User:
        user.name = data.name
        if data.avatar is not None:
            user.avatar = data.avatar
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)

    def hash_password(self, password: str) -> str:
        return get_password_hash(password)
