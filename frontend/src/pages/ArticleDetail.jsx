import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Bookmark, ExternalLink, ImageOff, Share2 } from 'lucide-react'
import { fetchArticle } from '../api/articles'
import { FullPageSpinner } from '../components/Spinner'
import { EmptyState } from '../components/EmptyState'
import { useToggleBookmark } from '../hooks/useToggleBookmark'
import { useShareArticle } from '../hooks/useShareArticle'
import { timeAgo } from '../utils/timeAgo'

export function ArticleDetail() {
  const { id } = useParams()
  const { toggle, isLoading: bookmarkLoading } = useToggleBookmark()
  const { share } = useShareArticle()

  const { data: article, isLoading, isError } = useQuery({
    queryKey: ['article', id],
    queryFn: () => fetchArticle(id),
  })

  if (isLoading) return <FullPageSpinner />

  if (isError || !article) {
    return (
      <EmptyState
        icon={ImageOff}
        title="Article not found"
        description="It may have been removed, or the link is invalid."
        action={
          <Link to="/" className="text-sm font-semibold text-brand-600 dark:text-brand-400">
            Back to feed
          </Link>
        }
      />
    )
  }

  return (
    <article className="mx-auto flex max-w-2xl flex-col gap-5">
      <Link
        to="/"
        className="flex w-fit items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-brand-600 dark:text-gray-400 dark:hover:text-brand-400"
      >
        <ArrowLeft size={16} /> Back
      </Link>

      {article.image_url && (
        <img
          src={article.image_url}
          alt=""
          className="aspect-[16/9] w-full rounded-2xl object-cover shadow-sm"
        />
      )}

      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-brand-700 dark:bg-brand-900/30 dark:text-brand-300">
          {article.category.name}
        </span>
        <span className="text-sm text-gray-400">
          {article.source.name} &middot; {timeAgo(article.published_at)}
        </span>
      </div>

      <h1 className="text-2xl font-bold leading-tight text-gray-900 dark:text-white sm:text-3xl">
        {article.title}
      </h1>

      {article.author && <p className="text-sm text-gray-500 dark:text-gray-400">By {article.author}</p>}

      {article.summary && (
        <p className="text-base leading-relaxed text-gray-700 dark:text-gray-300">{article.summary}</p>
      )}

      <div className="flex flex-wrap items-center gap-3 border-t border-gray-100 pt-5 dark:border-white/10">
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
        >
          Read full story <ExternalLink size={15} />
        </a>
        <button
          type="button"
          disabled={bookmarkLoading}
          onClick={() => toggle(article.id, article.is_bookmarked)}
          className="flex items-center gap-2 rounded-full border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:border-brand-300 hover:text-brand-700 disabled:opacity-60 dark:border-white/10 dark:text-gray-200"
        >
          <Bookmark size={15} className={article.is_bookmarked ? 'fill-accent-500 text-accent-500' : ''} />
          {article.is_bookmarked ? 'Saved' : 'Save'}
        </button>
        <button
          type="button"
          onClick={() => share(article)}
          className="flex items-center gap-2 rounded-full border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 transition hover:border-brand-300 hover:text-brand-700 dark:border-white/10 dark:text-gray-200"
        >
          <Share2 size={15} /> Share
        </button>
      </div>
    </article>
  )
}
