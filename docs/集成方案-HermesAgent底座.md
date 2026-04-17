# OpenClawHub × Hermes Agent 集成方案

> 版本：v1.1 | 日期：2026-04-17 | 状态：✅ 已批准并执行 Phase 0
> 角色：妙妙（Architect + PM）
> 目标：以 Hermes Agent 为底座，重构 OpenClawHub 技术架构

---

## 一、背景与目标

### 1.1 为什么选 Hermes Agent

| 选型因素 | 说明 |
|---------|------|
| **MIT License** | 可自由商用、闭源、二开 |
| **成熟的 Agent 执行引擎** | AIAgent ~10,700行，经过 3,000+ 测试 |
| **内置进化学习循环** | Skills 自优化、记忆管理、Cron 调度 |
| **多平台消息网关** | 支持 18 个平台（钉钉/飞书/企微/微信等） |
| **Skills 系统** | 渐进式加载(token 高效)，兼容 agentskills.io 标准 |
| **多 Agent 协作** | delegate_tool、spawn 隔离子 agent |

### 1.2 集成目标

1. 以 Hermes Agent 为**底层执行引擎**
2. OpenClawHub 作为**多租户 SaaS 管理层**
3. 数字员工的"角色能力"通过 **Hermes Skills** 实现
4. 保留 OpenClawHarness 的**进化闭环**能力（corrections → self-improve）

---

## 二、整体架构

### 2.1 分层架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenClawHub SaaS 层                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Web 管理后台 (Vue3)    ┌  移动端（响应式）                  │ │
│  │  租户管理 / 组织 / 用户  │  钉钉 / 飞书 / 企微小程序           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    REST API / WebSocket                     │ │
│  │            认证 / 租户 / 组织 / Agent / 工作流                │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    OpenClawHub 协作层                            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  任务调度器    │ │  团队协作协议  │ │  进化闭环引擎  │             │
│  │  TaskManager │ │  TeamProtocol │ │  SelfImprove │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│                    Hermes Agent 运行时                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  Tenant: tenant_001 / tenant_002 / ...（每个租户独立实例）     │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │  AIAgent (~10,700行) — 对话循环                         │ │ │
│  │  │  HermesCLI — CLI 交互入口                               │ │ │
│  │  │  Gateway — 多平台消息分发（钉钉/飞书/企微/微信/...）     │ │ │
│  │  │  ┌───────────────────────────────────────────────────┐   │ │ │
│  │  │  │  Skills System — 数字员工角色定义                 │   │ │ │
│  │  │  │  ├── pm-manager-skill（项目经理）               │   │ │ │
│  │  │  │  ├── architect-skill（架构师）                   │   │ │ │
│  │  │  │  ├── backend-dev-skill（后端开发）               │   │ │ │
│  │  │  │  ├── frontend-dev-skill（前端开发）              │   │ │ │
│  │  │  │  ├── tester-skill（测试工程师）                  │   │ │ │
│  │  │  │  └── ui-designer-skill（UI 设计师）              │   │ │ │
│  │  │  └───────────────────────────────────────────────────┘   │ │ │
│  │  │  Memory System — 有界记忆（MEMORY.md / USER.md）         │ │ │
│  │  │  Cron Scheduler — 定时任务 / 汇报                        │ │ │
│  │  │  MCP Client — 扩展工具（GitHub/GitLab/Jira/...）        │ │ │
│  │  │  Tools: 47 tools / 19 toolsets                         │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
OpenClawHub/
├── backend/                    # FastAPI 后端（新增/改造）
│   ├── api/                     # API 路由
│   │   ├── auth.py              # 认证（登录/注册/Token）
│   │   ├── tenants.py           # 租户管理
│   │   ├── organizations.py     # 组织管理
│   │   ├── users.py             # 用户管理
│   │   ├── agents.py            # 数字员工实例管理
│   │   ├── tasks.py             # 任务管理
│   │   └── workflows.py         # 工作流
│   ├── models/                  # SQLAlchemy 模型
│   ├── schemas/                 # Pydantic schemas
│   ├── services/
│   │   ├── hermes_service.py    # Hermes Agent 实例管理
│   │   ├── tenant_isolation.py  # 多租户隔离
│   │   └── evolution.py         # 进化闭环（集成 OpenClawHarness）
│   └── main.py
│
├── hermes-runtime/             # 🌟 Hermes Agent 运行时（新增）
│   ├── tenants/                 # 多租户隔离目录
│   │   └── {tenant_id}/
│   │       ├── hermes_home/     # HERMES_HOME（~.hermes）
│   │       │   ├── memories/    # MEMORY.md / USER.md
│   │       │   ├── skills/      # 角色 Skills
│   │       │   ├── jobs.json    # Cron 任务
│   │       │   └── sessions/    # SQLite 会话存储
│   │       ├── config.yaml      # 租户级配置
│   │       └── agents/          # 该租户的数字员工实例
│   │           └── {agent_id}/
│   │               └── agent.yaml
│   │
│   └── hermes_src/              # Hermes Agent 源码（forked）
│       ├── run_agent.py
│       ├── hermes_state.py
│       ├── tools/
│       ├── gateway/
│       └── ...
│
├── frontend/                    # Vue3 前端（已有，保持）
│   └── ...
│
├── openclawah-harness/          # 🌟 进化闭环层（复用）
│   ├── corrections/             # 反馈闭环
│   ├── evolver_insights.py      # 进化洞察
│   ├── graph_insights.py         # 图谱洞察
│   └── harness_run.py           # Agent 执行入口
│
└── docker/                      # Docker 部署（改造）
    ├── docker-compose.yml
    └── hermes/
        └── Dockerfile
