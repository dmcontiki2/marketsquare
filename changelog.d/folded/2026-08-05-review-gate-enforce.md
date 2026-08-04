## 2026-08-05 — The reviewer token is now ENFORCED at the origin (GATE-ENFORCE-1)

**David's ruling:** proper token gate for the testers (chosen over a country-IP allowlist, which the
Peer review said is not authentication).

**The gap this closes.** `/review/login` issued a proper bcrypt-checked, separately-signed 14-day
token, but nothing enforced it — nginx served the page and API without checking, so the "pre-launch"
screen was a client-side curtain only. This makes the token real.

**Two coupled changes:**

1. `bea_main.py` (GATE-ENFORCE-1): `/review/login` now also sets an HttpOnly, Secure, SameSite=Lax
   `ts_review` cookie (a top-level navigation cannot carry the X-Review-Token header, so a cookie is
   required for nginx to gate). `/review/verify` accepts the token from the header OR the cookie.
   Client unchanged — the existing curtain already POSTs the code; browsers send the cookie
   automatically on same-origin requests.

2. `migrations/007_review_gate_enforce.py`: adds `auth_request -> /review/verify` on the API
   catch-all in the live nginx config. Exempt (never gated): `/review/login`, `/review/verify`,
   `/health` (deploy rollback), `/payment/webhook` (Paystack), `/.well-known/` (certbot). Backs up
   the config, runs `nginx -t`, auto-rolls-back on failure. Idempotent.

**Scope decision:** gates the DATA API, not the static page shell. The shell holds no data
(everything sensitive is fetched through the now-gated API), so gating it adds deploy risk with no
confidentiality gain. Document-gating can be added later if wanted.

**Deploy order (safety):** the deploy places app code + restarts BEFORE post_deploy runs migration
007, so cookie-setting is live before the gate turns on — no lockout window. Expect data endpoints
(e.g. /wonders) to return 401 in any post-deploy smoke test: that is the gate working, and /health
stays 200 so auto-rollback is unaffected.

**Then:** once verified from David's (allowlisted) browser, the Cloudflare IP-only WAF rule is
relaxed so testers can reach the gate from anywhere; the origin firewall (RG-0028) still ensures
only Cloudflare reaches the box, and the app gate still ensures only the reviewer code gets data.
Testers' instructions are unchanged (open trustsquare.co, enter the code).

**Ledger:** RG-0029 to be added asserting an unauthenticated data endpoint returns 401 while /health
returns 200 (once deployed).
