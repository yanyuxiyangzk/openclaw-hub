import pytest
import uuid
from models.scheduler_job import SchedulerJob
from models.task import Task
from models.agent import Agent
from models.project import Project
from models.project_member import ProjectMember


class TestListSchedulerJobs:
    """Tests for GET /api/scheduler/jobs (T-511)"""

    def test_list_jobs_empty(self, client, auth_headers):
        """GET /api/scheduler/jobs - Empty list when no jobs"""
        response = client.get("/api/scheduler/jobs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["items"] == []
        assert data["data"]["total"] == 0

    def test_list_jobs_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/scheduler/jobs - List jobs for accessible tasks"""
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Scheduler Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        # Add user as project member
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            description="Test task for scheduler",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_user.id,
        )
        db.add(task)

        # Create agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Scheduler Test Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        # Create scheduler job
        job = SchedulerJob(
            id=str(uuid.uuid4()),
            name="Test Scheduler Job",
            task_template_id=task.id,
            cron_expression="0 9 * * *",
            agent_id=agent.id,
            enabled=True,
        )
        db.add(job)
        db.commit()

        response = client.get("/api/scheduler/jobs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1
        job_data = next((j for j in data["data"]["items"] if j["name"] == "Test Scheduler Job"), None)
        assert job_data is not None
        assert job_data["cron_expression"] == "0 9 * * *"
        assert job_data["enabled"] is True

    def test_list_jobs_unauthorized(self, client):
        """GET /api/scheduler/jobs - Unauthorized without token"""
        response = client.get("/api/scheduler/jobs")
        assert response.status_code == 401

    def test_list_jobs_filters_by_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/scheduler/jobs - Only shows jobs for accessible tasks"""
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Accessible Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        # Add user as project member
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Accessible Task",
            description="Task user can access",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_user.id,
        )
        db.add(task)

        # Create agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Accessible Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        # Create scheduler job for accessible task
        job = SchedulerJob(
            id=str(uuid.uuid4()),
            name="Accessible Job",
            task_template_id=task.id,
            cron_expression="0 9 * * *",
            agent_id=agent.id,
            enabled=True,
        )
        db.add(job)
        db.commit()

        response = client.get("/api/scheduler/jobs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        # Job should appear in the list since user has access to the task's project
        assert any(j["name"] == "Accessible Job" for j in data["data"]["items"])


class TestCreateSchedulerJob:
    """Tests for POST /api/scheduler/jobs (T-510)"""

    def test_create_job_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/scheduler/jobs - Create scheduled job"""
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Create Job Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        # Add user as project member
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Job Task",
            description="Task for scheduled job",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_user.id,
        )
        db.add(task)

        # Create agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Job Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.post("/api/scheduler/jobs", headers=auth_headers, json={
            "name": "New Scheduler Job",
            "task_template_id": task.id,
            "cron_expression": "0 9 * * *",
            "agent_id": agent.id,
            "enabled": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["name"] == "New Scheduler Job"
        assert data["data"]["cron_expression"] == "0 9 * * *"
        assert data["data"]["enabled"] is True

    def test_create_job_unauthorized(self, client, test_org, db, test_user):
        """POST /api/scheduler/jobs - Unauthorized without token"""
        response = client.post("/api/scheduler/jobs", json={
            "name": "Test Job",
            "task_template_id": str(uuid.uuid4()),
            "cron_expression": "0 9 * * *",
            "agent_id": str(uuid.uuid4()),
        })
        assert response.status_code == 401


class TestDeleteSchedulerJob:
    """Tests for DELETE /api/scheduler/jobs/{job_id} (T-512)"""

    def test_delete_job_success(self, client, auth_headers, test_org, db, test_user):
        """DELETE /api/scheduler/jobs/{id} - Delete scheduled job"""
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Delete Job Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        # Add user as project member
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Delete Task",
            description="Task to delete",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_user.id,
        )
        db.add(task)

        # Create agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Delete Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        # Create scheduler job
        job = SchedulerJob(
            id=str(uuid.uuid4()),
            name="Job To Delete",
            task_template_id=task.id,
            cron_expression="0 9 * * *",
            agent_id=agent.id,
            enabled=True,
        )
        db.add(job)
        db.commit()

        response = client.delete(f"/api/scheduler/jobs/{job.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_delete_job_not_found(self, client, auth_headers):
        """DELETE /api/scheduler/jobs/{id} - Job not found"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/scheduler/jobs/{fake_id}", headers=auth_headers)
        assert response.status_code == 404


class TestGetJobRuns:
    """Tests for GET /api/scheduler/jobs/{job_id}/runs (T-513)"""

    def test_get_job_runs_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/scheduler/jobs/{id}/runs - Empty runs list"""
        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Runs Job Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        # Add user as project member
        member = ProjectMember(
            id=str(uuid.uuid4()),
            project_id=project.id,
            user_id=test_user.id,
            role="owner",
        )
        db.add(member)

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Runs Task",
            description="Task with runs",
            status="todo",
            priority="medium",
            project_id=project.id,
            created_by=test_user.id,
        )
        db.add(task)

        # Create agent
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Runs Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)

        # Create scheduler job
        job = SchedulerJob(
            id=str(uuid.uuid4()),
            name="Job With Runs",
            task_template_id=task.id,
            cron_expression="0 9 * * *",
            agent_id=agent.id,
            enabled=True,
        )
        db.add(job)
        db.commit()

        response = client.get(f"/api/scheduler/jobs/{job.id}/runs", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["items"] == []
        assert data["data"]["total"] == 0

    def test_get_job_runs_not_found(self, client, auth_headers):
        """GET /api/scheduler/jobs/{id}/runs - Job not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/scheduler/jobs/{fake_id}/runs", headers=auth_headers)
        assert response.status_code == 404