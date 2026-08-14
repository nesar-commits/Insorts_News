const SAFE_PROTOCOLS = new Set(['http:', 'https:'])

/** Article URLs come from RSS feeds ingested by the backend — the backend
 * already rejects non-http(s) links at ingestion, but this is a second,
 * independent check right before rendering one as an anchor href, so a gap
 * anywhere upstream (a backfilled row, a future ingestion bug) can't turn
 * into a clickable javascript: URI.
 */
export function safeHref(url) {
  try {
    return SAFE_PROTOCOLS.has(new URL(url).protocol) ? url : '#'
  } catch {
    return '#'
  }
}
