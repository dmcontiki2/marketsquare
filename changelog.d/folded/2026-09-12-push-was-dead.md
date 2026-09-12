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

---

## Same day, second pass — David: *"I see open actions pushed for future David"*

He was right, and pushing them was wrong: the next thousand outreach emails would have landed on
the same dead functions. Both open items were closed in the same session, and closing them exposed a
worse fault than either.

### The service worker now has a fetch handler

The smallest handler that is honest work and **caches nothing**: only top-level page loads are
intercepted, they go straight to the network, and the worker only answers for itself when the
network has already failed — where the browser would have shown its own error page anyway. Every
other request (app bundle, API, images, POSTs) is untouched.

It was proven in a real headless Chromium **before** it went near the live site: registers and takes
control; navigation, a 302 redirect, a POST and an image all behave exactly as before; with the
server killed dead a navigation returns a proper offline card (503) instead of a browser error; with
the server back the real page returns and nothing is stale. Then verified again on the live site in
a real browser — the worker is active, controls the page, and a genuine navigation to `/privacy`
loads its full content through it.

A caching worker decides which version of the app a phone runs. This one deliberately does not, and
that is written into the file so nobody "improves" it into a cache without a ruling.

### The notification icon pointed at a 404

The worker asked for `/icon-192.png` for both the icon and the badge. That path 404s — the icons live
under `/static/brand/`. Every push that ever fired would have shown a blank generic bell instead of
the TrustSquare mark. Fixed, and the ledger now checks that whatever icon the worker names actually
loads.

### And then the real one: the server could not sign a push at all

Testing the send path end to end turned up a fault that had nothing to do with the web server.

`pywebpush` hands the private key to `py_vapid.Vapid.from_string()`, which strips newlines and
base64url-decodes **the whole string** — the `-----BEGIN PRIVATE KEY-----` header included. A PEM
therefore never parses. The app was passing exactly that. Every send raised
`ValueError: Could not deserialize key data` inside a bare `except Exception`, and the push
functions returned **zero delivered** with nothing above WARNING in the log.

So push was dead **twice over**: the worker was never being served, and even when it was, the server
could not sign a single message. Fixing only the first would have looked like a fix and changed
nothing.

The fix derives what the signer can actually read — the 32-byte private scalar, base64url, no
padding — once at bootstrap, on both the load path and the generate path, and hands that to both
send sites. The guards now test the sendable key rather than merely that a PEM was found on disk.

**Proven against Google's push service, not asserted:**

| | Result |
|---|---|
| PEM string (what the app was passing) | crashes before any network call |
| derived raw key | **HTTP 410** — *"push subscription has unsubscribed or expired"* |
| a `Vapid` object built from the PEM | HTTP 410 (the alternative fix; not taken) |

A 410 for a deliberately fake device is the push service **accepting the VAPID signature and the
encrypted payload** and simply not knowing that device. Everything upstream of the phone works.

After deploying, the same check was run again through the **running app's own module**: push library
available, sendable key present (43 characters, not a PEM), send → HTTP 410. The service's own
startup line now reads `VAPID keys loaded … (sendable=True)`.

### A deploy trap worth remembering

The first attempt to deploy this fix went nowhere. The repo file `bea_main.py` deploys to the server
as **`main.py`** — the server also carries a `bea_main.py`, which nothing runs. The file was copied,
the service restarted, and the startup line still showed the old wording. That mismatch is the only
reason it was caught; a report that stopped at "deployed and restarted" would have been false.

### Ledger

- **RG-0356 — LOCKED**, extended with a leg that the worker's notification icon actually loads. Its
  HTML-fallback leg was rewritten after it false-alarmed on the worker's own offline-card markup —
  the check being wrong, not the app, exactly as this file's header warns.
- **RG-0358 — now LOCKED.** The worker handles fetch.
- **RG-0359 — LOCKED.** The sender is handed a key form the signer can read, on both bootstrap
  paths, at both send sites, behind guards that test it. Proven red against the pre-fix source.

### The one decision left, and it is David's

The add-to-home-screen offer already exists and is wired to fire at the **first successful publish
handoff** — the seller's invested moment, ruled on 30 August. David's words were *"right at the
starting point of a user accepting it."* Those are two different moments. Nothing is being changed
without him: the offer now *works*, and where it fires is his call.
