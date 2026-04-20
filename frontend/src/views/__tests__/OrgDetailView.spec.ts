import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import OrgDetailView from '../OrgDetailView.vue'

vi.mock('@/stores/org', () => ({
  useOrgStore: vi.fn(() => ({
    fetchOrg: vi.fn(),
    updateOrg: vi.fn(),
    currentOrg: null,
  })),
}))

vi.mock('@/components/layout/AppLayout.vue', () => ({
  default: { template: '<div><slot /></div>' },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/orgs/:id', component: { template: '<div>OrgDetail</div>' } },
  ],
})

describe('OrgDetailView', () => {
  it('renders org detail header', async () => {
    const wrapper = mount(OrgDetailView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('.flex.items-center').exists()).toBe(true)
  })

  it('has edit and members buttons', async () => {
    const wrapper = mount(OrgDetailView, {
      global: { plugins: [router] },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.some(b => b.text() === '编辑组织')).toBe(true)
    expect(buttons.some(b => b.text() === '成员管理')).toBe(true)
  })
})
