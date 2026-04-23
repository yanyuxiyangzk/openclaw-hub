# OpenClawHub 部署文档

> 部署前请确保已阅读本文档全部内容

## 目录

- [前置要求](#前置要求)
- [环境配置](#环境配置)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [CI/CD 自动化部署](#cicd-自动化部署)
- [健康检查](#健康检查)
- [故障排查](#故障排查)

---

## 前置要求

### 必需软件

| 软件 | 版本 | 说明 |
|------|------|------|
| Docker | 20.10+ | 容器化部署 |
| Docker Compose | 2.0+ | 多容器编排 |
| PostgreSQL | 16+ | 生产数据库 |
| Redis | 7+ | 缓存和队列 |

### 服务器配置

最低配置：
- 2 CPU cores
- 4 GB RAM
- 40 GB SSD

推荐配置：
- 4 CPU cores
- 8 GB RAM
- 100 GB SSD

---

## 环境配置

### 1. 创建环境变量文件

```bash
cp .env.production.template .env.production
```

### 2. 配置必填环境变量

```env
# 数据库
POSTGRES_DB=openclawhub
POSTGRES_USER=openclawhub
POSTGRES_PASSWORD=<随机强密码>

# 安全密钥（生成命令: openssl rand -hex 32）
SECRET_KEY=<your-secret-key>

# 访问控制
ALLOWED_HOSTS=app.openclawhub.com,localhost

# CORS
CORS_ORIGINS=https://app.openclawhub.com

# 生产环境标识
ENVIRONMENT=production
```

### 3. 生成密钥

```bash
# Linux/macOS
openssl rand -hex 32
```

---

## 开发环境部署

```bash
docker-compose up -d
```

访问：
- 前端: http://localhost:80
- API: http://localhost:8008
- API Docs: http://localhost:8008/docs

---

## 生产环境部署

### Docker Compose

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 构建镜像
docker-compose -f docker/docker-compose.prod.yml build

# 3. 启动服务
docker-compose -f docker/docker-compose.prod.yml up -d

# 4. 检查健康状态
curl http://localhost:8080/health
```

### 一键部署脚本

Unix/macOS:
```bash
chmod +x deploy.sh
./deploy.sh --production
```

Windows PowerShell:
```powershell
.\deploy.ps1 -Env production
```

---

## CI/CD 自动化部署

在 GitHub 仓库 Settings > Secrets 添加：
- STAGING_HOST, STAGING_USER, STAGING_SSH_KEY
- PRODUCTION_HOST, PRODUCTION_USER, PRODUCTION_SSH_KEY

推送到 main 分支 → 自动部署到 Staging
推送到 master 分支 → 自动部署到生产

---

## 健康检查

| 端点 | 说明 |
|------|------|
| `GET /health` | 基础健康检查 |
| `GET /api/health` | API + 数据库健康检查 |

```bash
curl http://localhost:8080/health
# 返回: {"status": "healthy", "service": "openclawhub"}

curl http://localhost:8080/api/health
# 返回: {"status": "healthy", "service": "openclawhub-api", "database": "connected"}
```

---

## 故障排查

### 日志查看

```bash
docker-compose -f docker/docker-compose.prod.yml logs -f backend
```

### 常见问题

**端口冲突：**
```bash
netstat -tlnp | grep -E '80|8008|5432|6379'
```

**清理 Docker 缓存：**
```bash
docker builder prune -a
docker-compose -f docker/docker-compose.prod.yml build --no-cache
```

---

## 生产检查清单

- [ ] `/health` 端点返回 200
- [ ] `/api/health` 端点返回 200，database=connected
- [ ] 前端可访问
- [ ] 用户可登录
- [ ] Agent 可创建和启动
- [ ] Docker 容器状态为 healthy

---

_v1.0.0 - 2026-04-23_
