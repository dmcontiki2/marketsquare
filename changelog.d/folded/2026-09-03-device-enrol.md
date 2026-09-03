## 2026-09-03 — DEVICE-ENROL-1: David's phone opens the Ops Dashboard, Admin and CityLauncher with nothing to remember

**Asked:** David, 3 Sep: at work on his phone only the TrustSquare app worked — CityLauncher wanted the launch-api key, the Ops Dashboard and Admin want Basic-auth + PIN. "I did ask you to make it easy for me."

**Built (no nginx change — the Basic-auth paths are untouched, so nothing here can lock anyone out):** one QR scan enrols a phone. `GET /admin/enrol?t=<one-time, 20 min>` burns the token, sets a signed, revocable 180-day `ts_device` cookie (HttpOnly, Secure, SameSite=Lax) and lands on `/m` — a home-screen page with four big buttons. `/m/dashboard` and `/m/admin` serve the same deployed pages the gated paths serve, for enrolled devices only; the in-page gate now tries `/admin/device-token` first and mints its 8h admin JWT silently. CityLauncher's `require_launch_key` accepts the cookie in place of `X-Launch-Key` by asking the BEA on localhost (`/admin/device-ok`, 60 s cache, fail-closed). Devices listed/revoked at `/admin/devices` (admin token). Tokens minted server-side by `mint_enrol_link.py`.

**Trade-off stated:** the cookie is a bearer for the admin surfaces on that one phone for 180 days; revocation is one call, and the phone's own lock is the second factor. David's call to keep or shorten (`MS_DEVICE_DAYS`).