```

---

## 三、多租户隔离方案

### 3.1 隔离原则

每个租户 = 一个独立的 Hermes Agent 实例（进程），完全隔离：

| 资源 | 隔离方式 |
|------|---------|
| Hermes Home | `hermes-runtime/tenants/{tenant_id}/hermes_home/` |
| Skills | 租户私有 Skills + 平台共享 Skills |
| Memory | `MEMORY.md` / `USER.md` 在租户目录内 |
| Sessions | SQLite 在租户目录内 |
| Config | `config.yaml` 在租户目录内 |
| Cron Jobs | `jobs.json` 在租户目录内 |

### 3.2 平台共享 Skills

```
hermes-runtime/shared_skills/   # 所有租户共享
├── github-integration-skill/
├── gitlab-integration-skill/
├── jira-integration-skill/
└── common-tools-skill/
```

租户私有 Skills：
```
hermes-runtime/tenants/{tenant_id}/hermes_home/skills/
├── pm-manager-skill/            # 租户私有角色
├── backend-dev-skill/
└── ... + shared_skills/ 链接
```

### 3.3 租户级配置

```yaml
# hermes-runtime/tenants/{tenant_id}/config.yaml
tenant:
  id: "tenant_001"
  name: "老赵工作室"
  plan: "pro"                    # free / pro / enterprise

hermes:
  model: "minimax/MiniMax-M2.7"  # 可按租户配置模型
  provider: "portal.nousresearch.com"
  
limits:
  max_agents: 10                 # 最大数字员工数
  max_sessions_per_day: 1000
  max_cron_jobs: 20
