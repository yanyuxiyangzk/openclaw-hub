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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = !!authStore.token

  if (to.meta.auth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.guest && isAuthenticated) {
    next('/orgs')
  } else {
    next()
  }
})

export default router
