# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch went public **29 Aug 2026** · Full launch **1 Sep 2026** (RUL-001)*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check` (self-terminates after 1 Sep).
It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-09-01, 05:06–05:25 UTC (07:06–07:25 SAST) · LAUNCH DAY · T-0 · verdict GREEN.**
**THIS IS THE FINAL SWEEP.** The task self-terminates after today. From 2 Sep the standing
instruments are the daily watch (`DAILY_WATCH/OPEN_ITEMS.md`), the regression ledger and the
rulings check — this file stays as the launch-state record and is no longer maintained daily.

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

**Nothing.** Fourth consecutive empty RED list, and the one that counts: launch day. Every
functional probe green; ledger full board **exit 0 · 0 REGRESSED · 0 UNVERIFIED · 19 OPEN
(known defects, tracked)**; rulings **86/86 reflected, 0 FAIL, 0 WARN**; EULA three copies in
sync (117,749 B).

### DEPLOY DEBT — 7 commits · NO app code · 2 manifest-listed operator documents

`git log origin/deploy..HEAD` = **7 commits** (nightly checkpoint, daily watch, RG-0230/0231
ledger work, RUL-082/083 records, MAP-CARDS-1). 25 changed paths checked against
`ops/autodeploy/deploy_manifest.txt`: **2 are manifest-listed** — `DAILY_WATCH/OPEN_ITEMS.md`
(→ gated watch register) and `DEFENCE_COVERAGE_MAP.html` (→ gated defence map). Both are
operator/records surfaces behind the Basic-Auth gate — no app code, no user-facing page.
`origin/deploy` was last placed **2026-08-31T14:14:28Z** (`post_deploy_status.json` re-probed:
`ref=deploy`, seed ok · ladder_seed ok · migrations "none pending").
**The marketplace serving the public on launch day is the marketplace that was probed green.**

### WHAT MOVED OVERNIGHT AND THIS MORNING (READ — rulings dated today)

- **RUL-084 (31 Aug):** the launch-day outreach wave was scheduled to fire itself at **00:10
  today** (Task Scheduler one-shot, every send-guard still standing; National excluded by
  design). This sweep did **not** probe the wave outcome — that is David's stated morning
  check-in, and the outreach lane's own instruments own it.
- **RUL-085 (1 Sep, ~05:00 SAST):** the 74 search-engine scraper lanes revived on David's word,
  executed server-side; zero-yield backoff re-governs them from row one.
- **RUL-086 (1 Sep):** UGC cross-language translation design ratified into canon
  (`i18n/UGC_TRANSLATION_DESIGN.md`) — design lane, nothing third-party opened yet; MT vendor
  selection is RUL-009 class, David's.

## DAVID-ONLY ACTIONS, IN DATE ORDER
*Queue: `python3 scripts/david_queue.py` — 15 items, **5 open** (D5, D10, D11, D12, D15) after
this sweep closed D6 (below), plus register-tracked items not in the queue.*

