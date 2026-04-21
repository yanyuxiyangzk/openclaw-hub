import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../LoginView.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    login: vi.fn(),
    user: null,
    token: null,
    isAuthenticated: false,
  })),
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: { template: '<div>Login</div>' } },
    { path: '/orgs', component: { template: '<div>Orgs</div>' } },
  ],
})

describe('LoginView', () => {
  it('renders login form', async () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('h1').text()).toBe('OpenClawHub 登录')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toBe('登录')
  })

  it('shows register link', async () => {
    const wrapper = mount(LoginView, {
      global: { plugins: [router] },
    })
    expect(wrapper.find('a').text()).toBe('注册')
  })
})
