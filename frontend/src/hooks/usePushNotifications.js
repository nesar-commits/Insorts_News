import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

const CATEGORY_PREFS_KEY = 'insorts_push_categories'

function urlBase64ToUint8Array(base64) {
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=')
  const raw = window.atob(padded.replace(/-/g, '+').replace(/_/g, '/'))
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)))
}

function bufferToBase64(buffer) {
  return window.btoa(String.fromCharCode(...new Uint8Array(buffer)))
}

function isSupported() {
  return 'serviceWorker' in navigator && 'PushManager' in window
}

function subscriptionInfo(subscription) {
  return {
    endpoint: subscription.endpoint,
    keys: {
      p256dh: bufferToBase64(subscription.getKey('p256dh')),
      auth: bufferToBase64(subscription.getKey('auth')),
    },
  }
}

// Backend source of truth is per-subscription (endpoint+keys), not
// per-account — there's no GET-by-ownership endpoint (deliberately: proving
// ownership via keys in a GET's query string is awkward), so the UI's own
// last-set preference just lives here. null means "every category",
// matching what a subscriber with no explicit preference gets server-side.
function loadStoredCategoryIds() {
  try {
    const raw = localStorage.getItem(CATEGORY_PREFS_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function usePushNotifications() {
  const [subscribed, setSubscribed] = useState(false)
  const [loading, setLoading] = useState(true)
  const [categoryIds, setCategoryIds] = useState(loadStoredCategoryIds)

  useEffect(() => {
    if (!isSupported()) {
      setLoading(false)
      return
    }
    navigator.serviceWorker.ready
      .then((registration) => registration.pushManager.getSubscription())
      .then((subscription) => setSubscribed(!!subscription))
      .finally(() => setLoading(false))
  }, [])

  const subscribe = async () => {
    if (!isSupported()) return false

    const permission = await Notification.requestPermission()
    if (permission !== 'granted') return false

    const registration = await navigator.serviceWorker.ready
    const { data } = await apiClient.get('/push/vapid-public-key')
    const subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(data.key),
    })

    try {
      await apiClient.post('/push/subscribe', {
        ...subscriptionInfo(subscription),
        category_ids: categoryIds ?? undefined,
      })
    } catch (err) {
      // The browser now holds a subscription the backend never recorded —
      // undo it rather than leaving an orphaned subscription that silently
      // never receives anything while the UI still thinks it's inactive.
      await subscription.unsubscribe().catch(() => {})
      throw err
    }
    setSubscribed(true)
    return true
  }

  const unsubscribe = async () => {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()
    if (subscription) {
      await apiClient.delete('/push/subscribe', { data: subscriptionInfo(subscription) })
      await subscription.unsubscribe()
    }
    setSubscribed(false)
  }

  const updateCategoryIds = async (newCategoryIds) => {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()
    if (!subscription) return

    await apiClient.put('/push/categories', {
      ...subscriptionInfo(subscription),
      // null and [] are different preferences server-side (every category
      // vs. explicitly none) — don't collapse them into the same payload.
      category_ids: newCategoryIds,
    })
    setCategoryIds(newCategoryIds)
    if (newCategoryIds === null) {
      localStorage.removeItem(CATEGORY_PREFS_KEY)
    } else {
      localStorage.setItem(CATEGORY_PREFS_KEY, JSON.stringify(newCategoryIds))
    }
  }

  return {
    supported: isSupported(),
    subscribed,
    loading,
    subscribe,
    unsubscribe,
    categoryIds,
    updateCategoryIds,
  }
}
