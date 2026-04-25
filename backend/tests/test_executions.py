import pytest
import uuid
import json
from models.task import Task
from models.project import Project
from models.project_member import ProjectMember
from models.agent import Agent
from models.execution import Execution, ExecutionStatus


class TestTriggerExecution:
    """POST /api/tasks/{id}/execute - Trigger task execution (T-501)"""

    def test_trigger_execution_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Execution Test Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Task to Execute",
            description="A task to execute",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="An agent for testing",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/execute", headers=auth_headers, json={
            "task_id": task.id,
            "agent_id": agent.id,
            "input_data": {"action": "start"}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["task_id"] == task.id
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["status"] == "pending"

    def test_trigger_execution_task_not_found(self, client, auth_headers, test_org, db, test_user):
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="An agent for testing",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/execute", headers=auth_headers, json={
            "task_id": str(uuid.uuid4()),
            "agent_id": agent.id,
        })
        assert response.status_code == 404

    def test_trigger_execution_agent_not_found(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Execution Test Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Task to Execute",
            description="A task to execute",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/execute", headers=auth_headers, json={
            "task_id": task.id,
            "agent_id": str(uuid.uuid4()),
        })
        assert response.status_code == 404

    def test_trigger_execution_unauthorized(self, client, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Execution Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        task = Task(
            id=str(uuid.uuid4()),
            title="Task to Execute",
            description="A task to execute",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="An agent for testing",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/execute", json={
            "task_id": task.id,
            "agent_id": agent.id,
        })
        assert response.status_code == 401


class TestBatchExecute:
    """POST /api/tasks/{id}/execute/batch - Batch execution (T-502)"""

    def test_batch_execute_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Batch Execution Project",
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

        task1 = Task(
            id=str(uuid.uuid4()),
            title="Task 1",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task 2",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/tasks/{task1.id}/execute/batch", headers=auth_headers, json={
            "task_ids": [task2.id],
            "agent_id": agent.id,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2


class TestListExecutions:
    """GET /api/executions - List all executions with optional status filter (T-530)"""

    def test_list_executions_all(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="List Executions Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution1 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.pending.value,
        )
        execution2 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        db.add_all([execution1, execution2])
        db.commit()

        response = client.get("/api/executions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2

    def test_list_executions_filter_by_status(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Filter Executions Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution1 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.pending.value,
        )
        execution2 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        db.add_all([execution1, execution2])
        db.commit()

        response = client.get("/api/executions?status=completed", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 1
        assert data["data"]["items"][0]["status"] == "completed"


class TestGetExecution:
    """GET /api/executions/{id} - Execution record detail (T-503)"""

    def test_get_execution_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Get Execution Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.pending.value,
        )
        db.add(execution)
        db.commit()

        response = client.get(f"/api/executions/{execution.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == execution.id
        assert data["data"]["status"] == "pending"

    def test_get_execution_not_found(self, client, auth_headers):
        response = client.get(f"/api/executions/{str(uuid.uuid4())}", headers=auth_headers)
        assert response.status_code == 404


class TestGetTaskExecutions:
    """GET /api/tasks/{id}/executions - Task execution history (T-504)"""

    def test_get_task_executions_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Task Executions Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution1 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.pending.value,
        )
        execution2 = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        db.add_all([execution1, execution2])
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/executions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2


class TestCancelExecution:
    """POST /api/executions/{id}/cancel - Cancel execution (T-505)"""

    def test_cancel_execution_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Cancel Execution Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.pending.value,
        )
        db.add(execution)
        db.commit()

        response = client.post(f"/api/executions/{execution.id}/cancel", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "cancelled"

    def test_cancel_execution_already_completed(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Cancel Completed Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        db.add(execution)
        db.commit()

        response = client.post(f"/api/executions/{execution.id}/cancel", headers=auth_headers)
        assert response.status_code == 400


class TestRetryExecution:
    """POST /api/executions/{id}/retry - Retry execution (T-506)"""

    def test_retry_execution_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Retry Execution Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.failed.value,
        )
        db.add(execution)
        db.commit()

        response = client.post(f"/api/executions/{execution.id}/retry", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "pending"

    def test_retry_execution_not_failed(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Retry Running Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.running.value,
        )
        db.add(execution)
        db.commit()

        response = client.post(f"/api/executions/{execution.id}/retry", headers=auth_headers)
        assert response.status_code == 400


class TestGetExecutionOutput:
    """GET /api/executions/{id}/output - Execution output (T-507)"""

    def test_get_execution_output_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Output Execution Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
            output_data='{"result": "success"}',
        )
        db.add(execution)
        db.commit()

        response = client.get(f"/api/executions/{execution.id}/output", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "completed"


class TestGetActiveExecutions:
    """GET /api/executions/active - Current active executions (T-508)"""

    def test_get_active_executions_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Active Executions Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.running.value,
        )
        db.add(execution)
        db.commit()

        response = client.get("/api/executions/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1

    def test_get_active_executions_empty(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="No Active Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            project_id=project.id,
            status="todo",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            agent_type="hermes",
            config='{}',
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        execution = Execution(
            id=str(uuid.uuid4()),
            task_id=task.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        db.add(execution)
        db.commit()

        response = client.get("/api/executions/active", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0