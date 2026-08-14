import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/errors'

const inputClass =
  'rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-950 dark:text-white'

export function EditProfileCard() {
  const { user, updateProfile } = useAuth()
  const { showToast } = useToast()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [username, setUsername] = useState(user?.username || '')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    const trimmedUsername = username.trim()
    if (trimmedUsername.length < 3) {
      showToast('Username must be at least 3 characters', 'error')
      return
    }

    setSubmitting(true)
    try {
      await updateProfile({ username: trimmedUsername, fullName: fullName.trim() })
      showToast('Profile updated', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, 'Could not update your profile'), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-2xl border border-gray-100 bg-white p-4 dark:border-white/10 dark:bg-gray-900"
    >
      <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Edit profile</h2>
      <label className="flex flex-col gap-1.5">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Full name</span>
        <input value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputClass} />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="text-xs font-medium text-gray-500 dark:text-gray-400">Username</span>
        <input
          required
          minLength={3}
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className={inputClass}
        />
      </label>
      <button
        type="submit"
        disabled={submitting}
        className="self-start rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60"
      >
        Save changes
      </button>
    </form>
  )
}
