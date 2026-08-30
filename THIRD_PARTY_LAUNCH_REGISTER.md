# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch went public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check` (self-terminates after 1 Sep).
It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-30, 05:05–05:20 UTC (07:05–07:20 SAST) · SOFT-PUBLIC DAY 2 · 2 days to full launch · verdict GREEN.**

*The site is public, up (v1.3.1, db integrity ok), watched (Worker cron */5, heartbeat proven in
the inbox 29 Aug 06:00:22Z; today's is due 06:00 UTC — this sweep ran at 05:1x, before it), and
green on every functional probe. Launch evening was BUSY: the send freeze was lifted and ~90
outreach mails went out (RUL-063), the trademark was lodged (RUL-062), the tester fault channel
was retired for customers (RUL-064, probe-confirmed `fault_report:false`), D9 closed on two live
Paystack buys, and eight new ledger entries (RG-0203–0212) captured the feature work David set on
launch weekend. Rulings on the board grew 61 → 69; ledger 194 → 205 entries, 0 regressed.*

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

**Nothing.** Second consecutive empty RED list. Every functional probe green; ledger 0 REGRESSED,
0 UNVERIFIED (full board, 205 entries); rulings 69/69 reflected, 0 FAIL **0 WARN** (the 4 warns of
this morning's first check were cleared this run — see EXECUTED below).

### DEPLOY DEBT — 1 commit, 1 file, ZERO deployable

`git log origin/deploy..HEAD` = **1 commit** (f49a778, WATCH-SELFCOMMIT-1) touching only a
changelog fragment. Nothing user-facing is unpublished. Two releases already rode the deploy ref
this morning (06:08 and 06:58 SAST — docs/records only); `post_deploy_status.json` re-probed:
`generated_at 2026-08-30T04:59:48Z`, seed ok, ladder_seed ok, migrations "none pending".

**AMBER residue, tracked by machinery, none of it blocking:** RG-0198 + **RG-0211** (anonymous
`/dashboard/summary` still narrates seller/listing/intro counts, session numbers and the infra
line — re-probed 05:1x, unchanged; DW-078 day 4; heartbeat-only redaction is the CTO fix riding
the first post-launch deploy window) · RG-0180 (`connect-src`) · RG-0173 (agency journey probe) ·
RG-0132 (no production golden run on the OpenAI BASE lane) · RG-0203–0210 (launch-weekend feature
work, OPEN by design — funds gauge, sell-flow AI description, multi-photo vision, in-flow coach,
intro reminder ladder, A2HS trigger).

## DAVID-ONLY ACTIONS, IN DATE ORDER
*Queue: `python3 scripts/david_queue.py` — 12 items, **5 open** (D5, D6, D10, D11, D12), plus
three register-tracked items not in the queue (firewall arming, Anthropic click, trademark EFT).*

| When | Days left | Action | Why only David |
|---|---|---|---|
| **Mon 31 Aug** | **1** | **Activate Resend $20/mo 50k tier** (D6). RUL-061 fixed the flip for Monday; outreach was deliberately capped (~90 sent 29 Aug) to leave free-tier headroom for sign-in codes until then | Spend |
| **Mon 1 Sep (launch)** | **2** | **Arm the customer-email firewall** (RUL-069/RG-0212): `wrangler` var `CUSTOMER_FIREWALL=1` + worker deploy, then write `cloudflare_email_worker/ARMED_RECORD.md` with the var, worker version id and date. After launch no customer mail may land in a personal inbox | Lockout class (RUL-027) |
| **Before Tue 1 Sep** | **2** | **Anthropic subscription cancel click** if it auto-renews (D8 residue — DROP decided 28 Aug, successor wired `design → gpt-5.6-sol`) | Spend |
| **Soon (trademark)** | — | **EFT R1,770 ref AFGGPO** for the 29 Aug CIPC trade-mark filing (RUL-062, records 1644020/21/22 Queued) — unpaid filings do not process | Money |
| **Overdue — was ~25 Aug** | — | **Gemini key** (D5): budget-capped $10/mo at the vendor, then `add_gemini_key.bat`. Until then photo anonymisation stays **reject-only** (RUL-033) — quality cost, never a blocker | Money + secret |
| **Once** | — | One real **Didit ID check** (D10) → settles free-500-vs-$1.10-from-call-one. Lane re-probed ARMED today (`available:true, price_t:1`); still no real NPR query ever run | Real money |
| **David picks the moment** | — | **Travelpayouts tours resubmit** (D11). RUL-041 bars an unchanged resubmit; the public launch is the materially changed face | Commercial |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (D12) | Rotation residue |
| **Week 1** | — | Re-read the **Google OAuth user cap** (0/100 displayed; should not bind) · consider **Hetzner console 2FA** (account has none) | Console login |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 — RUL-023, "not optional and not deferrable") | Engagement + spend |
| ~~DONE 29 Aug~~ | — | ✅ **D9 CLOSED — two live real Tuppence buys through Paystack** (David's word, 29 Aug). *Noted, not hidden: the tab-close-mid-flow detached-credit variant is not confirmed as part of those buys — ordinary follow-up, not a gate* · ✅ Send freeze lifted + first waves out (RUL-063) · ✅ Trademark lodged (RUL-062) · ✅ Tester channel retired (RUL-064) | — |

## PROBED THIS RUN — the live facts (30 Aug 2026, 05:05–05:20 UTC)

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `ok` · **v1.3.1** · db primary present (2,879,488 B), integrity **ok** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com**, real client_id `869589580243-…` | PROBED |
| `GET /id-verify/status` | `available:true` · `price_t:1` · "READY — sellers can buy a check" | PROBED |
| `GET /payment/test` | `{"status":"ok","paystack_connected":true}` | PROBED |
| `GET /dashboard/bit` | **8/8 PASS**, worst 0, `failing: []` | PROBED |
| `GET /flags` | `ai_provider.active: openai` · card `2026-08-26.1` · **`fault_report:false`** (RUL-064 live) · `data.flights true` · no gemini (D5) | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| `/static/post_deploy_status.json` | `generated_at 2026-08-30T04:59:48Z` · seed ok · migrations "none pending" | PROBED |
| TLS certificate | valid to **2026-11-22 (84 days)** | PROBED |
| Heartbeat email | 29 Aug 06:00:22Z **in inbox**; today's due 06:00 UTC — sweep ran 05:1x, before it. RG-0138's 7-day staleness tripwire stands watch | PROBED (Gmail) |
| `GET /dashboard/summary` | 200 anonymous, still leaks counts + infra line → RG-0198/RG-0211 open, DW-078 day 4 | PROBED |
| `regression_ledger.py` | **exit 0 · 205 entries · 0 REGRESSED · 19 open · 0 UNVERIFIED** *(first invocation: 2 NOT EVALUATED — fresh sandbox lacked fastapi again; bootstrapped per RG-0200, full board re-run clean — the DW-082/DW-083 pattern, third day running)* | EXECUTED |
| `rulings_check.py` | **69 rulings, 0 FAIL, 0 WARN** (was 0 FAIL **4 WARN** at first check — fixed this run) | EXECUTED |
| `eula_sync.py --check` | in sync, 117,749 B across the three copies | EXECUTED |
| `check_canon_pointers.py` | ALL IN LINE ✓ | EXECUTED |
| `david_queue.py` | 12 items, **5 open** (D9 closed 29 Aug) | EXECUTED |
| `git log origin/deploy..HEAD` | 1 commit, 1 file, **0 deployable** | EXECUTED |

### EXECUTED THIS RUN — what Claude did rather than reported

1. **The 4 rulings_check WARNs were closed, not listed.** RUL-062/063/064/068 (all born launch
   evening) sat on the board as notes, not guarantees — no reflection assertions. Four assertion
   sets written into `scripts/rulings_check.py` (trademark record file, send-freeze lift + key
   row, support@ in privacy.html, the Auction Room concept file). `py_compile` green, re-run:
   **69 checked, 0 FAIL, 0 WARN.** Backup kept beside the file.
2. **A probe-vs-file disagreement was fixed in the same run** (the register's own standing rule):
   RUL-063 names `SECRETS_REGISTER.md new local key row` as a reflection point, but the register
   carried **no such row** (grep: 0 hits). The row was appended (dated, READ-grade, additive) and
   is now asserted by the new RUL-063 reflection check — it can never silently vanish again.
3. **The ledger's fresh-sandbox blind spot was cleared again** (fastapi absent → RG-0181/0182 NOT
   EVALUATED on first invocation; installed, full board re-run to exit 0). Third consecutive day —
   RG-0200's bootstrap-before-ledger clause remains each sweep's step 0.
4. **This register rewritten from today's probes**; changelog fragment dropped in `changelog.d/`.

### NOT DONE, DELIBERATELY

- **RG-0211 redaction** (anonymous `/dashboard/summary`): needs a deploy and touches the endpoint
  both operator consoles read — rides the first post-launch deploy window, per yesterday's
  reasoning, which still stands. Same for DW-062's dead example.com template links (ms.js).
- **RG-0203–0210 feature work**: launch-weekend build lane (CTO), not third-party readiness —
  tracked by the ledger, not re-listed here.
- **The stale scheduled-task prompt** (8 known-stale rows, documented 28–29 Aug): the task file is
  read-only to this run and self-terminates after 1 Sep — the corrections live in this register.

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
| **OpenAI** (BASE lane) | Serving — `active: openai`, card current (re-probed). Production golden run still unrecorded (RG-0132, first post-launch window) | PROBED | No |
| **Anthropic API** (failover) | No key on server by decision (SPEND-GUARD-1); failover proven in decision layer (RG-0128) | EXECUTED | No |
| **Anthropic subscription** (Fable) | **DROP executes 1 Sep** (D8 decided 28 Aug; successor `design → gpt-5.6-sol`, Scaleway standby). Residue: the cancel click if it auto-renews — David, before Tue | READ | No |
| **Gemini** | 🟠 Key still ABSENT (probe: not in `ai_provider.available`). Photo anonymisation reject-only (RUL-033). D5 | PROBED | No |
| **Scaleway** (EU last resort) | Configured, free tier | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks? |
|---|---|---|---|
| **Google OAuth** | ✅ LIVE — `google:true`, start 302s with real client_id (re-probed). RG-0111 LOCKED. Do not re-raise | PROBED | No |
| **Google consent screen** | ✅ PUBLISHED "In production" (27 Aug). Week-1 residuals: user cap 0/100 display; branding | READ | No |
| **Apple Sign-In** | OUT by ruling (RUL-030); `apple:false` (re-probed). Never re-propose | PROBED | — |
| **Didit** | ARMED — `available:true, price_t:1` (re-probed). No real NPR query yet (D10) | PROBED | No |
| **Resend** (app sending) | Sending live, free tier. **First outreach waves out 29 Aug (~90, capped for headroom). $20 Pro flip is TOMORROW, Mon 31 Aug (RUL-061/D6)** | PROBED (sends 29 Aug) | Flip is tomorrow |
| **Resend** (RED-alert watch key) | ALIVE (28 Aug probe 200; heartbeat delivery proven 29 Aug). RG-0201 LOCKED | PROBED (29 Aug) | No |
| **Local outreach key** (CityLauncher) | Burnt 22-Aug copy replaced 29 Aug with scoped sending-only key (RUL-063). Register row added this run | READ | No |
| **support@trustsquare.co** | RG-0174 LOCKED. **Now THE customer complaint lane (RUL-064)** — tester fault tab retired, `fault_report:false` probed live | PROBED | No |
| **Customer-email firewall** | Code carries the gate (RUL-069/RG-0212); **ARMING is David's launch-day act (1 Sep)** — see his table | READ (source) | The arming is a launch-day act |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug; personal address | PROBED (22 Aug) | Presentation only |
| **n8n** | Self-hosted, running (2 Jun) | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live, serving public day 2. SPOF accepted for launch scale. Firewall self-heal armed (RG-0188). No console 2FA (week 1) | PROBED | EUR 15.49 — RUL-025: never rescale | No |
| **Hetzner Object Storage** | Daily 3AM backup, 14-day retention | READ | EUR 5.99 | No |
| **Cloudflare** | Live; WAF deliberately open (RUL-034); hosts uptime Worker + email worker | PROBED | Free | No |
| **SSL** | valid to 2026-11-22 (84 days) | PROBED | Free | No |
| **Domain** | Cloudflare · expires 2026-12-30 · auto-renew ON · lock ON (RG-0137) | PROBED (28 Aug) | Included | No |
| **GitHub** | Live; deploy debt 1 commit, 0 deployable | EXECUTED | Free | No |
| **External uptime monitor** | LIVE — Worker cron */5, alert path proven end-to-end 29 Aug. RG-0138 LOCKED (staleness tripwire) | PROBED (29 Aug) | Free | No |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (`data.flights: true` re-probed), Numista (RG-0150),
free keyless set (RUL-022 — no paid FX ever).
**Tours:** DECLINED 24 Aug; resubmit is D11, David's moment (RUL-041 bars unchanged resubmit).
Drive loader stays OFF (RG-0025 inverted).
**Affiliate lane:** server-side link-out only, fails closed — RG-0181 `[ ok ]` this run.
**Deliberately dark:** JustTCG, Duffel, AeroDataBox, Mapbox, GeoNames, Places.
**Closed:** Google Places (OUT — never re-propose), Amadeus (dead), BrickLink.
**Unknown:** eBay keyset (last entry 7 Jun).

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | v1.15 LIVE (`/terms` re-probed); three copies in sync (117,749 B); canon pointers in line | PROBED | Counsel NOT a gate (RUL-020) |
| **Privacy Policy** | Live-exempted at origin; BACKLOG A1 open | READ | Bar G7 |
| **Privacy UK/US/AU supplements** | Never drafted (RUL-019 made launch worldwide) | READ | Bar G7 |
| **Trade mark** | Lodged 29 Aug (RUL-062): brand-logo device, classes 35/36/42, records 1644020/21/22 Queued. Payment pending (David) | READ | No |
| **IP Brief v6 / WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Deferred to week of 8 Sep by David | READ | Deferred |

---

## WATCH-OUTS

1. **`.env` files prove nothing** — verify at point of USE (RG-0147).
2. **"READY" is not "works"** — Didit probe is presence, not a run (D10). Same class: the
   detached-credit path — two real buys happened, the tab-close variant specifically did not.
3. **Header rot**: BACKLOG.md header still says 18 June; OPEN_LOOPS 🔴 section still physically
   carries discharged B1 (additive discipline — moves at next attended reconciliation).
4. **The scheduled task's prompt is stale on 8+ rows** (secrets "BLOCKING" — done 22 Aug ·
   Resend-422 misread · "no uptime monitor" — live + proven · "domain recorded NOWHERE" —
   RG-0137 · "nothing replaces Fable" — RUL-013/D8 · Paystack 2FA — ON · RG-0136 "stays OPEN" —
   LOCKED · Google OAuth residue). It self-terminates after 1 Sep; corrections live here.
5. **The fresh-sandbox fastapi gap fires every run** — bootstrap BEFORE the ledger (RG-0200
   step 0), or the first invocation reads 2 UNVERIFIED and lies about the board.

### Corrected 22–30 Aug (stands — do not re-raise)

- Secrets rotation DONE (22 Aug; RG-0146/0147 LOCKED). Residue: D12 tokens.
- Resend ~5-min 422 is the HEALTHY answer (INFRA-RESEND-1).
- RUL-013 + D8 answer "what replaces Fable": `design → gpt-5.6-sol`, Scaleway standby.
- `bit_flags.auth_fail_closed: false` is a MISREAD (narrowing switch; real control PASSES).
- RDAP is the wrong door for `.co` — `whois.iana.org` → `whois.registry.co`.
- SSL renews 2026-11-22. `post_deploy_status.json` serves at `/static/`.
- **NEW 30 Aug:** RUL-063's claimed SECRETS_REGISTER key row did not exist — appended and now
  asserted by rulings_check, which also gained RUL-062/064/068 assertions (warns 4 → 0).

---

## VERDICT

**SOFT-PUBLIC DAY 2 · 2 days to full launch (Mon 1 Sep) · GREEN.**

The site is public, up, watched and alarmed; the money rail took its first two real buys; the
first outreach waves are out; every locked fix holds (205 entries, 0 regressed, 0 unverified);
all 69 rulings are reflected with zero warnings for the first time. The path to Monday is three
David acts in order: **the Resend Pro flip tomorrow (D6), the Anthropic cancel click, and arming
the customer-email firewall at the launch flip (RUL-069)** — plus the trademark EFT so the filing
processes. Everything else is post-launch.
