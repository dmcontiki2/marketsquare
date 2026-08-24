# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug** — nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-24 ~08:1x UTC · 5 days to soft launch · verdict AMBER.**
Evidence grade on every row below: **PROBED** (measured live this run) · **EXECUTED** (the code path ran) ·
**READ** (a file says so) · **UNRECORDED** (nobody has ever written it down).
Only PROBED is reported as fact — the 21 Aug lesson (the register said Google OAuth was dark; `/auth/providers` said otherwise; the probe won).

---

## MACHINE-READ FIELDS
*The regression ledger reads these lines directly. They stay red until a human fills them in — that is the point.*

```
DOMAIN_REGISTRAR: UNKNOWN
DOMAIN_EXPIRY: UNKNOWN
DOMAIN_AUTORENEW: UNKNOWN
DOMAIN_VERIFIED_ON: UNKNOWN
GOOGLE_CONSENT_SCREEN: UNKNOWN
```
*Ledger: **RG-0137** (domain lifeline) · **RG-0139** (consent screen published). Both OPEN, both print
READY TO LOCK the moment the values above are real. Written 22 Aug so these two facts can never again
live only in a chat message. NOTE 24 Aug: this sweep tried to probe the registrar itself — the .co
registry RDAP endpoints are unreachable from the sandbox and rdap.org has no .co data, so these four
fields genuinely need David's registrar login. One glance settles all four.*

---

## 🟢 YESTERDAY'S TOP RED — CLEARED

**The deploy debt SHIPPED.** The 23 Aug sweep's #1 red (4 commits committed, not live) rode the
**04:25:40Z deploy this morning**: `run_daily_checks.py` deploy_drift reads **"clean — all 19 tracked
files match live"** (ahead [], never_deployed [], missing_local []), post_deploy_status.json (at
`/static/`) records seed ok / migrations none pending, and the ledger promoted the entries that were
waiting on the ride: **RG-0154** (session number derived) and **RG-0158** (SAW-1 teaser live with
honesty labels — teaser PROBED 200 again this run) are closed; **RG-0171** (bulk roster invites
actually send sign-in links) and **RG-0174** (customer email routes to the SUPPORT pipeline, ONE
reply per inbound, personal inbox = dead-letter only — E2E proven, Cloudflare worker wrangler-deployed)
are LOCKED. DW-058 CLOSED with probe evidence.

## 🔴 WHAT ACTUALLY BLOCKS OR THREATENS 29 AUG NOW

1. **Google consent screen Published-or-Testing is UNRECORDED** (RG-0139). A Testing-mode app 302s
   identically to a Published one — invisible to every instrument we own until a stranger tries to
   sign in on launch morning. One console glance settles it. (OAuth start itself re-PROBED this run:
   302 to accounts.google.com with a real client_id.)
2. **Domain registrar / expiry / auto-renew UNRECORDED** (RG-0137). The one dependency that can end
   everything silently. DNS on Cloudflare is PROBED; registry RDAP is unreachable from here (tried
   this run) — only David's registrar login answers it.
3. **RG-0156 — orchestrator.html**: outside the deploy manifest, hardcoded access code in a public
   web root, empty state renders outage as all-clear. Launch gate G2, hard 29 Aug. Claude's build in
   an attended session; must ride a deploy by **Wed 27 Aug (3 days)**.
4. **External uptime monitor still NOT DEPLOYED** (RG-0138) — built 22 Aug, unblocked since the
   rotation, 3 commands in `ops/cloudflare/UPTIME_MONITOR.md`. Every blind day is a blind day, and
   launch weekend unwatched is the worst possible blind spot.

