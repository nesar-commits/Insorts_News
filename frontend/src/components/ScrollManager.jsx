import { useEffect, useRef } from 'react'
import { useLocation, useNavigationType } from 'react-router-dom'

// In-memory only (intentionally not persisted) — a hard reload should always
// start at the top (see main.jsx's history.scrollRestoration = 'manual'),
// while in-app back/forward navigation restores the scroll position the
// user actually had, the way users expect a feed to behave.
const scrollPositions = new Map()
// Every navigation gets its own history key, so a long session with heavy
// in-app navigation (many searches, many articles opened) would otherwise
// grow this map forever — cap it and evict the oldest (Map iterates in
// insertion order), since only recent history entries are ever POPped back to.
const MAX_TRACKED_POSITIONS = 50

export function ScrollManager() {
  const location = useLocation()
  const navigationType = useNavigationType()
  const prevPathnameRef = useRef(location.pathname)

  useEffect(() => {
    const pathnameChanged = prevPathnameRef.current !== location.pathname
    prevPathnameRef.current = location.pathname

    if (navigationType === 'POP' && scrollPositions.has(location.key)) {
      window.scrollTo(0, scrollPositions.get(location.key))
    } else if (pathnameChanged) {
      window.scrollTo(0, 0)
    }
    // Same pathname with only search params changing (e.g. SearchPage's
    // debounced ?q= updates) isn't a real navigation — leave scroll alone.
  }, [location.key, location.pathname, navigationType])

  useEffect(() => {
    const handleScroll = () => {
      scrollPositions.delete(location.key) // re-set below, to refresh insertion order
      scrollPositions.set(location.key, window.scrollY)
      if (scrollPositions.size > MAX_TRACKED_POSITIONS) {
        scrollPositions.delete(scrollPositions.keys().next().value)
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [location.key])

  return null
}
