### Pre-soft-launch third-party sweep — 28 Aug 2026 (05:06–05:30 UTC, unattended)

**LAUNCH EVE. 1 day to soft-public (Fri 29 Aug) · 4 days to full launch (Mon 1 Sep) — RUL-001.
Verdict AMBER.** `THIRD_PARTY_LAUNCH_REGISTER.md` rewritten from this run's evidence.

The product is ready. Every functional probe is green, the ledger holds **180 locked fixes with 0
regressed**, all **59 rulings** are reflected, the legal documents are live and byte-in-sync, the
money rail answers, and sign-in works for strangers. **AMBER for one reason: the site goes public
with nothing watching it.**

- **RED, and it is two halves of one failure — both David's (RUL-037), neither code, neither needing
  a deploy.** (1) The **external uptime watcher** is built 22 Aug and **undeployed, day 6** —
  3 wrangler commands, `ops/cloudflare/UPTIME_MONITOR.md`, files verified on disk (RG-0138 · L8 · D4).
  (2) The **RED-alert Resend key is dead, day 3** — `/etc/marketsquare/resend.watch.conf` re-probed
  from the box at 04:39 UTC = **HTTP 400**, conf untouched (74 B, mtime `Aug 5 06:26`) (DW-076 · D3).
  Order matters: the key first, so the fresh one goes in with the watcher.
- **Every other historical RED is closed on a probe, not a file**: `/launch-api/prospects/list` 401 ·
  migrations `none pending` · full `script-src` CSP on `/` and `/terms` · port 22 open 3/3 · Google
  consent screen **In production** · **domain lifeline complete, RG-0137 LOCKED** (WHOIS re-probed:
  Cloudflare, expiry 2026-12-30 = 124 days, registrar lock ON, auto-renew ON).
- **Deploy debt is 4 commits and that number would have misled.** Zero of the 18 changed files appear
  in `deploy_manifest.txt` — no app behaviour is unpublished. The site Friday serves is `50c560b`
  (28 Aug 05:07 SAST). **No deploy is needed and none should happen on launch eve.**
- **`OPEN_LOOPS.md` corrected where probes overruled it** (backup beside it): it read "9 days to
  soft-public" (eight days stale) and named five blockers for 29 Aug, **four of them disproven by
  probes minutes earlier**. Its 🔴 BLOCKING NOW heading now states plainly that its only row (B1,
  secrets rotation) is discharged. The row itself stays until an attended reconciliation — that file
  has no compiler and edits stay additive.
- **Instrument note, second session running (LEDGER-DEPS-1):** the ledger's first run exited **2**
  with RG-0181/RG-0182 `NOT EVALUATED` on a missing `fastapi`. RG-0187's honest demotion and
  yesterday's LEDGER-UNVER-CAUSE-1 cause-naming both worked exactly as designed — but naming a blind
  spot is not knowing the answer. Installed `fastapi 0.141.1`, re-ran **exit 0, 0 UNVERIFIED**. Two
  consecutive sandbox sessions have now paid this by hand; the message already names the remedy, so
  it is recorded rather than re-engineered on launch eve.
- **RG-0198 deliberately not fixed** (anonymous `/dashboard/summary` still serves the internal
  engineering narrative). The honest fix is two-sided and its console half is unverifiable from this
  vantage; changing a live endpoint both operator dashboards read with no credential, on the eve of
  soft-public, is how a console goes dark unwatched over a launch weekend. It stays asserting.
- **Overdue, non-blocking:** Paystack 2FA (reminder was 27 Aug, not done) · Gemini key (funds
  expected ~25 Aug; photo anonymisation stays reject-only, RUL-033).
