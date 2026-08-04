# TrustSquare — how to get in (as of 4 Aug 2026, gate live)

Three separate doors, by the app's own design. There is NOT one shared password.

## 1. Marketplace (trustsquare.co) — you AND the four testers
- Enter the reviewer code **TSR-86HV-ZR33** once. Lasts 14 days (cookie). Never re-type it.
- If it "fails": it's a STALE BROWSER COOKIE, not the code/server (server returns 200 to the code).
  Fix: brand-new incognito, or clear site data for trustsquare.co, then enter the code once.
- There is an 8-attempts/10-min-per-IP brute-force limit. Heavy re-testing trips it; `systemctl
  restart marketsquare.service` clears it. Normal use (enter once) never hits it.

## 2. Admin + Dashboard — your admin password ONLY (NOT the reviewer code)
- These are exempt from the gate (GATE-EXEMPT-2). Open them directly, sign in with the admin password.
- Deliberately kept separate: the browse code must never grant admin control.

## 3. Your personal account — email + one-time sign-in link (no password)
- NOTE: /auth/* is currently BEHIND the gate. So to sign into your personal account you must enter
  the reviewer code first (step 1), THEN request your email link. Two steps.
- To remove that friction, we can exempt /auth/* from the gate (lets the public attempt account
  sign-in during pre-launch — fine for 4 testers). Not yet done.

## Simpler option for the testers (recommended when David is back)
Drop the reviewer code for testers entirely: allow-list their 4 IPs at Cloudflare so they just open
the site — nothing to type. Origin firewall (RG-0028) still blocks everyone else. Closest thing to
"no password, just works." Auditor-accepted as short-term containment.

## State right now
- Marketplace gated (public blocked, testers/you in with the code) — WORKING (server-proven).
- Admin/dashboard exempt — WORKING.
- Cloudflare WAF still CLOSED (only David's IP reaches the site). Testers NOT yet let in.
  Last step before testers can reach it: open/relax the WAF — do this only after David confirms
  his own browser login works cleanly.
