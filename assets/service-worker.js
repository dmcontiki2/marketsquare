/* TrustSquare service worker — handles Web Push for the Wishlist Feed.
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

/* SW-FETCH-1 (12 Sep 2026): Chrome will not fire beforeinstallprompt -- the one-tap
 * "add to home screen" -- unless the worker has a REAL fetch handler. It dropped that
 * requirement for installing from the browser MENU (v108 mobile / v112 desktop) but
 * KEPT it for the automatic prompt, and the prompt is the whole point.
 *
 * Deliberately the smallest handler that is honest work and cannot serve anything
 * stale: NOTHING IS EVER CACHED. Only top-level navigations are intercepted, they go
 * straight to the network, and the only time this worker answers for itself is when
 * the network has already failed -- in which case the browser would have shown its own
 * error page anyway. Every other request (the app bundle, the API, images, POSTs) is
 * left completely untouched: no respondWith, no interception, no behaviour change.
 *
 * Do not "improve" this into a cache without a ruling. A caching worker decides which
 * version of the app a phone runs, and that is a design decision, not a tidy-up.
 *
 * Proven in headless Chromium before it was deployed: registers and takes control;
 * navigation, a 302 redirect, a POST and an image all behave exactly as before; with
 * the server killed a navigation returns this card (503) instead of the browser's
 * error page; with the server back the real page returns and nothing is stale.
 */
const OFFLINE_HTML = '<!doctype html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>TrustSquare \u2014 offline</title><style>' +
  'body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;' +
  'background:#000;color:#fff;font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;' +
  'text-align:center;padding:24px;box-sizing:border-box}' +
  '.w{max-width:22rem}h1{font-size:1.25rem;margin:0 0 .5rem;color:#22C55E}' +
  'p{margin:0 0 1.25rem;color:#cbd5e1}' +
  'button{font:inherit;background:#22C55E;color:#04210f;border:0;border-radius:999px;' +
  'padding:.7rem 1.6rem;font-weight:600}</style></head><body><div class="w">' +
  '<h1>No connection</h1><p>TrustSquare needs the internet for this page. ' +
  'Your phone is offline right now.</p>' +
  '<button onclick="location.reload()">Try again</button>' +
  '</div></body></html>';

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // Only top-level page loads. Everything else is none of this worker's business.
  if (req.method !== 'GET' || req.mode !== 'navigate') return;
  event.respondWith((async () => {
    try {
      // fetch(req) preserves the navigation's redirect mode, so 301/302 still work.
      return await fetch(req);
    } catch (err) {
      return new Response(OFFLINE_HTML, {
        status: 503,
        headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' },
      });
    }
  })());
});

self.addEventListener('push', (event) => {
  let data = { title: 'TrustSquare', body: 'New match in your wishlist' };
  if (event.data) {
    try { data = event.data.json(); }
    catch (_e) { try { data.body = event.data.text(); } catch (_e2) {} }
  }
  const opts = {
    body:  data.body || 'New match in your wishlist',
    // SW-ICON-1 (12 Sep 2026): these pointed at /icon-192.png, which 404s -- the
    // icons live under /static/brand/. Every push that fired would have shown a
    // blank generic bell instead of the TrustSquare mark.
    icon:  '/static/brand/icon-192.png',
    badge: '/static/brand/icon-192.png',
    tag:   data.match_id ? ('match-' + data.match_id) : 'match',
    renotify: false,
    data: { match_id: data.match_id || null },
  };
  event.waitUntil(self.registration.showNotification(data.title || 'TrustSquare', opts));
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
