import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ChangePasswordCard } from './ChangePasswordCard'
import { ToastProvider } from '../context/ToastContext'
import { changePassword } from '../api/auth'

vi.mock('../api/auth', () => ({ changePassword: vi.fn() }))

function renderCard() {
  return render(
    <ToastProvider>
      <ChangePasswordCard />
    </ToastProvider>
  )
}

function fillAndSubmit({ current, next, confirm }) {
  fireEvent.change(screen.getByPlaceholderText('Current password'), { target: { value: current } })
  fireEvent.change(screen.getByPlaceholderText('New password'), { target: { value: next } })
  fireEvent.change(screen.getByPlaceholderText('Confirm new password'), { target: { value: confirm } })
  fireEvent.click(screen.getByRole('button', { name: 'Change password' }))
}

describe('ChangePasswordCard', () => {
  beforeEach(() => {
    changePassword.mockReset().mockResolvedValue(undefined)
  })

  it('submits current and new password to the API', async () => {
    renderCard()

    fillAndSubmit({ current: 'old-password1', next: 'new-password1', confirm: 'new-password1' })

    await waitFor(() =>
      expect(changePassword).toHaveBeenCalledWith({
        currentPassword: 'old-password1',
        newPassword: 'new-password1',
      })
    )
  })

  it('clears the fields after a successful change', async () => {
    renderCard()

    fillAndSubmit({ current: 'old-password1', next: 'new-password1', confirm: 'new-password1' })

    await screen.findByText('Password changed')
    expect(screen.getByPlaceholderText('New password')).toHaveValue('')
  })

  it('rejects mismatched confirmation without calling the API', async () => {
    renderCard()

    fillAndSubmit({ current: 'old-password1', next: 'new-password1', confirm: 'something-else1' })

    await screen.findByText('New passwords do not match')
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('rejects a too-short new password without calling the API', async () => {
    renderCard()

    fillAndSubmit({ current: 'old-password1', next: 'short1', confirm: 'short1' })

    await screen.findByText('New password must be at least 8 characters')
    expect(changePassword).not.toHaveBeenCalled()
  })

  it('shows an error toast when the API call fails', async () => {
    changePassword.mockRejectedValue({ response: { data: { detail: 'Current password is incorrect' } } })
    renderCard()

    fillAndSubmit({ current: 'wrong-password1', next: 'new-password1', confirm: 'new-password1' })

    await screen.findByText('Current password is incorrect')
  })
})
