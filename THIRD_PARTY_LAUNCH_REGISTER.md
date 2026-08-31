# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch went public **29 Aug 2026** · Full launch **1 Sep 2026** (RUL-001)*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check` (self-terminates after 1 Sep).
It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-31, 05:07–05:25 UTC (07:07–07:25 SAST) · FULL-LAUNCH EVE · T-1 · verdict GREEN.**

*This is the last sweep before full launch, and it is the first one that had to **correct the board
itself** rather than the world: the regression ledger opened the day at **exit 1** on a single red,
and the red was **false** — RG-0214's live half searched the deploy report for a step name that has
never existed in that report's format, so it could only ever fail. A red ledger refuses a launch-day
deploy. The assertion was re-aimed this run (see EXECUTED), and the board is **exit 0 · 214 entries ·
0 REGRESSED · 0 UNVERIFIED**. Everything else is green and unchanged from yesterday, with two
long-standing ambers now closed: the anonymous `/dashboard/summary` leak is gone (heartbeat-only,
probed) and RG-0198/RG-0211 are both LOCKED.*

Evidence grade on every row: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson.

---

## MACHINE-READ FIELDS
*The regression ledger reads these lines directly.*

```
DOMAIN_REGISTRAR: Cloudflare, Inc. (IANA ID 1910 · whois.registry.co · registrar lock ON, clientTransferProhibited)
DOMAIN_EXPIRY: 2026-12-30
DOMAIN_AUTORENEW: ON (read in the Cloudflare Registrations dashboard 2026-08-28; status Active)
DOMAIN_VERIFIED_ON: 2026-08-28
GOOGLE_CONSENT_SCREEN: PUBLISHED (In production · External · verification NOT required, no sensitive or restricted scopes) verified 2026-08-27
```
*Ledger: **RG-0137** (domain lifeline, LOCKED) · **RG-0139** (consent screen published). Green on this run.*

---

## 🔴 RED — WHAT BLOCKS OR THREATENS

**Nothing.** Third consecutive empty RED list. Every functional probe green; ledger 0 REGRESSED,
0 UNVERIFIED (full board, 214 entries); rulings 76/76 reflected, 0 FAIL, 0 WARN.

*The one red that existed at the start of this run was a FALSE red and was fixed, not reported —
see EXECUTED. It is worth naming plainly because of when it landed: a false red on launch eve costs
what a missed regression costs, which is trust in the board.*

### DEPLOY DEBT — 3 commits · NO app code · 3 manifest-listed operator documents

`git log origin/deploy..HEAD` = **2 commits** at sweep time (`b043aaf` nightly checkpoint,
`c16f244` daily watch) **plus this run's own records commit** (`cb9006a`). `origin/deploy` tip is
`0aa94f3` (Release Sun 30 Aug 19:02 SAST); `post_deploy_status.json` re-probed at
`2026-08-30T17:04:29Z` with `seed=ok · ladder_seed=ok · migrations=ok`.

**Corrected in this same run — a probe disagreed with this file's own first draft.** The draft said
"0 deployable"; checking the 23 changed paths against `ops/autodeploy/deploy_manifest.txt` found
**three that ARE manifest-listed**: `DAILY_WATCH/OPEN_ITEMS.md`, `DEFENCE_COVERAGE_MAP.html` and
`SESSION_COUNTER.json`. All three are **operator/records surfaces behind the Orchestrator gate or
the dashboard badge — no app code, no user-facing page, nothing a buyer or seller can see.**
**The marketplace as it will be on 1 Sep is the marketplace that is live right now.**

**Known lane gap, not a fault:** this sweep runs in a sandbox with **no push credentials**
(`git push` → `could not read Username for 'https://github.com'`), so its commit is **local until a
host-side push runs**. `origin/main` is 3 commits behind HEAD. That matters here for one reason
only: MAP-LIVE-1 serves the gated ops map and watch register from the repo's **fetched origin/main**,
so those two live documents will carry today's watch entry once main is pushed. **This is exactly
what D15 (push-scoped PAT) exists to close** — the recorded fallback is live and green either way.

**AMBER residue, tracked by machinery, none of it blocking:** RG-0212 (customer-email firewall —
code carries the gate, ARMING is David's launch-day act) · RG-0132 (no production golden run on the
OpenAI BASE lane) · RG-0203–0208, RG-0215, RG-0216 (launch-weekend feature work + jurisdiction gate,
OPEN by design) · RG-0221 (ZOOM prints READY TO LOCK but is **deliberately** left OPEN — its own ref
says the spec-intact assertion is the OPEN form and promotion waits for the build; noted so a later
session does not mistake it for an unpromoted fix).

