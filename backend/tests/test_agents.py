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


class TestAgentHistory:
    def test_get_agent_history_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/history - Get Agent History (T-313)"""
        from models.activity import Activity

        agent = Agent(
            id=str(uuid.uuid4()),
            name="History Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        activity = Activity(
            id=str(uuid.uuid4()),
            tenant_id=test_org.id,
            actor_id=str(uuid.uuid4()),
            actor_name="Test User",
            action_type="created",
            entity_type="agent",
            entity_id=agent.id,
            entity_name=agent.name,
        )
        db.add(activity)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "limit" in data["data"]
        assert "pages" in data["data"]
        assert len(data["data"]["items"]) >= 1
        assert data["data"]["items"][0]["entity_type"] == "agent"
        assert data["data"]["items"][0]["entity_id"] == agent.id

    def test_get_agent_history_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/history - Not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/history", headers=auth_headers)
        assert response.status_code == 404

    def test_get_agent_history_with_pagination(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/history - With pagination"""
        from models.activity import Activity

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Pagination Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        for i in range(3):
            activity = Activity(
                id=str(uuid.uuid4()),
                tenant_id=test_org.id,
                actor_id=str(uuid.uuid4()),
                actor_name=f"User {i}",
                action_type="updated",
                entity_type="agent",
                entity_id=agent.id,
                entity_name=agent.name,
            )
            db.add(activity)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/history?page=1&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]["items"]) == 2
        assert data["data"]["total"] == 3
        assert data["data"]["page"] == 1
        assert data["data"]["limit"] == 2
        assert data["data"]["pages"] == 2


class TestBindAgentSkill:
    def test_bind_agent_skill_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/skills - Bind a skill to an agent (T-306)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Skill Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/skills", headers=auth_headers, json={
            "skill_name": "code_generation",
            "skill_config": {"language": "python"},
            "enabled": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["skill_name"] == "code_generation"
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["enabled"] is True

    def test_bind_agent_skill_not_found(self, client, auth_headers):
        """POST /api/agents/{id}/skills - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/agents/{fake_id}/skills", headers=auth_headers, json={
            "skill_name": "test_skill",
        })
        assert response.status_code == 404

    def test_bind_duplicate_skill(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/skills - Duplicate skill should fail"""
        from models.agent_skill import AgentSkill
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Dup Skill Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        skill = AgentSkill(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            skill_name="duplicate_skill",
        )
        db.add(skill)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/skills", headers=auth_headers, json={
            "skill_name": "duplicate_skill",
        })
        assert response.status_code == 409


