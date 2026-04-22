# OpenClawHub API 文档

> 版本: 1.0.0
> 更新: 2026-04-21

---

## 概述

OpenClawHub 是一个数字员工 SaaS 平台 API，提供多租户管理、Agent 运行时（Hermes）和工作流协作功能。

**基础 URL:**
```
http://localhost:8000
```

**Swagger UI:**
```
http://localhost:8000/docs
```

**认证方式:**
所有 API（除 `/api/auth/*` 外）都需要 JWT Bearer Token 认证。

```
Authorization: Bearer <your_token>
```

---

## 认证 (Authentication)

### 注册用户
```
POST /api/auth/register
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "张三"
}
```

**响应:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "张三"
  }
}
```

---

### 登录
```
POST /api/auth/login
```

**请求体:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**响应:**
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer"
  }
}
```

---

### 刷新 Token
```
POST /api/auth/refresh
```

**请求体:**
```json
{
  "refresh_token": "eyJ..."
}
```

---

## 组织 (Organizations)

### 创建组织
```
POST /api/orgs
```

**请求体:**
```json
{
  "name": "我的公司"
}
```

---

### 获取组织列表
```
GET /api/orgs
```

---

### 获取组织详情
```
GET /api/orgs/{id}
```

---

### 更新组织
```
PUT /api/orgs/{id}
```

---

### 删除组织
```
DELETE /api/orgs/{id}
```

---

## 项目 (Projects)

### 创建项目
```
POST /api/projects
```

**请求体:**
```json
{
  "name": "项目名称",
  "description": "项目描述",
  "org_id": "uuid"
}
```

---

### 获取项目列表
```
GET /api/projects
```

**查询参数:**
- `status`: active | archived | deleted

---

### 获取项目详情
```
GET /api/projects/{id}
```

---

### 更新项目
```
PUT /api/projects/{id}
```

---

### 删除项目
```
DELETE /api/projects/{id}
```

---

### 获取项目成员
```
GET /api/projects/{id}/members
```

---

### 添加项目成员
```
POST /api/projects/{id}/members
```

**请求体:**
```json
{
  "user_id": "uuid",
  "role": "member"
}
```

---

### 移除项目成员
```
DELETE /api/projects/{id}/members/{user_id}
```

---

## Agent

### 创建 Agent
```
POST /api/agents
```

**请求体:**
```json
{
  "name": "助手Agent",
  "description": "负责协助处理日常任务",
  "agent_type": "hermes",
  "config": {}
}
```

---

### 获取 Agent 列表
```
GET /api/agents
```

---

### 获取 Agent 详情
```
GET /api/agents/{id}
```

---

### 更新 Agent
```
PUT /api/agents/{id}
```

---

### 删除 Agent
```
DELETE /api/agents/{id}
```

---

### 启动 Agent
```
POST /api/agents/{id}/start
```

---

### 停止 Agent
```
POST /api/agents/{id}/stop
```

---

### 获取 Agent 日志
```
GET /api/agents/{id}/logs
```

---

### 获取 Agent 健康状态
```
GET /api/agents/{id}/health
```

---

### 获取 Agent 状态
```
GET /api/agents/{id}/status
```

---

## 任务 (Tasks)

### 创建任务
```
POST /api/tasks
```

**请求体:**
```json
{
  "title": "任务标题",
  "description": "任务描述",
  "project_id": "uuid",
  "priority": "medium"
}
```

---

### 获取任务列表
```
GET /api/tasks
```

**查询参数:**
- `project_id`: 项目ID
- `status`: pending | in_progress | completed
- `assignee_id`: 负责人ID

---

### 获取任务详情
```
GET /api/tasks/{id}
```

---

### 更新任务
```
PUT /api/tasks/{id}
```

---

### 删除任务
```
DELETE /api/tasks/{id}
```

---

### 分配任务
```
POST /api/tasks/{id}/assign
```

**请求体:**
```json
{
  "assignee_id": "uuid",
  "assignee_type": "user" | "agent"
}
```

---

### 完成任务
```
POST /api/tasks/{id}/complete
```

---

### 添加评论
```
POST /api/tasks/{id}/comments
```

**请求体:**
```json
{
  "content": "这是评论内容"
}
```

---

### 获取评论列表
```
GET /api/tasks/{id}/comments
```

---

## WebSocket

### Agent 状态实时推送
```
WS /ws/agents/{id}/status
```

连接后会自动接收 Agent 状态变更推送。

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 冲突（如邮箱已注册）|
| 500 | 服务器内部错误 |

---

## 响应格式

所有 API 统一响应格式：

**成功:**
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

**失败:**
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": {}
}
```

---

_Last updated: 2026-04-21_
