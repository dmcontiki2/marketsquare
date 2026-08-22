# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug** — nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check`. It rewrites the status column from **evidence**, not from what this file claims.*

**Last swept: 2026-08-22 05:0x UTC · 7 days to soft launch · verdict AMBER.**
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

## 🔴 THE ONE BLOCKING ITEM — day 16

**Production secrets are exposed, twice, and have not been rotated.** *(READ — this task deliberately
never reads secrets.)* Compounded by RUL-034: the Cloudflare WAF allowlist is deliberately DOWN, so the
site is publicly reachable *while the burnt credentials are still live*.

Affected: `MS_API_KEY`, `PAYSTACK_WEBHOOK_SECRET`, `RESEND_API_KEY`, `CF_CACHE_TOKEN`,
`MS_DEPLOY_TOKEN`, `FOUNDERS_ID_SALT`, `TRAVELPAYOUTS_TOKEN`, `NUMISTA_API_KEY`, `JUSTTCG_API_KEY`.

**David:** run `ROTATE_SECRETS.bat`, then hand-edit the systemd unit for `MS_API_KEY`,
`MS_DEPLOY_TOKEN`, `FOUNDERS_ID_SALT`. Claude then drives Resend → Cloudflare →
Numista/JustTCG/Travelpayouts. **Do the rotation before deploying the uptime watcher** so the fresh
Resend key goes into it, not the burnt one.

---

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Days left | Action | Why only David |
|---|---|---|---|
| **NOW** | — | Rotate the exposed secrets (above) | Secrets · the one BLOCKING item |
| **NOW** | — | **Google Cloud console → OAuth consent screen: is it PUBLISHED or still in Testing?** Write the answer into `GOOGLE_CONSENT_SCREEN:` above | Console login. In Testing, only listed test users can sign in — invisible to every instrument we own until a stranger tries on 29 Aug |
| **NOW** | — | **Registrar, expiry and auto-renew for trustsquare.co** → the four `DOMAIN_*` fields above | Recorded *nowhere*. DNS is Cloudflare (probed), which does **not** prove who holds the registration |
| **~25 Aug** | 3 | Buy the budget-capped **Gemini** key, paste to server | Money + secret. Until then photo anonymisation is reject-only (RUL-033) |
| **By Wed 27 Aug** | 5 | **Ship the deploy backlog** (3 commits + uncommitted 21 Aug edits — see below) | Deploys reserved to David (RUL-037) |
| **27 Aug** | 5 | Turn on **Paystack 2FA** (reminder set) | Account security |
| **After rotation** | — | Deploy the **uptime watcher** — 3 commands, `ops/cloudflare/UPTIME_MONITOR.md` | Cloudflare token + Resend secret |
| **Launch flip** | 7 | Activate **Resend $20/mo 50k tier** (pre-approved B7 — execution, not a new decision) | Spend |
| **Launch flip** | 7 | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher | Config both sides |
| **Once** | — | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E | Real money on the live rail |
| **Once** | — | One real **Didit** ID check → closes RG-0136 and reveals the true billing shape | Real money |
| **1 Sep 09:00** | 10 | Say go on the **Travelpayouts tours** resubmission (already scheduled) | Commercial |
| **Before 1 Sep** | 10 | **Renew or drop the Anthropic subscription** — the *technical* successor is already decided and wired (see AI table); this is only the subscription question | Spend |
| **Month 1** | — | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

---

## PROBED THIS RUN — the live facts

| Probe | Result | Grade |
|---|---|---|
| `GET /health` | `{"status":"ok","service":"TrustSquare BEA","version":"1.3.1"}`, db integrity ok | PROBED |
| `GET /auth/providers` | `{"google":true,"apple":false}` | PROBED |
| `GET /auth/oauth/google/start` | **302 → accounts.google.com** with a real client_id | PROBED |
| `GET /auth/oauth/apple/start` | **503** — RUL-030 enforcing itself | PROBED |
| `GET /id-verify/status` | `available:true` · `"READY — sellers can buy a check"` · `price_t:1` | PROBED |
| TLS certificate | expires **2026-09-24** — **32 days** | PROBED |
| `regression_ledger.py` | **exit 0** · 132 entries · 0 REGRESSED · 6 honestly open | EXECUTED |
| `rulings_check.py` | **39 rulings, 0 FAIL, 0 WARN** | EXECUTED |
| `eula_sync.py --check` | **in sync**, 117,749 B across `eula_clean.html`, `terms.html`, `ms.js` | EXECUTED |
| `git log origin/deploy..HEAD` | **3 commits unpublished** + uncommitted edits (below) | EXECUTED |
| DNS for trustsquare.co | `ainsley.ns.cloudflare.com` / `koa.ns.cloudflare.com` | PROBED |

