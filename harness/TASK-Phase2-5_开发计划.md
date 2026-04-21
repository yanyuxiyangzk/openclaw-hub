# OpenClawHub Phase 2-5 开发计划

> 制定时间: 2026-04-21 19:10
> 制定角色: 架构师
> 依据文档: Phase2-9_全Phase规划草案_产品经理整改版
> 状态: 初稿，待项目经理审批

---

## 整体任务统计

| Phase | 后端任务 | 前端任务 | 数据库任务 | 测试任务 | 总计 |
|-------|----------|----------|------------|----------|------|
| Phase 2 | 28 | 12 | 4 | 8 | 52 |
| Phase 3 | 15 | 6 | 2 | 4 | 27 |
| Phase 4 | 22 | 10 | 2 | 6 | 40 |
| Phase 5 | 12 | 6 | 2 | 4 | 24 |
| **总计** | **77** | **34** | **10** | **22** | **143** |

---

## Phase 2: 项目管理 + Agent 管理

### 一、后端任务

#### 1.1 数据库任务（4 个）

**T-201: 创建 projects 表**
- 文件：`backend/models/project.py`（新建）
- 迁移：`backend/alembic/versions/xxx_create_projects.py`
- 依赖：[]
- 验收标准：表创建成功，包含 name/description/org_id/status/settings/created_by 字段

**T-202: 创建 agents 表**
- 文件：`backend/models/agent.py`（新建）
- 迁移：`backend/alembic/versions/xxx_create_agents.py`
- 依赖：[]
- 验收标准：表创建成功，包含 name/description/agent_type/config/org_id/status 字段

**T-203: 创建 project_agents 表**
- 文件：`backend/models/project_agent.py`（新建）
- 迁移：`backend/alembic/versions/xxx_create_project_agents.py`
- 依赖：[T-201, T-202]
- 验收标准：表创建成功，包含 project_id/agent_id/assigned_at，复合唯一索引

**T-204: 创建 project_members 表**
- 文件：`backend/models/project_member.py`（新建）
- 迁移：`backend/alembic/versions/xxx_create_project_members.py`
- 依赖：[T-201]
- 验收标准：表创建成功，复用 OrganizationMember 结构

---

#### 1.2 API 任务 - 项目管理（8 个）

**T-210: 实现 POST /api/projects**
- 路由：`backend/routers/projects.py`
- Schema：`backend/schemas/project.py`
- Service：`backend/services/project_service.py`
- 测试：`backend/tests/test_projects.py::test_create_project`
- 依赖：[T-201]
- 验收标准：能创建项目，返回项目详情

**T-211: 实现 GET /api/projects**
- 路由：`backend/routers/projects.py`
- Schema：`backend/schemas/project.py`
- 测试：`backend/tests/test_projects.py::test_list_projects`
- 依赖：[T-201]
- 验收标准：返回当前用户的项目列表

**T-212: 实现 GET /api/projects/{id}**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_get_project`
- 依赖：[T-201, T-210]
- 验收标准：返回项目详情，包含成员和 Agent

**T-213: 实现 PUT /api/projects/{id}**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_update_project`
- 依赖：[T-201, T-212]
- 验收标准：能更新项目名称/描述/状态

**T-214: 实现 DELETE /api/projects/{id}**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_delete_project`
- 依赖：[T-201, T-212]
- 验收标准：软删除（status='deleted'）

**T-215: 实现 GET /api/projects/{id}/members**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_list_project_members`
- 依赖：[T-204, T-212]
- 验收标准：返回项目成员列表

**T-216: 实现 POST /api/projects/{id}/members**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_add_project_member`
- 依赖：[T-204, T-212]
- 验收标准：能添加项目成员

**T-217: 实现 DELETE /api/projects/{id}/members/{user_id}**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_remove_project_member`
- 依赖：[T-204, T-212]
- 验收标准：能移除项目成员

---

#### 1.3 API 任务 - Agent 基础管理（10 个）

**T-220: 实现 POST /api/agents**
- 路由：`backend/routers/agents.py`（新建）
- Schema：`backend/schemas/agent.py`（新建）
- 测试：`backend/tests/test_agents.py::test_create_agent`
- 依赖：[T-202]
- 验收标准：能创建 Agent

