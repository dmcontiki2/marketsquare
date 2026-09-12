## 2026-09-12 — Push was dead at the front door, and the install prompt was never going to fire

David: *"there's a fault sitting in it right now, and it means push is currently dead — please fix
this one."* It is fixed, and fixing it turned up a second fault sitting behind it.

### The fault: the service worker was never being served

Every browser push registration starts by fetching `/service-worker.js` from the site root. That
path was returning **HTTP 404 with `content-type: application/json` and `content-length: 22`** —
which is the app's `{"detail":"Not Found"}`, not nginx's. The request was reaching FastAPI, so the
file was never being served at all.

The file was on the server the whole time (`/var/www/marketsquare/service-worker.js`, 1 659 bytes,
readable), the nginx root was right, and the deploy manifest mapped it correctly. The cause was in
the nginx config: **every root-level static file is served through its own explicit
`location = /file` block, and this one had never been given a block.** With no block the path fell
through to the app proxy.

Why nobody noticed: a failed worker registration lands in a `.catch` and the user sees nothing. No
error, no banner — just a phone that never buzzes. Anyone whose browser still held an older cached
copy kept working, which is exactly how a fault like this stays invisible.

### The fix, and the proof

A `location = /service-worker.js` block was added (SW-ROOT-1), with `Service-Worker-Allowed: /` so
the worker's scope covers the whole app. Config backed up, `nginx -t` passed, nginx reloaded.

Verified, not assumed:

- **Origin, direct:** HTTP 200, `application/javascript`, 1 659 bytes, the real worker body.
- **Through Cloudflare:** HTTP 200, `application/javascript`. The edge had been caching the 404; it
  revalidated on its own, so no purge was needed.
- **In a real browser on the live site:** the worker **registers**, `navigator.serviceWorker.ready`
  resolves, scope is `https://trustsquare.co/` — the whole app — the worker reaches `active`,
  `PushManager` is present, and the VAPID public key endpoint returns an 87-character key.

The one leg that cannot be proven from here is the actual buzz, because granting notification
permission is a tap on a real phone. That is David's test.

### The second fault, found behind the first

While answering David's long-standing add-to-home-screen question, the same class of check was run
against the install path. Two things were wrong:

- **The web app manifest had no `start_url` and no `scope`.** Chrome's install prompt wants them.
  Added, along with `id`. The manifest also existed **only on the server** — there was no copy in
  the repo — so one was saved at `assets/brand/site.webmanifest`, and the `?v=` cache-buster was
  bumped to 5 so the one-year `immutable` browser cache on the old URL could not keep serving the
  old file.
- **The service worker has no `fetch` handler.** Chrome dropped that requirement for installing
  from the browser *menu* (v108 mobile, v112 desktop) but **kept it for the automatic install
  prompt** — and the prompt is the whole point, because it is what lets the install be offered at a
  chosen moment with a single tap. This is left OPEN rather than patched, because a fetch handler is
  a caching decision and must be designed, not slipped in.

### Also checked while in there

Forty-six root-level files were compared against the nginx blocks. `privacy.html` and `terms.html`
404 at the `.html` spelling but are served correctly by the app at `/privacy` and `/terms`, so
nothing is broken there. `db.sqlite3`, `bea_main.py`, `auth.py` and `.env` all sit inside the web
root directory but have **no** location block, so they fall through to the app and return 404 — not
exposed. The fall-through that broke push is the same behaviour that keeps those private.

### Ledger

- **RG-0356 — LOCKED.** `/service-worker.js` answers 200 as JavaScript, carries a push handler, is
  not an HTML fallback, and the repo nginx copy still carries the SW-ROOT-1 block. Proven red first:
  run against the pre-fix values it failed on both the status and the JSON content-type, and a live
  control path with no block reproduced the same 404 + `application/json` signature.
- **RG-0357 — LOCKED.** The manifest is served as `manifest+json`, parses, and carries name,
  short_name, start_url, scope, `display: standalone` and working 192/512 icons, and the front page
  still links it. Proven red against the pre-fix manifest text.
- **RG-0358 — OPEN.** The worker has no fetch handler, so `beforeinstallprompt` cannot fire. It goes
  green, and can be locked, the moment a fetch handler lands.

### Drift closed

`assets/nginx_marketsquare.conf` in the repo was a **stale 6 July snapshot**, 3 586 bytes against
the live config's 14 kB. It was refreshed straight from the server and headed with a note saying so,
after checking it carries no credentials — it references `.htpasswd` files but contains no secrets.
