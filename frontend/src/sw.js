import { precacheAndRoute, createHandlerBoundToURL } from 'workbox-precaching'
import { NavigationRoute, registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'
import { ExpirationPlugin } from 'workbox-expiration'
import { CacheableResponsePlugin } from 'workbox-cacheable-response'

precacheAndRoute(self.__WB_MANIFEST)

// SPA offline navigation: any route (e.g. /article/42) falls back to the
// cached app shell instead of a browser-level 404 when offline.
registerRoute(new NavigationRoute(createHandlerBoundToURL('/index.html')))

// Matches both the local dev API and the deployed Render API — both are
// served under /api/ regardless of host. Authenticated requests (anything
// carrying a Bearer token — /users/me, /bookmarks, and the per-user
// is_bookmarked flags on /articles) are deliberately excluded: Workbox's
// cache key is the URL alone, so caching these would risk serving one
// logged-in user's personal data to a different user on the same shared
// device if a later request falls back to the stale cache entry offline.
// Excluded requests just pass through to the browser's normal network
// fetch, uncached — no route matches them here, so nothing intercepts them.
registerRoute(
  ({ url, request }) => url.pathname.startsWith('/api/') && !request.headers.has('Authorization'),
  new NetworkFirst({
    cacheName: 'insorts-api-cache',
    networkTimeoutSeconds: 10,
    plugins: [
      new CacheableResponsePlugin({ statuses: [0, 200] }),
      new ExpirationPlugin({ maxEntries: 200, maxAgeSeconds: 60 * 60 * 24 }),
    ],
  })
)

self.addEventListener('push', (event) => {
  let data = { title: 'Insorts News', body: '', url: '/' }
  try {
    data = { ...data, ...event.data?.json() }
  } catch {
    // Non-JSON push payload — fall back to the defaults above.
  }

  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/pwa-192x192.png',
      badge: '/pwa-192x192.png',
      data: { url: data.url },
    })
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/'

  event.waitUntil(
    (async () => {
      const clientsList = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
      const existing = clientsList.find((c) => new URL(c.url).pathname === url)
      if (existing) {
        existing.focus()
      } else {
        self.clients.openWindow(url)
      }
    })()
  )
})

self.skipWaiting()
self.addEventListener('activate', () => self.clients.claim())
