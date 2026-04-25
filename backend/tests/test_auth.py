import pytest


class TestAuthRegister:
    def test_register_success(self, client):
        response = client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["user"]["email"] == "newuser@example.com"
        assert data["data"]["user"]["name"] == "New User"

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Another User"
        })
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == 40904  # EmailAlreadyRegisteredException

    def test_register_invalid_email(self, client):
        response = client.post("/api/auth/register", json={
            "email": "invalid-email",
            "password": "password123",
            "name": "New User"
        })
        assert response.status_code == 422


class TestAuthLogin:
    def test_login_success(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_wrong_password(self, client, test_user):
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert response.json()["code"] == 40102  # InvalidCredentialsException

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401


class TestAuthMe:
    def test_get_me_success(self, client, auth_headers):
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["email"] == "test@example.com"

    def test_get_me_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401


class TestAuthUpdate:
    def test_update_me_success(self, client, auth_headers):
        response = client.put("/api/auth/me", headers=auth_headers, json={
            "name": "Updated Name",
            "avatar": "https://example.com/avatar.png"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["avatar"] == "https://example.com/avatar.png"


class TestAuthRefresh:
    def test_refresh_success(self, client, test_user):
        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        refresh_token = login_response.json()["data"]["refresh_token"]

        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]


class TestAuthLogout:
    def test_logout_success(self, client, auth_headers):
        response = client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "logged out" in data["message"].lower()


class TestAuthEdgeCases:
    def test_login_inactive_user(self, client, db):
        from models.user import User
        from core.security import get_password_hash
        import uuid

        user = User(
            id=str(uuid.uuid4()),
            email="inactive@example.com",
            password_hash=get_password_hash("password123"),
            name="Inactive User",
            is_active=False,
            is_superuser=False,
        )
        db.add(user)
        db.commit()

        response = client.post("/api/auth/login", json={
            "email": "inactive@example.com",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_refresh_invalid_token(self, client):
        response = client.post("/api/auth/refresh", json={
            "refresh_token": "invalid-token"
        })
        assert response.status_code == 401

    def test_access_with_invalid_scheme(self, client):
        response = client.get("/api/auth/me", headers={"Authorization": "Basic abc"})
        assert response.status_code == 401

    def test_access_deleted_user(self, client, db, test_user):
        from jose import jwt
        from config import get_settings

        settings = get_settings()
        token = jwt.encode({"sub": "nonexistent-user-id", "type": "access", "exp": 9999999999}, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401