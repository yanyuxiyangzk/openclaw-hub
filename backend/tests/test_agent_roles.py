import pytest
import uuid
from models.agent_role import AgentRole
from core.security import get_password_hash


class TestListAgentRoles:
    def test_list_agent_roles_success(self, client, auth_headers, test_org, db):
        """GET /api/agent-roles - List Agent Roles (T-301)"""
        # Create some agent roles
        role1 = AgentRole(
            id=str(uuid.uuid4()),
            name="Developer",
            description="Developer role",
            org_id=test_org.id,
        )
        role2 = AgentRole(
            id=str(uuid.uuid4()),
            name="Designer",
            description="Designer role",
            org_id=test_org.id,
        )
        db.add(role1)
        db.add(role2)
        db.commit()

        response = client.get("/api/agent-roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 2
        names = [r["name"] for r in data["data"]]
        assert "Developer" in names
        assert "Designer" in names

    def test_list_agent_roles_empty(self, client, auth_headers, test_org):
        """GET /api/agent-roles - Empty list"""
        response = client.get("/api/agent-roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_list_agent_roles_unauthorized(self, client):
        """GET /api/agent-roles - Unauthorized"""
        response = client.get("/api/agent-roles")
        assert response.status_code == 401

    def test_list_agent_roles_no_org(self, client, auth_headers, db):
        """GET /api/agent-roles - User without org returns 400"""
        # Create user without organization membership
        from models.user import User
        from models.organization import Organization

        new_user = User(
            id=str(uuid.uuid4()),
            email="noorg@test.com",
            password_hash=get_password_hash("dummy"),
            name="No Org User",
        )
        db.add(new_user)
        db.commit()

        # Login as the new user
        login_resp = client.post("/api/auth/login", json={
            "email": "noorg@test.com",
            "password": "dummy"
        })
        token = login_resp.json().get("data", {}).get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/agent-roles", headers=headers)
        assert response.status_code == 400


class TestCreateAgentRole:
    def test_create_agent_role_success(self, client, auth_headers, test_org):
        """POST /api/agent-roles - Create Agent Role (T-302)"""
        response = client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={
                "name": "Developer",
                "description": "Software developer role",
                "system_prompt_template": "You are a helpful developer.",
                "default_config": {"temperature": 0.7}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Developer"
        assert data["data"]["description"] == "Software developer role"
        assert data["data"]["system_prompt_template"] == "You are a helpful developer."
        assert data["data"]["default_config"]["temperature"] == 0.7
        assert data["data"]["org_id"] == test_org.id
        assert "id" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]

    def test_create_agent_role_minimal(self, client, auth_headers, test_org):
        """POST /api/agent-roles - Create with only required fields"""
        response = client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={"name": "Minimal Role"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Minimal Role"
        assert data["data"]["description"] is None
        assert data["data"]["system_prompt_template"] is None

    def test_create_agent_role_duplicate_name(self, client, auth_headers, test_org):
        """POST /api/agent-roles - Duplicate name conflict"""
        # Create first role
        client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={"name": "Unique Role", "description": "First"}
        )
        # Try to create second with same name
        response = client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={"name": "Unique Role", "description": "Second"}
        )
        assert response.status_code == 409
        data = response.json()
        assert data["code"] == 40902
        assert "already exists" in data["message"]

    def test_create_agent_role_unauthorized(self, client, test_org):
        """POST /api/agent-roles - Unauthorized (no token)"""
        response = client.post(
            "/api/agent-roles",
            json={"name": "Unauthorized Role"}
        )
        assert response.status_code == 401

    def test_create_agent_role_same_name_different_org(self, client, auth_headers, db, test_org, test_user):
        """POST /api/agent-roles - Same name allowed in different org"""
        # Create role in test_org
        client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={"name": "Org Role"}
        )
        # Create another org
        from models.organization import Organization, OrganizationMember
        org2 = Organization(
            id=str(uuid.uuid4()),
            name="Other Organization",
            owner_id=test_user.id,
        )
        db.add(org2)
        member2 = OrganizationMember(
            id=str(uuid.uuid4()),
            org_id=org2.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member2)
        db.commit()
        # Create role with same name in different org - this requires specifying org_id
        response = client.post(
            "/api/agent-roles",
            headers=auth_headers,
            json={"name": "Org Role", "org_id": org2.id}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Org Role"
        assert data["data"]["org_id"] == org2.id


class TestGetAgentRole:
    def test_get_agent_role_success(self, client, auth_headers, test_org, db):
        """GET /api/agent-roles/{id} - Get Agent Role (T-303)"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Test Role",
            description="Test description",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.get(f"/api/agent-roles/{agent_role.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == agent_role.id
        assert data["data"]["name"] == "Test Role"
        assert data["data"]["description"] == "Test description"

    def test_get_agent_role_not_found(self, client, auth_headers):
        """GET /api/agent-roles/{id} - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agent-roles/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_get_agent_role_unauthorized(self, client, test_org, db):
        """GET /api/agent-roles/{id} - Unauthorized"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Unauthorized Role",
            description="Test",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.get(f"/api/agent-roles/{agent_role.id}")
        assert response.status_code == 401

    def test_get_agent_role_access_denied(self, client, auth_headers, db):
        """GET /api/agent-roles/{id} - Access denied (different org)"""
        fake_org_id = str(uuid.uuid4())
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Other Org Role",
            description="Test",
            org_id=fake_org_id,
        )
        db.add(agent_role)
        db.commit()

        response = client.get(f"/api/agent-roles/{agent_role.id}", headers=auth_headers)
        assert response.status_code == 403


class TestUpdateAgentRole:
    def test_update_agent_role_success(self, client, auth_headers, test_org, db):
        """PUT /api/agent-roles/{id} - Update Agent Role (T-304)"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Original Name",
            description="Original description",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"name": "Updated Name", "description": "Updated description"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["description"] == "Updated description"

    def test_update_agent_role_partial(self, client, auth_headers, test_org, db):
        """PUT /api/agent-roles/{id} - Partial update (only name)"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Original Name",
            description="Original description",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"name": "New Name Only"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "New Name Only"
        assert data["data"]["description"] == "Original description"

    def test_update_agent_role_not_found(self, client, auth_headers):
        """PUT /api/agent-roles/{id} - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.put(
            f"/api/agent-roles/{fake_id}",
            headers=auth_headers,
            json={"name": "New Name"}
        )
        assert response.status_code == 404

    def test_update_agent_role_unauthorized(self, client, test_org, db):
        """PUT /api/agent-roles/{id} - Unauthorized"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Unauthorized Update",
            description="Test",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            json={"name": "New Name"}
        )
        assert response.status_code == 401

    def test_update_agent_role_access_denied(self, client, auth_headers, db):
        """PUT /api/agent-roles/{id} - Access denied (different org)"""
        fake_org_id = str(uuid.uuid4())
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Other Org Role",
            description="Test",
            org_id=fake_org_id,
        )
        db.add(agent_role)
        db.commit()

        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"name": "Hacked Name"}
        )
        assert response.status_code == 403

    def test_update_agent_role_duplicate_name(self, client, auth_headers, test_org, db):
        """PUT /api/agent-roles/{id} - Duplicate name conflict"""
        role1 = AgentRole(
            id=str(uuid.uuid4()),
            name="Role One",
            description="First",
            org_id=test_org.id,
        )
        role2 = AgentRole(
            id=str(uuid.uuid4()),
            name="Role Two",
            description="Second",
            org_id=test_org.id,
        )
        db.add(role1)
        db.add(role2)
        db.commit()

        response = client.put(
            f"/api/agent-roles/{role1.id}",
            headers=auth_headers,
            json={"name": "Role Two"}
        )
        assert response.status_code == 409

    def test_update_agent_role_default_config(self, client, auth_headers, test_org, db):
        """PUT /api/agent-roles/{id} - Update default_config (T-304)"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Test Role",
            description="Test description",
            org_id=test_org.id,
            default_config=None,
        )
        db.add(agent_role)
        db.commit()

        # Update with default_config
        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"default_config": {"temperature": 0.7, "top_p": 0.9}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["default_config"]["temperature"] == 0.7
        assert data["data"]["default_config"]["top_p"] == 0.9

        # Update again with different default_config
        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"default_config": {"temperature": 0.5}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["default_config"]["temperature"] == 0.5

        # Partial update - name only, default_config should remain unchanged
        response = client.put(
            f"/api/agent-roles/{agent_role.id}",
            headers=auth_headers,
            json={"name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name"
        assert data["data"]["default_config"]["temperature"] == 0.5  # unchanged


class TestDeleteAgentRole:
    def test_delete_agent_role_success(self, client, auth_headers, test_org, db):
        """DELETE /api/agent-roles/{id} - Delete Agent Role (T-305)"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Delete Me",
            description="To be deleted",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.delete(f"/api/agent-roles/{agent_role.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "deleted" in data["message"].lower()

        # Verify it's actually deleted from DB
        deleted = db.query(AgentRole).filter(AgentRole.id == agent_role.id).first()
        assert deleted is None

    def test_delete_agent_role_not_found(self, client, auth_headers):
        """DELETE /api/agent-roles/{id} - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/agent-roles/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_agent_role_unauthorized(self, client, test_org, db):
        """DELETE /api/agent-roles/{id} - Unauthorized"""
        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Unauthorized Delete",
            description="Test",
            org_id=test_org.id,
        )
        db.add(agent_role)
        db.commit()

        response = client.delete(f"/api/agent-roles/{agent_role.id}")
        assert response.status_code == 401

    def test_delete_agent_role_access_denied(self, client, auth_headers, test_org, db):
        """DELETE /api/agent-roles/{id} - Access denied (different org)"""
        # Create agent role in an org the test user doesn't belong to
        # Use a random org_id that definitely doesn't match test_org
        fake_org_id = str(uuid.uuid4())

        agent_role = AgentRole(
            id=str(uuid.uuid4()),
            name="Other Org Role",
            description="Test",
            org_id=fake_org_id,
        )
        db.add(agent_role)
        db.commit()

        response = client.delete(f"/api/agent-roles/{agent_role.id}", headers=auth_headers)
        assert response.status_code == 403