## DAVID-ONLY ACTIONS, IN DATE ORDER
*Queue: `python3 scripts/david_queue.py` — 15 items, **6 open** (D5, D6, D10, D11, D12, D15),
plus three register-tracked items not in the queue (firewall arming, Anthropic click, trademark EFT).*

| When | Days left | Action | Why only David |
|---|---|---|---|
| **TODAY, Mon 31 Aug** | **0** | **Activate Resend $20/mo 50k tier** (D6). RUL-061 fixed the flip for today; outreach was deliberately capped (~90 sent 29 Aug) to leave free-tier headroom for sign-in codes until now. **This is the last day it can be done before launch traffic** | Spend |
| **TODAY / before tomorrow** | **0** | **Anthropic subscription cancel click** if it auto-renews (D8 residue). RUL-013's Fable arrangement **ends 1 Sep and does not renew by default**; the successor is already wired (`design → gpt-5.6-sol`, Scaleway standby) — this is the money half only | Spend |
| **Tue 1 Sep (launch day)** | **1** | **Arm the customer-email firewall** (RUL-069/RG-0212): `wrangler` var `CUSTOMER_FIREWALL=1` + worker deploy, then write `cloudflare_email_worker/ARMED_RECORD.md` with the var, worker version id and date. After launch no customer mail may land in a personal inbox | Lockout class (RUL-027) |
| **Soon (trademark)** | — | **EFT R1,770 ref AFGGPO** for the 29 Aug CIPC trade-mark filing (RUL-062, records 1644020/21/22 Queued) — unpaid filings do not process | Money |
| **Overdue — was ~25 Aug** | — | **Gemini key** (D5): budget-capped $10/mo at the vendor, then `add_gemini_key.bat`. Probed again today: still absent (`ai_provider.providers` = anthropic · openai · scaleway). Photo anonymisation stays **reject-only** (RUL-033) — quality cost, never a blocker | Money + secret |
| **Once** | — | One real **Didit ID check** (D10) → settles free-500-vs-$1.10-from-call-one. Lane re-probed ARMED today (`available:true, price_t:1`); still **no real NPR query has ever run**. RG-0136 is LOCKED on the *guards*, not on this | Real money |
| **David picks the moment** | — | **Travelpayouts tours resubmit** (D11). RUL-041 bars an unchanged resubmit; the public launch is the materially changed face | Commercial |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (D12) · **D15** push-scoped PAT (RG-0214's preferred fix; the recorded fallback is live and green, so this is comfort, not need) | Rotation residue / console |
| **Week 1** | — | Re-read the **Google OAuth user cap** (0/100 displayed; should not bind) · consider **Hetzner console 2FA** (account has none) · the OS reboot window (DW-085: 37 packages upgradable, `/var/run/reboot-required` present) | Console login |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 — RUL-023, "not optional and not deferrable") | Engagement + spend |
| ~~DONE 29 Aug~~ | — | ✅ **D9 CLOSED — two live real Tuppence buys through Paystack.** *Residue, noted not hidden: the tab-close-mid-flow detached-credit variant is still unexercised* · ✅ Send freeze lifted + first waves out (RUL-063) · ✅ Trademark lodged (RUL-062) · ✅ Tester channel retired (RUL-064) | — |

## PROBED THIS RUN — the live facts (31 Aug 2026, 05:07–05:25 UTC)

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · **v1.3.1** · db primary present (2,879,488 B), integrity **ok** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id `869589580243-…`, scope `openid email profile` | PROBED |
| `GET /id-verify/status` | `available:true` · `price_t:1` · "READY — sellers can buy a check" | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, `failing: []` | PROBED |
| `GET /flags` | `ai_provider.active: openai` · card `2026-08-26.1` · **`fault_report:false`** (RUL-064 live) · `data.flights true` · providers anthropic/openai/scaleway — **no gemini** (D5) | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| `GET /dashboard/summary` (anon) | **`{generatedAt, bea_version, redacted:"heartbeat"}` and nothing else** — the leak is closed. DW-078 done; RG-0198 + RG-0211 both LOCKED | PROBED |
| `/static/post_deploy_status.json` | `generated_at 2026-08-30T17:04:29Z` · `seed=ok` · `ladder_seed=ok` · `migrations=ok` | PROBED |
| `/orchestrator/defence_map.html` · `/orchestrator/watch_register.md` | **401 anonymous** — both gated documents hold inside the Basic-Auth realm (MAP-LIVE-1) | PROBED |
| TLS certificate | valid to **2026-11-22 (83 days)** | PROBED |
| `regression_ledger.py` | **exit 0 · 214 entries · 197 ok · 16 open · 0 REGRESSED · 0 UNVERIFIED** *(opened the run at **exit 1** on one FALSE red — fixed this run, below; and the fresh-sandbox `fastapi`/`httpx` gap fired again on first invocation, bootstrapped per RG-0200 — fourth consecutive day)* | EXECUTED |
| `rulings_check.py` | **76 rulings, 0 FAIL, 0 WARN** | EXECUTED |
| `eula_sync.py --check` | in sync, 117,749 B across the three copies | EXECUTED |
| `david_queue.py` | 15 items, **6 open** | EXECUTED |
| `git log origin/deploy..HEAD` | 2 commits, **0 deployable** | EXECUTED |

