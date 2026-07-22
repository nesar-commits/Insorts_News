export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-gray-200 px-6 py-16 text-center dark:border-white/10">
      {Icon && (
        <div className="flex h-14 w-14 items-center justify-center rounded-full bg-brand-50 text-brand-600 dark:bg-white/5 dark:text-brand-400">
          <Icon size={26} />
        </div>
      )}
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{title}</h3>
      {description && <p className="max-w-sm text-sm text-gray-500 dark:text-gray-400">{description}</p>}
      {action}
    </div>
  )
}