class TestGetAgentSkills:
    def test_get_agent_skills_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/skills - Get all skills bound to an agent (T-308)"""
        from models.agent_skill import AgentSkill
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Get Skills Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        skill = AgentSkill(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            skill_name="test_skill",
        )
        db.add(skill)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/skills", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) >= 1
        assert any(s["skill_name"] == "test_skill" for s in data["data"])

    def test_get_agent_skills_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/skills - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/skills", headers=auth_headers)
        assert response.status_code == 404


class TestUnbindAgentSkill:
    def test_unbind_agent_skill_success(self, client, auth_headers, test_org, db):
        """DELETE /api/agents/{id}/skills/{skill_id} - Unbind a skill from an agent (T-307)"""
        from models.agent_skill import AgentSkill
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Unbind Skill Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        skill = AgentSkill(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            skill_name="to_be_removed",
        )
        db.add(skill)
        db.commit()

        response = client.delete(f"/api/agents/{agent.id}/skills/{skill.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "unbound" in data["message"].lower()

    def test_unbind_agent_skill_not_found(self, client, auth_headers, test_org, db):
        """DELETE /api/agents/{id}/skills/{skill_id} - Skill not found"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="No Skill Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        fake_skill_id = str(uuid.uuid4())
        response = client.delete(f"/api/agents/{agent.id}/skills/{fake_skill_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_unbind_agent_skill_agent_not_found(self, client, auth_headers):
        """DELETE /api/agents/{id}/skills/{skill_id} - Agent not found"""
        fake_agent_id = str(uuid.uuid4())
        fake_skill_id = str(uuid.uuid4())
        response = client.delete(f"/api/agents/{fake_agent_id}/skills/{fake_skill_id}", headers=auth_headers)
        assert response.status_code == 404


class TestOrgAgentUsage:
    def test_get_org_agent_usage_success(self, client, auth_headers, test_org, db):
        """GET /api/orgs/{id}/agents/usage - Get org agent usage (T-323)"""
        agent1 = Agent(
            id=str(uuid.uuid4()),
            name="Usage Agent 1",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        agent2 = Agent(
            id=str(uuid.uuid4()),
            name="Usage Agent 2",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent1)
        db.add(agent2)
        db.commit()

        response = client.get(f"/api/orgs/{test_org.id}/agents/usage", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["org_id"] == test_org.id
        assert data["data"]["total_agents"] == 2
        assert data["data"]["active_agents"] == 1
        assert len(data["data"]["agent_usages"]) == 2

    def test_get_org_agent_usage_no_agents(self, client, auth_headers, test_org):
        """GET /api/orgs/{id}/agents/usage - No agents in org"""
        response = client.get(f"/api/orgs/{test_org.id}/agents/usage", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["org_id"] == test_org.id
        assert data["data"]["total_agents"] == 0
        assert data["data"]["active_agents"] == 0
        assert data["data"]["agent_usages"] == []

    def test_get_org_agent_usage_wrong_org(self, client, auth_headers, test_org):
        """GET /api/orgs/{id}/agents/usage - Org not found returns 404"""
        wrong_org_id = str(uuid.uuid4())
        response = client.get(f"/api/orgs/{wrong_org_id}/agents/usage", headers=auth_headers)
        assert response.status_code == 404


class TestAgentDailyMetrics:
    def test_get_agent_daily_metrics_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/metrics/daily - Get Agent daily metrics (T-321)"""
        from datetime import date, timedelta
        from models.agent_metric import AgentMetric

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Daily Metrics Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        today = date.today()
        metric1 = AgentMetric(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            date=today - timedelta(days=1),
            tasks_completed=10,
            tasks_failed=2,
            avg_response_time_ms=150,
            token_usage=5000,
        )
        metric2 = AgentMetric(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            date=today,
            tasks_completed=15,
            tasks_failed=1,
            avg_response_time_ms=120,
            token_usage=7500,
        )
        db.add(metric1)
        db.add(metric2)
        db.commit()

        response = client.get(
            f"/api/agents/{agent.id}/metrics/daily",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == agent.id
        assert "start_date" in data["data"]
        assert "end_date" in data["data"]
        assert "daily_metrics" in data["data"]
        assert len(data["data"]["daily_metrics"]) == 2

    def test_get_agent_daily_metrics_with_date_range(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/metrics/daily - With custom date range"""
        from datetime import date, timedelta
        from models.agent_metric import AgentMetric

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Date Range Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        today = date.today()
        metric = AgentMetric(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            date=today,
            tasks_completed=5,
            tasks_failed=1,
            avg_response_time_ms=100,
            token_usage=2000,
        )
        db.add(metric)
        db.commit()

        start = (today - timedelta(days=7)).isoformat()
        end = today.isoformat()
        response = client.get(
            f"/api/agents/{agent.id}/metrics/daily?start_date={start}&end_date={end}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["start_date"] == start
        assert data["data"]["end_date"] == end
        assert len(data["data"]["daily_metrics"]) == 1

    def test_get_agent_daily_metrics_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/metrics/daily - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/metrics/daily", headers=auth_headers)
        assert response.status_code == 404

    def test_get_agent_daily_metrics_no_data(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/metrics/daily - No metrics data"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="No Metrics Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/metrics/daily", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == agent.id
        assert data["data"]["daily_metrics"] == []


class TestAgentTaskCounts:
    def test_get_agent_task_counts_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/tasks/count - Get Agent task execution counts (T-322)"""
        from models.execution import Execution, ExecutionStatus

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Task Count Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        # Create some executions for the agent
        from models.task import Task
        from models.project import Project

        project = Project(
            id=str(uuid.uuid4()),
            name="Test Project",
            org_id=test_org.id,
            status="active",
            created_by=test_org.id,
        )
        db.add(project)
        db.commit()

        task1 = Task(
            id=str(uuid.uuid4()),
            title="Task 1",
            project_id=project.id,
            created_by=test_org.id,
            status="todo",
        )
        task2 = Task(
            id=str(uuid.uuid4()),
            title="Task 2",
            project_id=project.id,
            created_by=test_org.id,
            status="todo",
        )
        task3 = Task(
            id=str(uuid.uuid4()),
            title="Task 3",
            project_id=project.id,
            created_by=test_org.id,
            status="todo",
        )
        db.add_all([task1, task2, task3])
        db.commit()

        exec1 = Execution(
            id=str(uuid.uuid4()),
            task_id=task1.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        exec2 = Execution(
            id=str(uuid.uuid4()),
            task_id=task2.id,
            agent_id=agent.id,
            status=ExecutionStatus.completed.value,
        )
        exec3 = Execution(
            id=str(uuid.uuid4()),
            task_id=task3.id,
            agent_id=agent.id,
            status=ExecutionStatus.failed.value,
        )
        db.add_all([exec1, exec2, exec3])
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/tasks/count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["total_tasks"] == 3
        assert data["data"]["completed_tasks"] == 2
        assert data["data"]["failed_tasks"] == 1

    def test_get_agent_task_counts_no_executions(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/tasks/count - No executions"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="No Tasks Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/tasks/count", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["total_tasks"] == 0
        assert data["data"]["completed_tasks"] == 0
        assert data["data"]["failed_tasks"] == 0

    def test_get_agent_task_counts_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/tasks/count - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/tasks/count", headers=auth_headers)
        assert response.status_code == 404


class TestAgentPerformance:
    def test_get_agent_performance_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/performance - Get Agent performance summary (T-324)"""
        from datetime import date, timedelta
        from models.agent_metric import AgentMetric

        agent = Agent(
            id=str(uuid.uuid4()),
            name="Performance Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="online",
        )
        db.add(agent)
        db.commit()

        today = date.today()
        metric1 = AgentMetric(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            date=today - timedelta(days=1),
            tasks_completed=10,
            tasks_failed=2,
            avg_response_time_ms=150,
            token_usage=5000,
        )
        metric2 = AgentMetric(
            id=str(uuid.uuid4()),
            agent_id=agent.id,
            date=today,
            tasks_completed=15,
            tasks_failed=1,
            avg_response_time_ms=120,
            token_usage=7500,
        )
        db.add(metric1)
        db.add(metric2)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/performance", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["status"] == "online"
        assert data["data"]["is_healthy"] is True
        assert data["data"]["tasks_completed"] == 25
        assert data["data"]["tasks_failed"] == 3
        assert data["data"]["success_rate"] == pytest.approx(89.29, rel=0.01)
        assert data["data"]["avg_response_time_ms"] == 135
        assert data["data"]["total_token_usage"] == 12500

    def test_get_agent_performance_no_metrics(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/performance - No metrics data"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="No Metrics Performance Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/performance", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["status"] == "offline"
        assert data["data"]["is_healthy"] is False
        assert data["data"]["tasks_completed"] == 0
        assert data["data"]["tasks_failed"] == 0
        assert data["data"]["success_rate"] == 0.0
        assert data["data"]["avg_response_time_ms"] == 0
        assert data["data"]["total_token_usage"] == 0

    def test_get_agent_performance_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/performance - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/performance", headers=auth_headers)
        assert response.status_code == 404

    def test_get_agent_performance_access_denied(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/performance - Access denied for wrong org"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Access Denied Agent",
            description="Test",
            agent_type="hermes",
            org_id=str(uuid.uuid4()),
            status="online",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/performance", headers=auth_headers)
        assert response.status_code == 403