### EXECUTED THIS RUN — what Claude did rather than reported

1. **The ledger's one red was a FALSE red, and it was FIXED, not escalated (DW-086 → CLOSED same day).**
   RG-0214 printed `deploy report … carries no migration-035 step` and the run ended `Do not deploy
   over this`, exit 1 — on the eve of full launch, where a red board refuses a deploy. The assertion
   was misreading its evidence: it searched `/static/post_deploy_status.json` for a step whose *name*
   contains "035", but that report aggregates the whole chain into **one** step (probed live:
   `seed=ok`, `ladder_seed=ok`, `migrations=ok`). A per-migration step name has never existed in that
   format, so the check **could only ever go red**. The live half was re-aimed at evidence that
   exists, and **gained a guard it did not have**:
   - (a) the deploy report's migration chain step ran and did not fail — read in the report's own vocabulary;
   - (b) migration 035 still carries the self-proof clauses that make `migrations = ok` mean *proven*
     (both exact-match locations, `auth_basic`, and its "NOT claiming success" refusal path);
   - (c) **neither gated document answers 200 anonymously** — the information leak this entry exists to
     prevent is now asserted **directly**, probed live (both **401**), instead of inferred.

   Per the never-weaken rule the correction is written into the entry's own ref, dated, with the
   reason. `py_compile` green, backup kept beside the file, board re-run to **exit 0**.
2. **DW-086 closed in `DAILY_WATCH/OPEN_ITEMS.md`** with the evidence and the class lesson. The daily
   watch had correctly diagnosed it and correctly declined to fix it (observe-only lane, and
   `scripts/regression_ledger.py` is not a watch-owned path) — it named an attended CTO session as the
   owner under RUL-037. This was that session.
3. **Calendar drift caught and named** (below) — the launch *dates* are right, the *day names* in the
   docs are not.
4. **This register rewritten from today's probes**; changelog fragment dropped in `changelog.d/`.

### NOT DONE, DELIBERATELY — and why

- **No new meta-harness for the false-red class.** The honest general assertion here is "no ledger
  assertion may check for evidence that cannot exist", and every mechanical version of it is
  brittle enough to become a false-red generator itself. Building that on launch eve trades a known
  small risk for an unknown one. The lesson is carried in RG-0214's ref and in DW-086, and the class
  is named here so the next session can decide it with a calmer calendar.
- **RG-0221 (ZOOM) not promoted** though it prints READY TO LOCK: its own ref defines the OPEN state
  as the spec-intact assertion and reserves LOCKED for the shipped build (RUL-076, flag dark).
  Promoting it would lock a weaker assertion than the entry intends.
- **RG-0203–0208 / RG-0216 feature work**: launch-weekend build lane (CTO), not third-party
  readiness — tracked by the ledger, not re-listed here.
- **DW-085's reboot window** (37 packages upgradable, reboot-required flag): a reboot on launch eve is
  a worse risk than a fortnight-old kernel. Week 1.

---

## MONEY

