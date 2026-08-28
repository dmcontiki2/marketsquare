# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day was **Wed 27 Aug — PASSED.** Nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-28, 05:06–05:30 UTC (07:06–07:30 SAST) · TOMORROW IS SOFT LAUNCH — 1 day · verdict AMBER.**

*The whole platform is green on every probe run this morning, and the RED list is down to **two
items which are really one item twice**: nothing on earth would tell David the site had fallen over
during launch weekend. The watcher that would notice has been built since 22 Aug and undeployed for
six days; the alert key that would carry the news has been dead for three. Neither is code, neither
needs a deploy, and both are David's by RUL-037 — they are a Cloudflare login and an SSH paste.*

*Everything else that this register has ever called RED is now closed on a live probe: the migration
chain, the edge CSP, the anonymous-PII endpoint, SSH, the Google consent screen and the entire
domain lifeline. **Deploy debt carries no app behaviour** (4 commits, zero manifest files).*

Evidence grade on every row: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson (the register said Google OAuth was dark;
`/auth/providers` said otherwise; the probe won).

---

## MACHINE-READ FIELDS
*The regression ledger reads these lines directly. They stay red until a human fills them in — that is the point.*

```
DOMAIN_REGISTRAR: Cloudflare, Inc. (IANA ID 1910 · whois.registry.co · registrar lock ON, clientTransferProhibited)
DOMAIN_EXPIRY: 2026-12-30
DOMAIN_AUTORENEW: ON (read in the Cloudflare Registrations dashboard 2026-08-28; status Active)
DOMAIN_VERIFIED_ON: 2026-08-28
GOOGLE_CONSENT_SCREEN: PUBLISHED (In production · External · verification NOT required, no sensitive or restricted scopes) verified 2026-08-27
```
*Ledger: **RG-0137** (domain lifeline, LOCKED 28 Aug) · **RG-0139** (consent screen published).*