```

---

## 四、数字员工角色定义（Skills）

### 4.1 角色 Skill 映射

| OpenClawHub 角色 | Hermes Skill | 核心职责 |
|-----------------|--------------|---------|
| PM（项目经理） | `pm-manager-skill` | 任务拆解、分配、进度跟踪、汇报 |
| Architect | `architect-skill` | 系统架构、技术方案、代码审查 |
| Backend-Dev | `backend-dev-skill` | 后端 API、数据库、业务逻辑 |
| Frontend-Dev | `frontend-dev-skill` | Web UI、交互、响应式 |
| Tester | `tester-skill` | 测试用例、自动化测试、Bug 报告 |
| UI-Designer | `ui-designer-skill` | 视觉设计、UI 规范、组件设计 |
| DevOps | `devops-skill` | CI/CD、部署、监控 |

### 4.2 Skill 结构（参考 Hermes SKILL.md 格式）

```
pm-manager-skill/
├── SKILL.md                     # 主技能定义
├── prompts/
│   ├── task-decompose.md        # 任务拆解 prompt
│   ├── progress-report.md       # 进度汇报 prompt
│   └── agent-assign.md          # 任务分配 prompt
└── templates/
    └── weekly-report.md         # 周报模板
```

### 4.3 SKILL.md 示例（pm-manager-skill）

```markdown
---
name: pm-manager-skill
description: 数字员工项目经理，负责任务拆解、分配、进度跟踪和汇报
version: 1.0.0
platforms: [linux, darwin, windows]
metadata:
  hermes:
    tags: [project-management, coordination]
    category: management
    requires_toolsets: [terminal, file]
---

# PM Manager Skill

## 当使用
当 CEO（创始人）或 Admin 创建项目、拆解任务、检查进度时触发。

## 职责
1. 将业务目标拆解为可执行的任务（WBS）
2. 根据角色分配任务给合适的数字员工
3. 跟踪进度，识别阻塞点
4. 生成结构化进度汇报

## 流程

### 任务拆解
1. 理解业务目标和约束条件
2. 识别依赖关系和里程碑
3. 拆解为 0.5-2 天的任务单元
4. 标记每个任务的负责人和截止日期

### 任务分配
1. 根据角色 Skill 匹配最合适的数字员工
2. 生成任务卡片（含描述、验收标准、截止）
3. 通过 Hermes Gateway 推送给对应 Agent

### 进度汇报
1. 汇总各 Agent 的任务状态
2. 识别风险和阻塞
3. 生成汇报（Text/JSON）供 CEO 审阅

## 工具使用
- file_tools: 读写任务文件
- terminal_tool: 执行命令
- delegate_tool: 委托子任务

## 验证
任务拆解后，检查：
- 每个任务有明确的验收标准
- 任务间依赖关系已标注
- 工期估算在合理范围（0.5-2天）
```

---

## 五、团队协作协议

### 5.1 Agent ↔ Agent 通信

Hermes 已内置 `delegate_tool`，支持 spawn 隔离子 agent。

新增 **team-protocol-skill** 定义协作规范：

```markdown
## Agent 间通信协议

### 1. 任务委托
当 PM 需要某角色执行任务时：
- 使用 delegate_tool spawn 对应角色的 sub-agent
- 传递：任务描述 + 验收标准 + 截止时间
- sub-agent 完成后返回结果

### 2. 结果汇总
PM 收集所有 sub-agent 结果后：
- 汇总状态（成功/失败/阻塞）
- 生成进度报告
- 更新任务看板状态

### 3. 冲突处理
- 同一任务被多个 Agent 抢接 → PM 仲裁
- 任务依赖循环 → Architect 解决
- 资源争用 → 按优先级调度

### 4. 汇报机制
- 每日 Cron：各 Agent 向 PM 汇报进度
- PM 汇总后向 CEO 汇报
- 阻塞超过 1 小时：立即上报
```

### 5.2 汇报流程

```
CEO（老赵）
    ↓ 下达业务目标
    ↓
PM Agent
    ↓ 拆解任务 + 分配
    ↓
Architect ←→ Backend-Dev ←→ Frontend-Dev ←→ Tester
    ↓ 执行 + 反馈
    ↓
PM Agent（汇总进度）
    ↓
