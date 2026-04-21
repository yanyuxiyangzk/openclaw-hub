# Phase 2 任务：Agent 基础管理 API 开发

## 任务概述

根据 `TASK-Phase2-5_开发计划.md` 执行 Agent 基础管理 API 开发任务。

**任务范围：** T-220 到 T-229（10 个 API）

---

## 项目信息

**项目路径：** `D:\project\aicoding\OpenClawHub`

**参考 Phase 1 实现：**
- `backend/routers/orgs.py` - 组织管理 API
- `backend/routers/users.py` - 用户管理 API

**Phase 2 数据库模型：**
- `backend/models/agent.py` - Agent 模型（已创建）
- `backend/models/project_agent.py` - ProjectAgent 模型（已创建）

**Phase 2 已完成：**
- 项目管理 API（T-210~T-217）

---

## API 任务清单

### T-220: 实现 POST /api/agents

创建 Agent

- 路由：`backend/routers/agents.py`
- Schema：`backend/schemas/agent.py`
- 测试：`backend/tests/test_agents.py::test_create_agent`
- 依赖：T-202
- 验收标准：能创建 Agent

### T-221: 实现 GET /api/agents

Agent 列表

- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_list_agents`
- 依赖：T-202
- 验收标准：返回当前组织的 Agent 列表

### T-222: 实现 GET /api/agents/{id}

Agent 详情

- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_get_agent`
- 依赖：T-202, T-220
- 验收标准：返回 Agent 详情

### T-223: 实现 PUT /api/agents/{id}

更新 Agent

- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_update_agent`
- 依赖：T-202, T-222
- 验收标准：能更新 Agent 配置

### T-224: 实现 DELETE /api/agents/{id}

删除 Agent

- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_delete_agent`
- 依赖：T-202, T-222
- 验收标准：软删除 Agent

### T-225: 实现 GET /api/agents/{id}/status

Agent 状态

- 路由：`backend/routers/agents.py`
- 依赖：T-202, T-222
- 验收标准：返回 Agent 当前状态

### T-226: 实现 POST /api/agents/{id}/projects/{project_id}

Agent 加入项目

- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_agent_join_project`
- 依赖：T-203, T-222
- 验收标准：Agent 加入项目

### T-227: 实现 GET /api/projects/{id}/agents

项目 Agent 列表

- 路由：`backend/routers/projects.py`（复用）
- 测试：`backend/tests/test_projects.py::test_list_project_agents`
- 依赖：T-203
- 验收标准：返回项目下的 Agent 列表

### T-228: 实现 GET /api/projects/{id}/agents/available

可用 Agent 列表

- 路由：`backend/routers/projects.py`（复用）
- 依赖：T-203
- 验收标准：返回项目可用 Agent（未加入的）

### T-229: 实现 DELETE /api/projects/{id}/agents/{agent_id}

从项目移除 Agent

- 路由：`backend/routers/projects.py`（复用）
- 测试：`backend/tests/test_projects.py::test_remove_project_agent`
- 依赖：T-203
- 验收标准：从项目移除 Agent

---

## 开发规范

1. **复制 Phase 1 模式** - 参考 `routers/orgs.py` 的结构
2. **使用相同的响应格式** - `{ code: 0, message: "success", data: {...} }`
3. **JWT 认证** - 使用 Phase 1 的认证中间件
4. **权限检查** - 组织成员才能访问组织资源
5. **边开发边写测试** - 每个 API 完成后写测试

---

## 输出文件

- 路由：`backend/routers/agents.py`
- Schema：`backend/schemas/agent.py`
- 服务：`backend/services/agent_service.py`
- 测试：`backend/tests/test_agents.py`

---

## 验收标准

- [ ] 10 个 API 全部实现
- [ ] 测试覆盖率 > 80%
- [ ] Phase 1 + Phase 2 项目管理 API 测试不受影响

---

**开始执行！**