**AMBER, close behind:** RG-0160 (the two example **dossier PDFs** the live SAW teaser is meant to
link do not serve yet — customer-visible on a live page once noticed; build + ride the 27 Aug deploy)
and RG-0173 (**agency journey probe** — the machinery answer to "how did we miss the funnel breaks";
build before the agency wave fires, ideally before 29 Aug).

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Days left | Action | Why only David |
|---|---|---|---|
| **NOW** | — | **Google Cloud console → OAuth consent screen: PUBLISHED or Testing?** Write the answer into `GOOGLE_CONSENT_SCREEN:` above | Console login. RG-0139 |
| **NOW** | — | **Registrar, expiry and auto-renew for trustsquare.co** → the four `DOMAIN_*` fields above | Recorded nowhere; RDAP unreachable. RG-0137 |
| **NOW** | — | **Deploy the uptime watcher** — 3 commands, `ops/cloudflare/UPTIME_MONITOR.md` | Cloudflare token + Resend secret. RG-0138 |
| **~25 Aug** | 1 | Buy the budget-capped **Gemini** key, paste to server | Money + secret. Until then photo anonymisation is reject-only (RUL-033) |
| **By Wed 27 Aug** | 3 | **Run the last pre-launch ship** (carries RG-0156 orchestrator fix + RG-0160 dossier PDFs + today's 3 record commits) | Deploys reserved to David (RUL-037) |
| **27 Aug** | 3 | Turn on **Paystack 2FA** (reminder set) | Account security |
| **Launch flip** | 5 | Activate **Resend $20/mo 50k tier** (pre-approved B7 — execution, not a new decision) | Spend |
| **Launch flip** | 5 | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher | Config both sides |
| **Once** | — | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → settles the free-500-vs-$1.10 billing shape (the unproven clause) | Real money |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`) | Dashboard login. Rotation residue, not blocking |
| **1 Sep 09:00** | 8 | **Travelpayouts tours: READ THE OUTCOME** — resubmitted 22 Aug (RUL-041, D10), 26 programs auto-connect on approval | Commercial |
| **Before 1 Sep** | 8 | **Renew or drop the Anthropic subscription** — technical successor decided and wired (RUL-013, `ai_provider.py`: `gpt-5.6-sol`, Scaleway standby); this is only the subscription question | Spend |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

## PROBED THIS RUN — the live facts

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `{"status":"ok","service":"TrustSquare BEA","version":"1.3.1"}`, db primary present, integrity ok | PROBED |
| `GET /` | 200 in **0.28 s** | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com** with a real client_id | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `"READY — sellers can buy a check"` · `price_t:1` | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** | PROBED |
| TLS certificate | **RENEWED — now expires 2026-11-22 (90 days)**, Google Trust Services. Yesterday's row said 24 Sep / 32 days; the probe won, row corrected | PROBED |
| `/static/studyabroad_teaser.html` | 200, live (RG-0158 now LOCKED) | PROBED |
| `/static/post_deploy_status.json` | 200 — 04:25:40Z placement, seed ok, migrations none pending (root path 404s; `/static/` is the real address) | PROBED |
| `regression_ledger.py` | **exit 0** · 167 entries · **0 REGRESSED** · 14 honestly open | EXECUTED |
| `rulings_check.py` | **51 rulings, 0 FAIL, 0 WARN** (was 42 on 23 Aug — RUL-043…051 landed and are reflected) | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies (source = v1.15) | EXECUTED |
| `git log origin/deploy..HEAD` | **3 commits unpublished — all ledger/ship RECORDS, no app code** (deploy_drift clean); they ride the next ship | EXECUTED |
| `/flags` anonymous | 200 — the gate is DOWN deliberately (pre-launch public face, per D10/RUL-034 posture); expected, not a finding | PROBED |

**Ledger open entries (14):** RG-0075 (admin-gate script ×5) · RG-0121 (photo-anon canary dark until
Gemini — by design) · RG-0132 (no production golden run for openai) · RG-0137, RG-0138, RG-0139 (this
file's machine fields + uptime watcher) · RG-0143 (BIT Mitigator flags must be read by the app) ·
RG-0144 (public dashboard names defence posture to strangers) · RG-0149/RG-0150 (feed licence
obligations / Numista data boundary) · RG-0151 (credential probes test own permission) · RG-0156
(orchestrator — red item 3) · **RG-0160 (dossier PDFs — NEW)** · **RG-0173 (agency journey probe — NEW)**.
Closed since yesterday: RG-0154, RG-0158 (rode the ship); RG-0171, RG-0174 locked.

### DEPLOY DEBT — the site on 29 Aug is whatever has SHIPPED

The 23 Aug debt (SESSION-COUNTER-1, PROVENANCE-1, DEPLOY-COHERENCE-1, SAW-1) **SHIPPED 24 Aug
04:25Z** — deploy_drift clean, all 19 tracked files match live, DW-058 CLOSED. Current debt:

- `eb928d1` / `819341a` / `5e2b0df` — RG-0174 ship record + promotion records (ledger/doc only,
  no deployable files). Publish with the next ship so the deploy ref carries the record.

Still to BUILD and ride the ≤27 Aug ship: RG-0156 orchestrator fix, RG-0160 dossier PDFs.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. `sk_live` install CONFIRMED BY PROBE (22 Aug). Webhook secret armed, RG-0091 passing. **2FA not set up** (27 Aug) | PROBED (22 Aug) | 2.9% + R1 | No — 2FA + E2E close-out remain |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving ($1.89 MTD of $100 cap, 313 calls). **No production golden run on record** — RG-0132 open: run `scripts/golden_seam_v2.py` on the box with the production key | EXECUTED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Local key rotated + probed 22 Aug. Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013). Successor decided and wired: `TASK_MODEL["design"] = "gpt-5.6-sol"`, Scaleway standby. Only the subscription renewal is open — a spend question, David's, before 1 Sep | READ + code | No |
| **Gemini** | Dark, key not bought. **Funds land ~25 Aug — tomorrow** (RUL-033). Canary OPEN by design (RG-0121) | READ | Indirectly — reject-only until then |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with a real client_id (re-probed this run). RG-0111 LOCKED | PROBED | No |
| **Google consent screen** | ⚠️ **UNRECORDED — Published or Testing unknown.** Not probeable anonymously | UNRECORDED | **Potentially yes** — RG-0139 |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing (re-probed). Do not re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1` (re-probed). **Unproven clause stands: no real NPR query has ever run** — billing shape (free-500 vs $1.10/call) and real-registry outcome mapping untested. One real check is on David's once-list | PROBED | No (never a blocker by RUL-039) |
| **Resend** | Sending live, free tier. Key rotated + probed 22 Aug. The ~5-min 422 is the HEALTHY answer (INFRA-RESEND-1 — disproven cry-wolf, do not re-raise). `mail.trustsquare.co` verified, root domain not | PROBED (22 Aug) | Operationally yes — it carries sign-in. $20 tier flips at launch |
| **Gmail SMTP** (fallback) | Authenticated 22 Aug (first time ever). Still sends from a personal address | PROBED (22 Aug) | Presentation risk at public launch |
| **support@trustsquare.co** | ✅ **UPGRADED 24 Aug — RG-0174 LOCKED:** inbound routes to the SUPPORT pipeline, ONE reply per inbound (fault ref carried), personal inbox is dead-letter only. CF worker wrangler-deployed, E2E proven (the old worker forwarded EVERYTHING to dmcontiki2@ and a complaint got two conflicting auto-replies) | EXECUTED + ledger | No |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8: the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live. **Single point of failure**. Disk 45% used / 40G free | READ | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention. ("HETZNER_S3" keys are actually Cloudflare R2 — SECRETS_REGISTER) | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034); origin gate DOWN by pre-launch posture (`/flags` 200 anonymous — expected) | PROBED | Free | No |
| **SSL** | ✅ **RENEWED — valid to 2026-11-22 (90 days)**. Yesterday's 24-Sep/32-day row corrected by probe | PROBED | Free | No |
| **GitHub** | Live. Deploy debt = **3 record-only commits** (no app code; drift clean) | EXECUTED | Free | No |
| **Domain registrar** | ⚠️ **UNRECORDED.** RG-0137. RDAP probe attempted this run — registry unreachable from sandbox; David's login required | UNRECORDED | Unknown | **Potentially catastrophic** |
| **External uptime monitor** | 🔴 **BUILT 22 Aug, STILL NOT DEPLOYED — day 2 unblocked.** 3 commands in `ops/cloudflare/UPTIME_MONITOR.md`. RG-0138 | EXECUTED (source) | Free | No — but launch weekend unwatched is the worst blind spot |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data_flights` dark; token UNROTATABLE-ACCEPTED),
Numista (rotated key probed 200; RG-0150 polices the data boundary), and the free keyless set (OSM, Scryfall,
Wikidata, Frankfurter, FX per RUL-022).
**Tours: RESUBMITTED 22 Aug (RUL-041, D10)** — awaiting Travelpayouts review; 26 programs auto-connect on
approval; on decline, read the reason, never resubmit unchanged, never weaken RUL-040 labelling to pass.
Follow-up reads the outcome 1 Sep.
**Deliberately dark:** JustTCG (key valid, UNSET — free tier is non-commercial; one paste the day David
subscribes $19/mo), Duffel, AeroDataBox, Mapbox, GeoNames.
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink.
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.15 IS LIVE** — `/terms` serves v1.15 (re-probed this run). Three copies byte-in-sync, 117,749 B | PROBED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists and is exempted at origin (migration 021); A1 still lists it open | READ | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Parked, **75 days** against a 7-day threshold (DW-010, formally deferred by David 21 Aug) | READ | Deferred by ruling |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (RG-0147, LOCKED).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
4. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no `LAUNCH_SPECIAL_DEADLINE` at all.
5. **A Testing-mode Google consent screen is invisible to every instrument we own.** The only
   remaining sign-in failure mode that would present for the first time on launch morning.
6. **The scheduled task's own prompt has gone stale** on two rows: it still calls the secrets
   rotation BLOCKING (done + probed 22 Aug, RG-0146/0147 LOCKED) and repeats the Resend
   "malformed-sender 422" claim (disproven 22 Aug — the 422 is the healthy answer). Neither
   re-raised; the prompt should be refreshed when David next edits the task.

### Corrected 24 Aug — files/rows the probes overruled this run

- **SSL row said "expires 2026-09-24 — 32 days"** — the certificate RENEWED; live probe reads
  **2026-11-22 (90 days)**. Row corrected.
- **"Deploy debt — 4 commits" as the #1 red** — shipped 04:25Z today; deploy_drift clean; replaced
  by the 3 record-only commits.
- **`post_deploy_status.json` probe address** — the canonical probe list's bare path 404s; the file
  serves at `/static/post_deploy_status.json` (200). Recorded here so no future sweep misreads a
  404 as a missing deploy record.
- Rulings count 42 → **51**; ledger 151 → **167 entries**, open list refreshed (RG-0154/0158 out,
  RG-0160/0173 in).

### Corrected 22–23 Aug (stands — do not re-raise)

- **Secrets rotation is DONE** (22 Aug): SECRETS_REGISTER "Still burnt" table EMPTY, RG-0146 +
  RG-0147 LOCKED and passing. Residue: two superseded Cloudflare tokens for David to delete;
  FOUNDERS_ID_SALT rotate-or-accept is Claude's pending call.
- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1). No cry-wolf exists.
- **The AI serving lane is resolved**: OpenAI base, Anthropic keyless by decision, failover proven (RG-0128).
- **Fable's successor is named and wired** (RUL-013 + `ai_provider.py`); only the subscription
  renewal is open, and it is a spend question.
- **LEGAL_VERSIONS.md corrected 23 Aug** (EULA v1.15 live) — holding.
