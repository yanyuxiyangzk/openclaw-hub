# OpenClawHub Phase 1 前端任务

**项目路径:** D:\project\aicoding\OpenClawHub
**任务类型:** frontend-dev
**并行任务:** backend-dev（同时进行）
**时间:** 2026-04-18

---

## 目标

使用 Vue3 + Vite + TypeScript + TailwindCSS 实现 OpenClawHub Phase 1 认证模块，涵盖 7 个页面。

**重要：** 前端需要等后端 API 准备好才能联调，但 UI 组件和页面结构可以先搭建mock数据。进度安排：
1. 先做页面 UI 和组件（不依赖真实 API）
2. 后端完成后，补充 API 调用层并联调

---

## 技术栈

- Vue3 + Vite + TypeScript
- TailwindCSS（已配置）
- Axios（HTTP 客户端）
- Vue Router（路由）
- Pinia（状态管理）
- 样式: 深色主题（bg-gray-900）+ 紫色主色调（purple-500）

---

## 页面清单（7个）

### 1. 登录页 `/login`

**功能：**
- 邮箱 + 密码登录
- 表单校验（邮箱格式、密码非空）
- 登录按钮 loading 状态
- 错误提示（邮箱或密码错误）
- 跳转到"注册账号"链接

**组件：**
```
src/views/auth/
├── LoginView.vue        # 登录页
├── RegisterView.vue      # 注册页
├── SettingsView.vue     # 个人设置
└── org/
    ├── OrgListView.vue      # 组织列表
    ├── OrgDetailView.vue     # 组织详情
    ├── InvitationView.vue   # 邀请接受页
    └── MemberManageView.vue  # 成员管理
```

**API 调用：**
- `POST /api/auth/login` → 登录

---

### 2. 注册页 `/register`

**功能：**
- 邮箱 + 密码 + 确认密码 + 昵称
- 密码强度校验（至少8位，含数字+字母）
- 确认密码一致性校验
- 注册成功自动登录，跳转到首页或组织创建页

**API 调用：**
- `POST /api/auth/register` → 注册

---

### 3. 个人设置页 `/settings`

**功能：**
- 显示当前用户信息（邮箱、昵称、头像）
- 修改昵称
- 修改密码（旧密码 + 新密码 + 确认）
- 登出按钮

**API 调用：**
- `GET /api/auth/me` → 获取当前用户
- `PUT /api/auth/me` → 更新用户信息
- `POST /api/auth/logout` → 登出

**组件：**
```
src/views/settings/
└── SettingsView.vue     # 个人设置
```

---

### 4. 组织列表页 `/orgs`

**功能：**
- 显示用户所在的所有组织
- 创建新组织按钮
- 点击组织进入组织详情
- 显示角色（owner/admin/member）

**API 调用：**
- `GET /api/orgs` → 获取组织列表

**组件：**
```
src/views/org/
├── OrgListView.vue      # 组织列表
```

---

### 5. 组织详情页 `/orgs/:id`

**功能：**
- 组织名称、创建时间
- 成员列表（显示角色）
- 邀请新成员按钮
- 成员管理入口

**API 调用：**
- `GET /api/orgs/{id}` → 组织详情
- `PUT /api/orgs/{id}` → 更新组织
- `GET /api/orgs/{id}/members` → 成员列表
- `DELETE /api/orgs/{id}/members/{user_id}` → 移除成员

**组件：**
```
src/views/org/
├── OrgDetailView.vue     # 组织详情
```

---

### 6. 邀请接受页 `/invite/:token`

**功能：**
- 解析 token 显示邀请信息（哪个组织、什么角色）
- 确认接受邀请按钮
- 已接受/已过期状态处理
- 接受后跳转到组织详情页

**API 调用：**
- `GET /api/invitations/{token}` → 验证邀请
- `POST /api/invitations/{token}/accept` → 接受邀请

**组件：**
```
src/views/org/
└── InvitationView.vue    # 邀请接受
```

---

### 7. 成员管理页 `/orgs/:id/members`

**功能：**
- 成员列表（用户、角色、加入时间）
- 发送邀请按钮 → 弹窗（输入邮箱、选择角色）
- 撤销邀请按钮
- 移除成员按钮（owner/admin 可见）
- 当前用户角色显示

**API 调用：**
- `GET /api/orgs/{id}/members` → 成员列表
- `POST /api/orgs/{id}/invitations` → 发送邀请
- `DELETE /api/invitations/{id}` → 撤销邀请

**组件：**
```
src/views/org/
└── MemberManageView.vue  # 成员管理
```

---

