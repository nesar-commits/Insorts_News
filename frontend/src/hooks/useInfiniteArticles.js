import { useInfiniteQuery } from '@tanstack/react-query'
import { fetchArticles } from '../api/articles'

export function useInfiniteArticles({ category, search, pageSize = 12, nearby = false, coords } = {}) {
  return useInfiniteQuery({
    queryKey: [
      'articles',
      { category: category || 'all', search: search || '', pageSize, nearby, coords: coords || null },
    ],
    queryFn: ({ pageParam }) => fetchArticles({ cursor: pageParam, pageSize, category, search, nearby, coords }),
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
    initialPageParam: undefined,
  })
}
