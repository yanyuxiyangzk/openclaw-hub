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
        assert data["data"]["email"] == "newuser@example.com"
        assert data["data"]["name"] == "New User"

    def test_register_duplicate_email(self, client, test_user):
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Another User"
        })
        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["code"] == 40901

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
        assert response.json()["detail"]["code"] == 40101

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