**Ledger open entries (6):** RG-0075 (admin-gate script duplicated ×5) · RG-0121 (photo-anon canary dark
by design until the Gemini key) · RG-0132 (openai has no production golden run on record) · **RG-0137,
RG-0138, RG-0139 — new this run.**

### DEPLOY DEBT — the site on 29 Aug is whatever has SHIPPED

Unpublished commits on `main` (last published ref `f77f08c`, Fri 21 Aug 13:52):

- `f2da615` ID-NPR-6 — the ID-verification lane on the infrastructure panel
- `c2ab57b` ONETAP-DOC-1 — Google OAuth was already live; the doc was stale
- `3838142` THIRD_PARTY_LAUNCH_REGISTER — this file

Plus **uncommitted** working-tree edits from the 21 Aug session: `bea_main.py` (8 lines),
`scripts/regression_ledger.py` (4 lines), `test_maintenance_agent.py`. This run added the three new
ledger entries and the uptime-watcher files on top. Tracked as **DW-058**; clears when
`deploy_drift` reads clean.

---

## MONEY

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. Webhook secret armed, RG-0091 passing. `sk_live` install never independently confirmed. **2FA not set up** | READ | 2.9% + R1 | No (B1 cleared) — 2FA + E2E close-out remain |
| **FNB business account** | Open | READ | — | No |
| **CIPC** | Company done (2026/340128/07). Provisional patent not filed (~R900, A7) | READ | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023: month 1, "not optional and not deferrable" | READ | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | READ | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **OpenAI** (BASE lane, 100% of live traffic) | Serving. **No production golden run on record** — ledger RG-0132 open: run `scripts/golden_seam_v2.py` on the box with the production key, then add the lane | EXECUTED | No — but the deferral is now tracked by machinery, not a doc |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover itself is now PROVEN in the decision layer — RG-0128 LOCKED, 13/13 checks | EXECUTED | No |
| **Anthropic subscription** (Fable, fix agent) | Active, **time-boxed to 1 Sep** (RUL-013). **Correction to the 21 Aug entry: the successor is NOT undecided.** RUL-013 names it and `ai_provider.py` already wires it — `TASK_MODEL["design"] = "gpt-5.6-sol"`, Scaleway standby. What expires on 1 Sep is the *subscription*, not the plan | READ + code | No |
| **Gemini** | Dark, key not bought. Funds ~25 Aug (RUL-033). Canary is OPEN by design (RG-0121) | READ | Indirectly — reject-only until then |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | READ | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Grade | Blocks 29 Aug? |
|---|---|---|---|
| **Google OAuth** | ✅ **LIVE** — `/auth/providers` `google:true`; `/auth/oauth/google/start` 302s to Google with a real client_id. RG-0111 LOCKED | PROBED | No |
| **Google consent screen** | ⚠️ **UNRECORDED — Published or Testing is unknown.** Not probeable anonymously: a Testing-mode app 302s identically. In Testing only listed test users can sign in | UNRECORDED | **Potentially yes** — one console glance settles it. RG-0139 |
| **Apple Sign-In** | **OUT by ruling (RUL-030).** `/auth/oauth/apple/start` → 503, enforcing. Do not re-propose | PROBED | — |
| **Didit** (DHA ID check) | **ARMED** — `available:true`, `price_t:1`. Front end shipped 21 Aug. **No real NPR query has ever run**, so the free-500-vs-$1.10-from-call-one question is still open — RG-0136 stays OPEN on that point | PROBED | No (never a blocker by RUL-039) |
| **Resend** | **Sending live** on the free tier. `mail.trustsquare.co` verified, root domain not | READ | Operationally yes — it carries sign-in |
| **Gmail SMTP** (fallback) | Live, sending **from a personal address** | READ | Presentation risk at public launch |
| **support@trustsquare.co** | Inbound live via Cloudflare worker; outbound via `mail.` with Reply-To. A5 still cites the dead Brevo plan | READ | Partly satisfied |
| **n8n** | Self-hosted, running (verified 2 Jun) | READ | No |
| **WhatsApp / Meta** | **Not a dependency.** Open question is AL-8: the SEV-1 wake channel | READ | No |

## INFRASTRUCTURE

