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
  },
  {
    path: '/agents/:id/config',
    name: 'AgentConfig',
    component: () => import('@/views/agents/AgentConfigView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agents/:id/memory',
    name: 'AgentMemory',
    component: () => import('@/views/agents/AgentMemoryView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agents/:id/metrics',
    name: 'AgentMetrics',
    component: () => import('@/views/agents/AgentMetricsView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agent-roles',
    name: 'AgentRoleList',
    component: () => import('@/views/agents/AgentRoleListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/agent-roles/new',
    name: 'AgentRoleCreate',
    component: () => import('@/views/agents/AgentRoleCreateView.vue'),
    meta: { auth: true }
  },
  {
    path: '/projects/:id/kanban',
    name: 'ProjectKanban',
    component: () => import('@/views/tasks/ProjectKanbanView.vue'),
    meta: { auth: true }
  },
  {
    path: '/projects/:id/tasks',
    name: 'ProjectTaskList',
    component: () => import('@/views/tasks/ProjectTaskListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/projects/:id/timeline',
    name: 'ProjectTimeline',
    component: () => import('@/views/tasks/ProjectTimelineView.vue'),
    meta: { auth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: () => import('@/views/tasks/TaskDetailView.vue'),
    meta: { auth: true }
  },
  {
    path: '/tasks/due-soon',
    name: 'DueSoon',
    component: () => import('@/views/tasks/DueSoonView.vue'),
    meta: { auth: true }
  },
  {
    path: '/executions',
    name: 'ExecutionList',
    component: () => import('@/views/executions/ExecutionListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/executions/:id',
    name: 'ExecutionDetail',
    component: () => import('@/views/executions/ExecutionDetailView.vue'),
    meta: { auth: true }
  },
  {
    path: '/scheduler',
    name: 'Scheduler',
    component: () => import('@/views/scheduler/SchedulerView.vue'),
    meta: { auth: true }
  },
  {
    path: '/workflows',
    name: 'WorkflowList',
    component: () => import('@/views/workflows/WorkflowListView.vue'),
    meta: { auth: true }
  },
  {
    path: '/workflows/:id',
    name: 'WorkflowDetail',
    component: () => import('@/views/workflows/WorkflowDetailView.vue'),
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
