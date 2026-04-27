import pytest
import uuid
from datetime import datetime, timezone, timedelta
from models.task import Task
from models.project import Project
from models.project_member import ProjectMember
from models.agent import Agent
from models.activity import Activity


class TestGetStats:
    def test_get_stats_success(self, client, auth_headers, test_org, db, test_user):
        """获取仪表盘统计数据"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Dashboard Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        task = Task(
            id=str(uuid.uuid4()),
            title="Test Task",
            description="Test",
            project_id=project.id,
            status="in_progress",
            priority="medium",
            created_by=test_user.id,
        )
        db.add(task)

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Test Agent",
            description="Test agent",
            org_id=test_org.id,
            agent_type="assistant",
            config="{}",
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project_count"] == 1
        assert data["data"]["task_count"] == 1
        assert data["data"]["agent_count"] == 1
        assert data["data"]["completed_today"] == 0

    def test_get_stats_no_org(self, client, auth_headers, db, test_user):
        """用户没有组织时返回零值"""
        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["project_count"] == 0
        assert data["data"]["task_count"] == 0
        assert data["data"]["agent_count"] == 0
        assert data["data"]["completed_today"] == 0

    def test_get_stats_unauthorized(self, client):
        """未授权访问"""
        response = client.get("/api/dashboard/stats")
        assert response.status_code == 401

    def test_get_stats_completed_today(self, client, auth_headers, test_org, db, test_user):
        """今日完成的任务数"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Completed Task Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        task = Task(
            id=str(uuid.uuid4()),
            title="Completed Task",
            description="Test",
            project_id=project.id,
            status="completed",
            priority="high",
            created_by=test_user.id,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(task)
        db.commit()

        response = client.get("/api/dashboard/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed_today"] == 1


class TestGetTaskTrend:
    def test_get_task_trend_success(self, client, auth_headers, test_org, db, test_user):
        """获取任务完成趋势"""
        project = Project(
            id=str(uuid.uuid4()),
            name="Trend Test Project",
            description="Test",
            org_id=test_org.id,
            status="active",
            created_by=test_user.id,
        )
        db.add(project)

        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday = today - timedelta(days=1)

        task1 = Task(
            id=str(uuid.uuid4()),
            title="Yesterday Task",
            description="Test",
            project_id=project.id,
            status="completed",
            priority="medium",
            created_by=test_user.id,
            completed_at=yesterday,
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Today Task",
            description="Test",
            project_id=project.id,
            status="completed",
            priority="medium",
            created_by=test_user.id,
            completed_at=today + timedelta(hours=12),
        )
        db.add_all([task1, task2])
        db.commit()

        response = client.get("/api/dashboard/task-trend", headers=auth_headers, params={"days": 7})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 7
        for item in data["data"]:
            assert "date" in item
            assert "count" in item

    def test_get_task_trend_no_org(self, client, auth_headers):
        """用户没有组织时返回空列表"""
        response = client.get("/api/dashboard/task-trend", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []

    def test_get_task_trend_unauthorized(self, client):
        """未授权访问"""
        response = client.get("/api/dashboard/task-trend")
        assert response.status_code == 401

    def test_get_task_trend_custom_days(self, client, auth_headers, test_org, db, test_user):
        """自定义天数"""
        response = client.get("/api/dashboard/task-trend", headers=auth_headers, params={"days": 14})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 14


class TestGetRecentActivities:
    def test_get_recent_activities_success(self, client, auth_headers, test_org, db, test_user):
        """获取最近活动"""
        activity = Activity(
            id=str(uuid.uuid4()),
            tenant_id=test_user.tenant_id,
            actor_id=test_user.id,
            actor_name=test_user.name,
            action_type="created",
            entity_type="task",
            entity_id=str(uuid.uuid4()),
            entity_name="Test Task",
        )
        db.add(activity)
        db.commit()

        response = client.get("/api/dashboard/recent-activities", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 1
        assert data["data"][0]["actor_name"] == test_user.name
        assert data["data"][0]["action_type"] == "created"
        assert data["data"][0]["entity_type"] == "task"
        assert data["data"][0]["entity_name"] == "Test Task"

    def test_get_recent_activities_with_limit(self, client, auth_headers, test_org, db, test_user):
        """限制返回数量"""
        for i in range(5):
            activity = Activity(
                id=str(uuid.uuid4()),
                tenant_id=test_user.tenant_id,
                actor_id=test_user.id,
                actor_name=test_user.name,
                action_type="created",
                entity_type="task",
                entity_id=str(uuid.uuid4()),
                entity_name=f"Task {i}",
            )
            db.add(activity)
        db.commit()

        response = client.get("/api/dashboard/recent-activities", headers=auth_headers, params={"limit": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 3

    def test_get_recent_activities_unauthorized(self, client):
        """未授权访问"""
        response = client.get("/api/dashboard/recent-activities")
        assert response.status_code == 401

    def test_get_recent_activities_empty(self, client, auth_headers, test_org, db, test_user):
        """没有活动时返回空列表"""
        response = client.get("/api/dashboard/recent-activities", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"] == []