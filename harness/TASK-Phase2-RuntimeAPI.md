# Phase 2 Task: Runtime Management API

## Overview

Implement T-230 to T-235 (6 APIs) for runtime management of Agents.

## Task Scope

### T-230: POST /api/agents/{id}/start
- Start an Agent using HermesInstanceManager
- Route: backend/routers/agents.py

### T-231: POST /api/agents/{id}/stop
- Stop an Agent using HermesInstanceManager
- Route: backend/routers/agents.py

### T-232: GET /api/agents/{id}/logs
- Read Agent logs from filesystem
- Route: backend/routers/agents.py

### T-233: GET /api/agents/{id}/health
- Agent health check
- Route: backend/routers/agents.py

### T-234: GET /api/agents/active
- List active Agents
- Route: backend/routers/agents.py

### T-235: WS /ws/agents/{id}/status
- WebSocket for Agent status updates
- Route: backend/routers/agents.py

## HermesInstanceManager Reference

```python
# In hermes-runtime/services/hermes_instance_manager.py
manager = HermesInstanceManager(hermes_src, tenants_root)
manager.start_instance(tenant_id, agent_id, mode="subprocess")
manager.stop_instance(instance_id)
manager.get_instance(instance_id).status
```

## Output Files

- backend/routers/agents.py (extend existing)
- backend/tests/test_agent_runtime.py

## Acceptance Criteria

- [ ] All 6 APIs implemented
- [ ] Agent start/stop works via HermesInstanceManager
- [ ] WebSocket connection works
- [ ] All previous tests still pass

## Start!