**RE-PROBED 28 Aug 2026 · `whois.iana.org` → `whois.registry.co`:** registrar **Cloudflare, Inc.**,
**Registry Expiry Date 2026-12-30T23:59:59.0Z — 124 days out**, status `clientTransferProhibited`
(registrar lock ON), nameservers `KOA.NS.CLOUDFLARE.COM` / `AINSLEY.NS.CLOUDFLARE.COM`,
**DNSSEC unsigned**. Registrar and DNS are the same party. `DOMAIN_AUTORENEW` = **ON** (read in
David's own Cloudflare dashboard 28 Aug: one domain, status Active, auto-renew toggle on).
**The domain lifeline is completely recorded and RG-0137 is LOCKED.** The silent-death risk this
register carried for a week is four months away, not days.

> **The method note is worth keeping.** Four consecutive sweeps declared these fields permanently
> machine-unanswerable, and the 26 Aug entry hardened that into canon. All four were *guessing RDAP
> hostnames* and reading 404s as proof the data did not exist; none asked the authority which server
> to use. `whois.iana.org:43 ← "co"` returns `refer: whois.registry.co`, and that server answers in
> about a second. **A negative result proves a negative only if the method was right.** Five wrong
> doors is not a locked building — the same shape as the 21 Aug Google-OAuth error this file exists
> to prevent.

*One discrepancy, recorded rather than reconciled:* WHOIS gives registry expiry as
**2026-12-30T23:59:59Z**; the dashboard displays **Dec 31, 2026**. Same instant, two timezones. The
register keeps the WHOIS value — the registry is the authority, the dashboard renders it.

---

## 🔴 RED — WHAT BLOCKS OR THREATENS 29 AUG

**One day out, the RED list is two items and they are the same failure twice: on the first weekend
real strangers use the site, nothing is watching it and nothing can wake David.** Both are David's
under RUL-037 (root on the box + credentials). Neither is code. Neither needs a deploy.

1. **External uptime watcher STILL NOT DEPLOYED — day 6** (RG-0138 · OPEN_LOOPS L8 · DAVID_QUEUE D4).
   Built 22 Aug, unblocked ever since, and it is the **only** RED that gets worse purely by waiting.
   The daily watch is desktop-bound and runs once at 06:30, so a closed laptop is a blind day; the
   RED-alert path is one SSH command to the same box that would be down. An edge-hosted watcher owes
   nothing to the box or the desktop. **3 wrangler commands, `ops/cloudflare/UPTIME_MONITOR.md`** —
   Cloudflare Worker, 5-min cron, 2-strike DOWN alert, recovery notice, daily heartbeat so a dead
   monitor cannot read as a healthy site. No new vendor, no cost. Files verified present on disk this
   run: `uptime_monitor_worker.js` (8,121 B), `uptime_wrangler.toml`, `UPTIME_MONITOR.md`.
   **Do it AFTER #2** so the fresh Resend key goes in with it.
2. **The RED-alert key is DEAD — day 3** (DW-076 · DAVID_QUEUE D3). The watch's separate Resend key
   in `/etc/marketsquare/resend.watch.conf` has been refused since the 22–23 Aug rotation orphaned
   it. **Re-probed from the box at 04:39 UTC today by the daily watch: HTTP 400 against
   `GET https://api.resend.com/domains`.** The conf file is unchanged for a third day — 74 B,
   `-rw-r----- root:msdeploy`, mtime still `Aug 5 06:26`. *Recorded discrepancy: this register has
   said `401 validation_error` since 26 Aug and today's probe measured `400`. Both mean refused; the
   probe's number is the one to trust and the older one is not re-asserted.* **The app's own email
   lane is unaffected** — different key, in `secrets.env`, sending fine. Not fixable from this
   vantage: the sandbox holds no SSH key.

**Nothing else is RED.** Every other item this register has ever escalated is closed on a probe run
this morning — see below.

### CLOSED — and re-verified live this run, not read off a file

- ~~**Anonymous PII on `/launch-api/prospects/list`**~~ — ✅ `401 {"detail":"X-Launch-Key required"}`. RG-0176 LOCKED.
- ~~**The migration chain is JAMMED**~~ — ✅ `/static/post_deploy_status.json` reads
  `generated_at 2026-08-28T03:08:38Z` · `seed ok` · `ladder_seed ok` · **`migrations ok — "none pending"`**.
- ~~**No `script-src` CSP at the edge**~~ — ✅ full policy served on **both** `/` and `/terms`, plus
  HSTS 31536000, `X-Frame-Options: SAMEORIGIN`, `X-Content-Type-Options: nosniff`.
- ~~**SSH down**~~ — ✅ origin port 22 **OPEN 3/3**, banner `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.1`.
- ~~**Google consent screen Published-or-Testing UNRECORDED**~~ — ✅ answered 27 Aug in the console:
  **In production** (published, not Testing), External, *"Verification is not required since your app
  is not requesting any sensitive or restricted scopes."* **Strangers can sign in tomorrow.**
  *Two residuals, neither blocking, both week-1:* the Audience page shows an OAuth user cap of
  **0/100** — that is the unverified-app cap and the console has just said verification is not
  required, so it should not bind; the symptom if it ever did would be sign-ins refusing at exactly
  100 users. And **branding is not shown**, so the consent screen displays the bare domain rather
  than the TrustSquare name and logo. Presentation, not function.
- ~~**Domain registrar / expiry / auto-renew UNRECORDED**~~ — ✅ **all four fields recorded**,
  RG-0137 **LOCKED**. Re-probed by WHOIS this run.
- ~~**Deploy debt**~~ — ✅ **carries no app behaviour.** See the next section — this is a change of
  reading, not a change of number.

### DEPLOY DEBT — 4 commits, and the number on its own would mislead

`git log origin/deploy..HEAD` = **4 commits** (`c908f7d` daily watch · `1d9efa7` D1 closed /
RG-0137 LOCKED · `1fec593` nightly checkpoint · `89882e1` DAVID-QUEUE-1). Yesterday it was zero, so
a bare count reads like fresh debt on launch eve.

**It is not.** Every changed path was checked against `ops/autodeploy/deploy_manifest.txt` (180
lines) this run and **not one of the 18 changed files is deployable**: they are registers,
`DAILY_WATCH/`, `DAVID_QUEUE.md`, `AUDIT_GLOBAL_QA/`, `changelog.d/`, `Records/`, `scripts/`,
`SESSION_COUNTER.json`, and two HTML files that are documentation, not app pages. **The site on
Friday is `50c560b`, released 28 Aug 05:07 SAST, and it already carries everything user-facing.**
No deploy is needed and none should happen on launch eve.

**AMBER, close behind:** RG-0198 (anonymous `/dashboard/summary` still serves the internal
engineering narrative) · RG-0180 (`connect-src` still `'self' https:` — but `script-src` now stops
anything executing, which was the load-bearing half) · RG-0173 (agency journey probe, still open).

## DAVID-ONLY ACTIONS, IN DATE ORDER
*Mirrors `DAVID_QUEUE.md` (12 items, 11 open — `python3 scripts/david_queue.py` prints the next one with its steps).*

| When | Days left | Action | Why only David |
|---|---|---|---|
| **NOW — before anything else** | **1** | 🔴 **Paste the current Resend key into `/etc/marketsquare/resend.watch.conf`** (keep `0640 root:msdeploy`). Dead 3 days, re-probed 400 today. RED #2 · D3 | Root on the box + credential |
| **NOW — immediately after** | **1** | 🔴 **Deploy the uptime watcher** — 3 wrangler commands, `ops/cloudflare/UPTIME_MONITOR.md`, then write `UPTIME_DEPLOYED.md`. RED #1 · D4 | Cloudflare token + Resend secret |
| **Overdue — was 27 Aug** | **−1** | Turn on **Paystack 2FA**. The reminder was yesterday and it did not happen. Paystack is the live money rail — the one account where a compromise costs money, not time. 3 minutes · D2 | Account security |
| **Overdue — was ~25 Aug** | — | Buy the budget-capped **Gemini** key and paste it to the server. Still absent; photo anonymisation stays **reject-only** (RUL-033). **Not a launch blocker** · D5 | Money + secret |
| **Launch flip (Fri/Mon)** | 1 | Activate **Resend $20/mo 50k tier** — pre-approved (B7), execution not a new decision. The free tier will not carry public volume · D6 | Spend |
| **Launch flip (Fri/Mon)** | 1 | **Launch special — on or off?** `launch_codes.enabled()` needs **all three** of `LAUNCH_SPECIAL_ENABLED`, `LAUNCH_CODE_SECRET` and `LAUNCH_SPECIAL_DEADLINE`. CityLauncher's `.env` has only the deadline (`2026-09-01`, set 27 Aug), so **the launch-special block is currently stripped from every outbound email.** Deliberately left off — switching on a customer-facing discount lane is launch scope, and `LAUNCH_CODE_SECRET` is an HMAC key · D7 | Launch scope + config |
| **Before 1 Sep** | 4 | **Renew or drop the Anthropic subscription.** RUL-013 time-boxes Fable to 1 Sep, "does not renew by default". **The successor is decided AND wired — re-verified on disk this run:** RUL-013 names it and `ai_provider.py:63` reads `"design":"gpt-5.6-sol"`, Scaleway standby. **Nothing is unbuilt.** Purely the subscription question · D8 | Spend |
| **Once** | — | One smallest-pack **Paystack** buy, close the tab mid-flow → closes the detached-credit E2E. `/payment/test` → `paystack_connected: true` re-probed today · D9 | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → settles free-500-vs-$1.10-from-call-one. **Re-probed this run: lane ARMED** (`available:true`, `price_t:1`, *"READY — sellers can buy a check"*) and **still no real NPR query has ever run.** RG-0136 reads `[ ok ]` because it asserts the SAFETY properties (a PARTIAL_MATCH never passes, a provider failure never charges, the tick never gates an introduction); the billing shape is unanswerable without one live check · D10 | Real money |
| **David picks the moment** | — | **Travelpayouts tours resubmit.** Declined twice, latest 24 Aug (26 available / 20 blocked incl. Booking.com, Viator, GetYourGuide). RUL-041 bars an unchanged resubmit — **tomorrow's soft launch is the first materially changed face** · D11 | Commercial |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`). Rotation residue, not blocking · D12 | Rotation residue |
| **Week 1, not now** | — | Re-read the **Google OAuth user cap** (Audience showed 0/100) and consider turning on **consent-screen branding** | Console login |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software — RUL-023, "not optional and not deferrable") | Engagement + spend |
| ~~DONE 28 Aug~~ | — | ✅ ~~`DOMAIN_AUTORENEW`~~ — **ON**, status Active. **RG-0137 LOCKED, domain lifeline complete.** Nothing was changed; the toggle was already on · D1 closed | Was a Cloudflare login |
| ~~DONE 27 Aug~~ | — | ✅ ~~Google consent screen~~ — **In production**, External, verification not required | Was a console login |
| ~~DONE 26 Aug~~ | — | ✅ Hetzner firewall IP · ✅ `LAUNCH_API_KEY` · ✅ `.secrets/hetzner_token.txt` populated (self-heal armed, RG-0188 `[ ok ]`) — all re-probed holding | — |

