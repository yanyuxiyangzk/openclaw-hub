import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import MemberManageView from '../MemberManageView.vue'

vi.mock('@/stores/org', () => ({
  useOrgStore: vi.fn(() => ({
    fetchMembers: vi.fn(),
    removeMember: vi.fn(),
    inviteMember: vi.fn(),
    members: [],
  })),
}))

vi.mock('@/components/layout/AppLayout.vue', () => ({
  default: { template: '<div><slot /></div>' },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/orgs/:id/members', component: { template: '<div>Members</div>' } },
  ],
})

describe('MemberManageView', () => {
  it('renders members header with invite button', async () => {
    const wrapper = mount(MemberManageView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('h2').text()).toBe('成员管理')
    expect(wrapper.findAll('button').some(b => b.text() === '邀请成员')).toBe(true)
  })

  it('has back button', async () => {
    const wrapper = mount(MemberManageView, {
      global: { plugins: [router] },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.some(b => b.text() === '返回组织')).toBe(true)
  })
})
