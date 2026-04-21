import api from './index'
import type { ApiResponse, User } from '@/types'

export const login = (data: { email: string; password: string }) =>
  api.post<ApiResponse<{ access_token: string; refresh_token: string }>>('/auth/login', data)

export const register = (data: { name: string; email: string; password: string }) =>
  api.post<ApiResponse<User>>('/auth/register', data)

export const getMe = () => api.get<ApiResponse<User>>('/auth/me')

export const updateMe = (data: { name?: string; avatar?: string | null }) =>
  api.put<ApiResponse<User>>('/auth/me', data)

export const logout = () => api.post<ApiResponse>('/auth/logout')

export const refreshToken = (refresh_token: string) =>
  api.post<ApiResponse<{ access_token: string; refresh_token: string }>>('/auth/refresh', { refresh_token })
