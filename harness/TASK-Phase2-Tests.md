# Phase 2 Task: Test Tasks

## Overview

Implement T-270 to T-277 (8 test tasks) for Phase 2.

## Task Scope

### Backend Tests

**T-270: Project Module Tests**
- File: backend/tests/test_projects.py
- Coverage target: > 80%

**T-271: Agent Module Tests**
- File: backend/tests/test_agents.py
- Coverage target: > 80%

**T-272: Agent Runtime Integration Tests**
- File: backend/tests/test_agent_runtime.py
- Test: start/stop/logs/health APIs

### Frontend Tests

**T-273: Project List View Tests**
- File: frontend/src/__tests__/views/ProjectListView.spec.ts
- Test: rendering, API calls

**T-274: Agent List View Tests**
- File: frontend/src/__tests__/views/AgentListView.spec.ts
- Test: rendering, API calls

**T-275: Project Detail View Tests**
- File: frontend/src/__tests__/views/ProjectDetailView.spec.ts
- Test: members/agents management

**T-276: Agent Detail View Tests**
- File: frontend/src/__tests__/views/AgentDetailView.spec.ts
- Test: health/logs/start/stop

### Integration Tests

**T-277: API Integration Tests**
- File: backend/tests/test_projects_agents_integration.py
- Test: end-to-end flow

## Test Command

Backend:
```bash
cd backend && pytest -v --cov=. --cov-report=term-missing
```

Frontend:
```bash
cd frontend && npm run test
```

## Acceptance Criteria

- [ ] All backend tests pass
- [ ] All frontend tests pass
- [ ] Coverage > 80% for backend modules
- [ ] Integration tests pass

## Start!
