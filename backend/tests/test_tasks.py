import pytest
import uuid
from models.task import Task, TaskStatus, TaskPriority
from models.project import Project
from models.project_member import ProjectMember
from models.user import User
from core.security import get_password_hash


class TestCreateTask:
    def test_create_task_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Task Test Project",
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

        response = client.post("/api/tasks", headers=auth_headers, json={
            "title": "Test Task",
            "description": "A test task",
            "project_id": project.id,
            "status": "todo",
            "priority": "medium"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Test Task"
        assert data["data"]["description"] == "A test task"
        assert data["data"]["project_id"] == project.id
        assert data["data"]["status"] == "todo"
        assert data["data"]["priority"] == "medium"

    def test_create_task_unauthorized(self, client, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Task Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.post("/api/tasks", json={
            "title": "Test Task",
            "project_id": project.id,
        })
        assert response.status_code == 401

    def test_create_task_project_not_found(self, client, auth_headers):
        response = client.post("/api/tasks", headers=auth_headers, json={
            "title": "Test Task",
            "project_id": str(uuid.uuid4()),
        })
        assert response.status_code == 404


class TestListTasks:
    def test_list_tasks_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="List Task Project",
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
            description="First task",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task 2",
            description="Second task",
            project_id=project.id,
            status="done",
            priority="low",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/api/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] >= 2

    def test_list_tasks_with_project_filter(self, client, auth_headers, test_org, db, test_user):
        project1 = Project(
            id=str(uuid.uuid4()),
            name="Project 1",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        project2 = Project(
            id=str(uuid.uuid4()),
            name="Project 2",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add_all([project1, project2])
        for p in [project1, project2]:
            member = ProjectMember(
                id=str(uuid.uuid4()),
                project_id=p.id,
                user_id=test_user.id,
                role="owner",
            )
            db.add(member)
        db.commit()

        task1 = Task(
            id=str(uuid.uuid4()),
            title="Task in Project 1",
            project_id=project1.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task in Project 2",
            project_id=project2.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/api/tasks?project_id={project1.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] >= 1
        for item in data["data"]["items"]:
            assert item["project_id"] == project1.id

    def test_list_tasks_with_status_filter(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Status Filter Project",
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
            title="Todo Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Done Task",
            project_id=project.id,
            status="done",
            priority="medium",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/api/tasks?status=todo", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        for item in data["data"]["items"]:
            assert item["status"] == "todo"

    def test_list_tasks_unauthorized(self, client):
        response = client.get("/api/tasks")
        assert response.status_code == 401


class TestGetTask:
    def test_get_task_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Get Task Project",
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
            title="Get Test Task",
            description="Test description",
            project_id=project.id,
            status="in_progress",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Get Test Task"
        assert data["data"]["id"] == task.id

    def test_get_task_not_found(self, client, auth_headers):
        response = client.get(f"/api/tasks/{str(uuid.uuid4())}", headers=auth_headers)
        assert response.status_code == 404


class TestUpdateTask:
    def test_update_task_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Update Task Project",
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
            title="Original Title",
            project_id=project.id,
            status="todo",
            priority="low",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.put(f"/api/tasks/{task.id}", headers=auth_headers, json={
            "title": "Updated Title",
            "status": "in_progress",
            "priority": "high"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Updated Title"
        assert data["data"]["status"] == "in_progress"
        assert data["data"]["priority"] == "high"


class TestDeleteTask:
    def test_delete_task_success(self, client, auth_headers, test_org, db, test_user):
        project = Project(
            id=str(uuid.uuid4()),
            name="Delete Task Project",
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
            title="Task to Delete",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.delete(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "Task deleted successfully"

    def test_delete_task_not_found(self, client, auth_headers):
        """DELETE /api/tasks/{id} - Returns 404 for non-existent task"""
        response = client.delete(f"/api/tasks/{str(uuid.uuid4())}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_task_unauthorized(self, client, test_org, db, test_user):
        """DELETE /api/tasks/{id} - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Delete Project",
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
            title="Task to Delete",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.delete(f"/api/tasks/{task.id}")
        assert response.status_code == 401

    def test_delete_task_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """DELETE /api/tasks/{id} - Returns 403 if no project access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Delete Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access

        task = Task(
            id=str(uuid.uuid4()),
            title="Task to Delete",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.delete(f"/api/tasks/{task.id}", headers=auth_headers)
        assert response.status_code == 403


class TestDueSoonTasks:
    def test_get_due_soon_tasks_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/due-soon - Returns tasks with upcoming reminders (T-431)"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Due Soon Project",
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

        now = datetime.now(timezone.utc)
        task1 = Task(
            id=str(uuid.uuid4()),
            title="Due Today Task",
            description="Task due today",
            project_id=project.id,
            status="todo",
            priority="high",
            assignee_id=test_user.id,
            reminder_at=now + timedelta(hours=2),
            due_date=now + timedelta(hours=2),
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Due Tomorrow Task",
            description="Task due tomorrow",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            assignee_id=test_user.id,
            reminder_at=now + timedelta(days=1),
            due_date=now + timedelta(days=1),
            created_by=test_user.id,
        )
        task3 = Task(
            id=str(uuid.uuid4()),
            title="Overdue Task",
            description="Task past due date",
            project_id=project.id,
            status="todo",
            priority="urgent",
            assignee_id=test_user.id,
            reminder_at=now - timedelta(hours=1),
            due_date=now - timedelta(hours=1),
            created_by=test_user.id,
        )
        task4 = Task(
            id=str(uuid.uuid4()),
            title="Done Task",
            description="Completed task",
            project_id=project.id,
            status="done",
            priority="medium",
            assignee_id=test_user.id,
            reminder_at=now + timedelta(hours=2),
            due_date=now + timedelta(hours=2),
            created_by=test_user.id,
        )
        db.add_all([task1, task2, task3, task4])
        db.commit()

        response = client.get("/api/tasks/due-soon?hours=168", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "tasks" in data["data"]
        assert "total" in data["data"]
        assert "overdue" in data["data"]
        assert "due_today" in data["data"]
        assert "due_this_week" in data["data"]
        assert data["data"]["overdue"] == 1
        task_ids = [t["id"] for t in data["data"]["tasks"]]
        assert task1.id in task_ids
        assert task2.id in task_ids
        assert task3.id in task_ids
        assert task4.id not in task_ids

    def test_get_due_soon_tasks_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/due-soon - Returns empty when no tasks due soon"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Due Soon Project",
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

        response = client.get("/api/tasks/due-soon", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["tasks"] == []

    def test_get_due_soon_tasks_unauthorized(self, client):
        """GET /api/tasks/due-soon - Returns 401 without auth"""
        response = client.get("/api/tasks/due-soon")
        assert response.status_code == 401

    def test_get_due_soon_tasks_only_returns_assigned_tasks(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/due-soon - Only returns tasks assigned to current user"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Assignment Filter Project",
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

        now = datetime.now(timezone.utc)
        other_user_id = str(uuid.uuid4())
        task_assigned = Task(
            id=str(uuid.uuid4()),
            title="Assigned Task",
            project_id=project.id,
            status="todo",
            priority="high",
            assignee_id=test_user.id,
            reminder_at=now + timedelta(hours=2),
            due_date=now + timedelta(hours=2),
            created_by=test_user.id,
        )
        task_other = Task(
            id=str(uuid.uuid4()),
            title="Other User Task",
            project_id=project.id,
            status="todo",
            priority="high",
            assignee_id=other_user_id,
            reminder_at=now + timedelta(hours=2),
            due_date=now + timedelta(hours=2),
            created_by=test_user.id,
        )
        db.add_all([task_assigned, task_other])
        db.commit()

        response = client.get("/api/tasks/due-soon?hours=168", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        task_ids = [t["id"] for t in data["data"]["tasks"]]
        assert task_assigned.id in task_ids
        assert task_other.id not in task_ids


class TestAssignTask:
    def test_assign_task_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/assign - Assign task to a user (T-410)"""
        from models.user import User
        from models.project import Project
        from models.project_member import ProjectMember

        # Create another user to assign to
        assignee = User(
            id=str(uuid.uuid4()),
            email="assignee@example.com",
            password_hash=get_password_hash("password123"),
            name="Assignee User",
            is_active=True,
            is_superuser=False,
            tenant_id=test_user.tenant_id,
        )
        db.add(assignee)

        # Create project
        project = Project(
            id=str(uuid.uuid4()),
            name="Assign Task Project",
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

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title="Task to Assign",
            description="Test assignment",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        # Assign the task
        response = client.post(f"/api/tasks/{task.id}/assign", headers=auth_headers, json={
            "assignee_id": assignee.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["assignee_id"] == assignee.id

    def test_assign_task_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/assign - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/assign", headers=auth_headers, json={
            "assignee_id": str(uuid.uuid4())
        })
        assert response.status_code == 404

    def test_assign_task_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/assign - Returns 401 without auth"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Assign Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/assign", json={
            "assignee_id": str(uuid.uuid4())
        })
        assert response.status_code == 401


class TestClaimTask:
    def test_claim_task_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/claim - Claim a task (T-411)"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Claim Task Project",
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
            title="Task to Claim",
            description="Test claiming",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/claim", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["assignee_id"] == test_user.id

    def test_claim_task_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/claim - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/claim", headers=auth_headers)
        assert response.status_code == 404

    def test_claim_task_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/claim - Returns 401 without auth"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Claim Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/claim")
        assert response.status_code == 401


class TestCompleteTask:
    def test_complete_task_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/complete - Complete a task (T-412)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Complete Task Project",
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
            title="Task to Complete",
            description="Test completion",
            project_id=project.id,
            status="in_progress",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/complete", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "done"
        assert data["data"]["completed_at"] is not None

    def test_complete_task_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/complete - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/complete", headers=auth_headers)
        assert response.status_code == 404

    def test_complete_task_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/complete - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Complete Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/complete")
        assert response.status_code == 401

    def test_complete_task_sets_completed_at(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/complete - Sets completed_at timestamp"""
        from datetime import datetime, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Timestamp Project",
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
            title="Task with Timestamp",
            description="Test",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()
        assert task.completed_at is None

        response = client.post(f"/api/tasks/{task.id}/complete", headers=auth_headers)
        assert response.status_code == 200

        db.refresh(task)
        assert task.status == "done"
        assert task.completed_at is not None


class TestBulkCreateTasks:
    """Tests for POST /api/tasks/bulk - Bulk create tasks (T-406)"""

    def test_bulk_create_tasks_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/bulk - Successfully create multiple tasks at once"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Bulk Create Project",
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

        response = client.post("/api/tasks/bulk", headers=auth_headers, json={
            "tasks": [
                {"title": "Bulk Task 1", "project_id": project.id, "status": "todo", "priority": "high"},
                {"title": "Bulk Task 2", "project_id": project.id, "status": "in_progress", "priority": "medium"},
                {"title": "Bulk Task 3", "project_id": project.id, "status": "done", "priority": "low"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 3
        assert len(data["data"]["items"]) == 3

        # Verify task details
        titles = [t["title"] for t in data["data"]["items"]]
        assert "Bulk Task 1" in titles
        assert "Bulk Task 2" in titles
        assert "Bulk Task 3" in titles

    def test_bulk_create_tasks_empty_list(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/bulk - Returns empty list for empty tasks array"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Bulk Project",
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

        response = client.post("/api/tasks/bulk", headers=auth_headers, json={
            "tasks": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    def test_bulk_create_tasks_missing_project_id(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/bulk - Returns error if project_id is missing"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Missing Project Bulk",
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

        response = client.post("/api/tasks/bulk", headers=auth_headers, json={
            "tasks": [
                {"title": "Task without project", "status": "todo", "priority": "medium"}
            ]
        })
        assert response.status_code == 404

    def test_bulk_create_tasks_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/bulk - Returns 401 without auth"""
        response = client.post("/api/tasks/bulk", json={
            "tasks": [{"title": "Task", "project_id": str(uuid.uuid4())}]
        })
        assert response.status_code == 401

    def test_bulk_create_tasks_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/bulk - Returns 403 if no access to project"""
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Bulk Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access
        db.commit()

        response = client.post("/api/tasks/bulk", headers=auth_headers, json={
            "tasks": [
                {"title": "Task 1", "project_id": project.id, "status": "todo", "priority": "medium"},
            ]
        })
        assert response.status_code == 403

    def test_bulk_create_tasks_mixed_projects(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/bulk - Create tasks across multiple projects user has access to"""
        project1 = Project(
            id=str(uuid.uuid4()),
            name="Bulk Project 1",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        project2 = Project(
            id=str(uuid.uuid4()),
            name="Bulk Project 2",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add_all([project1, project2])
        for p in [project1, project2]:
            member = ProjectMember(
                id=str(uuid.uuid4()),
                project_id=p.id,
                user_id=test_user.id,
                role="owner",
            )
            db.add(member)
        db.commit()

        response = client.post("/api/tasks/bulk", headers=auth_headers, json={
            "tasks": [
                {"title": "Task in Project 1", "project_id": project1.id, "status": "todo", "priority": "high"},
                {"title": "Task in Project 2", "project_id": project2.id, "status": "in_progress", "priority": "medium"},
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2


class TestBulkUpdateStatus:
    def test_bulk_update_status_success(self, client, auth_headers, test_org, db, test_user):
        """PUT /api/tasks/bulk/status - Bulk status update (T-407)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Bulk Status Project",
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
            priority="medium",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task 2",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.put("/api/tasks/bulk/status", headers=auth_headers, json={
            "task_ids": [task1.id, task2.id],
            "status": "in_progress"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2

        # Verify tasks were updated
        db.refresh(task1)
        db.refresh(task2)
        assert task1.status == "in_progress"
        assert task2.status == "in_progress"
        # Verify started_at was set
        assert task1.started_at is not None
        assert task2.started_at is not None

    def test_bulk_update_status_to_done(self, client, auth_headers, test_org, db, test_user):
        """PUT /api/tasks/bulk/status - Bulk status update to done sets completed_at"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Bulk Done Project",
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
            title="Task to Complete",
            project_id=project.id,
            status="in_progress",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.put("/api/tasks/bulk/status", headers=auth_headers, json={
            "task_ids": [task.id],
            "status": "done"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

        db.refresh(task)
        assert task.status == "done"
        assert task.completed_at is not None

    def test_bulk_update_status_invalid_status(self, client, auth_headers, test_org, db, test_user):
        """PUT /api/tasks/bulk/status - Returns 404 for invalid status value"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Invalid Status Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.put("/api/tasks/bulk/status", headers=auth_headers, json={
            "task_ids": [task.id],
            "status": "invalid_status"
        })
        assert response.status_code == 404

    def test_bulk_update_status_unauthorized(self, client, test_org, db, test_user):
        """PUT /api/tasks/bulk/status - Returns 401 without auth"""
        response = client.put("/api/tasks/bulk/status", json={
            "task_ids": [str(uuid.uuid4())],
            "status": "in_progress"
        })
        assert response.status_code == 401


class TestExportTasks:
    def test_export_tasks_json_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/export - Export tasks as JSON (T-408)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Export Project",
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
            title="Export Task 1",
            description="First task for export",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Export Task 2",
            description="Second task for export",
            project_id=project.id,
            status="done",
            priority="low",
            created_by=test_user.id,
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get(f"/api/tasks/export?project_id={project.id}&format=json", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["format"] == "json"
        import json
        content = json.loads(data["data"]["content"])
        assert len(content) == 2
        titles = [t["title"] for t in content]
        assert "Export Task 1" in titles
        assert "Export Task 2" in titles

    def test_export_tasks_csv_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/export - Export tasks as CSV (T-408)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="CSV Export Project",
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
            title="CSV Task",
            description="Task for CSV export",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/export?project_id={project.id}&format=csv", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["format"] == "csv"
        content = data["data"]["content"]
        # Check CSV header
        assert "id,title,description,status,priority" in content
        assert "CSV Task" in content

    def test_export_tasks_empty_project(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/export - Export empty project"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Export Project",
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

        response = client.get(f"/api/tasks/export?project_id={project.id}&format=json", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        import json
        content = json.loads(data["data"]["content"])
        assert content == []

    def test_export_tasks_unauthorized(self, client, test_org, db, test_user):
        """GET /api/tasks/export - Returns 401 without auth"""
        project_id = str(uuid.uuid4())
        response = client.get(f"/api/tasks/export?project_id={project_id}&format=json")
        assert response.status_code == 401

    def test_export_tasks_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/export - Returns 403 if no project access"""
        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/tasks/export?project_id={project.id}&format=json", headers=auth_headers)
        assert response.status_code == 403


class TestCreateSubtask:
    def test_create_subtask_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/subtasks - Create subtask (T-415)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Subtask Project",
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

        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Task",
            description="Parent task for subtask",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(parent_task)
        db.commit()

        response = client.post(f"/api/tasks/{parent_task.id}/subtasks", headers=auth_headers, json={
            "title": "Subtask 1",
            "description": "First subtask",
            "project_id": project.id,
            "status": "todo",
            "priority": "medium"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["title"] == "Subtask 1"
        assert data["data"]["parent_id"] == parent_task.id
        assert data["data"]["project_id"] == project.id

    def test_create_subtask_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/subtasks - Returns 404 for non-existent parent"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/subtasks", headers=auth_headers, json={
            "title": "Orphan Subtask",
            "project_id": str(uuid.uuid4()),
        })
        assert response.status_code == 404

    def test_create_subtask_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/subtasks - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Subtask Project",
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

        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(parent_task)
        db.commit()

        response = client.post(f"/api/tasks/{parent_task.id}/subtasks", json={
            "title": "Subtask",
            "project_id": project.id,
        })
        assert response.status_code == 401


class TestGetSubtasks:
    def test_get_subtasks_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/subtasks - List subtasks (T-416)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="List Subtasks Project",
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

        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Task",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(parent_task)

        subtask1 = Task(
            id=str(uuid.uuid4()),
            title="Subtask 1",
            description="First subtask",
            project_id=project.id,
            parent_id=parent_task.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        subtask2 = Task(
            id=str(uuid.uuid4()),
            title="Subtask 2",
            description="Second subtask",
            project_id=project.id,
            parent_id=parent_task.id,
            status="done",
            priority="low",
            created_by=test_user.id,
        )
        db.add_all([subtask1, subtask2])
        db.commit()

        response = client.get(f"/api/tasks/{parent_task.id}/subtasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2
        assert len(data["data"]["items"]) == 2

    def test_get_subtasks_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/subtasks - Returns empty when no subtasks"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Subtasks Project",
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

        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Without Subtasks",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(parent_task)
        db.commit()

        response = client.get(f"/api/tasks/{parent_task.id}/subtasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    def test_get_subtasks_not_found(self, client, auth_headers):
        """GET /api/tasks/{id}/subtasks - Returns 404 for non-existent parent"""
        response = client.get(f"/api/tasks/{str(uuid.uuid4())}/subtasks", headers=auth_headers)
        assert response.status_code == 404

    def test_get_subtasks_unauthorized(self, client, test_org, db, test_user):
        """GET /api/tasks/{id}/subtasks - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Get Project",
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

        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(parent_task)
        db.commit()

        response = client.get(f"/api/tasks/{parent_task.id}/subtasks")
        assert response.status_code == 401


class TestMoveTask:
    def test_move_task_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/move - Move task (T-424)"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Move Task Project",
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
            title="Task to Move",
            description="Test moving task",
            project_id=project.id,
            status="todo",
            priority="medium",
            position=0,
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        # Move task to in_progress with new position
        response = client.post(f"/api/tasks/{task.id}/move", headers=auth_headers, json={
            "status": "in_progress",
            "position": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "in_progress"
        assert data["data"]["position"] == 5

    def test_move_task_change_assignee(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/move - Move task to change assignee (T-424)"""
        from models.user import User
        from models.project_member import ProjectMember

        # Create another user
        new_assignee = User(
            id=str(uuid.uuid4()),
            email="newassignee@example.com",
            password_hash=get_password_hash("password123"),
            name="New Assignee",
            is_active=True,
            is_superuser=False,
            tenant_id=test_user.tenant_id,
        )
        db.add(new_assignee)

        project = Project(
            id=str(uuid.uuid4()),
            name="Assignee Move Project",
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
            title="Task to Reassign",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/move", headers=auth_headers, json={
            "assignee_id": new_assignee.id
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["assignee_id"] == new_assignee.id

    def test_move_task_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/move - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/move", headers=auth_headers, json={
            "status": "in_progress"
        })
        assert response.status_code == 404

    def test_move_task_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/move - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Move Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/move", json={
            "status": "in_progress"
        })
        assert response.status_code == 401

    def test_move_task_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/move - Returns 403 if no project access"""
        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        task = Task(
            id=str(uuid.uuid4()),
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/move", headers=auth_headers, json={
            "status": "in_progress"
        })
        assert response.status_code == 403


class TestSnoozeReminder:
    """Tests for POST /api/tasks/{id}/snooze - Snooze reminder (T-432)"""

    def test_snooze_reminder_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/snooze - Successfully snooze a reminder"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Snooze Test Project",
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

        now = datetime.now(timezone.utc)
        original_reminder = now + timedelta(hours=1)
        task = Task(
            id=str(uuid.uuid4()),
            title="Task with Reminder",
            description="Task to snooze",
            project_id=project.id,
            status="todo",
            priority="medium",
            assignee_id=test_user.id,
            reminder_at=original_reminder,
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/snooze", headers=auth_headers, json={
            "snooze_minutes": 30
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == task.id
        # Reminder should be 30 minutes later
        new_reminder_str = data["data"]["reminder_at"]
        if new_reminder_str.endswith("Z"):
            new_reminder = datetime.fromisoformat(new_reminder_str.replace("Z", "+00:00"))
        else:
            new_reminder = datetime.fromisoformat(new_reminder_str)
            if new_reminder.tzinfo is None:
                new_reminder = new_reminder.replace(tzinfo=timezone.utc)
        expected_reminder = original_reminder + timedelta(minutes=30)
        assert abs((new_reminder - expected_reminder).total_seconds()) < 5

    def test_snooze_reminder_no_existing_reminder(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/snooze - Snooze from current time if no reminder set"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Snooze No Reminder Project",
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
            title="Task without Reminder",
            description="Task to snooze",
            project_id=project.id,
            status="todo",
            priority="medium",
            assignee_id=test_user.id,
            reminder_at=None,
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        before_snooze = datetime.now(timezone.utc)
        response = client.post(f"/api/tasks/{task.id}/snooze", headers=auth_headers, json={
            "snooze_minutes": 60
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Reminder should be approximately 60 minutes from now
        new_reminder_str = data["data"]["reminder_at"]
        if new_reminder_str.endswith("Z"):
            new_reminder = datetime.fromisoformat(new_reminder_str.replace("Z", "+00:00"))
        else:
            new_reminder = datetime.fromisoformat(new_reminder_str)
            if new_reminder.tzinfo is None:
                new_reminder = new_reminder.replace(tzinfo=timezone.utc)
        expected_reminder = before_snooze + timedelta(minutes=60)
        assert abs((new_reminder - expected_reminder).total_seconds()) < 10

    def test_snooze_reminder_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/snooze - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{uuid.uuid4()}/snooze", headers=auth_headers, json={
            "snooze_minutes": 30
        })
        assert response.status_code == 404

    def test_snooze_reminder_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/snooze - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Snooze Unauthorized Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/snooze", json={
            "snooze_minutes": 30
        })
        assert response.status_code == 401

    def test_snooze_reminder_invalid_minutes(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/snooze - Returns 422 for invalid snooze_minutes"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Snooze Invalid Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        # snooze_minutes must be >= 1 and <= 10080 (7 days)
        response = client.post(f"/api/tasks/{task.id}/snooze", headers=auth_headers, json={
            "snooze_minutes": 0  # Invalid: must be >= 1
        })
        assert response.status_code == 422

    def test_snooze_reminder_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/snooze - Returns 403 if no project access"""
        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        task = Task(
            id=str(uuid.uuid4()),
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/snooze", headers=auth_headers, json={
            "snooze_minutes": 30
        })
        assert response.status_code == 403


class TestKanbanBoard:
    """Tests for GET /api/projects/{id}/kanban - Kanban board (T-420)"""

    def test_get_kanban_board_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/kanban - Returns kanban board with tasks grouped by status"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Kanban Test Project",
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

        # Create tasks in different statuses
        task_todo = Task(
            id=str(uuid.uuid4()),
            title="Todo Task",
            description="Task in todo status",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        task_in_progress = Task(
            id=str(uuid.uuid4()),
            title="In Progress Task",
            description="Task in progress",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            created_by=test_user.id,
        )
        task_done = Task(
            id=str(uuid.uuid4()),
            title="Done Task",
            description="Completed task",
            project_id=project.id,
            status="done",
            priority="low",
            created_by=test_user.id,
        )
        db.add_all([task_todo, task_in_progress, task_done])
        db.commit()

        response = client.get(f"/api/projects/{project.id}/kanban", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "columns" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] == 3

        # Should have columns for all task statuses
        columns = data["data"]["columns"]
        assert len(columns) == 5  # todo, in_progress, in_review, done, blocked

        # Check each column has the correct structure
        for col in columns:
            assert "status" in col
            assert "tasks" in col
            assert "count" in col

        # Verify tasks are in correct columns
        todo_col = next((c for c in columns if c["status"] == "todo"), None)
        assert todo_col is not None
        assert todo_col["count"] == 1
        assert todo_col["tasks"][0]["title"] == "Todo Task"

        in_progress_col = next((c for c in columns if c["status"] == "in_progress"), None)
        assert in_progress_col is not None
        assert in_progress_col["count"] == 1
        assert in_progress_col["tasks"][0]["title"] == "In Progress Task"

        done_col = next((c for c in columns if c["status"] == "done"), None)
        assert done_col is not None
        assert done_col["count"] == 1
        assert done_col["tasks"][0]["title"] == "Done Task"

    def test_get_kanban_board_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/kanban - Returns empty columns for project with no tasks"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Kanban Project",
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

        response = client.get(f"/api/projects/{project.id}/kanban", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        for col in data["data"]["columns"]:
            assert col["count"] == 0
            assert col["tasks"] == []

    def test_get_kanban_board_unauthorized(self, client, test_org, db, test_user):
        """GET /api/projects/{id}/kanban - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Kanban Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/kanban")
        assert response.status_code == 401

    def test_get_kanban_board_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/kanban - Returns 403 if no project access"""
        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Kanban Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/kanban", headers=auth_headers)
        assert response.status_code == 403


class TestTasksByStatus:
    """Tests for GET /api/projects/{id}/tasks/by-status - Tasks grouped by status (T-421)"""

    def test_get_tasks_by_status_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-status - Returns tasks grouped by status"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="By Status Test Project",
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

        # Create tasks in different statuses
        task_todo = Task(
            id=str(uuid.uuid4()),
            title="Todo Task",
            description="Task in todo status",
            project_id=project.id,
            status="todo",
            priority="high",
            created_by=test_user.id,
        )
        task_in_progress = Task(
            id=str(uuid.uuid4()),
            title="In Progress Task",
            description="Task in progress",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            created_by=test_user.id,
        )
        task_done = Task(
            id=str(uuid.uuid4()),
            title="Done Task",
            description="Completed task",
            project_id=project.id,
            status="done",
            priority="low",
            created_by=test_user.id,
        )
        db.add_all([task_todo, task_in_progress, task_done])
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], dict)

        # Should have all 5 status keys
        expected_statuses = ["todo", "in_progress", "in_review", "done", "blocked"]
        for status in expected_statuses:
            assert status in data["data"], f"Missing status: {status}"

        # Verify correct tasks in correct status groups
        assert len(data["data"]["todo"]) == 1
        assert data["data"]["todo"][0]["title"] == "Todo Task"

        assert len(data["data"]["in_progress"]) == 1
        assert data["data"]["in_progress"][0]["title"] == "In Progress Task"

        assert len(data["data"]["done"]) == 1
        assert data["data"]["done"][0]["title"] == "Done Task"

        # Other statuses should be empty
        assert data["data"]["in_review"] == []
        assert data["data"]["blocked"] == []

    def test_get_tasks_by_status_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-status - Returns all empty lists for project with no tasks"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Empty By Status Project",
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

        response = client.get(f"/api/projects/{project.id}/tasks/by-status", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

        # All status groups should be empty
        for status in ["todo", "in_progress", "in_review", "done", "blocked"]:
            assert data["data"][status] == [], f"Expected empty list for {status}"

    def test_get_tasks_by_status_unauthorized(self, client, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-status - Returns 401 without auth"""
        from models.project import Project

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized By Status Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-status")
        assert response.status_code == 401

    def test_get_tasks_by_status_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-status - Returns 403 if no project access"""
        from models.project import Project

        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access By Status Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-status", headers=auth_headers)
        assert response.status_code == 403


class TestGetTasksByAssignee:
    def test_get_tasks_by_assignee_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-assignee - Returns tasks grouped by assignee (T-422)"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="By Assignee Test Project",
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

        # Create tasks with different assignees
        task_assigned = Task(
            id=str(uuid.uuid4()),
            title="Assigned Task",
            description="Task assigned to user",
            project_id=project.id,
            status="todo",
            priority="high",
            assignee_id=test_user.id,
            created_by=test_user.id,
        )
        task_unassigned = Task(
            id=str(uuid.uuid4()),
            title="Unassigned Task",
            description="Task without assignee",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            created_by=test_user.id,
        )
        db.add_all([task_assigned, task_unassigned])
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-assignee", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], dict)

        # Should have two keys: the user id and "unassigned"
        assert str(test_user.id) in data["data"] or test_user.id in data["data"]
        assert "unassigned" in data["data"]

        # Verify correct tasks in correct assignee groups
        user_tasks = data["data"].get(str(test_user.id), data["data"].get(test_user.id, []))
        unassigned_tasks = data["data"].get("unassigned", [])

        assert len(user_tasks) == 1
        assert user_tasks[0]["title"] == "Assigned Task"

        assert len(unassigned_tasks) == 1
        assert unassigned_tasks[0]["title"] == "Unassigned Task"

    def test_get_tasks_by_assignee_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-assignee - Returns empty for project with no tasks"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Empty By Assignee Project",
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

        response = client.get(f"/api/projects/{project.id}/tasks/by-assignee", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Should return empty dict or dict with only unassigned
        assert data["data"] == {} or "unassigned" in data["data"]

    def test_get_tasks_by_assignee_unauthorized(self, client, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-assignee - Returns 401 without auth"""
        from models.project import Project

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized By Assignee Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-assignee")
        assert response.status_code == 401

    def test_get_tasks_by_assignee_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/by-assignee - Returns 403 if no project access"""
        from models.project import Project

        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access By Assignee Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/by-assignee", headers=auth_headers)
        assert response.status_code == 403


class TestGetActivity:
    def test_get_activity_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/activity - Get activity history (T-425)"""
        from models.project import Project
        from models.project_member import ProjectMember
        from models.task_comment import TaskComment

        project = Project(
            id=str(uuid.uuid4()),
            name="Activity Test Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Activity Test Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)

        comment = TaskComment(
            id=str(uuid.uuid4()),
            task_id=task.id,
            user_id=test_user.id,
            content="This is a test comment for activity"
        )
        db.add(comment)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/activity", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 1
        assert data["data"][0]["action"] == "commented"
        assert data["data"][0]["new_value"] == "This is a test comment for activity"

    def test_get_activity_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/activity - Returns empty list when no activity"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Activity Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Empty Activity Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/activity", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_get_activity_unauthorized(self, client, test_org, db, test_user):
        """GET /api/tasks/{id}/activity - Returns 401 without auth"""
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Activity Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Unauthorized Activity Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/activity")
        assert response.status_code == 401

    def test_get_activity_not_found(self, client, auth_headers):
        """GET /api/tasks/{id}/activity - Returns 404 for non-existent task"""
        response = client.get(f"/api/tasks/{uuid.uuid4()}/activity", headers=auth_headers)
        assert response.status_code == 404

    def test_get_activity_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/activity - Returns 403 if no project access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Activity Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access

        task = Task(
            id=str(uuid.uuid4()),
            title="No Access Activity Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/activity", headers=auth_headers)
        assert response.status_code == 403


class TestAddComment:
    """Tests for POST /api/tasks/{id}/comment - Add comment (T-413)"""

    def test_add_comment_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/comment - Successfully add a comment"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Comment Test Project",
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
            title="Task for Comment",
            description="Task to comment on",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/comment", headers=auth_headers, json={
            "content": "This is a test comment"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["content"] == "This is a test comment"
        assert data["data"]["task_id"] == task.id
        assert data["data"]["user_id"] == test_user.id
        assert data["data"]["author_email"] == test_user.email
        assert data["data"]["author_name"] == test_user.name

    def test_add_comment_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/comment - Returns 404 for non-existent task"""
        response = client.post(f"/api/tasks/{str(uuid.uuid4())}/comment", headers=auth_headers, json={
            "content": "This is a test comment"
        })
        assert response.status_code == 404

    def test_add_comment_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/comment - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Comment Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/comment", json={
            "content": "This is a test comment"
        })
        assert response.status_code == 401

    def test_add_comment_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/comment - Returns 403 if no project access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Comment Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access

        task = Task(
            id=str(uuid.uuid4()),
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/comment", headers=auth_headers, json={
            "content": "This is a test comment"
        })
        assert response.status_code == 403

    def test_add_comment_empty_content(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/comment - Returns 422 for empty content"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Content Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.post(f"/api/tasks/{task.id}/comment", headers=auth_headers, json={
            "content": ""
        })
        assert response.status_code == 422


class TestGetComments:
    """Tests for GET /api/tasks/{id}/comments - List comments (T-414)"""

    def test_get_comments_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/comments - Successfully list comments"""
        from models.task_comment import TaskComment

        project = Project(
            id=str(uuid.uuid4()),
            name="Get Comments Project",
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
            title="Task for Comments",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)

        comment1 = TaskComment(
            id=str(uuid.uuid4()),
            task_id=task.id,
            user_id=test_user.id,
            content="First comment"
        )
        comment2 = TaskComment(
            id=str(uuid.uuid4()),
            task_id=task.id,
            user_id=test_user.id,
            content="Second comment"
        )
        db.add_all([comment1, comment2])
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/comments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 2
        assert len(data["data"]["items"]) == 2
        # Comments should be ordered by created_at ascending
        assert data["data"]["items"][0]["content"] == "First comment"
        assert data["data"]["items"][1]["content"] == "Second comment"

    def test_get_comments_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/comments - Returns empty list when no comments"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Comments Project",
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
            title="Task without Comments",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/comments", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["total"] == 0
        assert data["data"]["items"] == []

    def test_get_comments_not_found(self, client, auth_headers):
        """GET /api/tasks/{id}/comments - Returns 404 for non-existent task"""
        response = client.get(f"/api/tasks/{str(uuid.uuid4())}/comments", headers=auth_headers)
        assert response.status_code == 404

    def test_get_comments_unauthorized(self, client, test_org, db, test_user):
        """GET /api/tasks/{id}/comments - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Get Comments Project",
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
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/comments")
        assert response.status_code == 401

    def test_get_comments_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/tasks/{id}/comments - Returns 403 if no project access"""
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Comments Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access

        task = Task(
            id=str(uuid.uuid4()),
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/tasks/{task.id}/comments", headers=auth_headers)
        assert response.status_code == 403


class TestSetReminder:
    """Tests for POST /api/tasks/{id}/remind - Set reminder (T-430)"""

    def test_set_reminder_success(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/remind - Successfully set a reminder"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Reminder Test Project",
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
            title="Task with Reminder",
            description="Task to remind",
            project_id=project.id,
            status="todo",
            priority="medium",
            assignee_id=test_user.id,
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        reminder_time = datetime.now(timezone.utc) + timedelta(hours=2)
        response = client.post(f"/api/tasks/{task.id}/remind", headers=auth_headers, json={
            "reminder_at": reminder_time.isoformat()
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == task.id
        assert data["data"]["reminder_at"] is not None

    def test_set_reminder_not_found(self, client, auth_headers):
        """POST /api/tasks/{id}/remind - Returns 404 for non-existent task"""
        from datetime import datetime, timedelta, timezone

        reminder_time = datetime.now(timezone.utc) + timedelta(hours=2)
        response = client.post(f"/api/tasks/{uuid.uuid4()}/remind", headers=auth_headers, json={
            "reminder_at": reminder_time.isoformat()
        })
        assert response.status_code == 404

    def test_set_reminder_unauthorized(self, client, test_org, db, test_user):
        """POST /api/tasks/{id}/remind - Returns 401 without auth"""
        from datetime import datetime, timedelta, timezone
        from models.project import Project
        from models.project_member import ProjectMember

        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Reminder Project",
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

        task = Task(
            id=str(uuid.uuid4()),
            title="Unauthorized Reminder Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        reminder_time = datetime.now(timezone.utc) + timedelta(hours=2)
        response = client.post(f"/api/tasks/{task.id}/remind", json={
            "reminder_at": reminder_time.isoformat()
        })
        assert response.status_code == 401

    def test_set_reminder_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """POST /api/tasks/{id}/remind - Returns 403 if no project access"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Reminder Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        # No member added - user has no access

        task = Task(
            id=str(uuid.uuid4()),
            title="No Access Reminder Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        reminder_time = datetime.now(timezone.utc) + timedelta(hours=2)
        response = client.post(f"/api/tasks/{task.id}/remind", headers=auth_headers, json={
            "reminder_at": reminder_time.isoformat()
        })
        assert response.status_code == 403


class TestGetTimeline:
    """Tests for GET /api/projects/{id}/tasks/timeline - Timeline view (T-423)"""

    def test_get_timeline_success(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/timeline - Returns tasks with due dates ordered by due_date"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Timeline Test Project",
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

        now = datetime.now(timezone.utc)
        task1 = Task(
            id=str(uuid.uuid4()),
            title="Task Due Later",
            description="Task with later due date",
            project_id=project.id,
            status="todo",
            priority="high",
            due_date=now + timedelta(days=5),
            created_by=test_user.id,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task Due Soon",
            description="Task with sooner due date",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            due_date=now + timedelta(days=2),
            created_by=test_user.id,
        )
        task3 = Task(
            id=str(uuid.uuid4()),
            title="Task No Due Date",
            description="Task without due date",
            project_id=project.id,
            status="todo",
            priority="low",
            due_date=None,
            created_by=test_user.id,
        )
        db.add_all([task1, task2, task3])
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        # Should return only tasks with due_date, ordered by due_date
        assert len(data["data"]) == 2
        # Task due sooner should be first
        assert data["data"][0]["title"] == "Task Due Soon"
        assert data["data"][1]["title"] == "Task Due Later"

    def test_get_timeline_empty(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/timeline - Returns empty list when no tasks with due dates"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Empty Timeline Project",
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

        # Create task without due date
        task = Task(
            id=str(uuid.uuid4()),
            title="Task Without Due Date",
            project_id=project.id,
            status="todo",
            priority="medium",
            due_date=None,
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_get_timeline_excludes_subtasks(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/timeline - Excludes subtasks (parent_id is not null)"""
        from datetime import datetime, timedelta, timezone

        project = Project(
            id=str(uuid.uuid4()),
            name="Subtask Timeline Project",
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

        now = datetime.now(timezone.utc)
        parent_task = Task(
            id=str(uuid.uuid4()),
            title="Parent Task",
            project_id=project.id,
            status="todo",
            priority="high",
            due_date=now + timedelta(days=3),
            created_by=test_user.id,
        )
        db.add(parent_task)

        subtask = Task(
            id=str(uuid.uuid4()),
            title="Subtask",
            project_id=project.id,
            status="todo",
            priority="medium",
            parent_id=parent_task.id,
            due_date=now + timedelta(days=1),
            created_by=test_user.id,
        )
        db.add(subtask)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/timeline", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Should only return parent task, not subtask
        assert len(data["data"]) == 1
        assert data["data"][0]["title"] == "Parent Task"

    def test_get_timeline_unauthorized(self, client, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/timeline - Returns 401 without auth"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Unauthorized Timeline Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/timeline")
        assert response.status_code == 401

    def test_get_timeline_no_project_access(self, client, auth_headers, test_org, db, test_user):
        """GET /api/projects/{id}/tasks/timeline - Returns 403 if no project access"""
        from datetime import datetime, timedelta, timezone

        # Create project without adding user as member
        project = Project(
            id=str(uuid.uuid4()),
            name="No Access Timeline Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)
        db.commit()

        now = datetime.now(timezone.utc)
        task = Task(
            id=str(uuid.uuid4()),
            title="Task",
            project_id=project.id,
            status="todo",
            priority="medium",
            due_date=now + timedelta(days=1),
            created_by=test_user.id,
        )
        db.add(task)
        db.commit()

        response = client.get(f"/api/projects/{project.id}/tasks/timeline", headers=auth_headers)
        assert response.status_code == 403

    def test_get_timeline_project_not_found(self, client, auth_headers):
        """GET /api/projects/{id}/tasks/timeline - Returns 404 for non-existent project"""
        response = client.get(f"/api/projects/{uuid.uuid4()}/tasks/timeline", headers=auth_headers)
        assert response.status_code == 404
