import pytest
import uuid
import json
from models.workflow import Workflow
from models.task import Task
from models.agent import Agent
from models.project import Project
from models.project_member import ProjectMember


class TestCreateWorkflow:
    def test_create_workflow_success(self, client, auth_headers, test_org, db):
        """POST /api/workflows - Create workflow (T-520)"""
        # Create a project first
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            org_id=test_org.id,
            status="active",
            created_by=test_org.owner_id,
        )
        db.add(project)
        db.commit()

        # Create a task
        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            description="Test Description",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_org.owner_id,
        )
        db.add(task)
        db.commit()

        # Create an agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test Agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.post("/api/workflows", headers=auth_headers, json={
            "name": "Test Workflow",
            "description": "A test workflow",
            "steps": [
                {
                    "step_id": "step1",
                    "name": "Step 1",
                    "task_template_id": task.id,
                    "agent_id": agent.id,
                    "depends_on": [],
                    "config": {}
                }
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Test Workflow"
        assert data["data"]["description"] == "A test workflow"

    def test_create_workflow_unauthorized(self, client, test_org):
        """POST /api/workflows - Unauthorized"""
        response = client.post("/api/workflows", json={
            "name": "Test Workflow",
            "steps": []
        })
        assert response.status_code == 401


class TestGetWorkflow:
    def test_get_workflow_success(self, client, auth_headers, test_org, db):
        """GET /api/workflows/{id} - Get workflow detail (T-521)"""
        # Create a project
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            org_id=test_org.id,
            status="active",
            created_by=test_org.owner_id,
        )
        db.add(project)
        db.commit()

        # Create a task
        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_org.owner_id,
        )
        db.add(task)
        db.commit()

        # Create an agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        # Create a workflow
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Get Workflow Test",
            description="Test",
            steps=json.dumps([{"step_id": "s1", "name": "Step 1", "task_template_id": task.id, "agent_id": agent.id}]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.get(f"/api/workflows/{workflow.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Get Workflow Test"

    def test_get_workflow_not_found(self, client, auth_headers):
        """GET /api/workflows/{id} - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/workflows/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


class TestExecuteWorkflow:
    def test_execute_workflow_success(self, client, auth_headers, test_org, db):
        """POST /api/workflows/{id}/execute - Execute workflow (T-522)"""
        # Create a project
        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            org_id=test_org.id,
            status="active",
            created_by=test_org.owner_id,
        )
        db.add(project)
        db.commit()

        # Create a task
        task = Task(
            id=str(uuid.uuid4()),
            title="Execute Task",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_org.owner_id,
        )
        db.add(task)
        db.commit()

        # Create an agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Execute Agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        # Create a workflow
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Execute Workflow Test",
            description="Test",
            steps=json.dumps([{"step_id": "s1", "name": "Step 1", "task_template_id": task.id, "agent_id": agent.id}]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.post(f"/api/workflows/{workflow.id}/execute", headers=auth_headers, json={
            "input_data": {"key": "value"},
            "agent_id": agent.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 1
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["task_id"] == task.id
        assert data["data"]["items"][0]["agent_id"] == agent.id

    def test_execute_workflow_not_found(self, client, auth_headers):
        """POST /api/workflows/{id}/execute - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/workflows/{fake_id}/execute", headers=auth_headers, json={})
        assert response.status_code == 404

    def test_execute_workflow_no_steps(self, client, auth_headers, test_org, db):
        """POST /api/workflows/{id}/execute - Workflow with no steps"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Empty Workflow",
            description="Test",
            steps=json.dumps([]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.post(f"/api/workflows/{workflow.id}/execute", headers=auth_headers, json={})
        assert response.status_code == 404


class TestListWorkflows:
    def test_list_workflows_success(self, client, auth_headers, test_org, db):
        """GET /api/workflows - List workflows"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="List Workflow Test",
            description="Test",
            steps=json.dumps([]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.get("/api/workflows", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

    def test_list_workflows_by_org(self, client, auth_headers, test_org, db):
        """GET /api/workflows?org_id=X - List workflows by org"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Org Workflow Test",
            description="Test",
            steps=json.dumps([]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.get(f"/api/workflows?org_id={test_org.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestUpdateWorkflow:
    def test_update_workflow_success(self, client, auth_headers, test_org, db):
        """PUT /api/workflows/{id} - Update workflow"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Update Workflow Test",
            description="Original",
            steps=json.dumps([]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.put(f"/api/workflows/{workflow.id}", headers=auth_headers, json={
            "name": "Updated Workflow",
            "description": "Updated description"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "Updated Workflow"
        assert data["data"]["description"] == "Updated description"


class TestDeleteWorkflow:
    def test_delete_workflow_success(self, client, auth_headers, test_org, db):
        """DELETE /api/workflows/{id} - Delete workflow"""
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name="Delete Workflow Test",
            description="Test",
            steps=json.dumps([]),
            org_id=test_org.id,
            created_by=test_org.owner_id,
        )
        db.add(workflow)
        db.commit()

        response = client.delete(f"/api/workflows/{workflow.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "deleted" in data["message"].lower()