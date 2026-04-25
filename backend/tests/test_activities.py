import pytest


class TestActivityCreate:
    def test_create_and_list_activity(self, client, auth_headers):
        # 创建 activity
        resp = client.post("/api/activities",
            headers=auth_headers,
            json={
                "actor_id": "test-actor",
                "actor_name": "Test Actor",
                "action_type": "created",
                "entity_type": "task",
                "entity_id": "task-001",
                "entity_name": "测试任务"
            }
        )
        assert resp.status_code == 200

        # 获取列表
        resp = client.get("/api/activities", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["total"] >= 1
