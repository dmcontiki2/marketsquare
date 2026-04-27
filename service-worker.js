/* MarketSquare service worker — handles Web Push for the Wishlist Feed.
 * Served from site root (/service-worker.js) so its scope covers the whole app.
 *
 * Payload contract (set in bea_main._send_push_for_match):
 *   { title, body, match_id }
 *
 * No seller identity, no listing_id, no price — privacy by design (PR-35).
 */

self.addEventListener('install', (event) => {
  // Activate immediately so updated SW takes over without a tab reload
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', (event) => {
  let data = { title: 'MarketSquare', body: 'New match in your wishlist' };
  if (event.data) {
    try { data = event.data.json(); }
    catch (_e) { try { data.body = event.data.text(); } catch (_e2) {} }
  }
  const opts = {
    body:  data.body || 'New match in your wishlist',
    icon:  '/icon-192.png',
    badge: '/icon-192.png',
    tag:   data.match_id ? ('match-' + data.match_id) : 'match',
    renotify: false,
    data: { match_id: data.match_id || null },
  };
  event.waitUntil(self.registration.showNotification(data.title || 'MarketSquare', opts));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  // Focus the app or open a new tab — the feed surfaces the match anyway
  event.waitUntil((async () => {
    const all = await clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const c of all) {
      if (c.url.includes(self.registration.scope) && 'focus' in c) return c.focus();
    }
    if (clients.openWindow) return clients.openWindow('/');
  })());
});
