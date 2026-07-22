import { apiClient } from './client'

export async function registerUser({ email, username, password, fullName }) {
  const { data } = await apiClient.post('/auth/register', {
    email,
    username,
    password,
    full_name: fullName || null,
  })
  return data
}

export async function loginUser({ email, password }) {
  const { data } = await apiClient.post('/auth/login', { email, password })
  return data
}

export async function fetchCurrentUser() {
  const { data } = await apiClient.get('/users/me')
  return data
}