## PROBED THIS RUN — the live facts (28 Aug 2026, 05:06–05:30 UTC)

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · `TrustSquare BEA` · **v1.3.1** · db primary present (2,879,488 B), integrity **ok** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id `869589580243-…`, `redirect_uri=https://trustsquare.co/auth/oauth/google/callback`, scope `openid email profile` | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `price_t:1` · *"READY — sellers can buy a check"* | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, `failing: []`. Includes `B-NEG-AUTH` (S1) = **PASS, HTTP 401** and `B-FEA-EXAMPLE` = PASS (10 endpoints) | PROBED |
| `GET /flags` | 200 anonymous (gate deliberately down, RUL-034). `ai_provider.active: openai` · `funnel.card_version 2026-08-26.1` (current) · `data.flights true`, `places/mapbox/ops false` | PROBED |
| `GET /launch-api/prospects/list` | **401 `X-Launch-Key required`** — holding | PROBED |
| **CSP on `/` and `/terms`** | ✅ **Identical full policy on both** — `default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; style-src …; img-src 'self' data: blob: https:; connect-src 'self' https:; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'`. Plus HSTS 31536000, SAMEORIGIN, nosniff | PROBED |
| `/static/post_deploy_status.json` | `generated_at` **`2026-08-28T03:08:38Z`** · `ref: deploy` · seed ok · ladder_seed ok · **migrations ok, "none pending"** | PROBED |
| `GET /dashboard/summary` | 200 anonymous. `currentSession 180`, generated `28 Aug 2026 · 05:12 UTC`. Still serves `lastDone`, `nextGoals`, `priorityItems`, `recentChangelog` verbatim, plus live counts (**104 listings · 59 sellers · 115 introductions**) → **RG-0198 still open** | PROBED |
| origin port 22 (`178.104.73.239:22`) | **OPEN — 3/3**, `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.1` | PROBED |
| TLS certificate | valid to **2026-11-22 02:55 GMT (85 days)**, Google Trust Services WE1 | PROBED |
| WHOIS `whois.registry.co` | Cloudflare, Inc. · expiry **2026-12-30 (124 days)** · `clientTransferProhibited` · KOA/AINSLEY NS · **DNSSEC unsigned** | PROBED |
| Resend RED-alert key | **HTTP 400 — refused, day 3.** Probed from the box 04:39 UTC by the daily watch (this sandbox has no SSH key) | PROBED (by daily watch) |
| `regression_ledger.py` | **exit 0** · **192 entries · 180 holding · 0 REGRESSED · 12 open · 0 READY TO LOCK · 0 UNVERIFIED** *(first run exited 2 — see below)* | EXECUTED |
| `rulings_check.py` | **59 rulings, 0 FAIL, 0 WARN** (was 58 on 27 Aug) | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies | EXECUTED |
| `check_canon_pointers.py` | **ALL IN LINE ✓** — docs ↔ `canon.yml` agree, mirrors identical, `eula = v1.15` on both sides | EXECUTED |
| `david_queue.py` | 12 items, **11 open**, exit 0; every item carries a usable VERIFY | EXECUTED |
| `git log origin/deploy..HEAD` | **4 commits — but 0 of 18 changed files are in `deploy_manifest.txt`.** No app behaviour is unpublished | EXECUTED |

