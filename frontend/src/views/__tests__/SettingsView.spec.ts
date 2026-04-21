import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import SettingsView from '../SettingsView.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    fetchMe: vi.fn(),
    updateUser: vi.fn(),
    logout: vi.fn(),
    user: { id: '1', name: 'Test', email: 'test@example.com', avatar: null },
  })),
}))

vi.mock('@/components/layout/AppLayout.vue', () => ({
  default: { template: '<div><slot /></div>' },
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/settings', component: { template: '<div>Settings</div>' } },
    { path: '/login', component: { template: '<div>Login</div>' } },
  ],
})

describe('SettingsView', () => {
  it('renders settings form', async () => {
    const wrapper = mount(SettingsView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('h2').text()).toBe('个人设置')
    expect(wrapper.findAll('input').length).toBe(3)
  })

  it('has logout button', async () => {
    const wrapper = mount(SettingsView, {
      global: { plugins: [router] },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.some(b => b.text() === '退出登录')).toBe(true)
  })
})
