import { Loader2 } from 'lucide-react'

export function Spinner({ size = 20, className = '' }) {
  return <Loader2 size={size} className={`animate-spin text-brand-600 dark:text-brand-400 ${className}`} />
}

export function FullPageSpinner() {
  return (
    <div className="flex flex-1 items-center justify-center py-24">
      <Spinner size={28} />
    </div>
  )
}