### EXECUTED THIS RUN — what Claude did rather than reported

1. **The ledger's `fastapi` blind spot was cleared instead of being tolerated.** The first run this
   morning exited **2** with RG-0181 and RG-0182 `NOT EVALUATED` — the harness dies at its import
   line on a machine without `fastapi`, so those two entries ran **zero** assertions. Yesterday's
   fix (LEDGER-UNVER-CAUSE-1) made the summary name the real cause honestly, which worked exactly as
   designed; **naming it is not the same as knowing.** `fastapi 0.141.1` was installed into this
   sandbox and the board re-run clean: **exit 0, 0 UNVERIFIED.** On the day before soft launch, "we
   could not check two entries" is not an acceptable state to report. *Sandbox-local — it does not
   persist to David's machine and does not need to; the point is that the answer is now known.*
2. **`OPEN_LOOPS.md` corrected where probes overruled it** (backup kept beside it). It carried
   **"9 days to soft-public"** — written 20 Aug and eight days stale — and a 🔴 BLOCKING NOW note
   naming five things as what blocks 29 Aug, **four of which were disproven by probes minutes
   earlier** (the anonymous-PII endpoint, the migration jam, the missing CSP, SSH down). It now
   states the day count correctly and names the two real threats. The heading also now says plainly
   that its only printed row (B1, secrets rotation) is **discharged** — a file whose top section
   reads "BLOCKING NOW" on launch eve, about work finished on 22 Aug, is precisely the rot this
   sweep exists to kill. *B1's row was left physically in place: that file has no compiler and edits
   stay additive (CHANGELOG-COLLISION-1 class), so it moves at the next attended reconciliation.*