**T-221: 实现 GET /api/agents**
- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_list_agents`
- 依赖：[T-202]
- 验收标准：返回当前组织的 Agent 列表

**T-222: 实现 GET /api/agents/{id}**
- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_get_agent`
- 依赖：[T-202, T-220]
- 验收标准：返回 Agent 详情

**T-223: 实现 PUT /api/agents/{id}**
- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_update_agent`
- 依赖：[T-202, T-222]
- 验收标准：能更新 Agent 配置

**T-224: 实现 DELETE /api/agents/{id}**
- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_delete_agent`
- 依赖：[T-202, T-222]
- 验收标准：软删除 Agent

**T-225: 实现 GET /api/agents/{id}/status**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202, T-222]
- 验收标准：返回 Agent 当前状态（通过 HermesInstanceManager）

**T-226: 实现 POST /api/agents/{id}/projects/{project_id}**
- 路由：`backend/routers/agents.py`
- 测试：`backend/tests/test_agents.py::test_agent_join_project`
- 依赖：[T-203, T-222, T-212]
- 验收标准：Agent 加入项目

**T-227: 实现 GET /api/projects/{id}/agents**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_list_project_agents`
- 依赖：[T-203, T-212]
- 验收标准：返回项目下的 Agent 列表

**T-228: 实现 GET /api/projects/{id}/agents/available**
- 路由：`backend/routers/projects.py`
- 依赖：[T-203, T-212]
- 验收标准：返回项目可用 Agent（未加入的）

**T-229: 实现 DELETE /api/projects/{id}/agents/{agent_id}**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_remove_project_agent`
- 依赖：[T-203, T-212]
- 验收标准：从项目移除 Agent

---

#### 1.4 API 任务 - 运行时管理（6 个）

**T-230: 实现 POST /api/agents/{id}/start**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202, T-222]
- 验收标准：调用 HermesInstanceManager 启动 Agent

**T-231: 实现 POST /api/agents/{id}/stop**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202, T-222]
- 验收标准：调用 HermesInstanceManager 停止 Agent

**T-232: 实现 GET /api/agents/{id}/logs**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202, T-222]
- 验收标准：从文件系统读取并返回 Agent 日志

**T-233: 实现 GET /api/agents/{id}/health**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202, T-222]
- 验收标准：返回 Agent 健康检查结果

**T-234: 实现 GET /api/agents/active**
- 路由：`backend/routers/agents.py`
- 依赖：[T-202]
- 验收标准：返回当前活跃的 Agent 列表

**T-235: 实现 WS /ws/agents/{id}/status**
- 路由：`backend/routers/agents.py`
- 依赖：[T-230, T-231]
- 验收标准：WebSocket 推送 Agent 状态变更

---

#### 1.5 API 任务 - 项目-Agent 关联（4 个）

