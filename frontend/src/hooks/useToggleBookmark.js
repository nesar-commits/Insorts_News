import { useMutation, useQueryClient } from '@tanstack/react-query'
import { addBookmark, removeBookmark } from '../api/bookmarks'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'

export function useToggleBookmark() {
  const queryClient = useQueryClient()
  const { isAuthenticated } = useAuth()
  const { showToast } = useToast()

  const invalidateAll = () => {
    queryClient.invalidateQueries({ queryKey: ['articles'] })
    queryClient.invalidateQueries({ queryKey: ['trending'] })
    queryClient.invalidateQueries({ queryKey: ['bookmarks'] })
    queryClient.invalidateQueries({ queryKey: ['article'] })
  }

  const mutation = useMutation({
    mutationFn: async ({ articleId, isBookmarked }) => {
      if (isBookmarked) {
        await removeBookmark(articleId)
      } else {
        await addBookmark(articleId)
      }
    },
    onSuccess: (_data, variables) => {
      invalidateAll()
      showToast(variables.isBookmarked ? 'Removed from bookmarks' : 'Saved to bookmarks', 'success')
    },
    onError: () => {
      showToast('Something went wrong. Please try again.', 'error')
    },
  })

  const toggle = (articleId, isBookmarked) => {
    if (!isAuthenticated) {
      showToast('Log in to save articles', 'info')
      return
    }
    mutation.mutate({ articleId, isBookmarked })
  }

  return { toggle, isLoading: mutation.isPending }
}
