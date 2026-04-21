import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password })
    const { access_token, refresh_token } = res.data.data
    token.value = access_token
    localStorage.setItem('token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    const meRes = await authApi.getMe()
    user.value = meRes.data.data
  }

  const register = async (name: string, email: string, password: string) => {
    const res = await authApi.register({ name, email, password })
    user.value = res.data.data
    const loginRes = await authApi.login({ email, password })
    const { access_token, refresh_token } = loginRes.data.data
    token.value = access_token
    localStorage.setItem('token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    }
  }

  const fetchMe = async () => {
    const res = await authApi.getMe()
    user.value = res.data.data
  }

  const updateUser = async (payload: { name?: string; avatar?: string | null }) => {
    const res = await authApi.updateMe(payload)
    user.value = res.data.data
  }

  return { user, token, isAuthenticated, login, register, logout, fetchMe, updateUser }
})
