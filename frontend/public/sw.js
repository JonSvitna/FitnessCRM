/**
 * Service Worker for FitnessCRM PWA
 * Phase 6: Mobile & Integrations - M6.1: Progressive Web App
 */

const CACHE_NAME = 'fitnesscrm-v1';
const RUNTIME_CACHE = 'fitnesscrm-runtime-v1';

// Assets to cache on install
// Note: Don't hardcode asset paths as Vite hashes them in production
// Instead, cache dynamically as assets are requested
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

// Install event - cache assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell');
        // Only cache essential files that we know exist
        // Other assets will be cached on-demand via fetch handler
        return cache.addAll(PRECACHE_ASSETS.map(url => new Request(url, { cache: 'reload' }))).catch((err) => {
          console.warn('[Service Worker] Some precache assets failed:', err);
          // Don't fail installation if some assets can't be cached
          return Promise.resolve();
        });
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE;
          })
          .map((cacheName) => {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
    .then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip service worker and manifest requests (they're handled separately)
  const url = new URL(event.request.url);
  if (url.pathname === '/sw.js' || url.pathname === '/manifest.json') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        // Return cached version if available
        if (cachedResponse) {
          return cachedResponse;
        }

        // Otherwise fetch from network
        return fetch(event.request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200) {
              return response;
            }

            // Don't cache opaque responses (CORS)
            if (response.type === 'opaque') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            // Cache the response
            caches.open(RUNTIME_CACHE)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          })
          .catch(() => {
            // If network fails, try to return offline page
            if (event.request.destination === 'document') {
              return caches.match('/index.html');
            }
            // Return a basic error response for other failed requests
            return new Response('Offline', { status: 503, statusText: 'Service Unavailable' });
          });
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [200, 100, 200],
    tag: 'fitnesscrm-notification',
    requireInteraction: false
  };

  event.waitUntil(
    self.registration.showNotification('FitnessCRM', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked');
  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});

// Helper function to sync data when back online
async function syncData() {
  // This would sync any queued actions when back online
  // Implementation depends on your offline queue system
  console.log('[Service Worker] Syncing data...');
}