## API 调用层

**文件位置：** `src/api/`

```
src/api/
├── index.ts              # axios 实例配置
├── auth.ts               # 认证 API
│   ├── login(data)       # POST /api/auth/login
│   ├── register(data)   # POST /api/auth/register
│   ├── getMe()          # GET /api/auth/me
│   ├── updateMe(data)   # PUT /api/auth/me
│   ├── logout()         # POST /api/auth/logout
│   └── refresh()         # POST /api/auth/refresh
├── users.ts              # 用户管理 API
│   ├── list(params)     # GET /api/users
│   ├── get(id)          # GET /api/users/{id}
│   ├── update(id, data) # PUT /api/users/{id}
│   ├── remove(id)       # DELETE /api/users/{id}
│   └── toggleActive(id) # PUT /api/users/{id}/toggle-active
└── orgs.ts              # 组织 + 邀请 API
    ├── list()           # GET /api/orgs
    ├── create(data)     # POST /api/orgs
    ├── get(id)          # GET /api/orgs/{id}
    ├── update(id, data) # PUT /api/orgs/{id}
    ├── remove(id)       # DELETE /api/orgs/{id}
    ├── members(id)      # GET /api/orgs/{id}/members
    ├── removeMember(orgId, userId)  # DELETE /api/orgs/{id}/members/{user_id}
    ├── sendInvitation(orgId, data)  # POST /api/orgs/{id}/invitations
    ├── verifyInvitation(token)     # GET /api/invitations/{token}
    ├── acceptInvitation(token)     # POST /api/invitations/{token}/accept
    └── revokeInvitation(invId)     # DELETE /api/invitations/{id}
```

**axios 实例配置要点：**
- baseURL: `/api`
- 自动携带 Cookie（`withCredentials: true`）
- 自动在请求头加 `Authorization: Bearer <token>`
- 响应拦截器：401 → 跳转登录页
- 响应格式统一：`res.data = { code, message, data }`

---

## 路由配置

```typescript
// src/router/index.ts
const routes = [
  { path: '/login', name: 'login', component: () => import('@/views/auth/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'register', component: () => import('@/views/auth/RegisterView.vue'), meta: { guest: true } },
  { path: '/settings', name: 'settings', component: () => import('@/views/settings/SettingsView.vue'), meta: { auth: true } },
  { path: '/orgs', name: 'org-list', component: () => import('@/views/org/OrgListView.vue'), meta: { auth: true } },
  { path: '/orgs/:id', name: 'org-detail', component: () => import('@/views/org/OrgDetailView.vue'), meta: { auth: true } },
  { path: '/orgs/:id/members', name: 'member-manage', component: () => import('@/views/org/MemberManageView.vue'), meta: { auth: true } },
  { path: '/invite/:token', name: 'invitation', component: () => import('@/views/org/InvitationView.vue'), meta: { guest: true } },
]
```

**路由守卫：**
- `meta.auth: true` → 未登录跳转 `/login`
- `meta.guest: true` → 已登录跳转 `/orgs`

---

## 状态管理（Pinia）

```typescript
// src/stores/auth.ts
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// src/stores/org.ts
interface OrgState {
  orgs: Organization[]
  currentOrg: Organization | null
  members: Member[]
}
```

---

## 公共组件

```
src/components/
├── auth/
│   └── AuthCard.vue      # 登录/注册卡片包装
├── layout/
│   ├── AppLayout.vue     # 主布局（侧边栏 + 顶部栏）
│   ├── Sidebar.vue       # 侧边栏
│   └── Topbar.vue        # 顶部栏
├── org/
│   ├── OrgCard.vue       # 组织卡片
│   ├── MemberList.vue    # 成员列表
│   └── InviteModal.vue   # 邀请弹窗
└── ui/
    ├── BaseButton.vue
    ├── BaseInput.vue
    ├── BaseModal.vue
    └── BaseTable.vue
```

---

## 开发规则（autodev）

**重要：每个页面完成后写测试！**

1. 使用 Vitest 做单元测试
2. 测试文件放在 `frontend/src/**/*.test.ts`
3. 每个 API 调用函数用 mock 验证参数
4. 每个页面组件写基本渲染测试
5. 代码和测试同时 commit

---

## 验收标准

- [ ] 7 个页面全部实现
- [ ] API 调用层完整（src/api/）
- [ ] 路由配置完成（含守卫）
- [ ] Pinia store 状态管理
- [ ] 深色主题 + 紫色主色调 UI
- [ ] Vitest 测试（每个页面至少一个测试）
- [ ] 代码和测试同时 commit
