import { useInfiniteQuery } from '@tanstack/react-query'
import { fetchArticles } from '../api/articles'

export function useInfiniteArticles({ category, search, pageSize = 12 } = {}) {
  return useInfiniteQuery({
    queryKey: ['articles', { category: category || 'all', search: search || '', pageSize }],
    queryFn: ({ pageParam }) => fetchArticles({ cursor: pageParam, pageSize, category, search }),
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
    initialPageParam: undefined,
  })
}
