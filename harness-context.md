# OpenClawHub - Harness Context

> 项目类型: 数字员工 SaaS 平台（多租户）
> 技术栈: FastAPI + Vue3 + PostgreSQL + Hermes Agent
> Phase: Phase 2 - 项目管理 + Agent 管理 ✅ 完成
> 更新: 2026-04-23

---

## 项目概述

OpenClawHub 是一个数字员工 SaaS 平台，目标是打造一人公司的数字员工团队。
平台提供：多租户管理 + Agent 运行时（Hermes）+ 工作流协作。

**核心技术选型：**
- 后端: Python FastAPI + SQLAlchemy 2.0 + Alembic + SQLite (开发环境) / PostgreSQL (生产环境)
- 前端: Vue3 + Vite + TypeScript + TailwindCSS + Pinia
- Agent 引擎: Hermes Agent（NousResearch，MIT License）
- 认证: JWT (HS256) + bcrypt

---

## Phase 2 开发状态

### ✅ 已完成

| 任务 | 状态 | 文件 |
|------|------|------|
| T-201: projects 表 | ✅ 完成 | backend/models/project.py |
| T-202: agents 表 | ✅ 完成 | backend/models/agent.py |
| T-203: project_agents 表 | ✅ 完成 | backend/models/project_agent.py |
| T-204: project_members 表 | ✅ 完成 | backend/models/project_member.py |
| 数据库迁移 | ✅ 完成 | backend/alembic/versions/64d21646b23e_*.py |
| T-210~T-217: 项目管理 API | ✅ 完成 (8/8) | backend/routers/projects.py |
| T-220~T-229: Agent API | ✅ 完成 (10/10) | backend/routers/agents.py |
| T-230~T-235: 运行时管理 | ✅ 完成 (6/6) | backend/routers/agents.py |
| T-240~T-243: 项目-Agent 关联 | ✅ 完成 | backend/routers/projects.py |
| 测试 | ✅ 完成 | 110 tests passed |

### 📋 待执行

| 任务 | 状态 |
|------|------|
| 前端页面（T-250~T-265） | ⏳ 待执行 |
| 测试任务（T-270~T-277） | ⏳ 待执行 |

---

## 数据库模型（Phase 2）

### projects 表
```python
- id: UUID (PK)
- name: VARCHAR(128)
- description: TEXT
- org_id: UUID (FK -> organizations.id)
- status: ENUM('active', 'archived', 'deleted')
- settings: JSON
- created_by: UUID (FK -> users.id)
- created_at, updated_at
```

### agents 表
```python
- id: UUID (PK)
- name: VARCHAR(64)
- description: TEXT
- agent_type: VARCHAR(32)  # 'hermes'
- config: JSON  # Agent 配置
- org_id: UUID (FK -> organizations.id)
- status: ENUM('offline', 'online', 'busy', 'error')
- last_seen_at: DATETIME
- created_at, updated_at
```

### project_agents 表
```python
- id: UUID (PK)
- project_id: UUID (FK)
- agent_id: UUID (FK)
- assigned_at: DATETIME
- UNIQUE(project_id, agent_id)
```

### project_members 表
```python
- id: UUID (PK)
- project_id: UUID (FK)
- user_id: UUID (FK)
- role: ENUM('owner', 'admin', 'member')
- joined_at
```

---

## Phase 2 API 清单

### 项目管理（8 个）
- POST /api/projects - 创建项目
- GET /api/projects - 项目列表
- GET /api/projects/{id} - 项目详情
- PUT /api/projects/{id} - 更新项目
- DELETE /api/projects/{id} - 删除项目（软删除）
- GET /api/projects/{id}/members - 成员列表
- POST /api/projects/{id}/members - 添加成员
- DELETE /api/projects/{id}/members/{user_id} - 移除成员

### Agent 管理（10 个）
- POST /api/agents - 创建 Agent
- GET /api/agents - Agent 列表
- GET /api/agents/{id} - Agent 详情
- PUT /api/agents/{id} - 更新 Agent
- DELETE /api/agents/{id} - 删除 Agent
- GET /api/agents/{id}/status - Agent 状态
- POST /api/agents/{id}/projects/{project_id} - Agent 加入项目
- GET /api/projects/{id}/agents - 项目 Agent 列表
- GET /api/projects/{id}/agents/available - 可用 Agent
- DELETE /api/projects/{id}/agents/{agent_id} - 从项目移除

### 运行时管理（6 个）
- POST /api/agents/{id}/start - 启动 Agent
- POST /api/agents/{id}/stop - 停止 Agent
- GET /api/agents/{id}/logs - Agent 日志
- GET /api/agents/{id}/health - 健康检查
- GET /api/agents/active - 活跃 Agent
- WS /ws/agents/{id}/status - 状态 WebSocket

---

## 目录结构

```
OpenClawHub/
├── backend/
│   ├── models/
│   │   ├── project.py      # ✅ 已创建
│   │   ├── agent.py        # ✅ 已创建
│   │   ├── project_agent.py # ✅ 已创建
│   │   ├── project_member.py # ✅ 已创建
│   │   ├── user.py
│   │   ├── organization.py
│   │   └── invitation.py
│   ├── routers/
│   │   ├── auth.py         # Phase 1
│   │   ├── users.py        # Phase 1
│   │   ├── orgs.py         # Phase 1
│   │   ├── invitations.py  # Phase 1
│   │   ├── projects.py     # ⏳ 需要创建
│   │   └── agents.py       # ⏳ 需要创建
│   ├── schemas/
│   │   ├── project.py       # ⏳ 需要创建
│   │   └── agent.py         # ⏳ 需要创建
│   ├── services/
│   │   ├── project_service.py # ⏳ 需要创建
│   │   └── agent_service.py   # ⏳ 需要创建
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial.py
│   │       └── 64d21646b23e_create_projects_agents_*.py # ✅ Phase 2
│   └── tests/
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_orgs.py
│       ├── test_projects.py  # ⏳ 需要创建
│       └── test_agents.py    # ⏳ 需要创建
└── frontend/
    └── src/
        ├── views/
        │   ├── projects/    # ⏳ 需要创建
        │   └── agents/      # ⏳ 需要创建
        ├── components/
        │   ├── projects/    # ⏳ 需要创建
        │   └── agents/      # ⏳ 需要创建
        └── api/
            ├── projects.ts  # ⏳ 需要创建
            └── agents.ts    # ⏳ 需要创建
```

---

## 开发规则

1. **响应格式统一：** `{ code: 0, message: "success", data: {...} }`
2. **JWT 认证：** 所有 API 需要认证
3. **权限检查：** 项目成员才能访问项目资源
4. **软删除：** DELETE 操作设置 status='deleted'
5. **测试要求：** 每个 API 需要写测试

---

## Phase 1 状态

Phase 1 认证模块已完成：
- 23 个 API
- 7 个前端页面
- 58 个测试用例全部通过

---

_Last updated: 2026-04-23_
