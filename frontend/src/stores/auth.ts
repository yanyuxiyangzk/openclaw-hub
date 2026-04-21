import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '@/api/auth'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = computed(() => !!token.value)
  const isInitialized = ref(false)

  const initialize = async () => {
    if (!token.value) {
      isInitialized.value = true
      return
    }
    try {
      const res = await authApi.getMe()
      user.value = res.data.data
    } catch {
      token.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('refresh_token')
    } finally {
      isInitialized.value = true
    }
  }

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password })
    const { access_token, refresh_token, user: userData } = res.data.data
    token.value = access_token
    localStorage.setItem('token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    if (userData) {
      user.value = userData
    } else {
      const meRes = await authApi.getMe()
      user.value = meRes.data.data
    }
  }

  const register = async (name: string, email: string, password: string) => {
    const res = await authApi.register({ name, email, password })
    const { access_token, refresh_token, user: userData } = res.data.data
    token.value = access_token
    localStorage.setItem('token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    user.value = userData
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

  return { user, token, isAuthenticated, isInitialized, login, register, logout, fetchMe, updateUser, initialize }
})
