## 8 Sep 2026 — DEVICE-AUTH-1: one login — an enrolled phone passes the ops Basic-auth gate

David, from the phone: *"when i want to view things inside the ops dashboard it asks for a new
password, is this really necessary, please remove it, we only need the first login?"*

**Fault:** DEVICE-ENROL-1 (3 Sep) enrolled the phone with a signed, revocable 180-day cookie, but only
the app honoured it (/m, /m/dashboard, /m/admin, CityLauncher). Every link out of the ops dashboard to
a page nginx fronts with Basic auth — /dashboard.html, /admin.html, /command.html, the Orchestration
cockpit, simulation, defence map, watch register — threw the browser's "Sign in to trustsquare.co"
box: a second password for a device the server had already recognised.

**Fix (`migrations/037_device_auth.py`, nginx only — the app side `GET /admin/device-ok` already
existed):** an internal `/_device_ok` location sub-requests the app with the visitor's cookies;
`snippets/internal_auth.conf` (already `satisfy any` + Basic) gains `auth_request /_device_ok;`, and
the six inline "TrustSquare Orchestrator" blocks gain `satisfy any; auth_request /_device_ok;`. Any
upstream ERROR (app down, timeout, 5xx) is mapped to 401 (`proxy_intercept_errors` + `error_page … =401
@device_deny`), so an outage falls back to Basic auth exactly as before — never a 500 on the ops pages.
Nothing is removed: the Basic credential works everywhere it did. Auctions (its own secret) and the
AdvertAgent dev realm untouched. The migration proves, after reload, that anonymous /dashboard.html
still answers 401 with a Basic challenge and that /admin/device-ok is alive and fail-closed.
