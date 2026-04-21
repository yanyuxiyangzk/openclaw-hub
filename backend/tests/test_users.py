import pytest


class TestUserList:
    def test_list_users_as_superuser(self, client, superuser_headers, test_user):
        response = client.get("/api/users", headers=superuser_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

    def test_list_users_as_regular_user(self, client, auth_headers):
        response = client.get("/api/users", headers=auth_headers)
        assert response.status_code == 403


class TestUserGet:
    def test_get_user_by_id(self, client, auth_headers, test_user):
        response = client.get(f"/api/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == test_user.id

    def test_get_user_by_id_as_superuser(self, client, superuser_headers, test_user):
        response = client.get(f"/api/users/{test_user.id}", headers=superuser_headers)
        assert response.status_code == 200

    def test_get_nonexistent_user(self, client, superuser_headers):
        response = client.get("/api/users/nonexistent-id", headers=superuser_headers)
        assert response.status_code == 404


class TestUserUpdate:
    def test_update_user(self, client, superuser_headers, test_user):
        response = client.put(f"/api/users/{test_user.id}", headers=superuser_headers, json={
            "name": "Updated User",
            "avatar": "https://example.com/new_avatar.png"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated User"


class TestUserDelete:
    def test_delete_user(self, client, superuser_headers, db, superuser):
        from models.user import User
        import uuid

        new_user = User(
            id=str(uuid.uuid4()),
            email='delete@example.com',
            password_hash='hash',
            name='Delete Me',
            is_active=True,
            is_superuser=False,
        )
        db.add(new_user)
        db.commit()

        response = client.delete(f"/api/users/{new_user.id}", headers=superuser_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_delete_self_forbidden(self, client, superuser_headers, superuser):
        response = client.delete(f"/api/users/{superuser.id}", headers=superuser_headers)
        assert response.status_code == 400


class TestUserPasswordChange:
    def test_change_password(self, client, superuser_headers, db, test_user):
        response = client.put(f"/api/users/{test_user.id}/password", headers=superuser_headers, json={
            "new_password": "newpassword123"
        })
        assert response.status_code == 200
        assert response.json()["code"] == 0


class TestUserToggleActive:
    def test_toggle_active(self, client, superuser_headers, db, test_user, superuser):
        response = client.put(f"/api/users/{test_user.id}/toggle-active", headers=superuser_headers, json={
            "is_active": False
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["is_active"] is False

    def test_toggle_self_forbidden(self, client, superuser_headers, superuser):
        response = client.put(f"/api/users/{superuser.id}/toggle-active", headers=superuser_headers, json={
            "is_active": False
        })
        assert response.status_code == 400


class TestUserAccessDenied:
    def test_get_other_user_denied(self, client, db, auth_headers):
        from models.user import User
        from core.security import get_password_hash
        import uuid

        other = User(
            id=str(uuid.uuid4()),
            email="other2@example.com",
            password_hash=get_password_hash("password123"),
            name="Other User",
            is_active=True,
            is_superuser=False,
        )
        db.add(other)
        db.commit()

        response = client.get(f"/api/users/{other.id}", headers=auth_headers)
        assert response.status_code == 403