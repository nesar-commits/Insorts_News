import { apiClient } from './client'

export async function fetchArticles({ cursor, pageSize = 12, category, search, nearby, coords } = {}) {
  const { data } = await apiClient.get('/articles', {
    params: {
      cursor,
      page_size: pageSize,
      category: category && category !== 'all' ? category : undefined,
      search: search || undefined,
      nearby: nearby || undefined,
      lat: coords?.lat,
      lon: coords?.lon,
    },
  })
  return data
}

export async function fetchTrendingArticles(limit = 8) {
  const { data } = await apiClient.get('/articles/trending', { params: { limit } })
  return data
}

export async function fetchArticle(id) {
  const { data } = await apiClient.get(`/articles/${id}`)
  return data
}

export async function fetchCategories() {
  const { data } = await apiClient.get('/categories')
  return data
}
