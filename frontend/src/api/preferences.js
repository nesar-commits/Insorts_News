import { apiClient } from './client'

export async function fetchMutedPreferences() {
  const { data } = await apiClient.get('/users/me/muted')
  return data
}

export async function muteSource(sourceId) {
  await apiClient.post(`/users/me/muted-sources/${sourceId}`)
}

export async function unmuteSource(sourceId) {
  await apiClient.delete(`/users/me/muted-sources/${sourceId}`)
}

export async function muteCategory(categoryId) {
  await apiClient.post(`/users/me/muted-categories/${categoryId}`)
}

export async function unmuteCategory(categoryId) {
  await apiClient.delete(`/users/me/muted-categories/${categoryId}`)
}
