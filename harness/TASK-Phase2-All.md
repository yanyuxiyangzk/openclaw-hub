# Phase 2 批量任务

## 任务概述

一次性执行 Phase 2 全部开发任务，减少人工干预。

**执行模式:**
- 顺序执行
- 遇到错误: 继续下一个批次
- 完成后: 输出执行摘要

---

## 批次 1: 数据库任务 (已合并到 Phase2-5)

**说明**: 数据库任务（T-201~T-204）已包含在 Phase2-5 开发计划中，由 Claude Code 自动完成。

### 执行内容
- 创建 projects 表
- 创建 agents 表
- 创建 project_agents 表
- 创建 project_members 表
- 执行数据库迁移

---

## 批次 2: 项目管理 API

**TASK 文件**: TASK-Phase2-项目管理API.md

### 执行内容
- POST /api/projects - 创建项目
- GET /api/projects - 项目列表
- GET /api/projects/{id} - 项目详情
- PUT /api/projects/{id} - 更新项目
- DELETE /api/projects/{id} - 删除项目
- GET /api/projects/{id}/members - 成员列表
- POST /api/projects/{id}/members - 添加成员
- DELETE /api/projects/{id}/members/{user_id} - 移除成员

---

## 批次 3: Agent 基础 API

**TASK 文件**: TASK-Phase2-Agent基础API.md

### 执行内容
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

---

## 批次 4: 运行时管理 API

**TASK 文件**: TASK-Phase2-RuntimeAPI.md

### 执行内容
- POST /api/agents/{id}/start - 启动 Agent
- POST /api/agents/{id}/stop - 停止 Agent
- GET /api/agents/{id}/logs - Agent 运行日志
- GET /api/agents/{id}/health - Agent 健康检查
- GET /api/agents/active - 活跃 Agent 列表
- WS /ws/agents/{id}/status - Agent 状态 WebSocket

---

## 批次 5: 前端页面开发

**TASK 文件**: TASK-Phase2-Frontend.md

### 执行内容
#### Pages
- /projects - ProjectListView
- /projects/new - CreateProjectView
- /projects/:id - ProjectDetailView
- /projects/:id/settings - ProjectSettingsView
- /agents - AgentListView
- /agents/:id - AgentDetailView

#### Components
- ProjectCard
- ProjectMembers
- ProjectAgents
- AgentCard
- AgentStatus
- AgentActions

---

## 批次 6: 测试任务

**TASK 文件**: TASK-Phase2-Tests.md

### 执行内容
- test_projects.py - Project 模块测试
- test_agents.py - Agent 模块测试
- test_agent_runtime.py - 运行时集成测试
- test_project_agents.py - 项目-Agent 关联测试
- 前端 Vitest 测试

---

## 执行要求

1. **顺序执行**: 按批次顺序执行，不要跳跃
2. **自动化测试**: 每批次执行完后自动运行测试
3. **遇到错误**:
   - 记录错误到 corrections/
   - 继续执行下一个批次
   - 最后汇总错误报告
4. **完成后**: 输出执行摘要

## 输出文件

- `D:\project\aicoding\OpenClawHub\harness\TASK-Phase2-All.md`

## 执行命令

```bash
# 使用 batch_runner.py 执行
python "D:\project\aicoding\OpenClawHarness\scripts\batch_runner.py" \
  --project "D:\project\aicoding\OpenClawHub" \
  --taskfile "D:\project\aicoding\OpenClawHub\harness\TASK-Phase2-All.md"
```

---

_Last updated: 2026-04-21_