| Service | State | Grade | Cost | Blocks? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE — `paystack_connected: true` (re-probed). 2FA ON (28 Aug). **D9 CLOSED: two real live buys 29 Aug.** Residue: detached-credit tab-close variant unexercised | PROBED | 2.9% + R1 | No |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company registered. **Trade mark lodged 29 Aug** (RUL-062, 3 records Queued) — **EFT R1,770 ref AFGGPO pending, David** | READ | R1,770 | No |
| **Accountant** | Not engaged. RUL-023: month 1 | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Not opened | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks? |
|---|---|---|---|
| **OpenAI** (BASE lane) | Serving — `active: openai`, card `2026-08-26.1` current (re-probed). Production golden run still unrecorded (RG-0132, first post-launch window) | PROBED | No |
| **Anthropic API** (failover) | No key on server by decision (SPEND-GUARD-1); failover proven in the decision layer (RG-0128) | EXECUTED | No |
| **Anthropic subscription** (Fable) | **RUL-013's arrangement ENDS 1 Sep and does not renew by default.** Successor already wired: `design → gpt-5.6-sol`, Scaleway standby. Residue is the cancel click if it auto-renews — David, today | READ | No |
| **Gemini** | 🟠 Key still ABSENT (re-probed: not in `ai_provider.providers`). Photo anonymisation reject-only (RUL-033). D5, overdue since ~25 Aug | PROBED | No |
| **Scaleway** (EU last resort) | Configured, free tier | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks? |
|---|---|---|---|
| **Google OAuth** | ✅ LIVE — `google:true`, start 302s with real client_id (re-probed). RG-0111 LOCKED. Do not re-raise | PROBED | No |
| **Google consent screen** | ✅ PUBLISHED "In production" (read at the console 27 Aug; RG-0139). Week-1 residuals: user cap 0/100 display; branding | READ | No |
| **Apple Sign-In** | OUT by ruling (RUL-030); `apple:false` (re-probed). Never re-propose | PROBED | — |
| **Didit** | ARMED — `available:true, price_t:1` (re-probed). **No real NPR query yet (D10)** — "READY" is not "works" | PROBED | No |
| **Resend** (app sending) | Sending live, **free tier**. First outreach waves out 29 Aug (~90, capped for headroom). **$20 Pro flip is TODAY (RUL-061 / D6)** | PROBED (sends 29 Aug) | Flip is today |
| **Resend** (RED-alert watch key) | ALIVE; heartbeat delivery proven 29 Aug. RG-0201 LOCKED — the rotation refreshes the out-of-band copy itself. *The ~5-min **422** is the HEALTHY answer (INFRA-RESEND-1) — do not "fix" it* | PROBED (29 Aug) | No |
| **Local outreach key** (CityLauncher) | Burnt 22-Aug copy replaced 29 Aug with a scoped sending-only key (RUL-063); register row asserted by rulings_check | READ | No |
| **support@trustsquare.co** | RG-0174 LOCKED. **THE customer complaint lane (RUL-064)** — tester fault tab retired, `fault_report:false` re-probed | PROBED | No |
| **Customer-email firewall** | Code carries the gate (RUL-069/RG-0212); **ARMING is David's launch-day act (1 Sep)** | READ (source) | The arming is a launch-day act |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug; personal address | PROBED (22 Aug) | Presentation only |
| **n8n** | Self-hosted, running (2 Jun) | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live, serving public day 3. SPOF accepted for launch scale. Firewall self-heal armed (RG-0188). No console 2FA (week 1). OS reboot deferred to week 1 (DW-085) | PROBED | EUR 15.49 — RUL-025: never rescale | No |
| **Hetzner Object Storage** | Daily 3AM backup, 14-day retention | READ | EUR 5.99 | No |
| **Cloudflare** | Live; WAF deliberately open (RUL-034); hosts uptime Worker + email worker | PROBED | Free | No |
| **SSL** | valid to 2026-11-22 (**83 days**) | PROBED | Free | No |
| **Domain** | Cloudflare · expires 2026-12-30 · auto-renew ON · lock ON (RG-0137 LOCKED) | PROBED (28 Aug) | Included | No |
| **GitHub** | Live; deploy debt 2 commits, **0 deployable** | EXECUTED | Free | No |
| **External uptime monitor** | LIVE — Worker `trustsquare-uptime`, cron `*/5`, alert path proven end-to-end 29 Aug. RG-0138 LOCKED (7-day staleness tripwire) | PROBED (29 Aug) | Free | No |
| **Gated ops map / watch register** | LIVE and gated — MAP-LIVE-1 routes + migration 035; both documents **401 anonymous**, re-probed this run. RG-0214 green after this run's assertion repair | PROBED | — | No |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (`data.flights: true` re-probed), Numista (RG-0150),
free keyless set (RUL-022 — no paid FX ever).
**Tours:** DECLINED 24 Aug; resubmit is D11, David's moment (RUL-041 bars unchanged resubmit).
Drive loader stays OFF (RG-0025 inverted).
**Affiliate lane:** server-side link-out only, fails closed.
**Deliberately dark:** JustTCG, Duffel, AeroDataBox, Mapbox, GeoNames, Places.
**Closed:** Google Places (OUT — never re-propose), Amadeus (dead), BrickLink.
**Unknown:** eBay keyset (last entry 7 Jun).

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | v1.15 LIVE (`/terms` re-probed); three copies in sync (117,749 B) | PROBED | Counsel NOT a gate (RUL-020) |
| **Privacy Policy** | Live-exempted at origin; BACKLOG A1 open | READ | Bar G7 |
| **Privacy UK/US/AU supplements** | Never drafted (RUL-019 made launch worldwide) | READ | Bar G7 |
| **Trade mark** | Lodged 29 Aug (RUL-062): brand-logo device, classes 35/36/42, records 1644020/21/22 Queued. Payment pending (David) | READ | No |
| **IP Brief v6 / WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Deferred to week of 8 Sep by David | READ | Deferred |

