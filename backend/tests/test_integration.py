"""Integration tests: unified error response format + end-to-end flows."""
import pytest
from fastapi.testclient import TestClient


class TestUnifiedErrorResponse:
    """All API errors must return {code, message, data} format."""

    def test_401_unauthorized_format(self, client):
        res = client.get("/api/auth/me")
        assert res.status_code == 401
        body = res.json()
        assert "code" in body
        assert "message" in body
        assert body["data"] is None

    def test_403_forbidden_format(self, client, test_user, auth_headers):
        res = client.get("/api/users", headers=auth_headers)
        assert res.status_code == 403
        body = res.json()
        assert "code" in body
        assert "message" in body
        assert body["data"] is None

    def test_404_not_found_format(self, client, superuser_headers):
        res = client.get("/api/users/nonexistent-id", headers=superuser_headers)
        assert res.status_code == 404
        body = res.json()
        assert "code" in body
        assert "message" in body
        assert body["data"] is None

    def test_409_conflict_format(self, client, test_user):
        res = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Duplicate"
        })
        assert res.status_code == 409
        body = res.json()
        assert "code" in body
        assert "message" in body
        assert body["data"] is None

    def test_success_response_format(self, client):
        res = client.post("/api/auth/register", json={
            "email": "new@example.com",
            "password": "password123",
            "name": "New User"
        })
        assert res.status_code == 200
        body = res.json()
        assert body["code"] == 0
        assert body["message"] == "success"
        assert body["data"] is not None


class TestEndToEndAuthFlow:
    """Full authentication flow: register → login → me → update → logout."""

    def test_full_auth_flow(self, client):
        # Register
        res = client.post("/api/auth/register", json={
            "email": "e2e@example.com",
            "password": "password123",
            "name": "E2E User"
        })
        assert res.status_code == 200
        assert res.json()["data"]["user"]["email"] == "e2e@example.com"

        # Login
        res = client.post("/api/auth/login", json={
            "email": "e2e@example.com",
            "password": "password123"
        })
        assert res.status_code == 200
        tokens = res.json()["data"]
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        # Get me
        res = client.get("/api/auth/me", headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["email"] == "e2e@example.com"

        # Update me
        res = client.put("/api/auth/me", json={"name": "Updated User"}, headers=headers)
        assert res.status_code == 200
        assert res.json()["data"]["name"] == "Updated User"

        # Refresh token
        res = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert res.status_code == 200
        new_tokens = res.json()["data"]
        assert "access_token" in new_tokens

        # Logout
        res = client.post("/api/auth/logout", headers=headers)
        assert res.status_code == 200


class TestEndToEndOrgFlow:
    """Full organization flow: create org → list → detail → invite → accept."""

    def test_full_org_flow(self, client, test_user, auth_headers):
        # Create org
        res = client.post("/api/orgs", json={"name": "Test Org"}, headers=auth_headers)
        assert res.status_code == 200
        org_id = res.json()["data"]["id"]

        # List orgs
        res = client.get("/api/orgs", headers=auth_headers)
        assert res.status_code == 200
        assert len(res.json()["data"]) >= 1

        # Get org detail
        res = client.get(f"/api/orgs/{org_id}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["name"] == "Test Org"

        # List members
        res = client.get(f"/api/orgs/{org_id}/members", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["total"] >= 1

        # Create invitation
        res = client.post(f"/api/orgs/{org_id}/invitations",
                          json={"email": "invite@example.com", "role": "member"},
                          headers=auth_headers)
        assert res.status_code == 200
        invitation_token = res.json()["data"]["token"]

        # Validate invitation
        res = client.get(f"/api/invitations/{invitation_token}")
        assert res.status_code == 200
        assert res.json()["data"]["valid"] is True

        # Update org
        res = client.put(f"/api/orgs/{org_id}", json={"name": "Updated Org"}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["data"]["name"] == "Updated Org"
