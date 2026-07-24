import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

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

export function usePushNotifications() {
  const [subscribed, setSubscribed] = useState(false)
  const [loading, setLoading] = useState(true)

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
        endpoint: subscription.endpoint,
        keys: {
          p256dh: bufferToBase64(subscription.getKey('p256dh')),
          auth: bufferToBase64(subscription.getKey('auth')),
        },
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
      await apiClient.delete('/push/subscribe', {
        data: {
          endpoint: subscription.endpoint,
          keys: {
            p256dh: bufferToBase64(subscription.getKey('p256dh')),
            auth: bufferToBase64(subscription.getKey('auth')),
          },
        },
      })
      await subscription.unsubscribe()
    }
    setSubscribed(false)
  }

  return { supported: isSupported(), subscribed, loading, subscribe, unsubscribe }
}
