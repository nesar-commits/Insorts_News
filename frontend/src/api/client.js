import axios from 'axios'

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
export const SESSION_EXPIRED_EVENT = 'insorts:session-expired'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('insorts_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const hadToken = !!localStorage.getItem('insorts_token')
      localStorage.removeItem('insorts_token')
      localStorage.removeItem('insorts_user')
      if (hadToken) {
        window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
      }
    }
    return Promise.reject(error)
  }
)
