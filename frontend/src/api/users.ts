import api from './index'

export const listUsers = (params?: { page?: number; pageSize?: number }) =>
  api.get('/users', { params })

export const getUser = (id: string) => api.get(`/users/${id}`)

export const updateUser = (id: string, data: { name?: string; email?: string }) =>
  api.put(`/users/${id}`, data)

export const deleteUser = (id: string) => api.delete(`/users/${id}`)

export const toggleActive = (id: string) => api.put(`/users/${id}/toggle-active`)
