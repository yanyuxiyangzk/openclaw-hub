import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import OrgListView from '../OrgListView.vue'

vi.mock('@/stores/org', () => ({
  useOrgStore: vi.fn(() => ({
    fetchOrgs: vi.fn(),
    createOrg: vi.fn(),
    orgs: [],
  })),
}))

vi.mock('@/components/layout/AppLayout.vue', () => ({
  default: { template: '<div><slot /></div>' },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/orgs', component: { template: '<div>Orgs</div>' } },
  ],
})

describe('OrgListView', () => {
  it('renders org list header with create button', async () => {
    const wrapper = mount(OrgListView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('h2').text()).toBe('我的组织')
    expect(wrapper.find('button').text()).toBe('创建组织')
  })

  it('shows empty state when no orgs', async () => {
    const wrapper = mount(OrgListView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.text-gray-400').text()).toContain('暂无组织')
  })
})
