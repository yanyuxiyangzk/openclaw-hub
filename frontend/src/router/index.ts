import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/orgs'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { guest: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue'),
    meta: { auth: true }
  },
  {
    path: '/orgs',
    name: 'OrgList',
    component: () => import('@/views/OrgListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/orgs/:id',
    name: 'OrgDetail',
    component: () => import('@/views/OrgDetailView.vue'),
    meta: { auth: true }
  },
  {
    path: '/orgs/:id/members',
    name: 'MemberManage',
    component: () => import('@/views/MemberManageView.vue'),
    meta: { auth: true }
  },
  {
    path: '/invite/:token',
    name: 'Invitation',
    component: () => import('@/views/InvitationView.vue'),
    meta: { guest: true }
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: () => import('@/views/projects/ProjectListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: () => import('@/views/projects/ProjectDetailView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agents',
    name: 'AgentList',
    component: () => import('@/views/agents/AgentListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agents/:id',
    name: 'AgentDetail',
    component: () => import('@/views/agents/AgentDetailView.vue'),
    meta: { auth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (!authStore.isInitialized) {
    next()
    return
  }

  if (to.meta.auth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && authStore.isAuthenticated) {
    next('/orgs')
  } else {
    next()
  }
})

export default router
