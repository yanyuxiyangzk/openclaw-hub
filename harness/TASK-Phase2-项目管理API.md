# Phase 2 任务：项目管理 API 开发

## 任务概述

根据 `TASK-Phase2-5_开发计划.md` 执行项目管理 API 开发任务。

**任务范围：** T-210 到 T-217（8 个 API）

---

## 项目信息

**项目路径：** `D:\project\aicoding\OpenClawHub`

**参考 Phase 1 实现：**
- `backend/routers/orgs.py` - 组织管理 API
- `backend/routers/users.py` - 用户管理 API
- `backend/schemas/organization.py` - 组织 Schema
- `backend/services/organization_service.py` - 组织服务

**Phase 2 数据库模型：**
- `backend/models/project.py` - Project 模型（已创建）
- `backend/models/project_member.py` - ProjectMember 模型（已创建）

---

## API 任务清单

### T-210: 实现 POST /api/projects

创建项目

- 路由：`backend/routers/projects.py`
- Schema：`backend/schemas/project.py`
- 测试：`backend/tests/test_projects.py::test_create_project`
- 依赖：T-201
- 验收标准：能创建项目，返回项目详情

### T-211: 实现 GET /api/projects

项目列表

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_list_projects`
- 依赖：T-201
- 验收标准：返回当前用户的项目列表

### T-212: 实现 GET /api/projects/{id}

项目详情

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_get_project`
- 依赖：T-201, T-210
- 验收标准：返回项目详情，包含成员和 Agent

### T-213: 实现 PUT /api/projects/{id}

更新项目

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_update_project`
- 依赖：T-201, T-212
- 验收标准：能更新项目名称/描述/状态

### T-214: 实现 DELETE /api/projects/{id}

删除项目

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_delete_project`
- 依赖：T-201, T-212
- 验收标准：软删除（status='deleted'）

### T-215: 实现 GET /api/projects/{id}/members

项目成员列表

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_list_project_members`
- 依赖：T-204, T-212
- 验收标准：返回项目成员列表

### T-216: 实现 POST /api/projects/{id}/members

添加项目成员

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_add_project_member`
- 依赖：T-204, T-212
- 验收标准：能添加项目成员

### T-217: 实现 DELETE /api/projects/{id}/members/{user_id}

移除项目成员

- 路由：`backend/routers/projects.py`
- 测试：`backend/tests/test_projects.py::test_remove_project_member`
- 依赖：T-204, T-212
- 验收标准：能移除项目成员

---

## 开发规范

1. **复制 Phase 1 模式** - 参考 `routers/orgs.py` 的结构
2. **使用相同的响应格式** - `{ code: 0, message: "success", data: {...} }`
3. **JWT 认证** - 使用 Phase 1 的认证中间件
4. **权限检查** - 项目成员才能访问项目资源
5. **边开发边写测试** - 每个 API 完成后写测试

---

## 输出文件

- 路由：`backend/routers/projects.py`
- Schema：`backend/schemas/project.py`
- 服务：`backend/services/project_service.py`
- 测试：`backend/tests/test_projects.py`

---

## 验收标准

- [ ] 8 个 API 全部实现
- [ ] 测试覆盖率 > 80%
- [ ] Phase 1 测试不受影响

---

**开始执行！**