3. **Deploy debt re-read against the manifest rather than counted.** 4 commits looked like fresh
   launch-eve debt; checking each path against `deploy_manifest.txt` showed none is deployable. The
   *number* would have sent David to deploy on launch eve for nothing.

### NOT DONE, DELIBERATELY — RG-0198, and the reason is on the record not in someone's head

`GET /dashboard/summary` still answers an anonymous stranger with today's internal engineering
changelog verbatim, the session number, live counts, and a `priorityItems` list. RG-0144's security
half is fixed and holding (`redacted: "posture"`); this is the confidentiality half, split into its
own entry so it cannot ride on RG-0144's coat-tails.

**It was not fixed today and should not be.** The honest fix is two-sided — the operator consoles
start sending the admin key, and the anonymous payload keeps its operational fields while the
narrative fields return withheld — and the second side cannot be verified from this vantage without
loading the consoles. POSTDEPLOY/POSTURE-REDACT-1's own comment records that *both* operator
dashboards fetch this endpoint with no credential. **Quietly changing a live endpoint the operator
console reads, on the eve of soft-public, is how a console goes dark unwatched over a launch
weekend** — and it would need a deploy, which launch eve does not get. It is in the ledger, where it
keeps asserting until it is done.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. `/payment/test` → **`paystack_connected: true`** (re-probed today). Webhook secret armed, RG-0091 LOCKED. 🟠 **2FA still not set up — the reminder was yesterday, 27 Aug** | PROBED | 2.9% + R1 | No — but 2FA is overdue and the E2E close-out remains |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, BACKLOG A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving — `/flags` shows `ai_provider.active: openai`, card version current (`2026-08-26.1`). **No production golden run on record** (RG-0132 open): run `scripts/golden_seam_v2.py` on the box with the production key | PROBED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013 — "ENDS 1 Sep 2026 and does not renew by default"). **Successor decided AND wired — re-verified on disk this run:** RUL-013 names the `design` tier successor and `ai_provider.py:63` reads `"design":"gpt-5.6-sol"`, Scaleway standby. Only the renewal is open, and it is a spend question | READ (code) | No |
| **Gemini** | 🟠 **Key still ABSENT** — funds were expected ~25 Aug. Photo anonymisation stays **reject-only** (RUL-033); RG-0121 OPEN by design. Price row first-party ($0.75 in / $3.75 out); canary year-1 $845, ~51% cheaper than terra-only. **A re-cost, not a re-decision — RUL-032 stands** | READ | Indirectly — reject-only until the key lands |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with a real client_id (re-probed today). RG-0111 LOCKED. **Do not re-raise this lane** | PROBED | No |
| **Google consent screen** | ✅ **PUBLISHED — "In production"**, External, verification not required (no sensitive/restricted scopes), read in the console 27 Aug. **Strangers can sign in tomorrow.** Residuals for week 1: OAuth user cap displayed 0/100; branding not shown | READ (console, 27 Aug) | No |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing (re-probed). Never re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1` (re-probed). **Still no real NPR query has ever run**, so the billing shape and the real-registry outcome mapping are both untested. One real check is on David's once-list (D10); RG-0136 stays open on the billing question | PROBED | No (never a blocker by RUL-039) |
| **Resend** (app sending) | Sending live, free tier. `mail.trustsquare.co` verified, root domain not. **The ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1) — settled, do not re-raise. $20 tier flips at launch (D6) | PROBED (22 Aug) | Operationally yes — it carries sign-in |
| **Resend** (RED-alert watch key) | 🔴 **DEAD — day 3.** Separate key, `/etc/marketsquare/resend.watch.conf`, **HTTP 400 re-probed from the box 04:39 UTC today**, conf unchanged (74 B, mtime `Aug 5 06:26`). **RED #2 · DW-076 · D3.** *Two different credentials from the app key — do not merge them again* | PROBED (from box) | **Yes, operationally** |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug. Still sends from a personal address | PROBED (22 Aug) | Presentation risk at public launch |
| **support@trustsquare.co** | ✅ RG-0174 LOCKED: inbound routes to the SUPPORT pipeline, ONE reply per inbound, personal inbox is dead-letter only | EXECUTED | No |
| **RED-alert channel** | 🔴 **Transport restored, key still dead.** SSH is back (port 22 open 3/3 today), so the channel no longer shares a failure with its own transport — but the key it sends with is refused, so it still cannot deliver. DW-073 + DW-076. **The uptime watcher (RED #1) is the structural answer to both** | PROBED | **Yes, operationally** |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8, the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live and serving. **Single point of failure.** Port 22 open 3/3 (re-probed). ✅ Firewall self-heal **ARMED** — `.secrets/hetzner_token.txt` populated, RG-0188 `[ ok ]`. Account has **no 2FA** (noted in passing). Disk 45% used / 40 G free | PROBED | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention. ("HETZNER_S3" keys are actually Cloudflare R2 — SECRETS_REGISTER) | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email/registrar) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034); origin gate down by pre-launch posture (`/flags` 200 anonymous — expected). Also the **registrar** — see MACHINE-READ FIELDS | PROBED | Free | No |
| **SSL** | ✅ valid to **2026-11-22 (85 days)**, Google Trust Services WE1 | PROBED | Free | No |
| **Domain registrar** | ✅ **Cloudflare, Inc. · expires 2026-12-30 (124 days) · auto-renew ON · registrar lock ON.** Fully recorded, **RG-0137 LOCKED**. *DNSSEC unsigned — noted, not raised: it is a hardening option, not a launch item* | PROBED | Included | No |
| **GitHub** | Live. Deploy debt 4 commits, **none deployable** — see above | EXECUTED | Free | No |
| **External uptime monitor** | 🔴 **BUILT 22 Aug, NOT DEPLOYED — day 6.** RG-0138. **RED #1** | EXECUTED (source) | Free | See RED #1 |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data.flights: true` on `/flags`, re-probed
today; token UNROTATABLE-ACCEPTED), Numista (rotated key; RG-0150 polices the data boundary), and the
free keyless set (OSM, Scryfall, Wikidata, Frankfurter, FX per RUL-022).
**Tours: DECLINED 24 Aug** (*"website under development or not yet ready"*) — 26 available / 20
blocked, incl. Booking.com, Viator, GetYourGuide. Per RUL-041 never resubmit unchanged; **David picks
the resubmit moment and tomorrow's soft launch is the first materially changed face.** Aviasales
flights unaffected. Drive loader stays OFF (RG-0025 inverted — no third-party script on any app page).
**Affiliate lane:** `travelpayouts_partners.py` (TP-LINKOUT-1) — server-side link-out, host allowlist,
fails closed, dark by flag. RG-0181 asserts the invariant; the lane being dark is deliberate, not a defect.
**Deliberately dark:** JustTCG (key valid, UNSET — free tier is non-commercial), Duffel, AeroDataBox,
Mapbox (`data.mapbox: false`), GeoNames, Places (`data.places: false`).
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink.
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.15 IS LIVE** — `/terms` serves v1.15 (re-probed today). Three copies byte-in-sync, 117,749 B. `canon.yml` and `LEGAL_VERSIONS.md` agree (`check_canon_pointers.py` ALL IN LINE) | PROBED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists and is exempted at origin (migration 021); BACKLOG A1 still lists it open | READ | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | **Formally deferred to the first post-launch week (from Mon 8 Sep)** by David 21 Aug. Not a gate. *David's veto point stands: if any single CC-002 item must land before launch, name it and it lands on its own* | READ | Deferred by ruling |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (RG-0147, LOCKED).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
4. **`BACKLOG.md`'s header still reads "Updated S140 · 18 June 2026"** and `LEGAL_VERSIONS.md`'s
   reads "Updated: 14 August 2026" while its content is dated 21–23 Aug. Both bodies are current;
   only the headers rot. Noted, not edited — neither misleads about a launch fact.
