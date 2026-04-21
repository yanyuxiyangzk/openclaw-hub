import pytest
from datetime import datetime, timedelta, timezone
import uuid


class TestInvitationValidate:
    def test_validate_valid_invitation(self, client, db, test_org, test_user):
        from models.invitation import Invitation

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="newuser@example.com",
            role="member",
            token="valid-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        response = client.get("/api/invitations/valid-token-123")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["valid"] is True
        assert data["data"]["organization_name"] == "Test Organization"

    def test_validate_invalid_token(self, client):
        response = client.get("/api/invitations/nonexistent-token")
        assert response.status_code == 404


class TestInvitationAccept:
    def test_accept_invitation(self, client, db, test_org):
        from models.invitation import Invitation
        from models.user import User
        from core.security import get_password_hash

        invitee = User(
            id=str(uuid.uuid4()),
            email="invitee@example.com",
            password_hash=get_password_hash("password"),
            name="Invitee User",
            is_active=True,
            is_superuser=False,
        )
        db.add(invitee)
        db.commit()

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="invitee@example.com",
            role="member",
            token="accept-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        login_response = client.post("/api/auth/login", json={
            "email": "invitee@example.com",
            "password": "password"
        })
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/invitations/accept-token-123/accept", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["success"] is True


class TestInvitationRevoke:
    def test_revoke_invitation(self, client, db, test_org, auth_headers):
        from models.invitation import Invitation

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="revoke@example.com",
            role="member",
            token="revoke-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        response = client.delete(f"/api/invitations/{invitation.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0

    def test_revoke_nonexistent_invitation(self, client, auth_headers):
        response = client.delete("/api/invitations/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestInvitationExpired:
    def test_accept_expired_invitation(self, client, db, test_org, test_user):
        from models.invitation import Invitation

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="expired@example.com",
            role="member",
            token="expired-token-123",
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        login_response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/invitations/expired-token-123/accept", headers=headers)
        assert response.status_code == 400


class TestInvitationEdgeCases:
    def test_accept_already_accepted(self, client, db, test_org):
        from models.invitation import Invitation
        from models.user import User
        from core.security import get_password_hash

        invitee = User(
            id=str(uuid.uuid4()),
            email="already@example.com",
            password_hash=get_password_hash("password"),
            name="Already Member",
            is_active=True,
            is_superuser=False,
        )
        db.add(invitee)
        db.commit()

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="already@example.com",
            role="member",
            token="accepted-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="accepted",
        )
        db.add(invitation)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "already@example.com", "password": "password"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.post("/api/invitations/accepted-token-123/accept", headers=headers)
        assert response.status_code == 400

    def test_revoke_not_owner(self, client, db, test_org):
        from models.invitation import Invitation
        from models.user import User
        from core.security import get_password_hash

        other = User(
            id=str(uuid.uuid4()),
            email="notowner@example.com",
            password_hash=get_password_hash("password"),
            name="Not Owner",
            is_active=True,
            is_superuser=False,
        )
        db.add(other)
        db.commit()

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="revokenonowner@example.com",
            role="member",
            token="revoke-notowner-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "notowner@example.com", "password": "password"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.delete(f"/api/invitations/{invitation.id}", headers=headers)
        assert response.status_code == 403

    def test_accept_already_member(self, client, db, test_org, test_user):
        from models.invitation import Invitation

        invitation = Invitation(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            email="test@example.com",
            role="member",
            token="already-member-token",
            expires_at=datetime.now(timezone.utc) + timedelta(days=1),
            status="pending",
        )
        db.add(invitation)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.post("/api/invitations/already-member-token/accept", headers=headers)
        assert response.status_code == 409