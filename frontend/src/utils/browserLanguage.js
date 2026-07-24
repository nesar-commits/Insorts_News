/** Browser's preferred language subtag (e.g. "hi-IN" -> "hi", "en-US" -> "en")
 * — no permission prompt needed, unlike geolocation; it's just always there.
 */
export function getBrowserLanguage() {
  const locale = navigator.language || navigator.languages?.[0]
  if (!locale) return null
  return locale.split('-')[0].toLowerCase()
}
