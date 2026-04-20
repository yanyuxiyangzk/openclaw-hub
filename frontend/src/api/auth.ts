import api from './index'

export const login = (data: { email: string; password: string }) =>
  api.post('/auth/login', data)

export const register = (data: { name: string; email: string; password: string }) =>
  api.post('/auth/register', data)

export const getMe = () => api.get('/auth/me')

export const updateMe = (data: { name?: string; email?: string }) =>
  api.put('/auth/me', data)

export const logout = () => api.post('/auth/logout')

export const refresh = () => api.post('/auth/refresh')