CEO（结构化汇报）
```

---

## 六、进化闭环集成

### 6.1 OpenClawHarness 进化能力继承

| OpenClawHarness 能力 | 集成到 Hermes |
|---------------------|--------------|
| `corrections/` 反馈闭环 | → Hermes Memory + Skill 自优化 |
| `evolver_insights.py` | → Hermes 内置进化循环 |
| `graph_insights.py` | → 新增 project-knowledge-skill |
| `enforcement_checker.py` | → tester-skill 内置代码质量检查 |

### 6.2 进化流程

```
任务执行完成
    ↓
correction 反馈（老赵/PM 评价）
    ↓
evolution.py 分析反馈
    ↓
更新相关 Skill（SKILL.md）
    ↓ 或
更新 MEMORY.md（经验沉淀）
    ↓
下次同类型任务自动应用新经验
```

### 6.3 定时进化任务

```yaml
# jobs.json（每个租户独立）
{
  "jobs": [
    {
      "id": "weekly-evolution",
      "schedule": "0 22 * * 0",      # 每周日 22:00
      "prompt": "review_recent_corrections",
      "skill": "evolution-skill",
      "target": "platform"           # 汇报给 CEO
    },
    {
      "id": "daily-standup",
      "schedule": "0 9 * * 1-5",     # 工作日 9:00
      "prompt": "collect_agent_status",
      "skill": "pm-manager-skill"
    }
  ]
}
```

---

## 七、API 设计（Phase 1）

### 7.1 OpenClawHub Backend API

```
认证（Auth）
POST   /api/v1/auth/register         # 注册
POST   /api/v1/auth/login            # 登录
POST   /api/v1/auth/logout           # 登出
POST   /api/v1/auth/refresh          # 刷新 Token
DELETE /api/v1/auth/account          # 删除账户

租户（Tenant）
GET    /api/v1/tenants/me            # 获取当前租户信息
PATCH  /api/v1/tenants/me            # 更新租户配置
GET    /api/v1/tenants/me/billing    # 计费信息

组织（Organization）
POST   /api/v1/orgs                   # 创建组织
GET    /api/v1/orgs                   # 列表
GET    /api/v1/orgs/{id}              # 详情
PATCH  /api/v1/orgs/{id}              # 更新
DELETE /api/v1/orgs/{id}              # 删除
GET    /api/v1/orgs/{id}/members      # 成员列表
POST   /api/v1/orgs/{id}/invite       # 邀请成员

用户（User）
GET    /api/v1/users/me              # 当前用户信息
PATCH  /api/v1/users/me              # 更新个人信息
GET    /api/v1/users/me/preferences   # 偏好设置
PATCH  /api/v1/users/me/preferences

数字员工（Agent）🌟 新增
GET    /api/v1/agents                 # 列表（租户内）
POST   /api/v1/agents                 # 创建数字员工实例
GET    /api/v1/agents/{id}            # 详情
PATCH  /api/v1/agents/{id}           # 更新配置
DELETE /api/v1/agents/{id}           # 删除
POST   /api/v1/agents/{id}/start      # 启动实例
POST   /api/v1/agents/{id}/stop       # 停止实例
GET    /api/v1/agents/{id}/status     # 运行状态
POST   /api/v1/agents/{id}/message    # 发送消息
GET    /api/v1/agents/{id}/sessions  # 会话历史

任务（Task）🌟 新增
GET    /api/v1/tasks                  # 列表
POST   /api/v1/tasks                  # 创建
GET    /api/v1/tasks/{id}            # 详情
PATCH  /api/v1/tasks/{id}            # 更新状态
DELETE /api/v1/tasks/{id}
GET    /api/v1/tasks/{id}/comments    # 评论/反馈

WebSocket
WS     /api/v1/ws/agent/{id}          # 数字员工实时通信
WS     /api/v1/ws/tasks/{id}          # 任务状态实时更新
```

### 7.2 Agent 实例创建流程

```yaml
# POST /api/v1/agents 请求体
{
  "name": "后端开发-张三",
  "role": "backend-dev",              # 角色标识
  "personality": "严谨、高效、代码规范",
  "model": "minimax/MiniMax-M2.7",   # 可选，使用租户默认
  "skills": ["backend-dev-skill", "github-integration-skill"],
  "limits": {
    "max_sessions_per_day": 100,
    "max_tool_calls_per_task": 500
  }
}

