import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchMutedPreferences,
  muteCategory,
  muteSource,
  unmuteCategory,
  unmuteSource,
} from '../api/preferences'

export function useMutePreferences() {
  const queryClient = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['muted-preferences'],
    queryFn: fetchMutedPreferences,
  })

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['muted-preferences'] })
    // Muting changes what the feed and trending list show, not just this
    // preferences screen, so both need to refetch too.
    queryClient.invalidateQueries({ queryKey: ['articles'] })
    queryClient.invalidateQueries({ queryKey: ['trending'] })
  }

  const toggleSourceMutation = useMutation({
    mutationFn: ({ sourceId, muted }) => (muted ? unmuteSource(sourceId) : muteSource(sourceId)),
    onSuccess: invalidate,
  })

  const toggleCategoryMutation = useMutation({
    mutationFn: ({ categoryId, muted }) => (muted ? unmuteCategory(categoryId) : muteCategory(categoryId)),
    onSuccess: invalidate,
  })

  const mutedSourceIds = new Set(data?.muted_source_ids ?? [])
  const mutedCategoryIds = new Set(data?.muted_category_ids ?? [])

  return {
    isLoading,
    mutedSourceIds,
    mutedCategoryIds,
    toggleSource: (sourceId) => toggleSourceMutation.mutate({ sourceId, muted: mutedSourceIds.has(sourceId) }),
    toggleCategory: (categoryId) =>
      toggleCategoryMutation.mutate({ categoryId, muted: mutedCategoryIds.has(categoryId) }),
  }
}
