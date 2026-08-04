## 2026-08-03 — The pre-launch gate becomes a door instead of a curtain (GATE-SERVERSIDE-1)

**David's ruling:** "close it immediately."

**The defect.** The "MARKETPLACE PREVIEW / Pre-launch access only" screen was never an access
control. It is a `<div id="admin-gate" style="display:none">` living inside `marketsquare.html`,
revealed by JavaScript — while nginx serves that file straight off disk
(`location = / { try_files /index.html }`). The complete page was therefore handed to anyone who
asked, with no credential checked, and JavaScript then painted a curtain over content that had
already arrived. View-source, `curl`, or simply disabling JavaScript read the entire marketplace.

Proven the same day: a page load with the gate showing and **no password entered** still returned
HTTP 200 on `/wonders`, `/flags`, `/local-market/listings`, `/geo/cities` and `/tuppence/balance`,
and executed every script in `<head>` — which is also precisely how the Travelpayouts loader ran
for every visitor regardless of the password.

**The fix.** `migrations/005_prelaunch_server_side_gate.py` adds nginx `auth_basic` to the five
document locations (`/`, `/rental.html`, `/dashboard.html`, `/admin.html`, `/command.html`), so
nginx refuses to send the bytes at all without credentials. Verified offline against the repo copy
of the site config: 5 locations gated, brace balance preserved, API catch-all untouched, idempotent
on re-run.

**Deliberately not gated** — gating these breaks the platform: the catch-all API proxy (keeps
`/health` alive, which `server_deploy.sh` health-checks and auto-rolls-back on, and keeps
`POST /payment/webhook` reachable for Paystack), `/.well-known/` (certbot), `/static/` and `/media/`.

**Arming is David's, by design.** The migration refuses to run without a password, so it can never
lock anyone out by accident. It exits non-zero when unarmed, so it is not recorded and retries on
the next deploy.

```
printf 'your-password' > /var/www/marketsquare/.prelaunch_pass && chmod 600 /var/www/marketsquare/.prelaunch_pass
```

Then deploy. Safety: backs up the site config, runs `nginx -t`, and restores the backup if the test
fails, so a bad edit can never leave nginx unable to start.

**Ledger.** `RG-0027` added as **OPEN** — it passes the moment an unauthenticated `GET /` returns
401, and flips to READY TO LOCK on its own. Scope stated honestly on the entry: documents only.

**Known remaining hole (phase 2).** The JSON API still answers unauthenticated. Closing it needs
per-path exemptions for `/health` and `/payment/webhook` handled one at a time, and is not covered
by this change or by RG-0027.
