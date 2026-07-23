import { useCallback, useEffect, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search as SearchIcon, X } from 'lucide-react'
import { ArticleCard } from '../components/ArticleCard'
import { ArticleGridSkeleton } from '../components/ArticleCardSkeleton'
import { EmptyState } from '../components/EmptyState'
import { Spinner } from '../components/Spinner'
import { useDebounce } from '../hooks/useDebounce'
import { useInfiniteArticles } from '../hooks/useInfiniteArticles'
import { useInView } from '../hooks/useInView'

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const debouncedQuery = useDebounce(query, 400)
  const lastPushedQuery = useRef(debouncedQuery)

  useEffect(() => {
    lastPushedQuery.current = debouncedQuery
    if (debouncedQuery) {
      setSearchParams({ q: debouncedQuery }, { replace: true })
    } else {
      setSearchParams({}, { replace: true })
    }
  }, [debouncedQuery, setSearchParams])

  // Someone navigated to /search?q=... while this page was already mounted
  // (e.g. the NavBar's desktop search box) — resync from the URL instead of
  // silently keeping the stale query/results.
  useEffect(() => {
    const urlQuery = searchParams.get('q') || ''
    if (urlQuery !== lastPushedQuery.current) {
      setQuery(urlQuery)
    }
  }, [searchParams])

  const { data, isLoading, isFetching, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteArticles({
    search: debouncedQuery,
  })

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) fetchNextPage()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const sentinelRef = useInView(loadMore, { enabled: !!debouncedQuery && hasNextPage })

  const articles = debouncedQuery ? data?.pages.flatMap((p) => p.items) ?? [] : []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-2 rounded-full border border-gray-200 bg-white px-4 py-3 shadow-sm focus-within:border-brand-400 dark:border-white/10 dark:bg-gray-900">
        <SearchIcon size={18} className="shrink-0 text-gray-400" />
        <input
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search news, topics, sources..."
          className="w-full bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-400 dark:text-gray-100"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            aria-label="Clear search"
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >
            <X size={16} />
          </button>
        )}
        {isFetching && !isFetchingNextPage && <Spinner size={16} />}
      </div>

      {!debouncedQuery && (
        <EmptyState
          icon={SearchIcon}
          title="Find what matters to you"
          description="Search across every headline, source and topic in Insorts News."
        />
      )}

      {debouncedQuery && isLoading && <ArticleGridSkeleton count={6} />}

      {debouncedQuery && !isLoading && articles.length === 0 && (
        <EmptyState
          icon={SearchIcon}
          title={`No results for "${debouncedQuery}"`}
          description="Try a different keyword, source name, or topic."
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
