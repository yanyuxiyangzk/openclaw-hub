import pytest
import uuid
import json
from models.agent import Agent


class TestGetAgentMemory:
    """GET /api/agents/{id}/memory - Get memory config (T-310)"""

    def test_get_agent_memory_success(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/memory - Get memory config"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Memory Agent",
            description="Test agent for memory",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            config=json.dumps({
                "memory_type": "shortterm",
                "max_context_tokens": 8192,
                "context_window": 20,
                "persist_context": True,
            }),
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/memory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["memory_type"] == "shortterm"
        assert data["data"]["max_context_tokens"] == 8192
        assert data["data"]["context_window"] == 20
        assert data["data"]["persist_context"] is True

    def test_get_agent_memory_default_values(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/memory - Default values when no config"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Default Memory Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            config=None,
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/memory", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["memory_type"] == "shortterm"
        assert data["data"]["max_context_tokens"] == 4096
        assert data["data"]["context_window"] == 10
        assert data["data"]["persist_context"] is True

    def test_get_agent_memory_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/memory - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/memory", headers=auth_headers)
        assert response.status_code == 404

    def test_get_agent_memory_unauthorized(self, client, test_org, db):
        """GET /api/agents/{id}/memory - Unauthorized"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Unauthorized Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/memory")
        assert response.status_code == 401

    def test_get_agent_memory_access_denied(self, client, auth_headers, db):
        """GET /api/agents/{id}/memory - Access denied (different org)"""
        fake_org_id = str(uuid.uuid4())
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Other Org Agent",
            description="Test",
            agent_type="hermes",
            org_id=fake_org_id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.get(f"/api/agents/{agent.id}/memory", headers=auth_headers)
        assert response.status_code == 403


class TestUpdateAgentMemory:
    """PUT /api/agents/{id}/memory - Update memory config (T-311)"""

    def test_update_agent_memory_success(self, client, auth_headers, test_org, db):
        """PUT /api/agents/{id}/memory - Update memory config"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Update Memory Agent",
            description="Test agent",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            config=json.dumps({
                "memory_type": "shortterm",
                "max_context_tokens": 4096,
                "context_window": 10,
                "persist_context": True,
            }),
        )
        db.add(agent)
        db.commit()

        response = client.put(
            f"/api/agents/{agent.id}/memory",
            headers=auth_headers,
            json={
                "memory_type": "longterm",
                "max_context_tokens": 16384,
                "context_window": 50,
                "persist_context": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["memory_type"] == "longterm"
        assert data["data"]["max_context_tokens"] == 16384
        assert data["data"]["context_window"] == 50
        assert data["data"]["persist_context"] is False

        # Verify persistence
        db.refresh(agent)
        saved_config = json.loads(agent.config)
        assert saved_config["memory_type"] == "longterm"
        assert saved_config["max_context_tokens"] == 16384
        assert saved_config["context_window"] == 50
        assert saved_config["persist_context"] is False

    def test_update_agent_memory_partial(self, client, auth_headers, test_org, db):
        """PUT /api/agents/{id}/memory - Partial update"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Partial Update Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            config=json.dumps({
                "memory_type": "shortterm",
                "max_context_tokens": 4096,
                "context_window": 10,
                "persist_context": True,
            }),
        )
        db.add(agent)
        db.commit()

        response = client.put(
            f"/api/agents/{agent.id}/memory",
            headers=auth_headers,
            json={
                "memory_type": "longterm",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["memory_type"] == "longterm"
        # Other fields should use defaults or remain unchanged based on implementation

    def test_update_agent_memory_not_found(self, client, auth_headers):
        """PUT /api/agents/{id}/memory - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.put(
            f"/api/agents/{fake_id}/memory",
            headers=auth_headers,
            json={
                "memory_type": "longterm",
                "max_context_tokens": 16384,
            },
        )
        assert response.status_code == 404

    def test_update_agent_memory_unauthorized(self, client, test_org, db):
        """PUT /api/agents/{id}/memory - Unauthorized"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Unauthorized Update Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.put(
            f"/api/agents/{agent.id}/memory",
            json={
                "memory_type": "longterm",
            },
        )
        assert response.status_code == 401

    def test_update_agent_memory_access_denied(self, client, auth_headers, db):
        """PUT /api/agents/{id}/memory - Access denied (different org)"""
        fake_org_id = str(uuid.uuid4())
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Other Org Agent",
            description="Test",
            agent_type="hermes",
            org_id=fake_org_id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.put(
            f"/api/agents/{agent.id}/memory",
            headers=auth_headers,
            json={
                "memory_type": "longterm",
            },
        )
        assert response.status_code == 403


class TestSetAgentContext:
    """POST /api/agents/{id}/context - Set context (T-312)"""

    def test_set_agent_context_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/context - Set context"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Context Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
        )
        db.add(agent)
        db.commit()

        response = client.post(
            f"/api/agents/{agent.id}/context",
            headers=auth_headers,
            json={
                "context": {"role": "system", "content": "You are a helpful assistant."},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["context"] == {"role": "system", "content": "You are a helpful assistant."}
        assert "success" in data["data"]["message"].lower()

    def test_set_agent_context_not_found(self, client, auth_headers):
        """POST /api/agents/{id}/context - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(
            f"/api/agents/{fake_id}/context",
            headers=auth_headers,
            json={"context": {"key": "value"}},
        )
        assert response.status_code == 404


class TestGetAgentHistory:
    """GET /api/agents/{id}/history - Get conversation history (T-313)

    NOTE: Due to route conflict with agents_router, this endpoint currently
    uses the Activity model instead of agent.config for conversation history.
    This test documents the current behavior.
    """

    def test_get_agent_history_empty(self, client, auth_headers, test_org, db):
        """GET /api/agents/{id}/history - Get history (empty)"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="History Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            config=json.dumps({
                "context_history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                ]
            }),
        )
        db.add(agent)
        db.commit()

        # Note: This hits agents_router which uses Activity model, not phase3
        response = client.get(f"/api/agents/{agent.id}/history?limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # agents_router returns paginated format
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]

    def test_get_agent_history_not_found(self, client, auth_headers):
        """GET /api/agents/{id}/history - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/agents/{fake_id}/history", headers=auth_headers)
        assert response.status_code == 404


class TestClearAgentMemory:
    """DELETE /api/agents/{id}/memory/clear - Clear memory (T-314)"""

    def test_clear_agent_memory_success(self, client, auth_headers, test_org, db):
        """DELETE /api/agents/{id}/memory/clear - Clear memory"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Clear Memory Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="offline",
            memory=json.dumps({
                "context": "Some context",
                "context_history": [{"role": "user", "content": "Hello"}],
            }),
        )
        db.add(agent)
        db.commit()

        response = client.delete(f"/api/agents/{agent.id}/memory/clear", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["memory_type"] == "shortterm"
        assert data["data"]["context_items"] == 0

    def test_clear_agent_memory_not_found(self, client, auth_headers):
        """DELETE /api/agents/{id}/memory/clear - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/agents/{fake_id}/memory/clear", headers=auth_headers)
        assert response.status_code == 404


class TestResetAgentState:
    """POST /api/agents/{id}/reset - Reset agent state (T-315)"""

    def test_reset_agent_state_success(self, client, auth_headers, test_org, db):
        """POST /api/agents/{id}/reset - Reset agent state"""
        agent = Agent(
            id=str(uuid.uuid4()),
            name="Reset Agent",
            description="Test",
            agent_type="hermes",
            org_id=test_org.id,
            status="busy",
            config=json.dumps({
                "context": "Some context",
                "context_history": [{"role": "user", "content": "Hello"}],
            }),
        )
        db.add(agent)
        db.commit()

        response = client.post(f"/api/agents/{agent.id}/reset", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["agent_id"] == agent.id
        assert data["data"]["status"] == "offline"

    def test_reset_agent_state_not_found(self, client, auth_headers):
        """POST /api/agents/{id}/reset - Agent not found"""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/agents/{fake_id}/reset", headers=auth_headers)
        assert response.status_code == 404