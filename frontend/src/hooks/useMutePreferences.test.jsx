import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useMutePreferences } from './useMutePreferences'
import * as preferencesApi from '../api/preferences'

vi.mock('../api/preferences', () => ({
  fetchMutedPreferences: vi.fn(),
  muteSource: vi.fn(),
  unmuteSource: vi.fn(),
  muteCategory: vi.fn(),
  unmuteCategory: vi.fn(),
}))

function renderWithClient(hook) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return renderHook(hook, {
    wrapper: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>,
  })
}

beforeEach(() => {
  preferencesApi.fetchMutedPreferences.mockReset().mockResolvedValue({
    muted_source_ids: [1, 2],
    muted_category_ids: [5],
  })
  preferencesApi.muteSource.mockReset().mockResolvedValue(undefined)
  preferencesApi.unmuteSource.mockReset().mockResolvedValue(undefined)
  preferencesApi.muteCategory.mockReset().mockResolvedValue(undefined)
  preferencesApi.unmuteCategory.mockReset().mockResolvedValue(undefined)
})

describe('useMutePreferences', () => {
  it('exposes the currently muted source and category ids', async () => {
    const { result } = renderWithClient(() => useMutePreferences())

    await waitFor(() => expect(result.current.isLoading).toBe(false))

    expect(result.current.mutedSourceIds.has(1)).toBe(true)
    expect(result.current.mutedSourceIds.has(2)).toBe(true)
    expect(result.current.mutedCategoryIds.has(5)).toBe(true)
  })

  it('toggleSource calls unmute when already muted, mute otherwise', async () => {
    const { result } = renderWithClient(() => useMutePreferences())
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(async () => result.current.toggleSource(1)) // already muted
    expect(preferencesApi.unmuteSource).toHaveBeenCalledWith(1)
    expect(preferencesApi.muteSource).not.toHaveBeenCalled()

    await act(async () => result.current.toggleSource(99)) // not muted
    expect(preferencesApi.muteSource).toHaveBeenCalledWith(99)
  })

  it('toggleCategory calls unmute when already muted, mute otherwise', async () => {
    const { result } = renderWithClient(() => useMutePreferences())
    await waitFor(() => expect(result.current.isLoading).toBe(false))

    await act(async () => result.current.toggleCategory(5)) // already muted
    expect(preferencesApi.unmuteCategory).toHaveBeenCalledWith(5)

    await act(async () => result.current.toggleCategory(7)) // not muted
    expect(preferencesApi.muteCategory).toHaveBeenCalledWith(7)
  })
})
