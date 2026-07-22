import { useEffect, useRef } from 'react'

export function useInView(onIntersect, { enabled = true, rootMargin = '400px' } = {}) {
  const targetRef = useRef(null)

  useEffect(() => {
    if (!enabled || !targetRef.current) return

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting) onIntersect()
      },
      { rootMargin }
    )

    observer.observe(targetRef.current)
    return () => observer.disconnect()
  }, [onIntersect, enabled, rootMargin])

  return targetRef
}
