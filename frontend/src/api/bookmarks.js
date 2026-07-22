import { apiClient } from './client'

export async function fetchBookmarks({ page = 1, pageSize = 12 } = {}) {
  const { data } = await apiClient.get('/bookmarks', { params: { page, page_size: pageSize } })
  return data
}

export async function addBookmark(articleId) {
  const { data } = await apiClient.post('/bookmarks', { article_id: articleId })
  return data
}

export async function removeBookmark(articleId) {
  await apiClient.delete(`/bookmarks/${articleId}`)
}
