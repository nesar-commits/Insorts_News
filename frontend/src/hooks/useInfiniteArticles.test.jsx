import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useInfiniteArticles } from './useInfiniteArticles'
import { fetchArticles } from '../api/articles'

vi.mock('../api/articles', () => ({ fetchArticles: vi.fn() }))

function renderWithClient(hook, options = {}) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return renderHook(hook, {
    ...options,
    wrapper: ({ children }) => <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>,
  })
}

beforeEach(() => {
  fetchArticles.mockReset()
  fetchArticles.mockResolvedValue({ items: [], total: 0, next_cursor: null })
})

describe('useInfiniteArticles', () => {
  it('passes through category, search, nearby, coords and lang', async () => {
    const coords = { lat: 51.5, lon: -0.1 }
    renderWithClient(() =>
      useInfiniteArticles({ category: 'tech', search: 'ai', nearby: true, coords, lang: 'en' })
    )

    await waitFor(() => expect(fetchArticles).toHaveBeenCalled())

    expect(fetchArticles).toHaveBeenCalledWith(
      expect.objectContaining({
        category: 'tech',
        search: 'ai',
        nearby: true,
        coords,
        lang: 'en',
        cursor: undefined,
      })
    )
  })

  it('refetches when coords change from null to a real fix', async () => {
    const { result, rerender } = renderWithClient(({ coords }) => useInfiniteArticles({ nearby: true, coords }), {
      initialProps: { coords: null },
    })

    await waitFor(() => expect(fetchArticles).toHaveBeenCalledTimes(1))
    expect(fetchArticles).toHaveBeenLastCalledWith(expect.objectContaining({ coords: null }))

    rerender({ coords: { lat: 1, lon: 2 } })

    await waitFor(() => expect(fetchArticles).toHaveBeenCalledTimes(2))
    expect(fetchArticles).toHaveBeenLastCalledWith(expect.objectContaining({ coords: { lat: 1, lon: 2 } }))
    expect(result.current).toBeDefined()
  })

  it('does not refetch for a new coords object with the same lat/lon', async () => {
    const { rerender } = renderWithClient(({ coords }) => useInfiniteArticles({ nearby: true, coords }), {
      initialProps: { coords: { lat: 1, lon: 2 } },
    })

    await waitFor(() => expect(fetchArticles).toHaveBeenCalledTimes(1))

    rerender({ coords: { lat: 1, lon: 2 } }) // new object, same values

    // React Query's queryKey is deep-compared, so an equivalent-but-new
    // coords object must not trigger a refetch storm on every render.
    await new Promise((r) => setTimeout(r, 50))
    expect(fetchArticles).toHaveBeenCalledTimes(1)
  })

  it('uses next_cursor as the next page param', async () => {
    fetchArticles.mockResolvedValue({ items: [{ id: 1 }], total: 1, next_cursor: 'abc_1' })
    const { result } = renderWithClient(() => useInfiniteArticles({}))

    await waitFor(() => expect(result.current.hasNextPage).toBe(true))
  })

  it('has no next page once next_cursor is null', async () => {
    fetchArticles.mockResolvedValue({ items: [{ id: 1 }], total: 1, next_cursor: null })
    const { result } = renderWithClient(() => useInfiniteArticles({}))

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.hasNextPage).toBe(false)
  })
})
