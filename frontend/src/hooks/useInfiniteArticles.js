import { useInfiniteQuery } from '@tanstack/react-query'
import { fetchArticles } from '../api/articles'

export function useInfiniteArticles({ category, search, pageSize = 12 } = {}) {
  return useInfiniteQuery({
    queryKey: ['articles', { category: category || 'all', search: search || '', pageSize }],
    queryFn: ({ pageParam = 1 }) => fetchArticles({ page: pageParam, pageSize, category, search }),
    getNextPageParam: (lastPage) => (lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined),
    initialPageParam: 1,
  })
}
