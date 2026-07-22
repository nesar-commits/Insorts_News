import { NavLink } from 'react-router-dom'
import { Home, Search, Zap, Bookmark, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const items = [
  { to: '/', label: 'Home', icon: Home, end: true },
  { to: '/search', label: 'Search', icon: Search },
  { to: '/briefs', label: 'Briefs', icon: Zap },
  { to: '/bookmarks', label: 'Saved', icon: Bookmark },
]

export function BottomNav() {
  const { isAuthenticated } = useAuth()

  return (
    <nav className="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-gray-100 bg-white/95 backdrop-blur-md dark:border-white/10 dark:bg-gray-950/95 sm:hidden">
      <div className="flex items-stretch justify-around px-2 pt-1">
        {items.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-0.5 rounded-lg py-2 text-[11px] font-medium ${
                isActive ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400 dark:text-gray-500'
              }`
            }
          >
            <Icon size={20} />
            {label}
          </NavLink>
        ))}
        <NavLink
          to={isAuthenticated ? '/profile' : '/login'}
          className={({ isActive }) =>
            `flex flex-1 flex-col items-center gap-0.5 rounded-lg py-2 text-[11px] font-medium ${
              isActive ? 'text-brand-600 dark:text-brand-400' : 'text-gray-400 dark:text-gray-500'
            }`
          }
        >
          <User size={20} />
          {isAuthenticated ? 'Profile' : 'Log in'}
        </NavLink>
      </div>
    </nav>
  )
}
