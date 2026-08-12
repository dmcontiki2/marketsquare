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

## 4. SSH to the server (you) - and the lockout that looks like a dead box

`ssh root@178.104.73.239` from PowerShell. Key is already at `C:\Users\David\.ssh\id_ed25519`.

**If it times out, DO NOT assume the server is down.** Diagnose in this order:

1. `curl https://trustsquare.co/health` - if it returns
   `{"status":"ok",...}` the server is UP and healthy. The problem is the firewall, not the box.
2. Get your current public IP (any IP-echo site, e.g. api.ipify.org).
3. Hetzner Console -> Firewalls -> `trustsquare-origin-lockdown` -> the port 22 rule.
   Add your current IP as a /32. Save. SSH works within seconds.

**Why it happens.** The Hetzner Cloud Firewall (ORIGIN-LOCKDOWN-1, 4 Aug 2026) allows TCP 22
from David's IP only. Your ISP rotates that address every so often, and a deny-all firewall
gives a TIMEOUT rather than a refusal - identical to what a crashed server looks like. Known
addresses so far: 197.185.169.80, 197.185.142.142, 197.185.155.69 (all 197.185.x.x).

**Do not "fix" this by widening the range.** Opening 197.185.0.0/16 would expose port 22 to
every other customer on that ISP block. RG-0028 depends on this firewall staying tight; the WAF
is decorative without it. Adding a /32 takes 30 seconds - do that instead.

**Note:** the Cowork sandbox egresses via David's public IP, so Claude's SSH dies and recovers
with David's. If a session says it cannot reach the server, check this rule before anything else.