**T-240: 实现 POST /api/projects/{id}/agents/assign**
- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_assign_agent_to_project`
- 依赖：[T-203, T-212]
- 验收标准：分配 Agent 到项目

**T-241: 实现 GET /api/projects/{id}/tasks**
- 路由：`backend/routers/projects.py`
- 依赖：[T-212]
- 验收标准：返回项目下的任务列表（Phase 4 预留）

**T-242: 实现 POST /api/projects/{id}/tasks**
- 路由：`backend/routers/projects.py`
- 依赖：[T-212]
- 验收标准：创建项目任务（Phase 4 预留）

**T-243: 实现 GET /api/projects/{id}/activity**
- 路由：`backend/routers/projects.py`
- 依赖：[T-212]
- 验收标准：返回项目活动流（Phase 6 预留）

---

### 二、前端任务

#### 2.1 页面任务（6 个）

**T-250: 实现 /projects 项目列表页**
- 页面：`frontend/src/views/projects/ProjectListView.vue`
- 组件：`frontend/src/components/projects/ProjectCard.vue`
- API：`frontend/src/api/projects.ts`（新建）
- 依赖：[T-210, T-211]
- 验收标准：显示项目列表，支持创建新项目

**T-251: 实现 /projects/new 创建项目页**
- 页面：`frontend/src/views/projects/CreateProjectView.vue`
- 依赖：[T-210, T-250]
- 验收标准：表单提交创建项目

**T-252: 实现 /projects/:id 项目详情页**
- 页面：`frontend/src/views/projects/ProjectDetailView.vue`
- 组件：`frontend/src/components/projects/ProjectMembers.vue`
- 组件：`frontend/src/components/projects/ProjectAgents.vue`
- 依赖：[T-212, T-215, T-216, T-217, T-227, T-228, T-240]
- 验收标准：显示项目详情，支持成员和 Agent 管理

**T-253: 实现 /projects/:id/settings 项目设置页**
- 页面：`frontend/src/views/projects/ProjectSettingsView.vue`
- 依赖：[T-213, T-214]
- 验收标准：支持修改和删除项目

**T-254: 实现 /agents Agent 列表页**
- 页面：`frontend/src/views/agents/AgentListView.vue`
- 组件：`frontend/src/components/agents/AgentCard.vue`
- API：`frontend/src/api/agents.ts`（新建）
- 依赖：[T-220, T-221]
- 验收标准：显示 Agent 列表，支持创建 Agent

**T-255: 实现 /agents/:id Agent 详情页**
- 页面：`frontend/src/views/agents/AgentDetailView.vue`
- 组件：`frontend/src/components/agents/AgentStatus.vue`
- 依赖：[T-222, T-223, T-224, T-225]
- 验收标准：显示 Agent 详情，支持配置和操作

---

#### 2.2 组件任务（6 个）

**T-260: 实现 ProjectCard 组件**
- 文件：`frontend/src/components/projects/ProjectCard.vue`
- 依赖：[T-250]
- 验收标准：显示项目卡片，支持快捷操作

**T-261: 实现 ProjectMembers 组件**
- 文件：`frontend/src/components/projects/ProjectMembers.vue`
- 依赖：[T-252]
- 验收标准：成员列表，支持添加/移除

**T-262: 实现 ProjectAgents 组件**
- 文件：`frontend/src/components/projects/ProjectAgents.vue`
- 依赖：[T-252]
- 验收标准：Agent 列表，支持分配/移除

**T-263: 实现 AgentCard 组件**
- 文件：`frontend/src/components/agents/AgentCard.vue`
- 依赖：[T-254]
- 验收标准：显示 Agent 卡片，支持状态显示

**T-264: 实现 AgentStatus 组件**
- 文件：`frontend/src/components/agents/AgentStatus.vue`
- 依赖：[T-255]
- 验收标准：显示 Agent 在线/离线/忙碌状态

**T-265: 实现 AgentActions 组件**
- 文件：`frontend/src/components/agents/AgentActions.vue`
- 依赖：[T-255]
- 验收标准：显示启动/停止/删除按钮

---

### 三、测试任务（8 个）

**T-270: 项目模块单元测试**
- 文件：`backend/tests/test_projects.py`
- 依赖：[T-210 到 T-217]
- 验收标准：覆盖率 > 80%

**T-271: Agent 模块单元测试**
- 文件：`backend/tests/test_agents.py`
- 依赖：[T-220 到 T-229]
- 验收标准：覆盖率 > 80%

**T-272: 运行时管理集成测试**
- 文件：`backend/tests/test_agent_runtime.py`
- 依赖：[T-230, T-231]
- 验收标准：启动/停止流程正常

**T-273: 前端项目页面测试**
- 文件：`frontend/src/__tests__/views/ProjectListView.spec.ts`
- 依赖：[T-250]
- 验收标准：Vitest 测试通过

**T-274: 前端 Agent 页面测试**
- 文件：`frontend/src/__tests__/views/AgentListView.spec.ts`
- 依赖：[T-254]
- 验收标准：Vitest 测试通过

**T-275: 前端项目详情页测试**
- 文件：`frontend/src/__tests__/views/ProjectDetailView.spec.ts`
- 依赖：[T-252]
- 验收标准：Vitest 测试通过

**T-276: 前端 Agent 详情页测试**
- 文件：`frontend/src/__tests__/views/AgentDetailView.spec.ts`
- 依赖：[T-255]
- 验收标准：Vitest 测试通过

**T-277: API 集成测试**
- 文件：`backend/tests/test_projects_agents_integration.py`
- 依赖：[T-210 到 T-243]
- 验收标准：前后端联调正常

---

## Phase 3: Agent 配置预设 + 监控指标

### 一、后端任务（15 个）

#### 数据库任务（2 个）

**T-301: 创建 agent_presets 表**
- 文件：`backend/models/agent_preset.py`
- 迁移：`backend/alembic/versions/xxx_create_agent_presets.py`
- 依赖：[]
- 验收标准：表创建成功

**T-302: 创建 agent_metrics 表**
- 文件：`backend/models/agent_metric.py`
- 迁移：`backend/alembic/versions/xxx_create_agent_metrics.py`
- 依赖：[]
- 验收标准：表创建成功

#### API 任务 - 配置预设（6 个）

**T-310: 实现 GET /api/agent-presets**
- 路由：`backend/routers/agent_presets.py`（新建）
- 依赖：[T-301]
- 验收标准：返回配置预设列表

**T-311: 实现 POST /api/agent-presets**
- 依赖：[T-301]
- 验收标准：创建配置预设

**T-312: 实现 GET /api/agent-presets/{id}**
- 依赖：[T-301]
- 验收标准：返回预设详情

**T-313: 实现 PUT /api/agent-presets/{id}**
- 依赖：[T-301]
- 验收标准：更新预设

**T-314: 实现 DELETE /api/agent-presets/{id}**
- 依赖：[T-301]
- 验收标准：删除预设

**T-315: 实现 POST /api/agents/{id}/apply-preset**
- 路由：`backend/routers/agents.py`
- 依赖：[T-301, T-222]
- 验收标准：Agent 应用预设配置

#### API 任务 - 上下文配置（4 个）

**T-320: 实现 GET /api/agents/{id}/context**
- 依赖：[T-222]
- 验收标准：返回上下文设置

**T-321: 实现 PUT /api/agents/{id}/context**
- 依赖：[T-222]
- 验收标准：更新上下文设置

**T-322: 实现 POST /api/agents/{id}/reset-context**
- 依赖：[T-222]
- 验收标准：重置上下文

**T-323: 实现 GET /api/agents/{id}/context/history**
- 依赖：[T-222]
- 验收标准：返回上下文历史

#### API 任务 - 监控指标（5 个）

**T-330: 实现 GET /api/agents/{id}/metrics**
- 依赖：[T-302, T-222]
- 验收标准：返回 Agent 指标

**T-331: 实现 GET /api/agents/{id}/metrics/daily**
- 依赖：[T-302, T-222]
- 验收标准：返回每日统计

**T-332: 实现 GET /api/orgs/{id}/agents/usage**
- 依赖：[T-302]
- 验收标准：返回组织内 Agent 使用统计

**T-333: 实现 GET /api/agents/{id}/tasks/stats**
- 依赖：[T-222]
- 验收标准：返回任务统计

**T-334: 实现 GET /api/agents/{id}/health/detailed**
- 依赖：[T-222]
- 验收标准：返回详细健康检查

### 二、前端任务（4 个）

**T-340: 实现 /agents/:id/config Agent 配置页**
- 页面：`frontend/src/views/agents/AgentConfigView.vue`
- 依赖：[T-315, T-320, T-321, T-322]
- 验收标准：支持配置预设和上下文

**T-341: 实现 /agents/:id/metrics Agent 指标页**
- 页面：`frontend/src/views/agents/AgentMetricsView.vue`
- 依赖：[T-330, T-331, T-332, T-333]
- 验收标准：显示指标图表

**T-342: 实现 /agent-presets 配置预设管理页**
- 页面：`frontend/src/views/agent-presets/AgentPresetsView.vue`
- 依赖：[T-310 到 T-314]
- 验收标准：CRUD 预设

**T-343: 实现 /agent-presets/new 创建预设页**
- 页面：`frontend/src/views/agent-presets/CreatePresetView.vue`
- 依赖：[T-311]
- 验收标准：表单提交

### 三、测试任务（4 个）

**T-350: 配置预设模块测试**
- 依赖：[T-310 到 T-315]
- 验收标准：覆盖率 > 80%

**T-351: 上下文配置测试**
- 依赖：[T-320 到 T-323]
- 验收标准：覆盖率 > 80%

**T-352: 监控指标测试**
- 依赖：[T-330 到 T-334]
- 验收标准：覆盖率 > 80%

**T-353: 前端配置页测试**
- 依赖：[T-340]
- 验收标准：Vitest 测试通过

---

## Phase 4: 任务看板模块

### 一、后端任务（22 个）

#### 数据库任务（2 个）

**T-401: 创建 tasks 表**
- 文件：`backend/models/task.py`
- 迁移：`backend/alembic/versions/xxx_create_tasks.py`
- 依赖：[]
- 验收标准：表创建成功，包含状态机字段

**T-402: 创建 task_comments 表**
- 文件：`backend/models/task_comment.py`
- 迁移：`backend/alembic/versions/xxx_create_task_comments.py`
- 依赖：[]
- 验收标准：表创建成功

#### API 任务 - 任务 CRUD（8 个）

**T-410: 实现 POST /api/tasks**
- 路由：`backend/routers/tasks.py`（新建）
- 依赖：[T-401]
- 验收标准：创建任务

**T-411: 实现 GET /api/tasks**
- 依赖：[T-401]
- 验收标准：返回任务列表，支持 filter

**T-412: 实现 GET /api/tasks/{id}**
- 依赖：[T-401]
- 验收标准：返回任务详情

**T-413: 实现 PUT /api/tasks/{id}**
- 依赖：[T-401]
- 验收标准：更新任务

**T-414: 实现 DELETE /api/tasks/{id}**
- 依赖：[T-401]
- 验收标准：软删除任务

**T-415: 实现 POST /api/tasks/bulk**
- 依赖：[T-401]
- 验收标准：批量创建任务

**T-416: 实现 PUT /api/tasks/bulk/status**
- 依赖：[T-401]
- 验收标准：批量更新状态

**T-417: 实现 GET /api/tasks/export**
- 依赖：[T-401]
- 验收标准：导出任务 CSV/JSON

#### API 任务 - 任务协作流程（8 个）

**T-420: 实现 POST /api/tasks/{id}/assign**
- 依赖：[T-401]
- 验收标准：分配任务给人或 Agent

**T-421: 实现 POST /api/tasks/{id}/claim**
- 依赖：[T-401]
- 验收标准：认领任务

**T-422: 实现 POST /api/tasks/{id}/start**
- 依赖：[T-401]
- 验收标准：设置 in_progress 状态

**T-423: 实现 POST /api/tasks/{id}/complete**
- 依赖：[T-401]
- 验收标准：设置 completed 状态

**T-424: 实现 POST /api/tasks/{id}/approve**
- 依赖：[T-401]
- 验收标准：审核通过，设置 approved 状态

**T-425: 实现 POST /api/tasks/{id}/reject**
- 依赖：[T-401]
- 验收标准：审核拒绝，设置 rejected 状态

**T-426: 实现 POST /api/tasks/{id}/comment**
- 路由：`backend/routers/task_comments.py`（新建）
- 依赖：[T-402, T-412]
- 验收标准：添加评论

**T-427: 实现 GET /api/tasks/{id}/comments**
- 依赖：[T-402, T-412]
- 验收标准：返回评论列表

#### API 任务 - 看板视图（4 个）

**T-430: 实现 GET /api/projects/{id}/kanban**
- 依赖：[T-401, T-212]
- 验收标准：返回看板数据

**T-431: 实现 POST /api/tasks/{id}/move**
- 依赖：[T-401]
- 验收标准：移动任务，更新 position

**T-432: 实现 GET /api/projects/{id}/tasks/by-status**
- 依赖：[T-401, T-212]
- 验收标准：按状态分组

**T-433: 实现 GET /api/projects/{id}/tasks/timeline**
- 依赖：[T-401, T-212]
- 验收标准：返回时间线视图

#### 子任务（2 个）

**T-440: 实现 POST /api/tasks/{id}/subtasks**
- 依赖：[T-401]
- 验收标准：创建子任务

**T-441: 实现 GET /api/tasks/{id}/subtasks**
- 依赖：[T-401]
- 验收标准：返回子任务列表

### 二、前端任务（5 个）

**T-450: 实现 /projects/:id/kanban 看板页**
- 页面：`frontend/src/views/tasks/KanbanView.vue`
- 组件：`frontend/src/components/kanban/KanbanBoard.vue`
- 组件：`frontend/src/components/kanban/KanbanColumn.vue`
- 组件：`frontend/src/components/kanban/TaskCard.vue`
- 依赖：[T-430, T-431, T-432]
- 验收标准：看板拖拽正常

**T-451: 实现 /projects/:id/tasks 任务列表页**
- 页面：`frontend/src/views/tasks/TaskListView.vue`
- 依赖：[T-411, T-412]
- 验收标准：列表展示正常

**T-452: 实现 /projects/:id/timeline 时间线页**
- 页面：`frontend/src/views/tasks/TimelineView.vue`
- 依赖：[T-433]
- 验收标准：时间线展示正常

**T-453: 实现 /tasks/:id 任务详情抽屉**
- 组件：`frontend/src/components/tasks/TaskDetailDrawer.vue`
- 依赖：[T-412, T-420 到 T-427]
- 验收标准：支持评论和状态操作

**T-454: 实现 /tasks/due-soon 即将到期页**
- 页面：`frontend/src/views/tasks/DueSoonView.vue`
- 依赖：[T-411]
- 验收标准：显示即将到期任务

### 三、测试任务（6 个）

**T-460: 任务模块测试**
- 依赖：[T-410 到 T-417]
- 验收标准：覆盖率 > 80%

**T-461: 任务协作流程测试**
- 依赖：[T-420 到 T-427]
- 验收标准：状态机正确

**T-462: 看板视图测试**
- 依赖：[T-430 到 T-433]
- 验收标准：视图正确

**T-463: 前端看板页测试**
- 依赖：[T-450]
- 验收标准：Vitest 测试通过

**T-464: 前端任务详情测试**
- 依赖：[T-453]
- 验收标准：Vitest 测试通过

**T-465: E2E 看板测试**
- 文件：`frontend/e2e/kanban.spec.ts`
- 依赖：[T-450, T-453]
- 验收标准：Playwright 测试通过

---

## Phase 5: 执行引擎集成

### 一、后端任务（12 个）

#### 数据库任务（2 个）

**T-501: 创建 executions 表**
- 文件：`backend/models/execution.py`
- 迁移：`backend/alembic/versions/xxx_create_executions.py`
- 依赖：[]
- 验收标准：表创建成功

**T-502: 创建 task_chains 表**
- 文件：`backend/models/task_chain.py`
- 迁移：`backend/alembic/versions/xxx_create_task_chains.py`
- 依赖：[]
- 验收标准：表创建成功

#### API 任务 - 执行触发（5 个）

**T-510: 实现 POST /api/tasks/{id}/execute**
- 路由：`backend/routers/executions.py`（新建）
- 依赖：[T-401, T-501]
- 验收标准：触发任务执行

**T-511: 实现 GET /api/executions/{id}**
- 依赖：[T-501]
- 验收标准：返回执行详情

**T-512: 实现 GET /api/tasks/{id}/executions**
- 依赖：[T-501]
- 验收标准：返回执行历史

**T-513: 实现 POST /api/executions/{id}/cancel**
- 依赖：[T-501]
- 验收标准：取消执行

**T-514: 实现 GET /api/executions/active**
- 依赖：[T-501]
- 验收标准：返回活跃执行

#### API 任务 - 任务链（3 个）

**T-520: 实现 POST /api/task-chains**
- 路由：`backend/routers/task_chains.py`（新建）
- 依赖：[T-502]
- 验收标准：创建任务链

**T-521: 实现 GET /api/task-chains/{id}**
- 依赖：[T-502]
- 验收标准：返回任务链详情

**T-522: 实现 POST /api/task-chains/{id}/execute**
- 依赖：[T-502, T-510]
- 验收标准：执行任务链

#### WebSocket 任务（4 个）

**T-530: 实现 WS /ws/executions/{execution_id}**
- 路由：`backend/routers/executions.py`
- 依赖：[T-510]
- 验收标准：推送执行状态

**T-531: 实现 WS /ws/tasks/{task_id}**
- 路由：`backend/routers/tasks.py`
- 依赖：[T-401]
- 验收标准：推送任务状态

**T-532: 实现 WS /ws/agents/{agent_id}**
- 路由：`backend/routers/agents.py`
- 依赖：[T-230, T-231]
- 验收标准：推送 Agent 状态

**T-533: 实现 GET /api/executions/{id}/logs**
- 依赖：[T-501]
- 验收标准：返回执行日志

### 二、前端任务（3 个）

**T-540: 实现 /executions 执行记录页**
- 页面：`frontend/src/views/executions/ExecutionListView.vue`
- 依赖：[T-511, T-512, T-514]
- 验收标准：显示执行列表

**T-541: 实现 /executions/:id 执行详情页**
- 页面：`frontend/src/views/executions/ExecutionDetailView.vue`
- 组件：`frontend/src/components/executions/ExecutionLogViewer.vue`
- 依赖：[T-511, T-530, T-533]
- 验收标准：显示执行详情和日志

**T-542: 实现 /task-chains 任务链管理页**
- 页面：`frontend/src/views/task-chains/TaskChainView.vue`
- 依赖：[T-520, T-521, T-522]
- 验收标准：显示和管理任务链

### 三、测试任务（4 个）

**T-550: 执行模块测试**
- 依赖：[T-510 到 T-514]
- 验收标准：覆盖率 > 80%

**T-551: 任务链测试**
- 依赖：[T-520 到 T-522]
- 验收标准：覆盖率 > 80%

**T-552: WebSocket 测试**
- 依赖：[T-530 到 T-532]
- 验收标准：连接正常

**T-553: 前端执行页测试**
- 依赖：[T-540, T-541]
- 验收标准：Vitest 测试通过

---

## Phase 6-7 里程碑（概要）

### Phase 6: Activity Feed

**里程碑：**
- M-601: 活动流 API 完成
- M-602: 通知中心页面完成
- M-603: WebSocket 推送完成

**关键技术任务：**
- T-601: 设计活动类型枚举
- T-602: 实现活动记录写入
- T-603: 实现已读/未读状态

### Phase 7: Dashboard

**里程碑：**
- M-701: 概览页面完成
- M-702: Agent 状态仪表板完成
- M-703: 图表集成完成

**关键技术任务：**
- T-701: 集成图表库（ECharts）
- T-702: 实现数据聚合 API
- T-703: 实现实时数据推送

---

## Phase 8-9 概要

### Phase 8: 测试 + 修复
- 单元测试覆盖率 > 80%
- 集成测试完整
- E2E 测试覆盖关键路径
- Bug 修复

### Phase 9: 部署上线
- Docker Compose 生产配置
- CI/CD 流水线
- SSL + 域名配置

---

## 执行顺序建议

```
Phase 2 (最优先):
  1. 数据库任务 (T-201 到 T-204)
  2. 项目管理 API (T-210 到 T-217)
  3. Agent 基础 API (T-220 到 T-229)
  4. 运行时管理 API (T-230 到 T-235)
  5. 前端页面 (T-250 到 T-265)
  6. 测试 (T-270 到 T-277)

Phase 3:
  7. 配置预设 + 上下文 + 指标

Phase 4:
  8. 任务看板（核心协作）

Phase 5:
  9. 执行引擎 + WebSocket

Phase 6-7:
  10. Activity Feed + Dashboard
```

---

**文档状态：** 初稿，待项目经理审批
**制定时间：** 2026-04-21 19:10
**制定角色：** 架构师
