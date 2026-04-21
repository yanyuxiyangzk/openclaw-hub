# OpenClawHub Phase 1 后端开发任务

## 项目路径
D:\project\aicoding\OpenClawHub

## 任务概述
使用 FastAPI + SQLAlchemy 2.0 实现 OpenClawHub Phase 1 认证模块，涵盖 23 个 API。

## 技术栈
- Python 3.12 + FastAPI + SQLAlchemy 2.0
- SQLite 开发数据库
- bcrypt (passlib) 密码加密
- python-jose (HS256) JWT
- pytest + pytest-asyncio 测试

## 数据库模型

### users 表
- id (UUID, PK), email (VARCHAR 64, UNIQUE), password_hash (VARCHAR 255)
- name (VARCHAR 64), avatar (VARCHAR 255, NULL)
- is_active (BOOLEAN, DEFAULT TRUE), is_superuser (BOOLEAN, DEFAULT FALSE)
- created_at, updated_at

### organizations 表
- id (UUID, PK), name (VARCHAR 64), owner_id (FK -> users.id)
- created_at, updated_at

### organization_members 表
- id (UUID, PK), org_id (FK), user_id (FK), role (owner/admin/member), joined_at

### invitations 表
- id (UUID, PK), org_id (FK), email, role, token (UNIQUE)
- expires_at, status (pending/accepted/expired), created_at

## API 清单（23个）

### 认证（6个）
1. POST /api/auth/register - 用户注册
2. POST /api/auth/login - 登录（返回 access_token + refresh_token）
3. POST /api/auth/refresh - 刷新令牌
4. GET /api/auth/me - 当前用户
5. PUT /api/auth/me - 更新用户
6. POST /api/auth/logout - 登出

### 用户管理（6个，需超级管理员权限）
7. GET /api/users - 用户列表（分页）
8. GET /api/users/{id} - 用户详情
9. PUT /api/users/{id} - 更新用户
10. DELETE /api/users/{id} - 删除用户
11. PUT /api/users/{id}/password - 修改密码
12. PUT /api/users/{id}/toggle-active - 启用/禁用

### 组织管理（7个）
13. POST /api/orgs - 创建组织
14. GET /api/orgs - 我的组织列表
15. GET /api/orgs/{id} - 组织详情
16. PUT /api/orgs/{id} - 更新组织
17. DELETE /api/orgs/{id} - 删除组织（仅所有者）
18. GET /api/orgs/{id}/members - 成员列表
19. DELETE /api/orgs/{id}/members/{user_id} - 移除成员

### 邀请管理（4个）
20. POST /api/orgs/{id}/invitations - 发送邀请
21. GET /api/invitations/{token} - 验证邀请
22. POST /api/invitations/{token}/accept - 接受邀请
23. DELETE /api/invitations/{id} - 撤销邀请

## 统一响应格式
{ "code": 0, "message": "success", "data": {} }

错误码：40101未授权, 40301禁止访问, 40401不存在, 40901冲突, 42201校验失败

## JWT 配置
- Access Token: 7天, HS256
- Refresh Token: 30天
- Cookie 存储（httponly）+ Header Authorization Bearer

## 开发规则（autodev）
1. **每个 API 模块写四件套 CURD 测试**，代码和测试必须同时 commit
2. 先做 auth 模块（建立信心），再做 users → orgs → invitations
3. 测试覆盖率目标 70%+

## 当前项目状态
backend/ 目录已存在，routers/ 为空（Phase 0 骨架已搭好）
backend/main.py 已存在
backend/requirements.txt 已存在

## 执行步骤
1. 安装依赖：pip install fastapi sqlalchemy pydantic bcrypt python-jose uvicorn pytest pytest-asyncio httpx alembic
2. 创建 backend/core/ 目录（config.py, security.py, database.py）
3. 创建 backend/models/ 目录（user.py, organization.py, invitation.py）
4. 创建 backend/schemas/ 目录（auth.py, user.py, organization.py, invitation.py）
5. 创建 backend/services/ 目录（auth_service.py, org_service.py）
6. 创建 backend/routers/ 目录（auth.py, users.py, orgs.py, invitations.py）— 23个API全部实现
7. 更新 backend/main.py 注册路由
8. 配置 alembic（alembic.ini + env.py + versions/）
9. alembic upgrade head 初始化数据库
10. 创建 CURD 测试（backend/tests/）
11. pytest 运行测试
12. git add + git commit
13. git push

完成后汇报：实现了哪些API、测试数量/通过率、commit hash。