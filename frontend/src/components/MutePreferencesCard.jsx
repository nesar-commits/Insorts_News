import { useQuery } from '@tanstack/react-query'
import { fetchCategories, fetchSources } from '../api/articles'
import { useMutePreferences } from '../hooks/useMutePreferences'

export function MutePreferencesCard() {
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: fetchCategories })
  const { data: sources } = useQuery({
    queryKey: ['sources'],
    queryFn: fetchSources,
    staleTime: 1000 * 60 * 10,
  })
  const { mutedSourceIds, mutedCategoryIds, toggleSource, toggleCategory } = useMutePreferences()

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-gray-100 bg-white p-4 dark:border-white/10 dark:bg-gray-900">
      <div>
        <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Muted categories</h2>
        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
          Hide a whole category from your feed and trending.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          {categories?.map((cat) => {
            const muted = mutedCategoryIds.has(cat.id)
            return (
              <button
                key={cat.id}
                type="button"
                onClick={() => toggleCategory(cat.id)}
                aria-pressed={muted}
                className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                  muted
                    ? 'border-accent-300 bg-accent-50 text-accent-700 dark:border-accent-500/40 dark:bg-accent-500/10 dark:text-accent-300'
                    : 'border-gray-200 text-gray-600 hover:border-brand-300 dark:border-white/10 dark:text-gray-300'
                }`}
              >
                {cat.name}
                {muted ? ' · Muted' : ''}
              </button>
            )
          })}
        </div>
      </div>

      <div>
        <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Muted sources</h2>
        <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">
          Not interested in a specific outlet? Hide it here.
        </p>
        <div className="mt-2 flex max-h-48 flex-col gap-0.5 overflow-y-auto">
          {sources?.map((source) => {
            const muted = mutedSourceIds.has(source.id)
            return (
              <button
                key={source.id}
                type="button"
                onClick={() => toggleSource(source.id)}
                aria-pressed={muted}
                className="flex items-center justify-between rounded-lg px-2 py-1.5 text-left text-sm transition hover:bg-gray-50 dark:hover:bg-white/5"
              >
                <span className={muted ? 'text-gray-400 line-through dark:text-gray-500' : 'text-gray-700 dark:text-gray-200'}>
                  {source.name}
                </span>
                <span
                  className={`text-xs font-medium ${
                    muted ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400 dark:text-gray-500'
                  }`}
                >
                  {muted ? 'Unmute' : 'Mute'}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
