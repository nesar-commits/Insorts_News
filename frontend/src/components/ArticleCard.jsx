import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bookmark } from 'lucide-react'
import { timeAgo } from '../utils/timeAgo'
import { useToggleBookmark } from '../hooks/useToggleBookmark'
import { getCategoryIcon } from '../utils/categoryIcons'
import { getCategoryGradient } from '../utils/categoryTheme'

export function ArticleCard({ article, variant = 'default' }) {
  const { toggle, isLoading } = useToggleBookmark()

  const handleBookmarkClick = (e) => {
    e.preventDefault()
    e.stopPropagation()
    toggle(article.id, article.is_bookmarked)
  }

  if (variant === 'horizontal') {
    return (
      <Link
        to={`/article/${article.id}`}
        className="group flex gap-3 rounded-2xl p-2 transition hover:bg-gray-100 dark:hover:bg-white/5"
      >
        <div className="h-20 w-24 shrink-0 overflow-hidden rounded-xl bg-gray-100 dark:bg-white/5 sm:h-24 sm:w-32">
          <ArticleImage article={article} />
        </div>
        <div className="flex min-w-0 flex-1 flex-col justify-center">
          <div className="mb-1 flex items-center gap-1.5 text-xs font-medium text-brand-600 dark:text-brand-400">
            <span className="truncate">{article.source.name}</span>
            <span className="text-gray-300 dark:text-gray-600">&middot;</span>
            <span className="shrink-0 text-gray-400 dark:text-gray-500">{timeAgo(article.published_at)}</span>
          </div>
          <h3 className="line-clamp-2 text-sm font-semibold text-gray-900 group-hover:text-brand-700 dark:text-gray-100 dark:group-hover:text-brand-300 sm:text-base">
            {article.title}
          </h3>
        </div>
      </Link>
    )
  }

  return (
    <Link
      to={`/article/${article.id}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-white/10 dark:bg-gray-900"
    >
      <div className="relative aspect-[16/10] w-full overflow-hidden bg-gray-100 dark:bg-white/5">
        <ArticleImage article={article} className="transition duration-300 group-hover:scale-105" />
        <span className="absolute left-3 top-3 rounded-full bg-black/60 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-white backdrop-blur-sm">
          {article.category.name}
        </span>
        <button
          type="button"
          onClick={handleBookmarkClick}
          disabled={isLoading}
          aria-label={article.is_bookmarked ? 'Remove bookmark' : 'Save article'}
          className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-full bg-black/50 text-white backdrop-blur-sm transition hover:bg-black/70 disabled:opacity-60"
        >
          <Bookmark size={16} className={article.is_bookmarked ? 'fill-accent-500 text-accent-500' : ''} />
        </button>
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center gap-1.5 text-xs font-medium text-brand-600 dark:text-brand-400">
          <span className="truncate">{article.source.name}</span>
          <span className="text-gray-300 dark:text-gray-600">&middot;</span>
          <span className="shrink-0 text-gray-400 dark:text-gray-500">{timeAgo(article.published_at)}</span>
        </div>
        <h3 className="line-clamp-2 text-base font-semibold leading-snug text-gray-900 group-hover:text-brand-700 dark:text-gray-100 dark:group-hover:text-brand-300">
          {article.title}
        </h3>
        {article.summary && (
          <p className="line-clamp-2 text-sm text-gray-500 dark:text-gray-400">{article.summary}</p>
        )}
      </div>
    </Link>
  )
}

function ArticleImage({ article, className = '' }) {
  const [errored, setErrored] = useState(false)

  if (!article.image_url || errored) {
    const Icon = getCategoryIcon(article.category.icon)
    const gradient = getCategoryGradient(article.category.slug)
    return (
      <div className={`relative flex h-full w-full items-center justify-center overflow-hidden bg-gradient-to-br ${gradient}`}>
        <Icon size={40} className="text-white/25" />
        <span className="absolute bottom-2 left-3 text-xs font-semibold text-white/70">{article.source.name}</span>
      </div>
    )
  }

  return (
    <img
      src={article.image_url}
      alt=""
      loading="lazy"
      onError={() => setErrored(true)}
      className={`h-full w-full object-cover ${className}`}
    />
  )
}
