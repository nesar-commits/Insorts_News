import { useToast } from '../context/ToastContext'

export function useShareArticle() {
  const { showToast } = useToast()

  const share = async (article) => {
    if (navigator.share) {
      try {
        await navigator.share({ title: article.title, url: article.url })
        return
      } catch (err) {
        // user explicitly dismissed the share sheet — do nothing
        if (err?.name === 'AbortError') return
      }
    }
    await navigator.clipboard.writeText(article.url)
    showToast('Link copied to clipboard', 'success')
  }

  return { share }
}
