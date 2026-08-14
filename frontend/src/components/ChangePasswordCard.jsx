import { useState } from 'react'
import { changePassword } from '../api/auth'
import { useToast } from '../context/ToastContext'
import { getErrorMessage } from '../utils/errors'
import { PasswordInput } from './PasswordInput'

const inputClass =
  'rounded-xl border border-gray-200 px-3 py-2 text-sm outline-none focus:border-brand-400 dark:border-white/10 dark:bg-gray-950 dark:text-white'

export function ChangePasswordCard() {
  const { showToast } = useToast()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (newPassword.length < 8) {
      showToast('New password must be at least 8 characters', 'error')
      return
    }
    if (newPassword !== confirmPassword) {
      showToast('New passwords do not match', 'error')
      return
    }

    setSubmitting(true)
    try {
      await changePassword({ currentPassword, newPassword })
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      showToast('Password changed', 'success')
    } catch (err) {
      showToast(getErrorMessage(err, 'Could not change your password'), 'error')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-3 rounded-2xl border border-gray-100 bg-white p-4 dark:border-white/10 dark:bg-gray-900"
    >
      <h2 className="text-sm font-semibold text-gray-900 dark:text-white">Change password</h2>
      <PasswordInput
        required
        placeholder="Current password"
        value={currentPassword}
        onChange={(e) => setCurrentPassword(e.target.value)}
        className={inputClass}
      />
      <PasswordInput
        required
        minLength={8}
        placeholder="New password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
        className={inputClass}
      />
      <PasswordInput
        required
        minLength={8}
        placeholder="Confirm new password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        className={inputClass}
      />
      <button
        type="submit"
        disabled={submitting}
        className="self-start rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:opacity-60"
      >
        Change password
      </button>
    </form>
  )
}
