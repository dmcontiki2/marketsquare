# TrustSquare — how to get in (as of 4 Aug 2026, gate live)

Three separate doors, by the app's own design. There is NOT one shared password.

## 1. Marketplace (trustsquare.co) — you AND the four testers
**GATE-EMAIL-1 (15 Aug 2026, ships with migration 019): the gate is now EMAIL-LINKED.**
- Tester enters their EMAIL on the gate screen -> one-time access link lands in their inbox
  (works once, expires in 30 min) -> click -> in, for 365 days (cookie). Nothing to remember.
- Who gets a link: only emails in `/var/www/marketsquare/review_emails.txt` (server file,
  one per line, re-read live — edit it to add/revoke a tester, no restart). Seeded: David x2,
  Maroushka, Maurice, Marietjie. Off-list emails get a silent "ok" and no mail (no enumeration).
- The reviewer code **TSR-86HV-ZR33** still works as BREAK-GLASS behind the "Have a code or
  admin password?" link on the gate screen — an email outage can never seal the gate.
- The old "locked out" class is also fixed at the root (GATE-COOKIE-2): the gate screen now
  checks the cookie itself, so a tester with a valid cookie is never re-asked for anything.
- The 8-attempts/10-min-per-IP limit covers link requests AND code tries. Heavy re-testing
  trips it; `systemctl restart marketsquare.service` clears it.

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

## State right now (updated 19 Aug 2026 — WAF-OPEN-1, RUL-034)
- Cloudflare edge OPEN: the "PRELAUNCH GATE - block all except allowlisted IPs" custom rule is
  DISABLED (kept in the CF dash as break-glass — re-enabling blocks ALL testers). Every visitor
  now reaches the ORIGIN gate; the email-link flow above is live and server-proven (link mail
  delivered to David's inbox in 1s, 19 Aug).
- Marketplace gated at the ORIGIN (GATE-ENFORCE-1 + GATE-EMAIL-1 allow-list) — the designed guard.
- Admin/dashboard exempt — WORKING (password door, RUL-015).
- Earlier note "WAF still CLOSED / testers NOT yet let in" is SUPERSEDED by this.

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