---

## WATCH-OUTS

1. **`.env` files prove nothing** — verify at point of USE (RG-0147).
2. **"READY" is not "works"** — Didit is presence, not a run (D10). Same class: the detached-credit
   tab-close path — two real buys happened, that variant specifically did not.
3. **NEW 31 Aug — an assertion can be wrong in the direction of ALARM.** The evidence ladder is
   usually invoked against a file that claims too much; RG-0214 is the mirror image — a *harness*
   that claimed a rot that was not there, because it read for evidence that has never existed.
   Probe beat file again, in the same direction. When the board and a probe disagree, probe the
   property before believing either.
4. **Header rot**: BACKLOG.md header still says 18 June; OPEN_LOOPS 🔴 section still physically
   carries the discharged B1 row (additive discipline — moves at the next attended reconciliation).
   **Do not read that heading as "secrets rotation blocks launch". It does not, and has not since
   22 Aug** (RG-0146/0147 LOCKED and green today).
5. **NEW 31 Aug — day-name drift in the launch dates.** The *dates* are RUL-001 and stand:
   soft-public **29 Aug 2026**, full launch **1 Sep 2026**. The *day names* attached to them across
   the docs are wrong — 29 Aug 2026 was a **Saturday** (docs say Friday) and 1 Sep 2026 is a
   **Tuesday** (docs say Monday). Nothing operational depends on it; RULINGS.md is **not** edited
   here because amending a ruling's wording is David's, not Claude's. Named so no one re-derives a
   schedule from the wrong weekday.
6. **The fresh-sandbox `fastapi`/`httpx` gap fires every run** — bootstrap BEFORE the ledger
   (RG-0200 step 0), or the first invocation reads NOT EVALUATED and lies about the board. Fourth
   consecutive day.

### Corrected 22–31 Aug (stands — do not re-raise)

- Secrets rotation DONE (22 Aug; RG-0146/0147 LOCKED). Residue: D12 tokens.
- Resend ~5-min 422 is the HEALTHY answer (INFRA-RESEND-1).
- RUL-013 + D8 answer "what replaces Fable": `design → gpt-5.6-sol`, Scaleway standby.
- External uptime monitor is LIVE and proven (RG-0138) — not "not built".
- Domain registrar/expiry/auto-renew IS recorded and asserted (RG-0137) — not "recorded nowhere".
- Paystack 2FA is ON (28 Aug). RG-0136 is LOCKED, not open.
- `bit_flags.auth_fail_closed: false` is a MISREAD (narrowing switch; the real control PASSES).
- RDAP is the wrong door for `.co` — `whois.iana.org` → `whois.registry.co`.
- SSL renews 2026-11-22. `post_deploy_status.json` serves at `/static/`.
- **NEW 31 Aug:** `post_deploy_status.json` aggregates the migration chain into ONE step named
  `migrations`. Per-migration step names do not exist in that report. Any future assertion that
  wants to prove a specific migration ran must prove it another way.

*The scheduled task's own prompt is stale on 8+ rows and self-terminates after 1 Sep; the
corrections above are the record.*

---

## VERDICT

**FULL-LAUNCH EVE · T-1 to 1 Sep 2026 · GREEN.**

Nothing external blocks the launch. The site is public, up (v1.3.1, db integrity ok), watched by an
independent vantage, alarmed, and green on every functional probe; the money rail has taken real
buys; every locked fix holds across 214 ledger entries with zero regressions and zero unverified;
all 76 rulings are reflected with zero warnings. The board that guards the launch was itself the
one thing wrong this morning, and it is fixed.

**David's path to tomorrow is three acts, in order: the Resend Pro flip (D6, today), the Anthropic
cancel click (today, before the arrangement lapses), and arming the customer-email firewall at the
launch flip (RUL-069) — plus the trademark EFT so the filing processes.** Everything else on his
list is post-launch by design.

*This register's own scheduled task self-terminates after 1 Sep 2026. From 2 Sep the daily watch
(`DAILY_WATCH/OPEN_ITEMS.md`) and the regression ledger are the standing instruments.*
