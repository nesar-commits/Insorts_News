export function getErrorMessage(err, fallback) {
  const detail = err?.response?.data?.detail

  if (!detail) return fallback
  if (typeof detail === 'string') return detail

  if (Array.isArray(detail)) {
    const messages = detail.map((item) => item?.msg).filter(Boolean)
    return messages.length ? messages.join(' ') : fallback
  }

  return fallback
}
