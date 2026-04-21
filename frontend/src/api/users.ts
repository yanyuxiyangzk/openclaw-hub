import api from './index'
import type { ApiResponse, User, PaginatedData } from '@/types'

export const listUsers = (params?: { page?: number; page_size?: number }) =>
  api.get<ApiResponse<PaginatedData<User>>>('/users', { params })

export const getUser = (id: string) => api.get<ApiResponse<User>>(`/users/${id}`)

export const updateUser = (id: string, data: { name?: string; avatar?: string | null }) =>
  api.put<ApiResponse<User>>(`/users/${id}`, data)

export const deleteUser = (id: string) => api.delete<ApiResponse>(`/users/${id}`)

export const changePassword = (id: string, new_password: string) =>
  api.put<ApiResponse>(`/users/${id}/password`, { new_password })

export const toggleActive = (id: string, is_active: boolean) =>
  api.put<ApiResponse<{ id: string; is_active: boolean }>>(`/users/${id}/toggle-active`, { is_active })