| When | Days left | Action | Why only David |
|---|---|---|---|
| **TODAY, Tue 1 Sep** | **0** | **Arm the customer-email firewall** (RUL-069/RG-0212): `wrangler` var `CUSTOMER_FIREWALL=1` + worker deploy, then write `cloudflare_email_worker/ARMED_RECORD.md` (var, worker version id, date). Probed this run: **ARMED_RECORD.md does not exist yet** — the act is still open. After launch no customer mail may land in a personal inbox | Lockout class (RUL-027) |
| **TODAY** | **0** | **Anthropic subscription cancel click** if it auto-renews (D8 residue). RUL-013's Fable arrangement **ends today and does not renew by default**; the successor is wired (`design → gpt-5.6-sol`, Scaleway standby). No record on disk says the click happened — if the account shows no auto-renew, no act is needed | Spend |
| **Soon (trademark)** | — | **EFT R1,770 ref AFGGPO** for the 29 Aug CIPC trade-mark filing (RUL-062, records 1644020/21/22 Queued) — unpaid filings do not process. No payment record on disk yet | Money |
| **Overdue — was ~25 Aug** | — | **Gemini key** (D5): $10/mo capped at the vendor, then `add_gemini_key.bat`. Re-probed today: still absent (`ai_provider.providers` = anthropic · openai · scaleway). Photo anonymisation stays **reject-only** (RUL-033) — quality cost that grows with every seller upload, never a blocker | Money + secret |
| **Once** | — | One real **Didit ID check** (D10) → settles free-500-vs-$1.10-from-call-one. Lane re-probed ARMED today (`available:true, price_t:1`); still no real NPR query has ever run | Real money |
| **David picks the moment** | — | **Travelpayouts tours resubmit** (D11). RUL-041 bars an unchanged resubmit; the public launch is the materially changed face | Commercial |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (D12) · **D15** push-scoped PAT (fallback live and green — comfort, not need) | Rotation residue |
| **Tomorrow, Wed 2 Sep** | 1 | **The attended root maintenance window** (DW-084 restart + DW-085 `apt upgrade` + reboot; 37 packages, reboot-required flag still up, re-probed today). One window, then /health + RG-0147 re-verify | Console + reboot risk |
| **Week 1** | — | Re-read the **Google OAuth user cap** (0/100 displayed; should not bind) · consider **Hetzner console 2FA** (account has none) | Console login |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 — RUL-023, "not optional and not deferrable") | Engagement + spend |
| ~~DONE 31 Aug~~ | — | ✅ **D6 CLOSED — Resend $20/50k Pro tier activated 31 Aug** (recorded in RUL-079's own text; the queue row sat stale at OPEN and was corrected this run). The Tue-1-Sep 420-send cliff RUL-061 existed to kill is dead | — |

## PROBED THIS RUN — the live facts (1 Sep 2026, 05:06–05:25 UTC)

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · **v1.3.1** · db primary present (2,879,488 B), integrity **ok** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id `869589580243-…`, scope `openid email profile` | PROBED |
| `GET /id-verify/status` | `available:true` · `price_t:1` · "READY — sellers can buy a check" | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, `failing: []` | PROBED |
| `GET /flags` | `mode:live` · `ai_provider.active: openai` · card `2026-08-26.1` · `fault_report:false` · `data.flights:true` · providers anthropic/openai/scaleway — **no gemini** (D5) | PROBED |
| `GET /terms` | 200; `eula_sync.py --check` in sync, 117,749 B across the three copies | PROBED + EXECUTED |
| `GET /dashboard/summary` (anon) | heartbeat only (`generatedAt, bea_version, redacted`) — leak stays closed | PROBED |
| `/static/post_deploy_status.json` | `2026-08-31T14:14:28Z` · `ref:deploy` · seed ok · ladder_seed ok · migrations "none pending" | PROBED |
| `/orchestrator/defence_map.html` · `/orchestrator/watch_register.md` | both **401 anonymous** — gated documents hold | PROBED |
| TLS certificate | valid to **2026-11-22** (82 days) | PROBED |
| `regression_ledger.py` | **exit 0 · every locked fix holding · 0 REGRESSED · 0 UNVERIFIED · 19 open (known, tracked)**. First invocation hit the fresh-sandbox `fastapi` gap again (fifth consecutive day) — bootstrapped per RG-0200, full board re-run | EXECUTED |
| `rulings_check.py` | **86 rulings, 0 FAIL, 0 WARN** (76 → 86 since the 31 Aug sweep: RUL-077–086) | EXECUTED |
| `david_queue.py` | 15 items, **5 open** after this run's D6 correction | EXECUTED |
| `git log origin/deploy..HEAD` | 7 commits · 25 paths · **2 manifest-listed, both gated operator docs, no app code** | EXECUTED |
| `cloudflare_email_worker/ARMED_RECORD.md` | **absent** — firewall arming (David's launch-day act) not yet done | PROBED (absence) |

### EXECUTED THIS RUN — what Claude did rather than reported

1. **Ledger bootstrapped before believing it (RG-0200 step 0).** First invocation reported
   RG-0181/0182 NOT EVALUATED because the fresh sandbox lacks `fastapi` — the run's own output
   says "that is not a green board". `pip install fastapi httpx` and a full re-run produced the
   real board: exit 0, every locked fix holding. The gap fired for the fifth consecutive day;
   it is a sandbox property, not a repo defect, and the bootstrap is the standing answer.
2. **D6 corrected from OPEN to DONE — a file lagged a ruling by two days.** RUL-079 (31 Aug)
   records in its own text that David "activated the Resend $20/50k tier" that day; DAVID_QUEUE.md
   still carried `STATE: OPEN` and yesterday's register listed the flip as today's act #1. The
   queue row now closes with the citation and the honest grade (READ — the billing tier is not
   probeable from the sandbox). Same class as the 21 Aug Google-OAuth lesson: the person and the
   dated record were right, the tracking file was stale.
3. **This register rewritten from today's probes**; changelog fragment
   `changelog.d/2026-09-01-third-party-final-sweep.md` dropped. Backups kept beside both edited
   files (`.bak-<ts>`).

### NOT DONE, DELIBERATELY — and why

- **The launch wave outcome (RUL-084) was not probed.** David's ruling names his own morning
  check-in as the verification act, the outreach lane has its own instruments (stop-loss,
  source_health, RG-0225–0229), and this register's remit is third-party readiness, not send ops.
- **No edits to RULINGS.md** (day-name drift noted 31 Aug stands recorded there and here;
  amending ruling wording is David's).
- **DW-084/DW-085 left for the 2 Sep attended root window** — a reboot on launch morning is a
  worse risk than a fortnight-old kernel, same call as yesterday, now with a date.

---

## MONEY

| Service | State | Grade | Cost | Blocks? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE — `paystack_connected: true` (re-probed). 2FA ON (28 Aug). D9 closed 29 Aug (two real buys). Residue: detached-credit tab-close variant unexercised | PROBED | 2.9% + R1 | No |
| **Resend Pro** | **$20/mo 50k tier ACTIVE since 31 Aug** (RUL-079 record; D6 closed this run) | READ | $20/mo | No |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Trade mark lodged 29 Aug (RUL-062, 3 records Queued) — **EFT R1,770 ref AFGGPO pending, David** | READ | R1,770 | No |
| **Accountant** | Not engaged. RUL-023: month 1 | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Not opened | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks? |
|---|---|---|---|
| **OpenAI** (BASE lane) | Serving — `active: openai`, card `2026-08-26.1` (re-probed). Production golden run still unrecorded (RG-0132, first post-launch window) | PROBED | No |
| **Anthropic API** (failover) | No key on server by decision (SPEND-GUARD-1); failover proven in the decision layer (RG-0128) | EXECUTED | No |
| **Anthropic subscription** (Fable) | **RUL-013's arrangement ENDS TODAY and does not renew by default.** Successor wired: `design → gpt-5.6-sol`, Scaleway standby. Residue: the cancel click if the account auto-renews — David, today | READ | No |
| **Gemini** | 🟠 Key still ABSENT (re-probed). Photo anonymisation reject-only (RUL-033). D5, overdue since ~25 Aug | PROBED | No |
| **Scaleway** (EU last resort) | Configured, free tier | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks? |
|---|---|---|---|
| **Google OAuth** | ✅ LIVE — `google:true`, start 302s with real client_id (re-probed). RG-0111 LOCKED. Do not re-raise | PROBED | No |
| **Google consent screen** | ✅ PUBLISHED (RG-0139). Week-1 residuals: user cap display; branding | READ | No |
| **Apple Sign-In** | OUT by ruling (RUL-030); `apple:false` (re-probed). Never re-propose | PROBED | — |
| **Didit** | ARMED — `available:true, price_t:1` (re-probed). No real NPR query yet (D10) — "READY" is not "works" | PROBED | No |
| **Resend** (app sending) | **Pro tier since 31 Aug (RUL-079)**; launch wave scheduled 00:10 today (RUL-084) | READ | No |
| **Resend** (RED-alert watch key) | ALIVE; RG-0201 LOCKED. *The ~5-min **422** is the HEALTHY answer (INFRA-RESEND-1) — do not "fix" it* | READ | No |
| **Local outreach key** (CityLauncher) | Scoped sending-only key since 29 Aug (RUL-063); asserted by rulings_check | READ | No |
| **support@trustsquare.co** | RG-0174 LOCKED. THE customer complaint lane (RUL-064); `fault_report:false` re-probed | PROBED | No |
| **Customer-email firewall** | Code carries the gate (RUL-069/RG-0212); **ARMING still open — ARMED_RECORD.md absent, probed this run. David's act, today** | PROBED (absence) | The arming is today's act |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug; personal address | PROBED (22 Aug) | Presentation only |
| **n8n** | Self-hosted, running (2 Jun) | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live, serving public day 4 — launch day. SPOF accepted for launch scale. Firewall self-heal armed (RG-0188). No console 2FA (week 1). Reboot window: tomorrow, 2 Sep (DW-084/085) | PROBED | EUR 15.49 — RUL-025: never rescale | No |
| **Hetzner Object Storage** | Daily 3AM backup, 14-day retention. Local archive lane now SELF-PROVING: RG-0234 extracts and integrity-checks the newest archive every ledger run (restore performed this run: users=70, integrity ok) | EXECUTED | EUR 5.99 | No |
| **Cloudflare** | Live; WAF deliberately open (RUL-034); hosts uptime Worker + email worker | PROBED | Free | No |
| **SSL** | valid to 2026-11-22 (**82 days**) | PROBED | Free | No |
| **Domain** | Cloudflare · expires 2026-12-30 · auto-renew ON · lock ON (RG-0137 LOCKED) | PROBED (28 Aug) | Included | No |
| **GitHub** | Live; deploy debt 7 commits, no app code | EXECUTED | Free | No |
| **External uptime monitor** | LIVE — Worker `trustsquare-uptime`, cron `*/5`; RG-0138 LOCKED (staleness tripwire) | READ (asserted) | Free | No |
| **Gated ops map / watch register** | LIVE and gated — both **401 anonymous**, re-probed. Deploy-engine self-check RG-0233 now asserts placement freshness every run | PROBED | — | No |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (`data.flights: true` re-probed), Numista (RG-0150),
free keyless set (RUL-022 — no paid FX ever).
**Tours:** DECLINED 24 Aug; resubmit is D11, David's moment (RUL-041 bars unchanged resubmit).
Drive loader stays OFF (RG-0025 inverted).
**Deliberately dark:** JustTCG, Duffel, AeroDataBox, Mapbox, GeoNames, Places.
**Closed:** Google Places (OUT — never re-propose), Amadeus (dead), BrickLink.
**Unknown:** eBay keyset (last entry 7 Jun).
**New design lane (nothing opened):** UGC machine translation (RUL-086) — vendor pick is
RUL-009 class, David's; flat-cost, hard-capped by canon when it comes.

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | LIVE (`/terms` 200); three copies in sync (117,749 B, EXECUTED this run) | PROBED | Counsel NOT a gate (RUL-020) |
| **Privacy Policy** | Live-exempted at origin; BACKLOG A1 open | READ | Bar G7 |
| **Trade mark** | Lodged 29 Aug (RUL-062), records Queued. Payment pending (David) | READ | No |
| **IP Brief v6 / WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Deferred to week of 8 Sep by David | READ | Deferred |

---

## WATCH-OUTS (standing — carried into the daily watch from 2 Sep)

1. **`.env` files prove nothing** — verify at point of USE (RG-0147). DW-084's three-fingerprint
   key drift is this class; restart window 2 Sep.
2. **"READY" is not "works"** — Didit is presence, not a run (D10); the detached-credit tab-close
   variant likewise.
3. **A tracking file can lag a ruling** — D6 sat OPEN for two days after RUL-079 recorded the act.
   The queue is READ-grade; rulings carry dates; when they disagree the dated record wins and the
   file is fixed in the same run.
4. **An assertion can be wrong in the direction of ALARM** (RG-0214, 31 Aug) — probe the property
   before believing either the board or the file.
5. **Day-name drift**: RUL-001's dates stand (29 Aug / 1 Sep); the day names in older docs are
   wrong (29 Aug was a Saturday; 1 Sep is a Tuesday — confirmed against the system clock today).
6. **The fresh-sandbox `fastapi`/`httpx` gap fires every run** — bootstrap BEFORE the ledger
   (RG-0200 step 0) or the first board lies. Fifth consecutive day.
7. **Header rot**: OPEN_LOOPS 🔴 section still physically carries the discharged B1 row (additive
   discipline — moves at the next attended reconciliation). It does NOT mean secrets block anything.

### Corrected 22 Aug – 1 Sep (stands — do not re-raise)

- Secrets rotation DONE (22 Aug; RG-0146/0147 LOCKED). Residue: D12 tokens.
- Resend ~5-min 422 is the HEALTHY answer (INFRA-RESEND-1).
- RUL-013 + D8 answer "what replaces Fable": `design → gpt-5.6-sol`, Scaleway standby.
- External uptime monitor is LIVE and proven (RG-0138) — not "not built".
- Domain registrar/expiry/auto-renew IS recorded and asserted (RG-0137) — not "recorded nowhere".
- Paystack 2FA is ON (28 Aug). RG-0136 is LOCKED, not open.
- **NEW 1 Sep:** Resend Pro flip DONE 31 Aug (RUL-079) — not "still due".
- `post_deploy_status.json` aggregates migrations into ONE step; per-migration names don't exist.

*The scheduled task's own prompt was stale on 8+ rows; the corrections above are the record.*

---

## VERDICT

**LAUNCH DAY · T-0 · 1 Sep 2026 · GREEN.**

Nothing external blocks the launch. The site is public and green on every functional probe
(v1.3.1, db integrity ok, BIT 8/8, money rail connected, sign-in live, ID checks armed);
every locked fix holds with zero regressions and zero unverified on the full board; all 86
rulings are reflected; the three EULA copies agree; the backup lane proved a restore this
morning as part of its own assertion.

**David's launch-day acts, in order: arm the customer-email firewall (RUL-069 — ARMED_RECORD.md
is the receipt), the Anthropic cancel click if the account shows auto-renew, and the trademark
EFT when banking is open.** Everything else on his list is post-launch by design, starting with
tomorrow's 2 Sep root maintenance window.

*This register's scheduled task self-terminates after today. It ends on a green board.*
