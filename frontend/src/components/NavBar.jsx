import { Link, useNavigate } from 'react-router-dom'
import { Moon, Sun, Search, Newspaper, Zap, LogOut, User as UserIcon, Download, Share, SquarePlus } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'
import { useAuth } from '../context/AuthContext'
import { usePwaInstall } from '../hooks/usePwaInstall'
import { useState } from 'react'

export function NavBar() {
  const { theme, toggleTheme } = useTheme()
  const { user, isAuthenticated, logout } = useAuth()
  const { canInstall, needsIosInstructions, install } = usePwaInstall()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)
  const [iosHelpOpen, setIosHelpOpen] = useState(false)

  const submitSearch = (e) => {
    e.preventDefault()
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query.trim())}`)
  }

  return (
    <header className="safe-top sticky top-0 z-40 border-b border-gray-100 bg-white/80 backdrop-blur-md dark:border-white/10 dark:bg-gray-950/80">
      <div className="mx-auto flex h-16 max-w-6xl items-center gap-4 px-4">
        <Link to="/" className="flex items-center gap-2 text-gray-900 dark:text-white">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-600 text-white">
            <Newspaper size={18} />
          </span>
          <span className="hidden text-lg font-bold tracking-tight sm:block">
            Insorts <span className="text-brand-600 dark:text-brand-400">News</span>
          </span>
        </Link>

        <Link
          to="/briefs"
          className="hidden shrink-0 items-center gap-1.5 rounded-full border border-gray-200 px-3.5 py-2 text-sm font-semibold text-gray-600 transition hover:border-brand-300 hover:text-brand-700 dark:border-white/10 dark:text-gray-300 dark:hover:border-brand-500 sm:flex"
        >
          <Zap size={16} /> Briefs
        </Link>

        <form onSubmit={submitSearch} className="ml-auto hidden max-w-md flex-1 md:block">
          <div className="flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-4 py-2 focus-within:border-brand-400 dark:border-white/10 dark:bg-white/5">
            <Search size={16} className="text-gray-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search news, topics, sources..."
              className="w-full bg-transparent text-sm text-gray-800 outline-none placeholder:text-gray-400 dark:text-gray-100"
            />
          </div>
        </form>

        <Link
          to="/search"
          className="ml-auto flex h-9 w-9 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/10 md:hidden"
        >
          <Search size={19} />
        </Link>

        {(canInstall || needsIosInstructions) && (
          <div className="relative">
            <button
              type="button"
              onClick={() => (canInstall ? install() : setIosHelpOpen((o) => !o))}
              className="flex h-9 shrink-0 items-center gap-1.5 rounded-full bg-brand-600 px-3 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
            >
              <Download size={15} />
              <span className="hidden sm:inline">Install app</span>
            </button>

            {iosHelpOpen && needsIosInstructions && (
              <div
                className="absolute right-0 top-11 w-64 rounded-xl border border-gray-100 bg-white p-4 text-sm shadow-lg dark:border-white/10 dark:bg-gray-900"
                onMouseLeave={() => setIosHelpOpen(false)}
              >
                <p className="font-medium text-gray-900 dark:text-gray-100">Install on iOS</p>
                <ol className="mt-2 flex flex-col gap-2 text-gray-600 dark:text-gray-300">
                  <li className="flex items-center gap-2">
                    <Share size={15} className="shrink-0 text-brand-600 dark:text-brand-400" /> Tap the Share button
                  </li>
                  <li className="flex items-center gap-2">
                    <SquarePlus size={15} className="shrink-0 text-brand-600 dark:text-brand-400" /> Tap "Add to Home
                    Screen"
                  </li>
                </ol>
                <button
                  type="button"
                  onClick={() => setIosHelpOpen(false)}
                  className="mt-3 w-full rounded-lg bg-gray-100 py-1.5 text-xs font-semibold text-gray-600 hover:bg-gray-200 dark:bg-white/10 dark:text-gray-300 dark:hover:bg-white/20"
                >
                  Got it
                </button>
              </div>
            )}
          </div>
        )}

        <button
          type="button"
          onClick={toggleTheme}
          aria-label="Toggle theme"
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-gray-500 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-white/10"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <div className="relative hidden sm:block">
          {isAuthenticated ? (
            <button
              type="button"
              onClick={() => setMenuOpen((o) => !o)}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 font-semibold text-brand-700 dark:bg-brand-900/40 dark:text-brand-300"
            >
              {user?.username?.[0]?.toUpperCase() || <UserIcon size={16} />}
            </button>
          ) : (
            <Link
              to="/login"
              className="rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
            >
              Log in
            </Link>
          )}

          {menuOpen && isAuthenticated && (
            <div
              className="absolute right-0 top-11 w-48 overflow-hidden rounded-xl border border-gray-100 bg-white py-1 shadow-lg dark:border-white/10 dark:bg-gray-900"
              onMouseLeave={() => setMenuOpen(false)}
            >
              <div className="border-b border-gray-100 px-4 py-2 text-sm dark:border-white/10">
                <p className="truncate font-medium text-gray-900 dark:text-gray-100">{user?.username}</p>
                <p className="truncate text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
              </div>
              <Link
                to="/profile"
                onClick={() => setMenuOpen(false)}
                className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:text-gray-200 dark:hover:bg-white/5"
              >
                Profile
              </Link>
              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false)
                  logout()
                  // Hard navigation on purpose — see Profile.jsx's logout
                  // handler for why (races ProtectedRoute's own redirect
                  // when logging out from a protected page).
                  window.location.href = '/'
                }}
                className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-accent-600 hover:bg-gray-50 dark:hover:bg-white/5"
              >
                <LogOut size={14} /> Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
