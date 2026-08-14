import { useQuery } from '@tanstack/react-query'
import { fetchCategories } from '../api/articles'

const pillClass = (selected) =>
  `rounded-full border px-3 py-1 text-xs font-medium transition ${
    selected
      ? 'border-brand-300 bg-brand-50 text-brand-700 dark:border-brand-500/40 dark:bg-brand-500/10 dark:text-brand-300'
      : 'border-gray-200 text-gray-600 hover:border-brand-300 dark:border-white/10 dark:text-gray-300'
  }`

/** categoryIds is null for "every category" (the default) or an explicit
 * array of opted-in category ids — see usePushNotifications.
 */
export function NotificationCategoryPicker({ categoryIds, onChange }) {
  const { data: categories } = useQuery({ queryKey: ['categories'], queryFn: fetchCategories })
  const allSelected = categoryIds === null

  const toggleOne = (id) => {
    const current = categoryIds ?? categories?.map((c) => c.id) ?? []
    const next = current.includes(id) ? current.filter((c) => c !== id) : [...current, id]
    onChange(next)
  }

  return (
    <div className="flex flex-col gap-2 border-t border-gray-100 px-4 py-3.5 dark:border-white/10">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Notify me about</p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => onChange(null)}
          aria-pressed={allSelected}
          className={pillClass(allSelected)}
        >
          All categories
        </button>
        {categories?.map((cat) => {
          const selected = allSelected || (categoryIds ?? []).includes(cat.id)
          return (
            <button
              key={cat.id}
              type="button"
              onClick={() => toggleOne(cat.id)}
              aria-pressed={selected}
              className={pillClass(selected)}
            >
              {cat.name}
            </button>
          )
        })}
      </div>
    </div>
  )
}