| Service | State | Grade | Cost | Blocks 29 Aug? |
|---|---|---|---|---|
| **Hetzner CPX32** | Live. **Single point of failure** | READ | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale** (any rescale reprices to EUR 35.49 permanently) | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention | READ | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live; nameservers `ainsley`/`koa`. **WAF deliberately open** (RUL-034) | PROBED | Free | No |
| **SSL** | Valid to **2026-09-24 — 32 days**. Renews well after launch | PROBED | Free | No |
| **GitHub** | Live. **Repo ahead of live — deploy debt** (3 commits + uncommitted) | EXECUTED | Free | **Yes, in effect** (bar G3) |
| **Domain registrar** | ⚠️ **UNRECORDED.** Now tracked by **RG-0137** — registrar, expiry, auto-renew and the date it was verified | UNRECORDED | Unknown | **Potentially catastrophic** |
| **External uptime monitor** | 🟡 **BUILT 22 Aug, NOT DEPLOYED.** Cloudflare Worker, 5-min cron, 2-strike alert, recovery notice, daily heartbeat. Zero new vendor, zero cost. Deploy = 3 commands. Tracked by **RG-0138** | EXECUTED (source) | Free | No — L8 is no longer waiting on a vendor decision |

## DATA FEEDS

**Live:** Travelpayouts (partner 758984; `data_flights` dark; tours declined 5 Aug — do not resubmit
unchanged), Numista, JustTCG, and the free keyless set (OSM, Scryfall, Wikidata, Frankfurter, FX per RUL-022).
**Dark / deferred:** Duffel, AeroDataBox, Mapbox, GeoNames.
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink (no ZA ops).
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid property/vehicle/collectible vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Grade | Gate? |
|---|---|---|---|
| **EULA** | **v1.14 IS LIVE** (shipped in release `f77f08c`, 21 Aug). The three copies are byte-in-sync — `eula_sync.py --check` passes, 117,749 B | EXECUTED | Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists and is exempted at origin (migration 021); A1 still lists it open | READ | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | READ | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, lands with the EULA | READ | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | READ | No |
| **CC-002 pricing/AI canon** | Parked, 72 days against a 7-day threshold | READ | Land it or formally defer |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **`.env` files prove nothing** — the service reads systemd, not `/var/www/marketsquare/.env` (established 21 Aug).
2. **A10 was marked ARMED the same day RUL-019 said the pastes were still owed.** The ruling register is
   append-only and was never amended, so a session reading it alone will believe `sk_live` is outstanding.
   `PAYSTACK_SECRET_KEY` is never independently confirmed installed anywhere.
3. **`AGENT_BRIEFING` v1.9 is stale** on Paystack ("test mode, live pending CIPC") — treat its other rows with the same caution.
4. **"READY" is not "works"** — the Didit probe is a presence check. No real NPR query has run.
5. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no `LAUNCH_SPECIAL_DEADLINE` at all.
6. **A Testing-mode Google consent screen is invisible to every instrument we own.** It is the only
   remaining sign-in failure mode that would present for the first time on launch morning.

### Corrected 22 Aug — the file was wrong, the code was right

- **"Resend's own health probe 422s every ~5 min on a malformed sender / cries wolf."** **Not a defect.**
  `_infra_resend()` (INFRA-RESEND-1, 22 Jul) posts a deliberately **empty body** and treats **422 as the
  healthy answer** — auth passed, payload rejected, nothing sent. It was chosen because the production key
  is send-scoped and 401s on `/domains` even while sending perfectly. 401/403 is the failure signal, and it
  is mapped to `fail`. There is no cry-wolf and nothing to fix. The separate 7 Aug incident — a genuinely
  malformed `from` losing real mail — was class-fixed the same day as **RESEND-FROM-1** (`_safe_from()`
  validates the sender and falls back to the verified domain). Two different 422s; the register had merged them.
- **"Which AI lane is actually serving?"** Resolved: OpenAI is the base lane, Anthropic carries no server key
  by decision (SPEND-GUARD-1), and RG-0128 proved failover in the decision layer on 21 Aug. The residue is
  RG-0132 (no production golden run for openai), which is tracked machinery, not a contradiction.
- **"Nothing on disk says what replaces Fable."** Wrong — RUL-013 names the successor and `ai_provider.py`
  already wires it (`TASK_MODEL["design"] = "gpt-5.6-sol"`, Scaleway standby). Only the subscription
  renewal is an open question, and it is a spend question.
