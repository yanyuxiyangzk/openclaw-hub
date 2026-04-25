import axios from 'axios'
import router from '@/router'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res && res.code !== undefined && res.code !== 0) {
      return Promise.reject(new Error(res.message || 'Request failed'))
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config
    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || originalRequest.url?.includes('/auth/register')
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const res = await api.post('/auth/refresh', { refresh_token: refreshToken })
          const { access_token, refresh_token: new_refresh } = res.data.data
          localStorage.setItem('token', access_token)
          localStorage.setItem('refresh_token', new_refresh)
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('token')
          localStorage.removeItem('refresh_token')
          router.push('/login')
        }
      } else {
        localStorage.removeItem('token')
        router.push('/login')
      }
    }
    return Promise.reject(error)
  }
)

export default api
