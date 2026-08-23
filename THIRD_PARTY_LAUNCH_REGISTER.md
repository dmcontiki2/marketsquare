# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug** — nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-23 ~07:1x UTC · 6 days to soft launch · verdict AMBER.**
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
live only in a chat message.*

---

## 🟢 YESTERDAY'S ONE BLOCKING ITEM — CLEARED

**The secrets rotation is DONE.** This register's 22 Aug sweep still carried it as the one BLOCKING
item; the rotation completed later that same day, after the sweep ran. Evidence, not prose:
`SECRETS_REGISTER.md`'s **"Still burnt" table is EMPTY** (REGISTER_VERIFIED: 2026-08-22), and ledger
**RG-0146 is LOCKED and passing** — *"no credential is still marked BURNT"* (EXECUTED this run, exit 0).
Every rotated credential was verified at the point of USE (RG-0147): Paystack 200, Resend 422-healthy,
Anthropic /v1/models 200, R2 ListObjects, real cache purge, Numista/JustTCG 200s. The Google ACCOUNT
password was changed 22 Aug; the Gmail SMTP fallback authenticated for the first time EVER (the old
"app password" was the account password and had never worked).

Residue, none blocking: David deletes two superseded Cloudflare tokens in the dashboard
(`MarketSquare Media`, `Trustsquare Cache Purge`); `FOUNDERS_ID_SALT` rotate-or-accept is Claude's
call (rotating invalidates existing ID hashes), tracked in SECRETS_REGISTER.md; TRAVELPAYOUTS_TOKEN
is UNROTATABLE-ACCEPTED (dated reasoning in the register, policed by RG-0146). OPEN_LOOPS B1's
"Ten still BURNT" cell was stale mid-rotation text — corrected by this sweep.

## 🔴 WHAT ACTUALLY BLOCKS OR THREATENS 29 AUG NOW

1. **Deploy debt — 4 commits committed, NOT live** (ship by **Wed 27 Aug**, 4 days). The site on
   29 Aug is whatever has SHIPPED. Details under DEPLOY DEBT below. Deploys are David's (RUL-037).
2. **Google consent screen Published-or-Testing is UNRECORDED** (RG-0139). A Testing-mode app 302s
   identically to a Published one — invisible to every instrument we own until a stranger tries to
   sign in on launch morning. One console glance settles it.
3. **Domain registrar / expiry / auto-renew UNRECORDED** (RG-0137). The one dependency that can end
   everything silently. DNS on Cloudflare is PROBED, but that does not prove who holds the registration.
