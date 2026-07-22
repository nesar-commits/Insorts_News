import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { fetchCurrentUser, loginUser, registerUser } from '../api/auth'
import { SESSION_EXPIRED_EVENT } from '../api/client'
import { useToast } from './ToastContext'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const { showToast } = useToast()
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('insorts_user')
    return raw ? JSON.parse(raw) : null
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('insorts_token')
    if (!token) {
      setLoading(false)
      return
    }
    fetchCurrentUser()
      .then((freshUser) => {
        setUser(freshUser)
        localStorage.setItem('insorts_user', JSON.stringify(freshUser))
      })
      .catch(() => {
        localStorage.removeItem('insorts_token')
        localStorage.removeItem('insorts_user')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    const handleSessionExpired = () => {
      setUser(null)
      showToast('Your session has expired. Please log in again.', 'info')
    }
    window.addEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
    return () => window.removeEventListener(SESSION_EXPIRED_EVENT, handleSessionExpired)
  }, [showToast])

  const persistSession = (token, sessionUser) => {
    localStorage.setItem('insorts_token', token)
    localStorage.setItem('insorts_user', JSON.stringify(sessionUser))
    setUser(sessionUser)
  }

  const login = async (email, password) => {
    const data = await loginUser({ email, password })
    persistSession(data.access_token, data.user)
    return data.user
  }

  const register = async ({ email, username, password, fullName }) => {
    const data = await registerUser({ email, username, password, fullName })
    persistSession(data.access_token, data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('insorts_token')
    localStorage.removeItem('insorts_user')
    setUser(null)
  }

  const value = useMemo(
    () => ({ user, loading, isAuthenticated: !!user, login, register, logout }),
    [user, loading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
