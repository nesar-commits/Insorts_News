import { useCallback } from 'react'
import { Bookmark } from 'lucide-react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { fetchBookmarks } from '../api/bookmarks'
import { ArticleCard } from '../components/ArticleCard'
import { ArticleGridSkeleton } from '../components/ArticleCardSkeleton'
import { EmptyState } from '../components/EmptyState'
import { Spinner } from '../components/Spinner'
import { useInView } from '../hooks/useInView'

export function Bookmarks() {
  const { data, isLoading, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['bookmarks'],
    queryFn: ({ pageParam = 1 }) => fetchBookmarks({ page: pageParam }),
    getNextPageParam: (lastPage) => (lastPage.page < lastPage.total_pages ? lastPage.page + 1 : undefined),
    initialPageParam: 1,
  })

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) fetchNextPage()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const sentinelRef = useInView(loadMore, { enabled: hasNextPage })

  const articles = data?.pages.flatMap((p) => p.items) ?? []

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Saved Articles</h1>

      {isLoading && <ArticleGridSkeleton count={6} />}

      {!isLoading && articles.length === 0 && (
        <EmptyState
          icon={Bookmark}
          title="No saved articles yet"
          description="Tap the bookmark icon on any story to save it here for later."
        />
      )}

      {articles.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      <div ref={sentinelRef} className="flex justify-center py-4">
        {isFetchingNextPage && <Spinner />}
      </div>
    </div>
  )
}
