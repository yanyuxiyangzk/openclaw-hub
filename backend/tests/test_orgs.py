import pytest


class TestOrgCreate:
    def test_create_org_success(self, client, auth_headers):
        response = client.post("/api/orgs", headers=auth_headers, json={
            "name": "My New Organization"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "My New Organization"
        assert data["data"]["owner_id"] is not None


class TestOrgList:
    def test_list_my_orgs(self, client, auth_headers, test_org):
        response = client.get("/api/orgs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1


class TestOrgGet:
    def test_get_org_success(self, client, auth_headers, test_org):
        response = client.get(f"/api/orgs/{test_org.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == test_org.id

    def test_get_org_not_found(self, client, auth_headers):
        response = client.get("/api/orgs/nonexistent-id", headers=auth_headers)
        assert response.status_code == 404


class TestOrgUpdate:
    def test_update_org_as_owner(self, client, auth_headers, test_org):
        response = client.put(f"/api/orgs/{test_org.id}", headers=auth_headers, json={
            "name": "Updated Org Name"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Org Name"


class TestOrgDelete:
    def test_delete_org_as_owner(self, client, auth_headers, db, test_user):
        from models.organization import Organization, OrganizationMember
        import uuid

        org = Organization(
            id=str(uuid.uuid4()),
            name="Org To Delete",
            owner_id=test_user.id,
        )
        db.add(org)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=org.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.delete(f"/api/orgs/{org.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0


class TestOrgMembers:
    def test_list_members(self, client, auth_headers, test_org):
        response = client.get(f"/api/orgs/{test_org.id}/members", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

    def test_remove_member(self, client, auth_headers, db, test_org, test_user):
        from models.organization import OrganizationMember
        from models.user import User
        import uuid

        new_user = User(
            id=str(uuid.uuid4()),
            email="member@example.com",
            password_hash="hash",
            name="Member User",
            is_active=True,
            is_superuser=False,
        )
        db.add(new_user)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            user_id=new_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        response = client.delete(f"/api/orgs/{test_org.id}/members/{new_user.id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["code"] == 0


class TestOrgInvitation:
    def test_create_invitation(self, client, auth_headers, test_org):
        response = client.post(f"/api/orgs/{test_org.id}/invitations", headers=auth_headers, json={
            "email": "invitee@example.com",
            "role": "member"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["email"] == "invitee@example.com"
        assert data["data"]["status"] == "pending"


class TestOrgAccessDenied:
    def test_get_org_not_member(self, client, db, test_org):
        from models.user import User
        from core.security import get_password_hash
        import uuid

        other = User(
            id=str(uuid.uuid4()),
            email="other@example.com",
            password_hash=get_password_hash("password123"),
            name="Other User",
            is_active=True,
            is_superuser=False,
        )
        db.add(other)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "other@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.get(f"/api/orgs/{test_org.id}", headers=headers)
        assert response.status_code == 403

    def test_update_org_not_owner(self, client, db, test_org):
        from models.user import User
        from models.organization import OrganizationMember
        from core.security import get_password_hash
        import uuid

        member_user = User(
            id=str(uuid.uuid4()),
            email="member2@example.com",
            password_hash=get_password_hash("password123"),
            name="Member User",
            is_active=True,
            is_superuser=False,
        )
        db.add(member_user)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            user_id=member_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "member2@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.put(f"/api/orgs/{test_org.id}", headers=headers, json={"name": "Hacked"})
        assert response.status_code == 403

    def test_delete_org_not_owner(self, client, db, test_org):
        from models.user import User
        from models.organization import OrganizationMember
        from core.security import get_password_hash
        import uuid

        member_user = User(
            id=str(uuid.uuid4()),
            email="member3@example.com",
            password_hash=get_password_hash("password123"),
            name="Member User 3",
            is_active=True,
            is_superuser=False,
        )
        db.add(member_user)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            user_id=member_user.id,
            role="admin",
        )
        db.add(member)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "member3@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.delete(f"/api/orgs/{test_org.id}", headers=headers)
        assert response.status_code == 403

    def test_remove_member_not_admin(self, client, db, test_org):
        from models.user import User
        from models.organization import OrganizationMember
        from core.security import get_password_hash
        import uuid

        member_user = User(
            id=str(uuid.uuid4()),
            email="member4@example.com",
            password_hash=get_password_hash("password123"),
            name="Member User 4",
            is_active=True,
            is_superuser=False,
        )
        db.add(member_user)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            user_id=member_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "member4@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.delete(f"/api/orgs/{test_org.id}/members/{member_user.id}", headers=headers)
        assert response.status_code == 403

    def test_remove_owner_forbidden(self, client, auth_headers, test_org, test_user):
        response = client.delete(f"/api/orgs/{test_org.id}/members/{test_user.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_create_invitation_not_admin(self, client, db, test_org):
        from models.user import User
        from models.organization import OrganizationMember
        from core.security import get_password_hash
        import uuid

        member_user = User(
            id=str(uuid.uuid4()),
            email="member5@example.com",
            password_hash=get_password_hash("password123"),
            name="Member User 5",
            is_active=True,
            is_superuser=False,
        )
        db.add(member_user)
        db.commit()

        member = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=test_org.id,
            user_id=member_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        login = client.post("/api/auth/login", json={"email": "member5@example.com", "password": "password123"})
        headers = {"Authorization": f"Bearer {login.json()['data']['access_token']}"}

        response = client.post(f"/api/orgs/{test_org.id}/invitations", headers=headers, json={
            "email": "newinvite@example.com",
            "role": "member"
        })
        assert response.status_code == 403