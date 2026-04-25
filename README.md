# OpenClawHub

> 一人公司的数字员工 SaaS 平台

## 项目定位

OpenClawHub 是面向「一人公司」和「小团队」的多 Agent 协作 SaaS 平台。
让 AI 从「聊天工具」进化为「数字员工」，每个 AI Agent 有角色、记忆、任务、产出。

## 技术栈

- **前端**: Vue3 + Vite + TypeScript + TailwindCSS
- **后端**: Python FastAPI + SQLAlchemy
- **数据库**: SQLite（开发）/ PostgreSQL（生产）
- **实时**: WebSocket
- **部署**: Docker Compose

## 快速开始

### 开发环境

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8008

# 前端（新开终端）
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

### Docker 部署

```bash
docker-compose up -d
```

## 目录结构

```
OpenClawHub/
├── backend/          # FastAPI 后端
├── frontend/         # Vue3 前端
├── docker/           # Docker 配置
├── docs/             # 项目文档
├── data/             # 数据目录
├── harness/          # 执行引擎
└── logs/             # 日志目录
```

## 开发阶段

- Phase 0: 项目初始化 ✅
- Phase 1: 认证模块 ✅
- Phase 2: 项目管理模块 ✅
- Phase 3: Agent 管理模块 ✅
- Phase 4: 任务看板模块 ✅
- Phase 5: 执行引擎集成 ✅
- Phase 6: Activity Feed ✅
- Phase 7: Dashboard ✅
- Phase 8: 测试 + 修复 ✅
- Phase 9: 部署上线 ✅ (当前)

## 部署

### 生产环境部署

```bash
# Unix/macOS
./deploy.sh --production

# Windows PowerShell
.\deploy.ps1 -Env production
```

### Docker Compose 生产部署

```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

### 健康检查

- 整体健康: `http://localhost:8080/health`
- API 健康: `http://localhost:8080/api/health`

详见 [DEPLOY.md](./DEPLOY.md)

## 文档

- [PRD](./docs/PRD-产品需求文档.md)
- [技术架构](./docs/技术架构文档.md)
- [Agent 角色定义](./docs/Agent-角色定义.md)
- [开发计划](./docs/开发计划-Phase规划.md)

---

_v0.1 MVP - 2026-04-16_
