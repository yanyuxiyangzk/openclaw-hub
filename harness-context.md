# OpenClawHub - Harness Context

> 项目类型: 数字员工 SaaS 平台（多租户）
> 技术栈: FastAPI + Vue3 + PostgreSQL + Hermes Agent
> 版本: v0.1 MVP | Phase: Phase 9 部署上线 ✅ 完成
> 更新: 2026-04-26

---

## 项目概述

OpenClawHub 是一个数字员工 SaaS 平台，目标是打造一人公司的数字员工团队。
平台提供：多租户管理 + Agent 运行时（Hermes）+ 工作流协作。

**核心技术选型：**
- 后端: Python FastAPI + SQLAlchemy 2.0 + Alembic + SQLite(开发) / PostgreSQL(生产)
- 前端: Vue3 + Vite + TypeScript + TailwindCSS + Pinia
- Agent 引擎: Hermes Agent（NousResearch，MIT License）
- 认证: JWT (HS256) + bcrypt
- 部署: Docker Compose

---

## Phase 完成状态

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 0 | 项目初始化 | ✅ |
| Phase 1 | 认证模块（23 API + 7 前端页面 + 58 测试） | ✅ |
| Phase 2 | 项目管理模块（T-201~T-243） | ✅ |
| Phase 3 | Agent 管理模块（T-301~T-334） | ✅ |
| Phase 4 | 任务看板模块（T-401~T-445） | ✅ |
| Phase 5 | 执行引擎集成（T-501~T-533） | ✅ |
| Phase 6 | Activity Feed | ✅ |
| Phase 7 | Dashboard | ✅ |
| Phase 8 | 测试 + 修复 | ✅ |
| Phase 9 | 部署上线 | ✅ |

---

## 技术架构

### 后端路由
```
backend/routers/
├── auth.py         # 认证（Phase 1）
├── users.py        # 用户管理（Phase 1）
├── orgs.py         # 组织管理（Phase 1）
├── invitations.py  # 邀请（Phase 1）
├── projects.py     # 项目管理（Phase 2）
├── agents.py       # Agent 管理（Phase 2-3）
├── agent_roles.py  # Agent 角色（Phase 3）
├── tasks.py        # 任务管理（Phase 4）
├── executions.py   # 执行记录（Phase 5）
├── scheduler.py    # 定时任务（Phase 5）
├── workflows.py    # 工作流（Phase 5）
├── activities.py   # Activity Feed（Phase 6）
├── dashboard.py    # Dashboard（Phase 7）
├── phase3.py       # Agent 高级功能
└── ws.py          # WebSocket
```

### 前端页面
```
frontend/src/views/
├── LoginView.vue          # 登录
├── RegisterView.vue        # 注册
├── OrgListView.vue        # 组织列表
├── OrgDetailView.vue      # 组织详情
├── InvitationView.vue     # 邀请管理
├── MemberManageView.vue   # 成员管理
├── SettingsView.vue       # 设置
├── DashboardView.vue      # 仪表盘（Phase 7）
├── agents/               # Agent 相关页面（Phase 3）
├── tasks/                # 任务相关页面（Phase 4）
├── executions/           # 执行记录页面（Phase 5）
├── scheduler/            # 定时任务页面（Phase 5）
└── workflows/           # 工作流编辑器（Phase 5）
```

---

## 开发规则

1. **响应格式统一：** `{ code: 0, message: "success", data: {...} }`
2. **JWT 认证：** 所有 API 需要认证
3. **权限检查：** 项目成员才能访问项目资源
4. **软删除：** DELETE 操作设置 status='deleted'
5. **测试要求：** 每个 API 需要写测试

---

## corrections 历史

- **失败记录：** 79 个（主要是 Phase 3/4/5 自主测试阶段的历史记录）
- **最新失败：** LoginView.spec.ts 文本不匹配 → ✅ 已修复（2026-04-26）

---

## 部署信息

- **健康检查：** `http://localhost:8080/health`
- **API：** `http://localhost:8080/api/health`
- **部署文档：** `DEPLOY.md`
- **Docker Compose：** `docker/docker-compose.prod.yml`

---

_Last updated: 2026-04-26_
