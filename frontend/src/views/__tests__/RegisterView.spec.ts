import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { setActivePinia, createPinia } from 'pinia'
import RegisterView from '../RegisterView.vue'

vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    register: vi.fn().mockResolvedValue({}),
  })),
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/register', component: { template: '<div>Register</div>' } },
    { path: '/orgs', component: { template: '<div>Orgs</div>' } },
  ],
})

describe('RegisterView', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders registration form', async () => {
    const wrapper = mount(RegisterView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.findAll('input').length).toBe(4)
  })

  it('has submit button', async () => {
    const wrapper = mount(RegisterView, {
      global: { plugins: [router] },
    })
    await flushPromises()
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })
})
