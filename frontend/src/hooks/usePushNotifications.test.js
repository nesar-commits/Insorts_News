import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { usePushNotifications } from './usePushNotifications'
import { apiClient } from '../api/client'

vi.mock('../api/client', () => ({
  apiClient: { get: vi.fn(), post: vi.fn(), delete: vi.fn(), put: vi.fn() },
}))

const CATEGORY_PREFS_KEY = 'insorts_push_categories'

function fakeSubscription(overrides = {}) {
  return {
    endpoint: 'https://push.example.com/x',
    getKey: (name) => new TextEncoder().encode(name),
    unsubscribe: vi.fn().mockResolvedValue(true),
    ...overrides,
  }
}

function mockServiceWorker(subscription) {
  Object.defineProperty(navigator, 'serviceWorker', {
    value: {
      ready: Promise.resolve({
        pushManager: {
          getSubscription: vi.fn().mockResolvedValue(subscription),
          subscribe: vi.fn().mockResolvedValue(subscription),
        },
      }),
    },
    configurable: true,
  })
}

beforeEach(() => {
  localStorage.clear()
  vi.clearAllMocks()
  window.PushManager = function () {}
})

afterEach(() => {
  delete navigator.serviceWorker
  delete window.PushManager
})

describe('usePushNotifications category preferences', () => {
  it('defaults categoryIds to null (every category) with nothing stored', () => {
    mockServiceWorker(null)
    const { result } = renderHook(() => usePushNotifications())

    expect(result.current.categoryIds).toBeNull()
  })

  it('loads a previously stored category preference', () => {
    localStorage.setItem(CATEGORY_PREFS_KEY, JSON.stringify([1, 2]))
    mockServiceWorker(null)
    const { result } = renderHook(() => usePushNotifications())

    expect(result.current.categoryIds).toEqual([1, 2])
  })

  it('ignores corrupted localStorage instead of throwing', () => {
    localStorage.setItem(CATEGORY_PREFS_KEY, 'not-json')
    mockServiceWorker(null)
    const { result } = renderHook(() => usePushNotifications())

    expect(result.current.categoryIds).toBeNull()
  })

  it('updateCategoryIds sends the subscription info and persists the choice', async () => {
    const sub = fakeSubscription()
    mockServiceWorker(sub)
    apiClient.put.mockResolvedValue({})
    const { result } = renderHook(() => usePushNotifications())

    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => result.current.updateCategoryIds([3, 4]))

    expect(apiClient.put).toHaveBeenCalledWith(
      '/push/categories',
      expect.objectContaining({ endpoint: sub.endpoint, category_ids: [3, 4] })
    )
    expect(result.current.categoryIds).toEqual([3, 4])
    expect(JSON.parse(localStorage.getItem(CATEGORY_PREFS_KEY))).toEqual([3, 4])
  })

  it('updateCategoryIds(null) clears the stored preference', async () => {
    localStorage.setItem(CATEGORY_PREFS_KEY, JSON.stringify([1]))
    const sub = fakeSubscription()
    mockServiceWorker(sub)
    apiClient.put.mockResolvedValue({})
    const { result } = renderHook(() => usePushNotifications())

    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => result.current.updateCategoryIds(null))

    expect(result.current.categoryIds).toBeNull()
    expect(localStorage.getItem(CATEGORY_PREFS_KEY)).toBeNull()
  })

  it('updateCategoryIds([]) sends an explicit empty list, not null-as-all', async () => {
    // Regression: [] ("opted out of every category") must reach the
    // backend as [], not get collapsed into the "all categories" payload —
    // those are different preferences server-side.
    const sub = fakeSubscription()
    mockServiceWorker(sub)
    apiClient.put.mockResolvedValue({})
    const { result } = renderHook(() => usePushNotifications())

    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => result.current.updateCategoryIds([]))

    expect(apiClient.put).toHaveBeenCalledWith(
      '/push/categories',
      expect.objectContaining({ endpoint: sub.endpoint, category_ids: [] })
    )
    expect(result.current.categoryIds).toEqual([])
  })

  it('updateCategoryIds(null) sends null, not an empty list', async () => {
    const sub = fakeSubscription()
    mockServiceWorker(sub)
    apiClient.put.mockResolvedValue({})
    const { result } = renderHook(() => usePushNotifications())

    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => result.current.updateCategoryIds(null))

    expect(apiClient.put).toHaveBeenCalledWith(
      '/push/categories',
      expect.objectContaining({ endpoint: sub.endpoint, category_ids: null })
    )
  })

  it('updateCategoryIds is a no-op with no active subscription', async () => {
    mockServiceWorker(null)
    const { result } = renderHook(() => usePushNotifications())

    await waitFor(() => expect(result.current.loading).toBe(false))
    await act(async () => result.current.updateCategoryIds([1]))

    expect(apiClient.put).not.toHaveBeenCalled()
  })
})
