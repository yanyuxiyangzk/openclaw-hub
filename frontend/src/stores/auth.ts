import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { mockUser } from '@/utils/mock'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (email: string, _password: string) => {
    await new Promise(resolve => setTimeout(resolve, 500))
    token.value = 'mock-token-' + Date.now()
    user.value = { ...mockUser, email }
    localStorage.setItem('token', token.value)
  }

  const register = async (name: string, email: string, _password: string) => {
    await new Promise(resolve => setTimeout(resolve, 500))
    token.value = 'mock-token-' + Date.now()
    user.value = { id: '1', name, email }
    localStorage.setItem('token', token.value)
  }

  const logout = async () => {
    await new Promise(resolve => setTimeout(resolve, 200))
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  const fetchMe = async () => {
    await new Promise(resolve => setTimeout(resolve, 300))
    user.value = mockUser
  }

  const updateUser = async (payload: { name?: string; email?: string }) => {
    await new Promise(resolve => setTimeout(resolve, 300))
    if (user.value) {
      user.value = { ...user.value, ...payload }
    }
  }

  return { user, token, isAuthenticated, login, register, logout, fetchMe, updateUser }
})
