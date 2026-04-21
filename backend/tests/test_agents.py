import pytest
import uuid
from models.agent import Agent


class TestCreateAgent:
    def test_create_agent_success(self, client, auth_headers, test_org):
        """POST /api/agents - Create Agent"""
        response = client.post("/api/agents", headers=auth_headers, json={
            "name": "Test Agent",
            "description": "A test agent",
            "agent_type": "hermes",
            "org_id": test_org.id,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Test Agent"
        assert data["data"]["agent_type"] == "hermes"
        assert data["data"]["status"] == "offline"

    def test_create_agent_unauthorized(self, client, test_org):
        """POST /api/agents - Unauthorized"""
        response = client.post("/api/agents", json={
            "name": "Test Agent",
            "org_id": test_org.id,
        })
        assert response.status_code == 401


class TestListAgents:
    def test_list_agents_success(self, client, auth_headers, test_org, db):
        """GET /api/agents - List Agents"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Listed Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get("/api/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1
        assert any(a["name"] == "Listed Agent" for a in data["data"])


class TestGetAgent:
    def test_get_agent_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id} - Get Agent detail"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Get Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Get Agent"

    def test_get_agent_not_found(self, client, auth_headers):
        """GET /api/agents/{id} - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateAgent:
    def test_update_agent_success(self, client, auth_headers, test_org, db):
        """PUT /api/agents/{id} - Update Agent"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Update Agent",
            description="Original",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.put(f"/api/agents/{agent.id}", headers=auth_headers, json={
            "name": "Updated Agent",
            "description": "Updated description",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Agent"
        assert data["data"]["description"] == "Updated description"


class TestDeleteAgent:
    def test_delete_agent_success(self, client, auth_headers, test_org, db):
        """DELETE /api/agents/{id} - Delete Agent (soft delete)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Delete Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.delete(f"/api/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "deleted" in data["message"].lower()

        db.refresh(agent)
        assert agent.status == "deleted"


class TestAgentStatus:
    def test_get_agent_status_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/status - Get Agent status"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Status Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "online"


class TestAgentJoinProject:
    def test_agent_join_project_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/projects/{project_id} - Agent joins project"""
        from models.project import Project
        from models.project_member import ProjectMember

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Join Project Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            org_id=test_org.id,
            status="active",
            created_by=agent.org_id,
        )
        db.add(project)
        db.commit()

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=agent.org_id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/projects/{project.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project_id"] == project.id
        assert data["data"]["agent_id"] == agent.id


class TestStartAgent:
    def test_start_agent_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/start - Start Agent (T-230)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Start Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/start", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "online"
        assert "started" in data["data"]["message"].lower()

    def test_start_agent_not_found(self, client, auth_headers):
        """POST /api/agents/{id}/start - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/agents/{fake_id}/start", headers=auth_headers)
        assert response.status_code == 404


class TestStopAgent:
    def test_stop_agent_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/stop - Stop Agent (T-231)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Stop Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/stop", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "offline"
        assert "stopped" in data["data"]["message"].lower()

    def test_stop_agent_not_found(self, client, auth_headers):
        """POST /api/agents/{id}/stop - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/agents/{fake_id}/stop", headers=auth_headers)
        assert response.status_code == 404


class TestAgentLogs:
    def test_get_agent_logs_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/logs - Get Agent Logs (T-232)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Logs Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/logs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "logs" in data["data"]
        assert "total" in data["data"]

    def test_get_agent_logs_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/logs - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/logs", headers=auth_headers)
        assert response.status_code == 404


class TestAgentHealth:
    def test_get_agent_health_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/health - Get Agent Health (T-233)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Health Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/health", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["healthy"] is True
        assert "cpu_percent" in data["data"]
        assert "memory_mb" in data["data"]
        assert "uptime_seconds" in data["data"]

    def test_get_agent_health_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/health - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/health", headers=auth_headers)
        assert response.status_code == 404


class TestListActiveAgents:
    def test_list_active_agents_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/active - List Active Agents (T-234)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Active Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get("/api/agents/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert any(a["name"] == "Active Agent" for a in data["data"])

    def test_list_active_agents_none_found(self, client, auth_headers, test_org, db):
        """GET /api/agents/active - No active agents"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Inactive Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get("/api/agents/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert all(a["status"] in ("online", "busy") for a in data["data"])
