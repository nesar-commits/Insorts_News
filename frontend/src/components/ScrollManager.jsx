import { useEffect } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

// In-memory only (intentionally not persisted) — a hard reload should always
// start at the top (see main.jsx's history.scrollRestoration = 'manual'),
// while in-app back/forward navigation restores the scroll position the
// user actually had, the way users expect a feed to behave.
const scrollPositions = new Map()

export function ScrollManager() {
  const location = useLocation()
  const navigationType = useNavigationType()

  useEffect(() => {
    if (navigationType === 'POP' && scrollPositions.has(location.key)) {
      window.scrollTo(0, scrollPositions.get(location.key))
    } else {
      window.scrollTo(0, 0)
    }
  }, [location.key, navigationType])

  useEffect(() => {
    const handleScroll = () => {
      scrollPositions.set(location.key, window.scrollY)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [location.key])

  return null
}
