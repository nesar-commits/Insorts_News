import { useCallback, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Newspaper, MapPin, RefreshCw } from 'lucide-react'
import { CategoryTabs } from '../components/CategoryTabs'
import { HeroCarousel } from '../components/HeroCarousel'
import { ArticleCard } from '../components/ArticleCard'
import { ArticleGridSkeleton } from '../components/ArticleCardSkeleton'
import { EmptyState } from '../components/EmptyState'
import { Spinner } from '../components/Spinner'
import { useInfiniteArticles } from '../hooks/useInfiniteArticles'
import { useInView } from '../hooks/useInView'
import { useGeolocation } from '../hooks/useGeolocation'
import { getBrowserLanguage } from '../utils/browserLanguage'
import { fetchTrendingArticles } from '../api/articles'

const REGION_NAMES = { GB: 'the UK', US: 'the US', QA: 'Qatar', IN: 'India' }
const LANGUAGE_NAMES = {
  hi: 'Hindi',
  bn: 'Bengali',
  ta: 'Tamil',
  te: 'Telugu',
  mr: 'Marathi',
  gu: 'Gujarati',
  pa: 'Punjabi',
  ur: 'Urdu',
  ne: 'Nepali',
  kn: 'Kannada',
  ml: 'Malayalam',
  or: 'Odia',
  en: 'English',
}

export function Feed() {
  const { slug = 'all' } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isForYou = slug === 'all'
  const coords = useGeolocation(isForYou)
  const lang = isForYou ? getBrowserLanguage() : undefined
  const [refreshing, setRefreshing] = useState(false)

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
    lang,
  })

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) fetchNextPage()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  const sentinelRef = useInView(loadMore, { enabled: hasNextPage })

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      // Reset rather than refetch — refetch would re-fetch every already
      // loaded page in place, but a "refresh" should collapse back down to
      // a fresh first page, same as a first visit.
      await queryClient.resetQueries({ queryKey: ['articles'] })
      if (isForYou) await queryClient.resetQueries({ queryKey: ['trending'] })
    } finally {
      setRefreshing(false)
    }
  }

  const articles = data?.pages.flatMap((p) => p.items) ?? []
  const matchedCity = data?.pages[0]?.city
  const matchedRegion = data?.pages[0]?.region
  const matchedLanguage = data?.pages[0]?.language
  const matchedPlace = matchedCity || (matchedRegion && (REGION_NAMES[matchedRegion] || matchedRegion))

  return (
    <div className="flex flex-col gap-6">
      {isForYou && trending?.length > 0 && <HeroCarousel articles={trending} />}

      <div className="flex items-center gap-2">
        <div className="min-w-0 flex-1">
          <CategoryTabs
            activeSlug={slug}
            onSelect={(newSlug) => navigate(newSlug === 'all' ? '/' : `/category/${newSlug}`)}
          />
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          disabled={refreshing}
          aria-label="Refresh"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-brand-300 hover:text-brand-700 disabled:opacity-50 dark:border-white/10 dark:text-gray-300 dark:hover:border-brand-500"
        >
          <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
        </button>
      </div>

      {isForYou && matchedPlace && (
        <p className="-mt-2 flex items-center gap-1.5 text-xs font-medium text-gray-500 dark:text-gray-400">
          <MapPin size={13} /> Showing news near you in {matchedPlace}
          {matchedLanguage && ` (${LANGUAGE_NAMES[matchedLanguage] || matchedLanguage})`}
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
