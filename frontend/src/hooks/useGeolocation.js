import { useEffect, useState } from 'react'

/** GPS-precise location for "nearby news" — the browser only prompts once;
 * after that it silently succeeds (already granted) or fails (denied),
 * so it's safe to request on every "For You" tab visit. When unavailable
 * or denied, coords stays null and the backend falls back to IP-based
 * detection on its own.
 */
export function useGeolocation(enabled) {
  const [coords, setCoords] = useState(null)

  useEffect(() => {
    if (!enabled || !navigator.geolocation) return

    let cancelled = false
    navigator.geolocation.getCurrentPosition(
      (position) => {
        if (cancelled) return
        setCoords({ lat: position.coords.latitude, lon: position.coords.longitude })
      },
      () => {
        // Permission denied, timed out, or position unavailable — leave
        // coords as null so the caller falls back to IP-based detection.
      },
      { maximumAge: 1000 * 60 * 10, timeout: 5000 }
    )

    return () => {
      cancelled = true
    }
  }, [enabled])

  return coords
}
