## 2026-08-28 — Pre-soft-launch third-party sweep: launch eve, AMBER, RED list down to two

**1 day to soft-public (Fri 29 Aug) · 4 days to full launch (Mon 1 Sep) — RUL-001.**

Daily `pre-soft-launch-third-party-check` run, 05:06–05:30 UTC. `THIRD_PARTY_LAUNCH_REGISTER.md`
rewritten from this run's evidence.

**Verdict AMBER.** Every functional probe green; the RED list is two items that are the same failure
twice — **on the first weekend strangers use the site, nothing is watching it and nothing can wake
David.** Both are David's under RUL-037, neither is code, neither needs a deploy:

1. **External uptime watcher — built 22 Aug, undeployed, day 6.** RG-0138 · OPEN_LOOPS L8 ·
   DAVID_QUEUE D4. Three wrangler commands, `ops/cloudflare/UPTIME_MONITOR.md`; worker/toml/runbook
   all verified present on disk this run.
2. **RED-alert Resend key dead, day 3.** `/etc/marketsquare/resend.watch.conf` re-probed from the box
   04:39 UTC = **HTTP 400**; conf unchanged, 74 B, mtime `Aug 5 06:26`. DW-076 · D3. *Register had
   said `401` since 26 Aug; today's measured `400` supersedes it — both mean refused.* Do this first
   so the fresh key goes in with the watcher.

**Everything this register ever called RED is otherwise closed on a live probe:**
`/launch-api/prospects/list` → 401 · migrations `none pending` (post_deploy `2026-08-28T03:08:38Z`) ·
full `script-src` CSP on `/` and `/terms` · port 22 open 3/3 · Google consent screen **In production**
(27 Aug) · domain lifeline complete, **RG-0137 LOCKED** (WHOIS re-probed: Cloudflare, expiry
2026-12-30, 124 days, registrar lock ON, auto-renew ON, DNSSEC unsigned).

**Executed this run — three things done rather than reported:**

- **The ledger's `fastapi` blind spot cleared, not tolerated.** First run exited **2** with RG-0181
  and RG-0182 `NOT EVALUATED` — the harness dies at its import line and runs zero assertions.
  Yesterday's LEDGER-UNVER-CAUSE-1 named the cause honestly and worked exactly as designed, but
  **naming a blind spot is not knowing the answer.** Installed `fastapi 0.141.1`; board re-ran
  **exit 0 · 192 entries · 180 holding · 0 REGRESSED · 12 open · 0 UNVERIFIED**. On launch eve,
  "two entries could not be checked" is not a reportable state.
- **`OPEN_LOOPS.md` corrected where probes overruled it** (backup kept). It read **"9 days to
  soft-public"** — written 20 Aug, eight days stale — and its 🔴 BLOCKING NOW note named five things
  as blocking 29 Aug, **four disproven by probes minutes earlier**. Now states the day count, names
  the two real threats, and says plainly that its only printed row (B1, secrets rotation) is
  **discharged** — a section headed BLOCKING NOW on launch eve, about work finished 22 Aug, is the
  exact rot this sweep exists to kill. B1's row stays physically in place (no compiler on that file;
  edits stay additive, CHANGELOG-COLLISION-1 class) and moves at the next attended reconciliation.
- **Deploy debt re-read against the manifest instead of counted.** `origin/deploy..HEAD` = 4 commits,
  which on launch eve reads like fresh debt. **Zero of the 18 changed files are in
  `ops/autodeploy/deploy_manifest.txt`** — registers, DAILY_WATCH, changelog.d, scripts, two doc HTMLs.
  The site Friday serves is `50c560b` (released 28 Aug 05:07 SAST) and already carries everything
  user-facing. **No deploy needed; none should happen on launch eve.**

**Deliberately NOT fixed: RG-0198** (anonymous `/dashboard/summary` still serves the internal
engineering narrative). The honest fix is two-sided — consoles start sending the admin key, anonymous
payload withholds the narrative fields — and the console half cannot be verified from this vantage.
Changing a live endpoint both operator dashboards read with no credential, on the eve of soft-public,
is how a console goes dark unwatched over a launch weekend. It stays asserting in the ledger.

**Overdue and worth David's eye:** Paystack 2FA (reminder was 27 Aug, not done) and the Gemini key
(funds expected ~25 Aug; photo anonymisation stays reject-only, RUL-033). Neither blocks Friday.

**Board:** ledger exit 0 · 192/180 holding · 0 REGRESSED · 12 open · `rulings_check` 59/0 FAIL/0 WARN ·
`eula_sync --check` in sync 117,749 B · `check_canon_pointers` ALL IN LINE · `david_queue` 12 items,
11 open · TLS 85 days · BIT 8/8 PASS.
