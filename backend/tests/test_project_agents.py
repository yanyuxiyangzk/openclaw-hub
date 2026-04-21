import pytest
import uuid
from models.agent import Agent
from models.project import Project
from models.project_agent import ProjectAgent
from models.project_member import ProjectMember


class TestListProjectAgents:
    """GET /api/projects/{id}/agents - List project agents (T-270)"""

    def test_list_project_agents_success(self, client, auth_headers, test_org, db, test_user):
        """T-270: List project agents - success case"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Project Agent One",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        project_agent = ProjectAgent(
            id=str(uuid.uuid4()),
            project_id=project.id,
            agent_id=agent.id,
        )
        db.add(project_agent)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] >= 1
        assert any(item["agent_id"] == agent.id for item in data["data"]["items"])

    def test_list_project_agents_unauthorized(self, client, test_org, db, test_user):
        """T-271: List project agents - unauthorized access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents")
        assert response.status_code == 401

    def test_list_project_agents_not_member(self, client, auth_headers, test_org, db, test_user):
        """T-271: List project agents - not a project member"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Private Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents", headers=auth_headers)
        assert response.status_code == 403

    def test_list_project_agents_project_not_found(self, client, auth_headers):
        """T-271: List project agents - project not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/projects/{fake_id}/agents", headers=auth_headers)
        assert response.status_code == 404


class TestListAvailableAgents:
    """GET /api/projects/{id}/agents/available - List available agents (T-272)"""

    def test_list_available_agents_success(self, client, auth_headers, test_org, db, test_user):
        """T-272: List available agents - success case"""
        available_agent = Agent(
            id=str(uuid.uuid4()),
            name="Available Agent",
            description="Can be assigned",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(available_agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents/available", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert any(a["name"] == "Available Agent" for a in data["data"])

    def test_list_available_agents_unauthorized(self, client, test_org, db, test_user):
        """T-273: List available agents - unauthorized access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents/available")
        assert response.status_code == 401

    def test_list_available_agents_not_member(self, client, auth_headers, test_org, db, test_user):
        """T-273: List available agents - not a project member"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Private Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/agents/available", headers=auth_headers)
        assert response.status_code == 403


class TestAssignAgentToProject:
    """POST /api/projects/{id}/agents - Assign Agent to project (T-274)"""

    def test_assign_agent_to_project_success(self, client, auth_headers, test_org, db, test_user):
        """T-274: Assign agent to project - success case"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="To Be Assigned Agent",
            description="Will be assigned",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/agents", headers=auth_headers, json={
            "agent_id": agent.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["project_id"] == project.id

    def test_assign_agent_to_project_unauthorized(self, client, test_org, db, test_user):
        """T-275: Assign agent to project - unauthorized"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/agents", json={
            "agent_id": agent.id
        })
        assert response.status_code == 401

    def test_assign_agent_to_project_not_admin(self, client, auth_headers, test_org, db, test_user):
        """T-275: Assign agent to project - not admin/owner"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="member",
        )
        db.add(member)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/agents", headers=auth_headers, json={
            "agent_id": agent.id
        })
        assert response.status_code == 403

    def test_assign_agent_to_project_agent_not_found(self, client, auth_headers, test_org, db, test_user):
        """T-275: Assign agent to project - agent not found"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/agents", headers=auth_headers, json={
            "agent_id": str(uuid.uuid4())
        })
        assert response.status_code == 404

    def test_assign_agent_to_project_missing_agent_id(self, client, auth_headers, test_org, db, test_user):
        """T-275: Assign agent to project - missing agent_id"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.post(f"/api/projects/{project.id}/agents", headers=auth_headers, json={})
        assert response.status_code == 400


class TestRemoveProjectAgent:
    """DELETE /api/projects/{id}/agents/{agent_id} - Remove Agent from project (T-276)"""

    def test_remove_project_agent_success(self, client, auth_headers, test_org, db, test_user):
        """T-276: Remove agent from project - success case"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="To Be Removed Agent",
            description="Will be removed",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        project_agent = ProjectAgent(
            id=str(uuid.uuid4()),
            project_id=project.id,
            agent_id=agent.id,
        )
        db.add(project_agent)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "removed" in data["message"].lower()

    def test_remove_project_agent_unauthorized(self, client, test_org, db, test_user):
        """T-277: Remove agent from project - unauthorized"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        project_agent = ProjectAgent(
            id=str(uuid.uuid4()),
            project_id=project.id,
            agent_id=agent.id,
        )
        db.add(project_agent)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/agents/{agent.id}")
        assert response.status_code == 401

    def test_remove_project_agent_not_admin(self, client, auth_headers, test_org, db, test_user):
        """T-277: Remove agent from project - not admin/owner"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="member",
        )
        db.add(member)

        project_agent = ProjectAgent(
            id=str(uuid.uuid4()),
            project_id=project.id,
            agent_id=agent.id,
        )
        db.add(project_agent)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 403

    def test_remove_project_agent_not_assigned(self, client, auth_headers, test_org, db, test_user):
        """T-277: Remove agent from project - agent not assigned to project"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Unassigned Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)
        db.commit()

        response = client.delete(f"/api/projects/{project.id}/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 404

    def test_remove_project_agent_project_not_found(self, client, auth_headers, test_org, db):
        """T-277: Remove agent from project - project not found"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.delete(f"/api/projects/{str(uuid.uuid4())}/agents/{agent.id}", headers=auth_headers)
        assert response.status_code == 404
