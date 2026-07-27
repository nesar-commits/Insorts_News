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
  const [state, setState] = useState({ coords: null, denied: false, loading: enabled })
  // Bumped by recheck() to force the effect below to re-run and re-request
  // permission — otherwise a permission change made after the initial grant
  // (or denial) would never be picked up until the app fully remounts.
  const [nonce, setNonce] = useState(0)

  useEffect(() => {
    if (!enabled) return

    if (!navigator.geolocation) {
      setState({ coords: null, denied: true, loading: false })
      return
    }

    setState((s) => ({ ...s, loading: true }))

    let cancelled = false
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (cancelled) return
        setState({
          coords: { lat: position.coords.latitude, lon: position.coords.longitude },
          denied: false,
          loading: false,
        })
      },
      (error) => {
        if (cancelled) return
        setState({ coords: null, denied: error.code === error.PERMISSION_DENIED, loading: false })
      },
      // High accuracy forces the device's GPS chip rather than coarse
      // WiFi/cell-tower positioning — same tradeoff delivery apps make for
      // exact location. That fix can take longer to acquire (especially
      // indoors), so the timeout is generous; maximumAge allows reusing a
      // very recent fix instead of forcing a brand-new GPS read on every
      // "For You" visit within the same minute.
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    )

    return () => {
      cancelled = true
    }
  }, [enabled, nonce])

  const recheck = () => setNonce((n) => n + 1)

  return { ...state, recheck }
}
