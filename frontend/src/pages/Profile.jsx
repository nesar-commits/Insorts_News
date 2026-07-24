import { LogOut, Mail, User as UserIcon, Moon, Sun, Bell, BellOff } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'
import { usePushNotifications } from '../hooks/usePushNotifications'
import { useToast } from '../context/ToastContext'

export function Profile() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const { supported, subscribed, loading, subscribe, unsubscribe } = usePushNotifications()
  const { showToast } = useToast()

  const handleToggleNotifications = async () => {
    if (subscribed) {
      await unsubscribe()
      showToast('Breaking news notifications turned off', 'info')
      return
    }
    const granted = await subscribe()
    if (granted) {
      showToast('Breaking news notifications turned on', 'success')
    } else {
      showToast('Notifications were blocked — enable them in your browser settings', 'error')
    }
  }

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 pt-4">
      <div className="flex flex-col items-center gap-3 rounded-2xl border border-gray-100 bg-white p-6 text-center shadow-sm dark:border-white/10 dark:bg-gray-900">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-100 text-2xl font-bold text-brand-700 dark:bg-brand-900/40 dark:text-brand-300">
          {user?.username?.[0]?.toUpperCase() || <UserIcon size={24} />}
        </div>
        <div>
          <p className="text-lg font-bold text-gray-900 dark:text-white">{user?.full_name || user?.username}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">@{user?.username}</p>
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white dark:border-white/10 dark:bg-gray-900">
        <div className="flex items-center gap-3 border-b border-gray-100 px-4 py-3.5 dark:border-white/10">
          <Mail size={18} className="text-gray-400" />
          <span className="text-sm text-gray-700 dark:text-gray-200">{user?.email}</span>
        </div>
        <button
          type="button"
          onClick={toggleTheme}
          className="flex w-full items-center gap-3 px-4 py-3.5 text-left"
        >
          {theme === 'dark' ? (
            <Sun size={18} className="text-gray-400" />
          ) : (
            <Moon size={18} className="text-gray-400" />
          )}
          <span className="text-sm text-gray-700 dark:text-gray-200">
            Switch to {theme === 'dark' ? 'light' : 'dark'} mode
          </span>
        </button>

        {supported && !loading && (
          <button
            type="button"
            onClick={handleToggleNotifications}
            className="flex w-full items-center gap-3 border-t border-gray-100 px-4 py-3.5 text-left dark:border-white/10"
          >
            {subscribed ? (
              <BellOff size={18} className="text-gray-400" />
            ) : (
              <Bell size={18} className="text-gray-400" />
            )}
            <span className="text-sm text-gray-700 dark:text-gray-200">
              {subscribed ? 'Turn off breaking news notifications' : 'Get breaking news notifications'}
            </span>
          </button>
        )}
      </div>

      <button
        type="button"
        onClick={() => {
          logout()
          // Hard navigation on purpose: logging out while mounted on a
          // protected route races React Router's own redirect-to-/login,
          // which reliably wins. A full reload sidesteps that entirely and
          // also clears any cached per-user data in memory.
          window.location.href = '/'
        }}
        className="flex items-center justify-center gap-2 rounded-xl border border-accent-200 py-3 text-sm font-semibold text-accent-600 transition hover:bg-accent-50 dark:border-accent-500/30 dark:hover:bg-accent-500/10"
      >
        <LogOut size={16} /> Log out
      </button>
    </div>
  )
}
