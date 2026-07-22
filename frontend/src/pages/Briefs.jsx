import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Bookmark, ExternalLink, Share2, Zap } from 'lucide-react'
import { useInfiniteArticles } from '../hooks/useInfiniteArticles'
import { useInView } from '../hooks/useInView'
import { useToggleBookmark } from '../hooks/useToggleBookmark'
import { useShareArticle } from '../hooks/useShareArticle'
import { getCategoryIcon } from '../utils/categoryIcons'
import { getCategoryGradient } from '../utils/categoryTheme'
import { timeAgo } from '../utils/timeAgo'
import { EmptyState } from '../components/EmptyState'
import { Spinner } from '../components/Spinner'

export function Briefs() {
  const { data, isLoading, isError, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteArticles({
    pageSize: 10,
  })

  const loadMore = useCallback(() => {
    if (hasNextPage && !isFetchingNextPage) fetchNextPage()
  }, [hasNextPage, isFetchingNextPage, fetchNextPage])

  // Large rootMargin so the next page starts loading a slide or two before the
  // user actually reaches the end — full-screen slides are tall, a small margin
  // wouldn't give the fetch enough time to land before the sentinel is visible.
  const sentinelRef = useInView(loadMore, { enabled: hasNextPage, rootMargin: '1000px' })

  const articles = data?.pages.flatMap((p) => p.items) ?? []

  return (
    <div className="fixed inset-0 z-50 bg-black">
      <Link
        to="/"
        aria-label="Back to feed"
        className="safe-top fixed left-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-sm transition hover:bg-black/60"
      >
        <ArrowLeft size={20} />
      </Link>

      {isLoading && (
        <div className="flex h-full w-full items-center justify-center">
          <Spinner size={28} className="!text-white" />
        </div>
      )}

      {!isLoading && isError && (
        <div className="flex h-full w-full items-center justify-center px-8">
          <EmptyState
            icon={Zap}
            title="Couldn't load Briefs"
            description="Check your connection and try again."
          />
        </div>
      )}

      {!isLoading && !isError && articles.length === 0 && (
        <div className="flex h-full w-full items-center justify-center px-8 text-center text-white/70">
          No articles to show right now.
        </div>
      )}

      {articles.length > 0 && (
        <div className="scrollbar-none h-dvh w-full snap-y snap-mandatory overflow-y-scroll scroll-smooth">
          {articles.map((article) => (
            <BriefSlide key={article.id} article={article} />
          ))}

          <div ref={sentinelRef} className="flex h-dvh w-full snap-start items-center justify-center">
            {isFetchingNextPage && <Spinner size={24} className="!text-white" />}
          </div>
        </div>
      )}
    </div>
  )
}

function BriefSlide({ article }) {
  const [imgError, setImgError] = useState(false)
  const { toggle, isLoading: bookmarkLoading } = useToggleBookmark()
  const { share } = useShareArticle()
  const Icon = getCategoryIcon(article.category.icon)
  const gradient = getCategoryGradient(article.category.slug)

  const withStop = (fn) => (e) => {
    e.preventDefault()
    e.stopPropagation()
    fn()
  }

  return (
    <section className="relative flex h-dvh w-full snap-start snap-always items-end overflow-hidden">
      <Link to={`/article/${article.id}`} className="absolute inset-0">
        {article.image_url && !imgError ? (
          <img
            src={article.image_url}
            alt=""
            loading="lazy"
            onError={() => setImgError(true)}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className={`flex h-full w-full items-center justify-center bg-gradient-to-br ${gradient}`}>
            <Icon size={72} className="text-white/20" />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/95 via-black/25 to-black/40" />
      </Link>

      <div className="safe-bottom relative flex w-full items-end justify-between gap-3 p-5 pb-12">
        <Link to={`/article/${article.id}`} className="flex min-w-0 flex-1 flex-col gap-2">
          <span className="w-fit rounded-full bg-white/15 px-3 py-1 text-xs font-bold uppercase tracking-wide text-white backdrop-blur-sm">
            {article.category.name}
          </span>
          <h2 className="line-clamp-3 text-xl font-bold leading-snug text-white">{article.title}</h2>
          {article.summary && (
            <p className="line-clamp-2 text-sm text-white/80">{article.summary}</p>
          )}
          <p className="text-xs font-medium text-white/60">
            {article.source.name} &middot; {timeAgo(article.published_at)}
          </p>
        </Link>

        <div className="flex shrink-0 flex-col items-center gap-5">
          <button
            type="button"
            onClick={withStop(() => toggle(article.id, article.is_bookmarked))}
            disabled={bookmarkLoading}
            aria-label={article.is_bookmarked ? 'Remove bookmark' : 'Save article'}
            className="flex flex-col items-center gap-1 text-white disabled:opacity-60"
          >
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/15 backdrop-blur-sm">
              <Bookmark size={22} className={article.is_bookmarked ? 'fill-accent-500 text-accent-500' : ''} />
            </span>
            <span className="text-[11px] font-medium">{article.is_bookmarked ? 'Saved' : 'Save'}</span>
          </button>

          <button
            type="button"
            onClick={withStop(() => share(article))}
            aria-label="Share article"
            className="flex flex-col items-center gap-1 text-white"
          >
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/15 backdrop-blur-sm">
              <Share2 size={20} />
            </span>
            <span className="text-[11px] font-medium">Share</span>
          </button>

          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            aria-label="Open original article"
            className="flex flex-col items-center gap-1 text-white"
          >
            <span className="flex h-12 w-12 items-center justify-center rounded-full bg-white/15 backdrop-blur-sm">
              <ExternalLink size={20} />
            </span>
            <span className="text-[11px] font-medium">Visit</span>
          </a>
        </div>
      </div>
    </section>
  )
}
