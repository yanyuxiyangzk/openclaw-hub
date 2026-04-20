import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import InvitationView from '../InvitationView.vue'

vi.mock('@/stores/org', () => ({
  useOrgStore: vi.fn(() => ({
    checkInvitation: vi.fn(),
    acceptInvite: vi.fn(),
  })),
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/invite/:token', component: { template: '<div>Invite</div>' } },
    { path: '/orgs', component: { template: '<div>Orgs</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
  ],
})

describe('InvitationView', () => {
  it('renders invitation form', async () => {
    const wrapper = mount(InvitationView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('h1').text()).toBe('加入组织')
  })

  it('has accept button', async () => {
    const wrapper = mount(InvitationView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('button').text()).toBe('接受邀请')
  })
})
