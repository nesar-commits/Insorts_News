import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { timeAgo } from '../utils/timeAgo'
import { getCategoryIcon } from '../utils/categoryIcons'

export function HeroCarousel({ articles }) {
  const [index, setIndex] = useState(0)
  const timerRef = useRef(null)

  const goTo = useCallback(
    (i) => {
      if (!articles.length) return
      setIndex(((i % articles.length) + articles.length) % articles.length)
    },
    [articles.length]
  )

  useEffect(() => {
    if (!articles.length) return
    timerRef.current = setInterval(() => goTo(index + 1), 6000)
    return () => clearInterval(timerRef.current)
  }, [index, goTo, articles.length])

  if (!articles.length) return null

  // `articles` can shrink out from under an already-mounted carousel (e.g.
  // any bookmark toggle anywhere in the app invalidates the ['trending']
  // query, refetching it live) while `index` still points past the new
  // end — clamp defensively rather than indexing straight into a
  // shorter array and crashing on `article.category` below.
  const safeIndex = Math.min(index, articles.length - 1)
  const article = articles[safeIndex]

  return (
    <div className="relative overflow-hidden rounded-3xl bg-gray-900 shadow-lg">
      <Link to={`/article/${article.id}`} className="block">
        <div className="relative aspect-[16/9] w-full sm:aspect-[21/9]">
          <CarouselImage key={article.id} article={article} />
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
          <div className="absolute inset-x-0 bottom-0 p-5 sm:p-8">
            <span className="mb-2 inline-block rounded-full bg-accent-600 px-3 py-1 text-xs font-bold uppercase tracking-wide text-white">
              Trending &middot; {article.category.name}
            </span>
            <h2 className="max-w-2xl text-lg font-bold leading-snug text-white sm:text-2xl md:text-3xl">
              {article.title}
            </h2>
            <p className="mt-2 text-xs font-medium text-gray-300 sm:text-sm">
              {article.source.name} &middot; {timeAgo(article.published_at)}
            </p>
          </div>
        </div>
      </Link>

      <button
        type="button"
        onClick={() => goTo(safeIndex - 1)}
        aria-label="Previous"
        className="absolute left-2 top-1/2 hidden h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-sm transition hover:bg-black/60 sm:flex"
      >
        <ChevronLeft size={20} />
      </button>
      <button
        type="button"
        onClick={() => goTo(safeIndex + 1)}
        aria-label="Next"
        className="absolute right-2 top-1/2 hidden h-9 w-9 -translate-y-1/2 items-center justify-center rounded-full bg-black/40 text-white backdrop-blur-sm transition hover:bg-black/60 sm:flex"
      >
        <ChevronRight size={20} />
      </button>

      <div className="absolute bottom-3 right-4 flex gap-1.5 sm:right-6">
        {articles.map((_, i) => (
          <button
            key={i}
            type="button"
            aria-label={`Go to slide ${i + 1}`}
            onClick={() => goTo(i)}
            className={`h-1.5 rounded-full transition-all ${
              i === safeIndex ? 'w-6 bg-white' : 'w-1.5 bg-white/40'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

function CarouselImage({ article }) {
  const [imgError, setImgError] = useState(false)
  const Icon = getCategoryIcon(article.category.icon)

  if (article.image_url && !imgError) {
    return (
      <img
        src={article.image_url}
        alt=""
        className="h-full w-full object-cover opacity-80"
        onError={() => setImgError(true)}
      />
    )
  }

  return (
    <div className="flex h-full w-full items-start justify-end bg-gradient-to-br from-brand-800 to-gray-900 p-5 text-brand-400/40 sm:p-8">
      <Icon size={40} className="sm:h-14 sm:w-14" />
    </div>
  )
}

