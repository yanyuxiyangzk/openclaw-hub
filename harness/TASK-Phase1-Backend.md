# OpenClawHub Phase 1 后端任务

**项目路径:** D:\project\aicoding\OpenClawHub
**任务类型:** backend-dev
**并行任务:** frontend-dev（同时进行）
**时间:** 2026-04-18

---

## 目标

使用 FastAPI + SQLAlchemy 2.0 实现 OpenClawHub Phase 1 认证模块，涵盖 23 个 API。

---

## 技术栈

- Python 3.12 + FastAPI + SQLAlchemy 2.0
- PostgreSQL（生产）/ SQLite（开发，本地开发用 SQLite）
- Alembic 数据库迁移
- bcrypt (passlib) 密码加密
- python-jose (HS256) JWT
- 开发模式: autodev（参考 OpenClawHarness 的 auto-dev 模式，边开发边写 CURD 测试）

---

## 数据库模型

### users 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, auto | 用户ID |
| email | VARCHAR(64) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt加密 |
| name | VARCHAR(64) | NOT NULL | 显示名 |
| avatar | VARCHAR(255) | NULL | 头像URL |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| is_superuser | BOOLEAN | DEFAULT FALSE | 超级管理员 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### organizations 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, auto | 组织ID |
| name | VARCHAR(64) | NOT NULL | 组织名 |
| owner_id | UUID | FK -> users.id | 所有者 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### organization_members 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, auto | ID |
| org_id | UUID | FK -> organizations.id | 组织ID |
| user_id | UUID | FK -> users.id | 用户ID |
| role | VARCHAR(32) | NOT NULL | owner/admin/member |
| joined_at | DATETIME | NOT NULL | 加入时间 |

### invitations 表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | UUID | PK, auto | ID |
| org_id | UUID | FK -> organizations.id | 组织ID |
| email | VARCHAR(64) | NOT NULL | 邀请邮箱 |
| role | VARCHAR(32) | NOT NULL | 邀请角色 |
| token | VARCHAR(128) | UNIQUE, NOT NULL | 邀请令牌 |
| expires_at | DATETIME | NOT NULL | 过期时间 |
| status | VARCHAR(16) | DEFAULT pending | pending/accepted/expired |
| created_at | DATETIME | NOT NULL | 创建时间 |

---

## API 清单（23个）

### 认证模块（6个）

1. `POST /api/auth/register` - 用户注册
2. `POST /api/auth/login` - 用户登录（返回 access_token + refresh_token）
3. `POST /api/auth/refresh` - 刷新令牌
4. `GET /api/auth/me` - 获取当前用户
5. `PUT /api/auth/me` - 更新当前用户信息
6. `POST /api/auth/logout` - 登出

### 用户管理（6个，超级管理员）

7. `GET /api/users` - 用户列表（分页）
8. `GET /api/users/{id}` - 获取用户详情
9. `PUT /api/users/{id}` - 更新用户
10. `DELETE /api/users/{id}` - 删除用户
11. `PUT /api/users/{id}/password` - 修改密码（管理员）
12. `PUT /api/users/{id}/toggle-active` - 启用/禁用用户

### 组织管理（7个）

13. `POST /api/orgs` - 创建组织
14. `GET /api/orgs` - 我的组织列表
15. `GET /api/orgs/{id}` - 组织详情
16. `PUT /api/orgs/{id}` - 更新组织
17. `DELETE /api/orgs/{id}` - 删除组织（仅所有者）
18. `GET /api/orgs/{id}/members` - 成员列表
19. `DELETE /api/orgs/{id}/members/{user_id}` - 移除成员

### 邀请管理（4个）

20. `POST /api/orgs/{id}/invitations` - 发送邀请
21. `GET /api/invitations/{token}` - 验证邀请（通过链接）
22. `POST /api/invitations/{token}/accept` - 接受邀请
23. `DELETE /api/invitations/{id}` - 撤销邀请

---

## 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

错误码：
- 40101: 未授权
- 40301: 禁止访问
- 40401: 资源不存在
- 40901: 资源冲突（邮箱已注册）
- 42201: 参数校验失败

---

## JWT 认证

- Access Token: 7天有效期，HS256
- Refresh Token: 30天有效期
- Cookie 方式存储（httponly; secure; samesite=lax）
- 同时支持 Header `Authorization: Bearer <token>`

---

## 开发规则（autodev）

**重要：边开发边写测试！**

1. 每个 API 模块写四件套：CURD 测试（Create/Read/Update/Delete）
2. 代码和测试必须同时 commit
3. 使用 pytest + pytest-asyncio
4. 测试文件放在 backend/tests/ 目录
5. 测试覆盖率目标: 70%+
6. 每完成一个 API 模块立即写测试并运行验证

---

## 目录结构要求

```
backend/
├── alembic/              # 数据库迁移
├── models/               # SQLAlchemy 模型
│   ├── __init__.py
│   ├── user.py
│   ├── organization.py
│   └── invitation.py
├── routers/              # API 路由（重点！！当前为空）
│   ├── __init__.py
│   ├── auth.py           # 认证 6个
│   ├── users.py         # 用户管理 6个
│   ├── orgs.py          # 组织管理 7个
│   └── invitations.py   # 邀请管理 4个
├── schemas/              # Pydantic schemas
│   ├── __init__.py
│   ├── auth.py
│   ├── user.py
│   ├── organization.py
│   └── invitation.py
├── services/             # 业务逻辑
│   ├── __init__.py
│   ├── auth_service.py
│   └── org_service.py
├── core/                 # 核心配置
│   ├── __init__.py
│   ├── config.py         # 从 config.py 迁移
│   ├── security.py       # JWT + bcrypt
│   └── database.py       # 数据库连接
├── tests/                # 测试（每个模块写四件套）
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_orgs.py
│   └── test_invitations.py
├── alembic.ini
├── requirements.txt      # 补充依赖
└── main.py               # 更新注册路由
```

---

## 执行步骤

1. 先创建数据库模型（models/）
2. 创建 Pydantic schemas
3. 创建核心配置（core/config.py, core/security.py, core/database.py）
4. 创建服务层（services/）
5. 创建 API 路由（routers/）- **每个路由文件都要写**
6. 更新 main.py 注册所有路由
7. 配置 Alembic 迁移
8. 运行 alembic upgrade head 初始化数据库
9. 为每个模块写 CURD 测试
10. pytest 运行测试，确保全部通过
11. git commit

---

## CURD 测试要求

每个 API 都要有：

```python
# 示例：auth.py 的 CURD 测试
def test_register_success():
    """注册成功"""

def test_register_duplicate_email():
    """注册失败-邮箱已存在"""

def test_login_success():
    """登录成功"""

def test_login_wrong_password():
    """登录失败-密码错误"""

def test_get_me_authenticated():
    """获取当前用户-已认证"""

def test_get_me_unauthenticated():
    """获取当前用户-未认证-返回401"""
```

---

## 验收标准

- [ ] 23 个 API 全部实现
- [ ] pytest 全部通过
- [ ] alembic 迁移脚本可用
- [ ] API 响应格式统一
- [ ] JWT 认证正常工作
- [ ] 代码和测试同时 commit
