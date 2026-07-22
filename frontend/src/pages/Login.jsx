import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Newspaper, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/errors'
import { PasswordInput } from '../components/PasswordInput'

export function Login() {
  const { login } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()
  const location = useLocation()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(email, password)
      showToast('Welcome back!', 'success')
      navigate(location.state?.from?.pathname || '/', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, 'Incorrect email or password'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col items-center gap-6 pt-8">
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 text-white">
        <Newspaper size={24} />
      </div>
      <div className="text-center">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Welcome back</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Log in to save and sync your articles</p>
      </div>

      <form onSubmit={handleSubmit} className="flex w-full flex-col gap-4">
        {error && (
          <p className="rounded-lg bg-accent-50 px-3 py-2 text-sm text-accent-600 dark:bg-accent-500/10">{error}</p>
        )}

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="you@example.com"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Password</span>
          <PasswordInput
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="••••••••"
          />
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="flex items-center justify-center gap-2 rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-70"
        >
          {submitting && <Loader2 size={16} className="animate-spin" />}
          Log in
        </button>
      </form>

      <p className="text-sm text-gray-500 dark:text-gray-400">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="font-semibold text-brand-600 dark:text-brand-400">
          Sign up
        </Link>
      </p>
    </div>
  )
}