5. **The scheduled task's own prompt is stale on six rows** and has been for a week. Listed once here
   so no future sweep re-raises them, and so David can fix the prompt in one pass:
   it calls the **secrets rotation** BLOCKING and unrotated (done + probed 22 Aug; RG-0146/RG-0147
   LOCKED and green today) · repeats the **Resend malformed-sender 422** claim (disproven — the 422
   is the healthy answer; the genuinely dead credential is the *separate watch key*) · says the
   **uptime monitor** has "no vendor named" and was "due 22 Aug" without noting it is BUILT and needs
   only 3 commands · says the **domain registrar is recorded nowhere** (all four fields recorded,
   RG-0137 LOCKED) · says nothing on disk names **Fable's successor** (RUL-013 + `ai_provider.py:63`
   both name it) · still lists **Google OAuth** residue as though the lane were in doubt.
6. **`OPEN_LOOPS.md`'s 🔴 BLOCKING NOW section was corrected this run** — see EXECUTED above. Its B1
   row is discharged and physically stays until an attended reconciliation moves it.

### Corrected 28 Aug — files the probes overruled this run

- **`OPEN_LOOPS.md` "9 days to soft-public"** — it is **1 day**. Corrected in the file.
- **`OPEN_LOOPS.md` "what genuinely blocks 29 Aug"** — named five items; **four disproven by probe**
  minutes before the correction. Rewritten in the file with the probe results.
