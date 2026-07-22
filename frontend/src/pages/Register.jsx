import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Newspaper, Loader2 } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/errors'
import { PasswordInput } from '../components/PasswordInput'

export function Register() {
  const { register } = useAuth()
  const { showToast } = useToast()
  const navigate = useNavigate()

  const [form, setForm] = useState({ fullName: '', username: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (field) => (e) => setForm((f) => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (form.password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setSubmitting(true)
    try {
      await register(form)
      showToast('Account created — welcome to Insorts News!', 'success')
      navigate('/', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, 'Could not create your account'))
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
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Create your account</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Personalize your feed and save stories</p>
      </div>

      <form onSubmit={handleSubmit} className="flex w-full flex-col gap-4">
        {error && (
          <p className="rounded-lg bg-accent-50 px-3 py-2 text-sm text-accent-600 dark:bg-accent-500/10">{error}</p>
        )}

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Full name</span>
          <input
            value={form.fullName}
            onChange={update('fullName')}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="Jane Doe"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Username</span>
          <input
            required
            minLength={3}
            value={form.username}
            onChange={update('username')}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="janedoe"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Email</span>
          <input
            type="email"
            required
            value={form.email}
            onChange={update('email')}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="you@example.com"
          />
        </label>

        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Password</span>
          <PasswordInput
            required
            minLength={8}
            value={form.password}
            onChange={update('password')}
            className="rounded-xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-900 dark:text-white"
            placeholder="At least 8 characters"
          />
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="flex items-center justify-center gap-2 rounded-xl bg-brand-600 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 disabled:opacity-70"
        >
          {submitting && <Loader2 size={16} className="animate-spin" />}
          Create account
        </button>
      </form>

      <p className="text-sm text-gray-500 dark:text-gray-400">
        Already have an account?{' '}
        <Link to="/login" className="font-semibold text-brand-600 dark:text-brand-400">
          Log in
        </Link>
      </p>
    </div>
  )
}