# 响应
{
  "id": "agent_001",
  "tenant_id": "tenant_001",
  "hermes_instance_id": "hermes_abc123",  # Hermes 实例标识
  "status": "stopped",                     # stopped / running / error
  "skills": ["backend-dev-skill", "github-integration-skill"],
  "created_at": "2026-04-17T15:30:00Z"
}
```

---

## 八、数据模型

### 8.1 新增模型

```python
# backend/models/tenant.py
class Tenant(Base):
    __tablename__ = "tenants"
    
    id: UUID
    name: str
    plan: str                          # free / pro / enterprise
    hermes_home_path: str              # hermes-runtime/tenants/{id}/hermes_home
    config: dict                       # JSON 配置
    created_at: datetime
    updated_at: datetime

# backend/models/agent.py
class Agent(Base):
    __tablename__ = "agents"
    
    id: UUID
    tenant_id: UUID                    # FK → tenants
    name: str
    role: str                         # backend-dev / frontend-dev / pm / ...
    hermes_instance_id: str           # Hermes Agent 实例标识
    status: str                       # stopped / running / error
    skills: list[str]                 # 启用的 Skills
    config: dict
    created_at: datetime
    updated_at: datetime

# backend/models/task.py
class Task(Base):
    __tablename__ = "tasks"
    
    id: UUID
    tenant_id: UUID
    project_id: UUID
    title: str
    description: str
    status: str                       # todo / in_progress / review / done / blocked
    priority: int                     # 1-5
    assignee_id: UUID                  # FK → agents
    reporter_id: UUID                 # FK → users
    due_date: datetime
    created_at: datetime
    updated_at: datetime
