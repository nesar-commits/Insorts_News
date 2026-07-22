export function ArticleCardSkeleton() {
  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white dark:border-white/10 dark:bg-gray-900">
      <div className="skeleton aspect-[16/10] w-full bg-gray-100 dark:bg-white/5" />
      <div className="flex flex-col gap-3 p-4">
        <div className="skeleton h-3 w-24 rounded bg-gray-100 dark:bg-white/5" />
        <div className="skeleton h-4 w-full rounded bg-gray-100 dark:bg-white/5" />
        <div className="skeleton h-4 w-2/3 rounded bg-gray-100 dark:bg-white/5" />
      </div>
    </div>
  )
}

export function ArticleGridSkeleton({ count = 6 }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <ArticleCardSkeleton key={i} />
      ))}
    </div>
  )
}