- **A bare deploy-debt count of 4** would have read as launch-eve debt. **Zero deployable files.**
- **The ledger's own board read `exit 2 / 2 UNVERIFIED`** on the first run — a missing `fastapi`, not
  a fault. Dependency installed, re-run **exit 0, 0 UNVERIFIED**.

### Corrected 22–27 Aug (stands — do not re-raise)

- **Secrets rotation is DONE** (22 Aug). Residue: two superseded Cloudflare tokens for David to
  delete; FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1) — the *separate watch key* is
  genuinely dead (DW-076). Two different credentials; do not merge them again.
- **`bit_flags.auth_fail_closed: false` is a MISREAD** — it is a *narrowing* switch, not the base
  auth control. The real control is fail-closed and proven: `B-NEG-AUTH` (S1) = PASS, HTTP 401.
- **"The CSP header is emitted at the Cloudflare edge"** (26 Aug hypothesis) — **DISPROVEN.** nginx
  was the emitter; migration 033 had been measuring the port-80 301 redirect.
- **"Nothing on disk says what replaces Fable"** — **wrong.** RUL-013 + `ai_provider.py:63`.
- **The AI serving lane is resolved**: OpenAI base, Anthropic keyless by decision, failover proven (RG-0128).
- **SSL renewed** — 2026-11-22, not the 24 Sep an older row claimed.
- **`post_deploy_status.json` serves at `/static/`** — the bare path 404s. Not a missing deploy record.
- **Anonymous PII on `/launch-api/prospects/list` is SHUT** (401, re-probed again today). RG-0176 LOCKED.
- **RDAP is the wrong door for `.co`** — use `whois.iana.org` → `whois.registry.co`. The "permanently
  machine-unanswerable" verdict four sweeps had hardened into canon was itself wrong.

---

## VERDICT

**1 day to soft launch (Fri 29 Aug) · 4 days to full launch (Mon 1 Sep) · AMBER.**

The product is ready: every functional probe is green, the ledger holds 180 locked fixes with **0
regressed**, all 59 rulings are reflected, the legal documents are live and in sync, the money rail
answers, sign-in works for strangers, and the site Friday serves is already published. **AMBER, not
GREEN, for one reason only — the site will go public with nothing watching it.** Two clicks from
David close that, in this order: the Resend watch key, then the three wrangler commands.
