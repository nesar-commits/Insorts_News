import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { EditProfileCard } from './EditProfileCard'
import { ToastProvider } from '../context/ToastContext'
import { useAuth } from '../context/AuthContext'

vi.mock('../context/AuthContext', () => ({ useAuth: vi.fn() }))

function renderCard() {
  return render(
    <ToastProvider>
      <EditProfileCard />
    </ToastProvider>
  )
}

describe('EditProfileCard', () => {
  let updateProfile

  beforeEach(() => {
    updateProfile = vi.fn().mockResolvedValue({})
    useAuth.mockReturnValue({
      user: { username: 'janedoe', full_name: 'Jane Doe' },
      updateProfile,
    })
  })

  it('prefills the form with the current user', () => {
    renderCard()

    expect(screen.getByDisplayValue('Jane Doe')).toBeInTheDocument()
    expect(screen.getByDisplayValue('janedoe')).toBeInTheDocument()
  })

  it('submits the trimmed username and full name', async () => {
    renderCard()

    fireEvent.change(screen.getByDisplayValue('janedoe'), { target: { value: '  newname  ' } })
    fireEvent.click(screen.getByText('Save changes'))

    await waitFor(() =>
      expect(updateProfile).toHaveBeenCalledWith({ username: 'newname', fullName: 'Jane Doe' })
    )
  })

  it('rejects a too-short username before calling the API', async () => {
    renderCard()

    fireEvent.change(screen.getByDisplayValue('janedoe'), { target: { value: 'ab' } })
    fireEvent.click(screen.getByText('Save changes'))

    await screen.findByText('Username must be at least 3 characters')
    expect(updateProfile).not.toHaveBeenCalled()
  })
})
