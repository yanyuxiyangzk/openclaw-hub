# Phase 2 任务：运行时管理 API 开发

## 任务概述

根据 `TASK-Phase2-5_开发计划.md` 执行运行时管理 API 开发任务。

**任务范围：** T-230 到 T-235（6 个 API）

---

## 项目信息

**项目路径：** `D:\project\aicoding\OpenClawHub`

**运行时管理器：** `D:\project\aicoding\OpenClawHub\hermes-runtime\services\hermes_instance_manager.py`

**Phase 2 数据库模型：**
- `backend/models/agent.py` - Agent 模型（已创建）

**Phase 2 已完成：**
- 数据库任务（T-201~T-204）
- 项目管理 API（T-210~T-217）
- Agent 基础 API（T-220~T-229）

---

## API 任务清单

### T-230: 实现 POST /api/agents/{id}/start

启动 Agent

- 路由：`backend/routers/agents.py`
- 依赖：T-202, T-222
- 验收标准：调用 HermesInstanceManager 启动 Agent

### T-231: 实现 POST /api/agents/{id}/stop

停止 Agent

- 路由：`backend/routers/agents.py`
- 依赖：T-202, T-222
- 验收标准：调用 HermesInstanceManager 停止 Agent

### T-232: 实现 GET /api/agents/{id}/logs

Agent 运行日志

- 路由：`backend/routers/agents.py`
- 依赖：T-202, T-222
- 验收标准：从文件系统读取并返回 Agent 日志

### T-233: 实现 GET /api/agents/{id}/health

Agent 健康检查

- 路由：`backend/routers/agents.py`
- 依赖：T-202, T-222
- 验收标准：返回 Agent 健康检查结果

### T-234: 实现 GET /api/agents/active

活跃 Agent 列表

- 路由：`backend/routers/agents.py`
- 依赖：T-202
- 验收标准：返回当前活跃的 Agent 列表

### T-235: 实现 WS /ws/agents/{id}/status

Agent 状态 WebSocket

- 路由：`backend/routers/agents.py`
- 依赖：T-230, T-231
- 验收标准：WebSocket 推送 Agent 状态变更

---

## HermesInstanceManager 参考

```python
# 启动 Agent
HermesInstanceManager.start_instance(tenant_id, agent_id, mode="subprocess")

# 停止 Agent
HermesInstanceManager.stop_instance(instance_id)

# 获取状态
HermesInstanceManager.get_instance(instance_id).status

# 获取日志（从文件系统）
hermes-runtime/tenants/{tenant_id}/agents/{agent_id}/logs/*.log
```

---

## 开发规范

1. **调用 HermesInstanceManager** - 使用 subprocess 模式启动/停止
2. **WebSocket 使用 FastAPI WebSocket** - 参考 FastAPI 文档
3. **JWT 认证** - 所有 API 需要认证
4. **边开发边写测试** - 每个 API 完成后写测试

---

## 输出文件

- 路由：`backend/routers/agents.py`（扩展现有）
- 测试：`backend/tests/test_agent_runtime.py`

---

## 验收标准

- [ ] 6 个 API 全部实现
- [ ] Agent 启动/停止功能正常
- [ ] WebSocket 连接正常
- [ ] 之前所有测试不受影响

---

**开始执行！**
