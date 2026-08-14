import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { useGeolocation } from './useGeolocation'

const PERMISSION_DENIED = 1
const POSITION_UNAVAILABLE = 2
const TIMEOUT = 3

function mockGeolocation(implementation) {
  Object.defineProperty(navigator, 'geolocation', {
    value: { getCurrentPosition: vi.fn(implementation) },
    configurable: true,
  })
}

afterEach(() => {
  vi.restoreAllMocks()
  delete navigator.geolocation
})

describe('useGeolocation', () => {
  it('does nothing when disabled', () => {
    mockGeolocation(() => {})
    const { result } = renderHook(() => useGeolocation(false))

    expect(result.current.coords).toBeNull()
    expect(result.current.denied).toBe(false)
    expect(result.current.loading).toBe(false)
    expect(navigator.geolocation.getCurrentPosition).not.toHaveBeenCalled()
  })

  it('is loading while the position request is in flight', () => {
    mockGeolocation(() => {}) // never resolves
    const { result } = renderHook(() => useGeolocation(true))

    expect(result.current.loading).toBe(true)
  })

  it('requests high-accuracy GPS with a generous timeout', () => {
    mockGeolocation(() => {})
    renderHook(() => useGeolocation(true))

    expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function),
      expect.objectContaining({ enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 })
    )
  })

  it('sets coords and clears loading on success', async () => {
    mockGeolocation((success) => {
      success({ coords: { latitude: 51.5074, longitude: -0.1278 } })
    })
    const { result } = renderHook(() => useGeolocation(true))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.coords).toEqual({ lat: 51.5074, lon: -0.1278 })
    expect(result.current.denied).toBe(false)
  })

  it('sets denied=true only for an explicit PERMISSION_DENIED', async () => {
    mockGeolocation((_success, error) => {
      error({ code: PERMISSION_DENIED, PERMISSION_DENIED })
    })
    const { result } = renderHook(() => useGeolocation(true))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.denied).toBe(true)
    expect(result.current.coords).toBeNull()
  })

  it('leaves denied=false for a transient failure like a timeout', async () => {
    mockGeolocation((_success, error) => {
      error({ code: TIMEOUT, PERMISSION_DENIED })
    })
    const { result } = renderHook(() => useGeolocation(true))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.denied).toBe(false)
    expect(result.current.coords).toBeNull()
  })

  it('leaves denied=false for position-unavailable', async () => {
    mockGeolocation((_success, error) => {
      error({ code: POSITION_UNAVAILABLE, PERMISSION_DENIED })
    })
    const { result } = renderHook(() => useGeolocation(true))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.denied).toBe(false)
  })

  it('treats missing navigator.geolocation as denied, not loading forever', () => {
    delete navigator.geolocation
    const { result } = renderHook(() => useGeolocation(true))

    expect(result.current.denied).toBe(true)
    expect(result.current.loading).toBe(false)
  })

  it('recheck() re-requests the position', async () => {
    let calls = 0
    mockGeolocation((success) => {
      calls += 1
      success({ coords: { latitude: calls, longitude: calls } })
    })
    const { result } = renderHook(() => useGeolocation(true))

    await waitFor(() => expect(result.current.coords).toEqual({ lat: 1, lon: 1 }))

    act(() => result.current.recheck())

    await waitFor(() => expect(result.current.coords).toEqual({ lat: 2, lon: 2 }))
    expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalledTimes(2)
  })

  it('ignores a stale response after being disabled mid-flight', async () => {
    let resolvePosition
    mockGeolocation((success) => {
      resolvePosition = success
    })
    const { result, rerender } = renderHook(({ enabled }) => useGeolocation(enabled), {
      initialProps: { enabled: true },
    })

    rerender({ enabled: false })
    act(() => resolvePosition({ coords: { latitude: 1, longitude: 1 } }))

    expect(result.current.coords).toBeNull()
  })
})