```

### 8.2 Hermes 运行时数据（每个租户独立）

```
hermes-runtime/tenants/{tenant_id}/
├── hermes_home/
│   ├── memories/
│   │   ├── MEMORY.md               # Agent 记忆（~2200 chars）
│   │   └── USER.md                 # 用户画像（~1375 chars）
│   ├── skills/                      # Skills 目录
│   ├── sessions/                    # SQLite（会话历史）
│   ├── jobs.json                    # Cron 任务
│   └── hermes_state.db              # Hermes 状态数据库
└── config.yaml                      # 租户级 Hermes 配置
```

---

## 九、技术实现路径

### 9.1 Phase 0：Hermes 集成准备（1-2天）

**目标**：fork Hermes Agent，搭建多租户运行时

**任务**：
1. Fork [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
2. 改造目录结构，支持多租户隔离
3. 实现 `TenantIsolation` 服务（创建/删除租户 Hermes 实例）
4. 实现 `HermesInstanceManager`（启动/停止/监控 Agent 实例）
5. 编写 Docker 镜像

**验收标准**：
- [ ] 单个 Hermes Agent 实例可正常启动
- [ ] 多租户目录隔离验证
- [ ] Docker 镜像构建成功

### 9.2 Phase 1：认证 + Agent 管理 API（3-4天）

**目标**：完成多租户认证 + 数字员工 CRUD

**任务**：
1. 实现 `/api/v1/auth/*`（JWT 认证）
2. 实现 `/api/v1/tenants/*`（租户管理）
3. 实现 `/api/v1/orgs/*`（组织管理）
4. 实现 `/api/v1/agents/*`（数字员工 CRUD）
5. 集成 `HermesInstanceManager`
6. 前端：登录/注册/Agent 列表页面

**验收标准**：
- [ ] 用户注册 → 自动创建租户目录
- [ ] 创建 Agent → 自动初始化 Hermes 实例
- [ ] 启动/停止 Agent 正常工作
- [ ] JWT Token 认证通过

### 9.3 Phase 2：角色 Skills 开发（2-3天）

**目标**：编写 6 个核心角色 Skill

**任务**：
1. 编写 `pm-manager-skill`
2. 编写 `architect-skill`
3. 编写 `backend-dev-skill`
4. 编写 `frontend-dev-skill`
5. 编写 `tester-skill`
6. 编写 `ui-designer-skill`
7. 集成 OpenClawHarness 进化闭环

**验收标准**：
- [ ] Skills 可通过 `/skills` 命令查看
- [ ] 角色 Skill 包含完整职责定义和流程
- [ ] Skills 支持渐进式加载

### 9.4 Phase 3：任务 + 协作（3-4天）

**目标**：任务管理 + Agent 间协作

**任务**：
1. 实现 `/api/v1/tasks/*`（CRUD + 状态流转）
2. 实现 WebSocket 实时通信
3. 实现 `TeamProtocol` 协作服务
4. 实现 `delegate_tool` 任务委托
5. 前端：看板页面 + 任务详情

**验收标准**：
- [ ] 任务创建 → PM 自动拆解 → 分配给 Agent
- [ ] Agent 执行 → 实时日志推送 → WebSocket
- [ ] 任务状态变更 → 实时更新看板

### 9.5 Phase 4+：完善（参考原计划）

| Phase | 内容 |
|-------|------|
| Phase 5 | Activity Feed |
| Phase 6 | Dashboard |
| Phase 7 | 测试 + Bug 修复 |
| Phase 8 | 部署上线 |

---

## 十、与原方案对比

| 维度 | 原方案（OpenClawHarness 为底座） | 新方案（Hermes Agent 为底座） |
|------|--------------------------------|-------------------------------|
| **Agent 执行引擎** | 自研 harness_run.py | Hermes AIAgent（10,700行，成熟） |
| **进化闭环** | corrections → evolver → graph | Hermes Skills 自优化 + corrections 集成 |
| **多平台** | 需自研 | 内置 18 个平台适配器 |
| **Skills 系统** | RULES.md | SKILL.md（标准格式，渐进加载） |
| **多 Agent 协作** | delegate 需自研 | 内置 delegate_tool |
| **测试覆盖** | ~3,000 测试 | 继承 Hermes 3,000+ 测试 |
| **开发工作量** | 高（自研 Agent 引擎） | 中（偏重集成+Skills） |
| **技术风险** | 高（自研） | 低（成熟开源） |

**核心变化**：Phase 1-3 的工作量从"自研 Agent 引擎"变成"集成 Hermes + 开发 Skills"，风险更低，效果更好。

---

## 十一、风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| Hermes 升级 break Change | 低 | 中 | 锁定版本，定期同步 |
| 多租户隔离不彻底 | 中 | 高 | 严格目录权限 + 进程隔离 |
| Skills 编写质量参差 | 中 | 中 | 参考 Hermes 官方 Skills + 老赵评审 |
| Hermes 内存泄漏 | 低 | 中 | 监控 + 定时重启 |
| Docker 资源占用 | 中 | 低 | 按需分配 CPU/内存限制 |

---

## 十二、结论

以 Hermes Agent 为底座是完全可行的，MIT License 允许闭源商用。

**优势**：
- 省去 Agent 执行引擎的重复开发
- 继承成熟的多平台消息网关
- Skills 系统比 RULES.md 更标准化
- 3,000+ 测试覆盖保证质量

**工作量变化**：
- Phase 0-1：增加 Hermes 集成准备（约 +1-2 天）
- Phase 2：Skills 开发（可并行，约 2-3 天）
- Phase 3-4：与原计划持平

**建议执行顺序**：
1. Phase 0：Hermes 集成 + 多租户隔离
2. Phase 1：认证 + Agent CRUD
3. Phase 2：Skills 开发 + 进化闭环
4. Phase 3+：任务协作 + 完善

---

_整理：妙妙 | 日期：2026-04-17_
_待老赵审批后执行_
