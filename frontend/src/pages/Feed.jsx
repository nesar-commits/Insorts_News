import { useCallback } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Newspaper, MapPin } from 'lucide-react'
import { CategoryTabs } from '../components/CategoryTabs'
import { HeroCarousel } from '../components/HeroCarousel'
import { ArticleCard } from '../components/ArticleCard'
import { ArticleGridSkeleton } from '../components/ArticleCardSkeleton'
import { EmptyState } from '../components/EmptyState'
import { Spinner } from '../components/Spinner'
import { useInfiniteArticles } from '../hooks/useInfiniteArticles'
import { useInView } from '../hooks/useInView'
import { useGeolocation } from '../hooks/useGeolocation'
import { fetchTrendingArticles } from '../api/articles'

const REGION_NAMES = { GB: 'the UK', US: 'the US', QA: 'Qatar' }

export function Feed() {
  const { slug = 'all' } = useParams()
  const navigate = useNavigate()
  const isForYou = slug === 'all'
  const coords = useGeolocation(isForYou)

  const { data: trending } = useQuery({
    queryKey: ['trending'],
    queryFn: () => fetchTrendingArticles(6),
    enabled: isForYou,
    staleTime: 1000 * 60 * 5,
  })

  const { data, isLoading, isError, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteArticles({
    category: slug,
    nearby: isForYou,
    coords: isForYou ? coords : undefined,
  })

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) fetchNextPage()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const sentinelRef = useInView(loadMore, { enabled: hasNextPage })

  const articles = data?.pages.flatMap((p) => p.items) ?? []
  const matchedRegion = data?.pages[0]?.region

  return (
    <div className="flex flex-col gap-6">
      {isForYou && trending?.length > 0 && <HeroCarousel articles={trending} />}

      <CategoryTabs
        activeSlug={slug}
        onSelect={(newSlug) => navigate(newSlug === 'all' ? '/' : `/category/${newSlug}`)}
      />

      {isForYou && matchedRegion && (
        <p className="-mt-2 flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400">
          <MapPin size={13} /> Showing news near you in {REGION_NAMES[matchedRegion] || matchedRegion}
        </p>
      )}

      {isLoading && <ArticleGridSkeleton count={9} />}

      {isError && (
        <EmptyState
          icon={Newspaper}
          title="Couldn't load the news"
          description="Check your connection and try again in a moment."
        />
      )}

      {!isLoading && !isError && articles.length === 0 && (
        <EmptyState
          icon={Newspaper}
          title="No articles yet"
          description="This category hasn't been ingested yet. Try again shortly."
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
