import { useQuery } from '@tanstack/react-query'
import { LayoutGrid } from 'lucide-react'
import { fetchCategories } from '../api/articles'
import { getCategoryIcon } from '../utils/categoryIcons'

export function CategoryTabs({ activeSlug = 'all', onSelect }) {
  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: fetchCategories,
    staleTime: 1000 * 60 * 30,
  })

  const tabs = [{ id: 'all', slug: 'all', name: 'For You', icon: null }, ...categories]

  return (
    <div className="scrollbar-none -mx-4 flex gap-2 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0">
      {tabs.map((tab) => {
        const Icon = tab.icon ? getCategoryIcon(tab.icon) : LayoutGrid
        const isActive = tab.slug === activeSlug
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onSelect(tab.slug)}
            className={`flex shrink-0 items-center gap-1.5 rounded-full border px-4 py-2 text-sm font-medium transition ${
              isActive
                ? 'border-brand-600 bg-brand-600 text-white shadow-sm'
                : 'border-gray-200 bg-white text-gray-600 hover:border-brand-300 hover:text-brand-700 dark:border-white/10 dark:bg-gray-900 dark:text-gray-300 dark:hover:border-brand-500'
            }`}
          >
            <Icon size={15} />
            {tab.name}
          </button>
        )
      })}
    </div>
  )
}
