import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import InvitationView from '../InvitationView.vue'

vi.mock('@/stores/org', () => ({
  useOrgStore: vi.fn(() => ({
    checkInvitation: vi.fn().mockResolvedValue({ orgName: 'Test Org' }),
    acceptInvite: vi.fn().mockResolvedValue({}),
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
    router.push('/invite/test-token')
    await router.isReady()
    const wrapper = mount(InvitationView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('加入组织')
  })

  it('has accept button', async () => {
    router.push('/invite/test-token')
    await router.isReady()
    const wrapper = mount(InvitationView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.find('button').text()).toBe('接受邀请')
  })
})
