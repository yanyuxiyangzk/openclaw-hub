# OpenClawHub Phase 1 前后端联调任务

**项目路径:** D:\project\aicoding\OpenClawHub
**任务类型:** frontend-dev + backend-dev（联合联调）
**参考文档:** 
- D:\project\aicoding\OpenClawHub\harness\TASK-Phase1-Backend.md
- D:\project\aicoding\OpenClawHub\harness\TASK-Phase1-Frontend.md
**执行规则:** 遵守 auto-dev 开发规范（边开发边写测试）

---

## 任务目标

Phase 1 的前端 API 层（src/api/*.ts）和后端 FastAPI（backend/routers/）需要实际联调，确保：
1. 前端 axios 请求能正确调用后端 API
2. 后端响应格式被前端正确解析
3. JWT Token 在请求头中正确携带
4. 错误处理（401/403/404）正确

---

## 当前状态

### 后端（已完成）
- 23 个 API 全部实现并通过测试（37 passed）
- JWT 认证正常工作
- 响应格式：`{ code: 0, message: "success", data: {} }`

### 前端（已完成骨架）
- 7 个页面全部创建
- src/api/auth.ts, users.ts, orgs.ts 已创建
- Pinia store 已配置
- 路由守卫已配置
- **⚠️ 还未实际调用后端 API（后端没运行）**

---

## 联调任务清单

### 1. 启动后端服务（dev 模式）

```bash
cd D:\project\aicoding\OpenClawHub\backend
uvicorn main:app --reload --port 8008
```

验证：
- GET http://localhost:8008/health 返回 {"status":"ok", "version": "0.1.0"}
- POST /api/auth/register 能创建用户
- POST /api/auth/login 能返回 token

### 2. 修复前端 API 层

检查 `src/api/index.ts`：
- baseURL: '/api' 是否正确
- withCredentials: true
- 请求拦截器是否正确添加 `Authorization: Bearer <token>`
- 响应拦截器是否处理 code != 0 的情况

检查 `src/api/auth.ts`：
- login(email, password) → POST /api/auth/login
- register(data) → POST /api/auth/register  
- getMe() → GET /api/auth/me
- updateMe(data) → PUT /api/auth/me
- logout() → POST /api/auth/logout
- refresh() → POST /api/auth/refresh

检查 `src/api/users.ts`：
- list(params) → GET /api/users
- get(id) → GET /api/users/{id}
- update(id, data) → PUT /api/users/{id}
- remove(id) → DELETE /api/users/{id}
- changePassword(id, data) → PUT /api/users/{id}/password
- toggleActive(id) → PUT /api/users/{id}/toggle-active

检查 `src/api/orgs.ts`：
- list() → GET /api/orgs
- create(data) → POST /api/orgs
- get(id) → GET /api/orgs/{id}
- update(id, data) → PUT /api/orgs/{id}
- remove(id) → DELETE /api/orgs/{id}
- members(id) → GET /api/orgs/{id}/members
- removeMember(orgId, userId) → DELETE /api/orgs/{id}/members/{user_id}
- sendInvitation(orgId, data) → POST /api/orgs/{id}/invitations
- verifyInvitation(token) → GET /api/invitations/{token}
- acceptInvitation(token) → POST /api/invitations/{token}/accept
- revokeInvitation(id) → DELETE /api/invitations/{id}

### 3. 修复前端 View 组件

检查每个 View 是否：
- 正确 import API 函数
- 正确处理 loading/error 状态
- 登录成功跳转 /orgs
- 注册成功跳转 /orgs 或自动登录

需要检查的页面：
- LoginView.vue - 登录页
- RegisterView.vue - 注册页
- SettingsView.vue - 个人设置
- OrgListView.vue - 组织列表
- OrgDetailView.vue - 组织详情
- InvitationView.vue - 邀请接受页
- MemberManageView.vue - 成员管理

### 4. 前端 Mock 数据 vs 真实 API

在 Vite 开发服务器中，前端运行在 5173 端口，后端在 8008 端口。
vite.config.ts 已配置 proxy：
- /api → http://localhost:8008（已配置）
- /ws → ws://localhost:8008（已配置）

确保前端代码不直接使用 localhost:8008，而是使用相对路径 /api。

### 5. 测试验证

启动前后端后，手动测试：
1. POST /api/auth/register 创建账号
2. POST /api/auth/login 登录，获取 token
3. GET /api/auth/me 验证 token 有效
4. POST /api/orgs 创建组织
5. GET /api/orgs 查看组织列表

---

## 执行规则（auto-dev）

1. **先阅读 harness-context.md**：了解项目上下文
2. **边开发边写测试**：每修复一个问题写一个测试
3. **代码和测试同时 commit**
4. **遇到问题参考 corrections/ 中的历史经验**

---

## 验收标准

- [ ] 后端 `uvicorn main:app --reload --port 8008` 能正常启动
- [ ] 前端 `npm run dev` 能正常启动（5173 端口）
- [ ] 前端代理配置正确（/api → localhost:8008）
- [ ] 登录页能调用 POST /api/auth/login 并显示结果
- [ ] 注册页能调用 POST /api/auth/register 并显示结果
- [ ] 组织列表页能调用 GET /api/orgs 并显示结果
- [ ] JWT Token 在后续请求中正确携带
- [ ] 401 错误正确跳转到登录页