4. **RG-0156 — orchestrator.html**: outside the deploy manifest, hardcoded access code `96315` in a
   public web root, empty state renders outage as all-clear. The ledger calls it launch gate G2,
   hard 29 Aug. The one BUILD still owed before 27 Aug — Claude's work in an attended session, rides
   David's deploy. Tracked by machinery (OPEN entry), per RUL-037.

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Days left | Action | Why only David |
|---|---|---|---|
| **NOW** | — | **Google Cloud console → OAuth consent screen: PUBLISHED or Testing?** Write the answer into `GOOGLE_CONSENT_SCREEN:` above | Console login. RG-0139 |
| **NOW** | — | **Registrar, expiry and auto-renew for trustsquare.co** → the four `DOMAIN_*` fields above | Recorded nowhere. RG-0137 |
| **NOW — unblocked** | — | **Deploy the uptime watcher** — 3 commands, `ops/cloudflare/UPTIME_MONITOR.md`. The rotation it was waiting on is DONE; the fresh Resend key goes in | Cloudflare token + Resend secret. RG-0138 |
| **~25 Aug** | 2 | Buy the budget-capped **Gemini** key, paste to server | Money + secret. Until then photo anonymisation is reject-only (RUL-033) |
| **By Wed 27 Aug** | 4 | **Ship the deploy backlog** (4 commits, below) | Deploys reserved to David (RUL-037) |
| **27 Aug** | 4 | Turn on **Paystack 2FA** (reminder set) | Account security |
| **Launch flip** | 6 | Activate **Resend $20/mo 50k tier** (pre-approved B7 — execution, not a new decision) | Spend |
| **Launch flip** | 6 | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher | Config both sides |
| **Once** | — | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → settles the free-500-vs-$1.10 billing shape (RG-0136's unproven clause) | Real money |
| **When convenient** | — | Delete the two superseded **Cloudflare tokens** (`MarketSquare Media`, `Trustsquare Cache Purge`) | Dashboard login. Rotation residue, not blocking |
| **1 Sep 09:00** | 9 | **Travelpayouts tours: READ THE OUTCOME** — resubmitted 22 Aug (RUL-041, D10), 26 programs auto-connect on approval | Commercial |
| **Before 1 Sep** | 9 | **Renew or drop the Anthropic subscription** — the technical successor is decided and wired (RUL-013, `ai_provider.py`: `gpt-5.6-sol`, Scaleway standby); this is only the subscription question | Spend |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

## PROBED THIS RUN — the live facts

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `{"status":"ok","service":"TrustSquare BEA","version":"1.3.1"}`, db integrity ok | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com** with a real client_id | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `"READY — sellers can buy a check"` · `price_t:1` | PROBED |
| `GET /terms` | 200, serving **EULA v1.15** — LEGAL_VERSIONS said "not yet deployed"; the probe won, file corrected this run | PROBED |
| TLS certificate | expires **2026-09-24** — **32 days** | PROBED |
| `/static/studyabroad_teaser.html` | **404** — SAW-1 is committed, not shipped (RG-0158's honest red) | PROBED |
| `regression_ledger.py` | **exit 0** · 151 entries · **0 REGRESSED** · 14 honestly open | EXECUTED |
| `rulings_check.py` | **42 rulings, 0 FAIL, 0 WARN** | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across the three copies (source = v1.15) | EXECUTED |
| `git log origin/deploy..HEAD` | **4 commits unpublished** (+ the nightly checkpoint marker); working tree carries only daily watch/audit artifacts | EXECUTED |

**Ledger open entries (14):** RG-0075 (admin-gate script ×5) · RG-0121 (photo-anon canary dark until
Gemini) · RG-0132 (no production golden run for openai) · RG-0137, RG-0138, RG-0139 (this file's
machine fields + uptime watcher) · RG-0143 (BIT Mitigator flags must be read by the app) · RG-0144
(public dashboard names defence posture to strangers) · RG-0149/RG-0150 (feed licence obligations /
Numista data boundary) · RG-0151 (credential probes test own permission) · RG-0154 (session-number
mechanism — **fix committed, closes on ship**) · RG-0156 (orchestrator, item 4 above) · RG-0158
(SAW-1 teaser — **fix committed, closes on ship**).

### DEPLOY DEBT — the site on 29 Aug is whatever has SHIPPED

The 21 Aug session's debt SHIPPED (live ms.js moved v514 → v517; EULA v1.15 live). New debt —
unpublished commits on `main` vs `origin/deploy`:

- `76606ff` SESSION-COUNTER-1 — derived session number, dated badge (RG-0154 closes on ship)
- `085430f` PROVENANCE-1 — dashboard inventory (RG-0155 locked, needs the ship to hold live)
- `02d9184` DEPLOY-COHERENCE-1 — migration 030 committed so schema ships with code (RG-0157)
- `b6a3777` SAW-1 — Study & Work Abroad teaser + banner + manifest (RG-0158 closes on ship)
- `49e6ed3` nightly checkpoint marker (no deploy)

Files local-ahead of live per deploy_drift: `bea_main.py`, `dashboard.server.html`,
`marketsquare.html`. Tracked as **DW-058**; clears when `deploy_drift` reads clean.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. **`sk_live` install now CONFIRMED BY PROBE** (22 Aug rotation: `GET /transaction/totals` 200 with the fresh key). Webhook secret armed, RG-0091 passing. **2FA not set up** (27 Aug) | PROBED (22 Aug) | 2.9% + R1 | No — 2FA + E2E close-out remain |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving. **No production golden run on record** — RG-0132 open: run `scripts/golden_seam_v2.py` on the box with the production key | EXECUTED | No — tracked by machinery |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Local key ROTATED + probed 22 Aug (`/v1/models` 200). Failover PROVEN in the decision layer — RG-0128 LOCKED | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013). Successor decided and wired: `TASK_MODEL["design"] = "gpt-5.6-sol"`, Scaleway standby. Only the subscription renewal is open — a spend question | READ + code | No |
| **Gemini** | Dark, key not bought. Funds ~25 Aug (RUL-033). Canary OPEN by design (RG-0121) | READ | Indirectly — reject-only until then |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `google:true`; start 302s to Google with a real client_id. RG-0111 LOCKED and passing | PROBED | No |
| **Google consent screen** | ⚠️ **UNRECORDED — Published or Testing unknown.** Not probeable anonymously | UNRECORDED | **Potentially yes** — RG-0139 |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** start → 503, enforcing. Do not re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1`. RG-0136 LOCKED 21 Aug (14 guards). **Unproven clause stands: no real NPR query has ever run** — billing shape (free-500 vs $1.10/call) and real-registry outcome mapping untested | PROBED | No (never a blocker by RUL-039) |
| **Resend** | Sending live, free tier. **Key ROTATED + probed 22 Aug** (422-healthy by design — INFRA-RESEND-1; the "cry-wolf 422" claim was disproven 22 Aug, do not re-raise). `mail.trustsquare.co` verified, root domain not | PROBED (22 Aug) | Operationally yes — it carries sign-in. $20 tier flips at launch |
| **Gmail SMTP** (fallback) | **Authenticated for the FIRST TIME 22 Aug** — a real app password now installed; the old value was the account password and had never worked. Still sends from a personal address | PROBED (22 Aug) | Presentation risk at public launch |
| **support@trustsquare.co** | Inbound live via Cloudflare worker; outbound via `mail.` with Reply-To. A5 still cites the dead Brevo plan | READ | Partly satisfied |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8: the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live. **Single point of failure** | READ | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention. **The "HETZNER_S3" keys are actually Cloudflare R2** (name lies — SECRETS_REGISTER), new token scoped to the media bucket only | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034) — tolerable now the secrets are rotated | PROBED | Free | No |
| **SSL** | Valid to **2026-09-24 — 32 days**. Renews well after launch | PROBED | Free | No |
| **GitHub** | Live. **Repo ahead of live — deploy debt** (4 commits) | EXECUTED | Free | **Yes, in effect** (bar G3) |
| **Domain registrar** | ⚠️ **UNRECORDED.** RG-0137 | UNRECORDED | Unknown | **Potentially catastrophic** |
| **External uptime monitor** | 🟡 **BUILT 22 Aug, NOT DEPLOYED — now UNBLOCKED** (rotation done, fresh Resend key available). Cloudflare Worker, 5-min cron, 2-strike alert, recovery notice, daily heartbeat. Deploy = 3 commands in `ops/cloudflare/UPTIME_MONITOR.md`. RG-0138 | EXECUTED (source) | Free | No — but every blind day is a blind day |

## DATA FEEDS

**Live:** Travelpayouts flights Data API (partner 758984; `data_flights` dark; token UNROTATABLE-ACCEPTED),
Numista (rotated key probed 200; RG-0150 polices the data boundary), and the free keyless set (OSM, Scryfall,
Wikidata, Frankfurter, FX per RUL-022).
**Tours: RESUBMITTED 22 Aug (RUL-041, D10)** — awaiting Travelpayouts review; 26 programs auto-connect on
approval; on decline, read the reason, never resubmit unchanged, never weaken RUL-040 labelling to pass.
**Deliberately dark:** JustTCG (key rotated + valid, UNSET 22 Aug — free tier is non-commercial;
one paste the day David subscribes $19/mo; FEED_LICENCES.md + RG-0148), Duffel, AeroDataBox, Mapbox, GeoNames.
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink.
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.15 IS LIVE** — `/terms` serves v1.15 (PROBED this run; LEGAL_VERSIONS' "not yet deployed" was stale and is corrected). Three copies byte-in-sync, 117,749 B | PROBED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists and is exempted at origin (migration 021); A1 still lists it open | READ | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Parked, 73 days against a 7-day threshold | READ | Land it or formally defer |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — verify at the point of USE (`/proc/<pid>/environ` + a live
   authenticated call), never from the file written to. Now asserted by RG-0147 (LOCKED), paid for
   by the Paystack incident (a correct write reported success while production held the revoked key).
2. **`AGENT_BRIEFING` v1.9 is stale** on Paystack — treat its other rows with the same caution.
3. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
4. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no `LAUNCH_SPECIAL_DEADLINE` at all.
5. **A Testing-mode Google consent screen is invisible to every instrument we own.** The only
   remaining sign-in failure mode that would present for the first time on launch morning.

### Corrected 23 Aug — files the probes overruled this run

- **This register's own "ONE BLOCKING ITEM" (secrets burnt)** — stale by half a day: rotation
  completed 22 Aug after the sweep. SECRETS_REGISTER "Still burnt" table EMPTY, RG-0146 locked and
  passing. **OPEN_LOOPS B1's "Ten still BURNT" cell corrected** the same way.
- **"`sk_live` install never independently confirmed"** — confirmed 22 Aug by probe (Paystack 200).
- **LEGAL_VERSIONS.md said EULA v1.15 "Not yet deployed"** — `/terms` serves v1.15. File corrected.
- **"tours declined 5 Aug — do not resubmit unchanged"** stood as the last word — resubmitted 22 Aug
  per RUL-041 (D10); the register now says AWAIT OUTCOME.
- Rulings count 39 → **42** (RUL-040/041/042); ledger 132 → **151 entries**, open 6 → **14** (the
  20 Aug licence/mitigator/posture sweeps added honest reds; two of the 14 close on the next ship).

### Corrected 22 Aug (stands — do not re-raise)

- **Resend's ~5-min 422 is the HEALTHY answer** (INFRA-RESEND-1 posts an empty body by design;
  401/403 is the failure signal). The 7 Aug malformed-sender incident was separately class-fixed
  (RESEND-FROM-1). No cry-wolf exists.
- **The AI serving lane is resolved**: OpenAI base, Anthropic keyless by decision, failover proven (RG-0128).
- **Fable's successor is named and wired** (RUL-013 + `ai_provider.py`); only the subscription
  renewal is open, and it is a spend question.
