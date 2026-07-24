import { useEffect, useState } from 'react'

/** GPS-precise location for "nearby news" — the browser only prompts once;
 * after that it silently succeeds (already granted) or fails (denied),
 * so it's safe to request on every "For You" tab visit. `denied` is only
 * true for an explicit PERMISSION_DENIED (or no geolocation support at
 * all) — the caller uses that to show general news instead of quietly
 * falling back to IP-based location, since the user actively said no.
 * A transient failure (timeout, position unavailable) leaves `denied`
 * false so the backend's IP fallback still applies.
 */
export function useGeolocation(enabled) {
  const [state, setState] = useState({ coords: null, denied: false })

  useEffect(() => {
    if (!enabled) return

    if (!navigator.geolocation) {
      setState({ coords: null, denied: true })
      return
    }

    let cancelled = false
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (cancelled) return
        setState({ coords: { lat: position.coords.latitude, lon: position.coords.longitude }, denied: false })
      },
      (error) => {
        if (cancelled) return
        setState({ coords: null, denied: error.code === error.PERMISSION_DENIED })
      },
      { maximumAge: 1000 * 60 * 10, timeout: 5000 }
    )

    return () => {
      cancelled = true
    }
  }, [enabled])

  return state
}
