# OpenClawHub Phase 1 前端开发任务

## 项目路径
D:\project\aicoding\OpenClawHub

## 任务概述
使用 Vue3 + Vite + TypeScript + TailwindCSS 实现 OpenClawHub Phase 1 认证模块，7个页面。

## 技术栈
- Vue3 + Vite + TypeScript
- TailwindCSS（已配置：深色主题 bg-gray-900，紫色主色调 purple-500）
- Axios（HTTP 客户端）
- Vue Router（路由）
- Pinia（状态管理）
- Vitest（测试）

## 当前项目状态
frontend/ 目录已存在，src/views/ 有 Phase 0 残留的空文件（LoginView.vue, RegisterView.vue, ProjectListView.vue）
frontend/src/api/ 为空
frontend/src/router/ 已配置基础路由
frontend/package.json 已存在

## 页面清单（7个）
1. /login - 登录页（邮箱+密码，表单校验，loading状态）
2. /register - 注册页（邮箱+密码+确认密码+昵称，密码强度校验）
3. /settings - 个人设置（信息修改+登出）
4. /orgs - 组织列表（显示所有组织+创建组织）
5. /orgs/:id - 组织详情（组织信息+成员列表）
6. /orgs/:id/members - 成员管理（成员列表+邀请+移除）
7. /invite/:token - 邀请接受页（验证+接受邀请）

## API 调用层（src/api/）
```typescript
// auth.ts
export const login = (data) => post('/auth/login', data)
export const register = (data) => post('/auth/register', data)
export const getMe = () => get('/auth/me')
export const updateMe = (data) => put('/auth/me', data)
export const logout = () => post('/auth/logout')
export const refresh = () => post('/auth/refresh')

// users.ts
export const listUsers = (params) => get('/users', { params })
export const getUser = (id) => get(`/users/${id}`)
export const updateUser = (id, data) => put(`/users/${id}`, data)
export const deleteUser = (id) => delete(`/users/${id}`)
export const toggleActive = (id) => put(`/users/${id}/toggle-active`)

// orgs.ts
export const listOrgs = () => get('/orgs')
export const createOrg = (data) => post('/orgs', data)
export const getOrg = (id) => get(`/orgs/${id}`)
export const updateOrg = (id, data) => put(`/orgs/${id}`, data)
export const deleteOrg = (id) => delete(`/orgs/${id}`)
export const getMembers = (orgId) => get(`/orgs/${orgId}/members`)
export const removeMember = (orgId, userId) => delete(`/orgs/${orgId}/members/${userId}`)
export const sendInvitation = (orgId, data) => post(`/orgs/${orgId}/invitations`, data)
export const verifyInvitation = (token) => get(`/invitations/${token}`)
export const acceptInvitation = (token) => post(`/invitations/${token}/accept`)
export const revokeInvitation = (invId) => delete(`/invitations/${invId}`)
```

## axios 实例配置（src/api/index.ts）
- baseURL: /api
- withCredentials: true（携带 cookie）
- 自动添加 Authorization: Bearer <token>
- 响应拦截器：401 → 跳转 /login

## 路由配置（src/router/index.ts）
```typescript
routes = [
  { path: '/login', component: LoginView, meta: { guest: true } },
  { path: '/register', component: RegisterView, meta: { guest: true } },
  { path: '/settings', component: SettingsView, meta: { auth: true } },
  { path: '/orgs', component: OrgListView, meta: { auth: true } },
  { path: '/orgs/:id', component: OrgDetailView, meta: { auth: true } },
  { path: '/orgs/:id/members', component: MemberManageView, meta: { auth: true } },
  { path: '/invite/:token', component: InvitationView, meta: { guest: true } },
]
```
路由守卫：meta.auth && !isAuthenticated → /login；meta.guest && isAuthenticated → /orgs

## Pinia Store（src/stores/auth.ts）
```typescript
state: { user: null, token: null, isAuthenticated: false }
actions: login(), register(), logout(), fetchMe(), updateMe()
```

## 开发规则（autodev）
1. **每个页面写 Vitest 测试**，代码和测试同时 commit
2. API 调用先用 mock 数据（因为后端还没好），等后端完成再替换
3. 深色主题（bg-gray-900 body，bg-gray-800 卡片）+ 紫色主色调（purple-500 buttons）

## 执行步骤
1. 安装依赖：npm install axios vue-router pinia
2. 创建 src/api/index.ts（axios 实例）
3. 创建 src/api/auth.ts, users.ts, orgs.ts（API 调用）
4. 创建 src/stores/auth.ts, org.ts（Pinia store）
5. 更新 src/router/index.ts（完整路由配置+守卫）
6. 创建7个页面（先写好 UI，API 调用先 mock）
7. 创建 src/components/layout/AppLayout.vue, Sidebar.vue, Topbar.vue
8. 为每个页面写 Vitest 测试
9. npm run build 验证
10. git add + git commit

完成后汇报：实现了哪些页面、测试数量、编译是否通过、commit hash。