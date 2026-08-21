# THIRD-PARTY LAUNCH REGISTER
**Every external account, key, subscription and legal document — and whether it is actually ready.**

*Created 21 Aug 2026 · Soft launch to public **Fri 29 Aug 2026** · Full launch **Mon 1 Sep 2026** (RUL-001)*
*Last ship day **Wed 27 Aug** — nothing deploys on launch eve.*
*Maintained by the daily scheduled task `pre-soft-launch-third-party-check` (07:00). It rewrites the status column from evidence, not from what this file claims.*

---

## 🔴 THE ONE BLOCKING ITEM

**Production secrets are exposed, twice, and have not been rotated.** This is the only item the
project itself calls BLOCKING (`OPEN_LOOPS.md`). It is compounded by RUL-034: the Cloudflare WAF
allowlist is deliberately DOWN, so the site is publicly reachable *while the burnt credentials are
still live*. Day 15 open.

Affected: `MS_API_KEY`, `PAYSTACK_WEBHOOK_SECRET`, `RESEND_API_KEY`, `CF_CACHE_TOKEN`,
`MS_DEPLOY_TOKEN`, `FOUNDERS_ID_SALT`, `TRAVELPAYOUTS_TOKEN`, `NUMISTA_API_KEY`, `JUSTTCG_API_KEY`.

**David:** run `ROTATE_SECRETS.bat`, then hand-edit the systemd unit for `MS_API_KEY`,
`MS_DEPLOY_TOKEN`, `FOUNDERS_ID_SALT`. Claude then drives Resend → Cloudflare →
Numista/JustTCG/Travelpayouts. Launch bar G2 makes this **hard by 29 Aug**.

---

## DAVID-ONLY ACTIONS, IN DATE ORDER

| When | Action | Why only David |
|---|---|---|
| **NOW** | Rotate the exposed secrets (above) | Secrets · the one BLOCKING item |
| **NOW** | **Confirm the domain registrar, expiry and auto-renew for trustsquare.co** | Recorded *nowhere*. The only dependency that can take the whole platform down with no warning, no owner and no monitor |
| **NOW** | Name an external uptime monitor (or say "pick one") | Vendor choice. Was due 22 Aug; still not built |
| **~25 Aug** | Buy the budget-capped **Gemini** key, paste to server | Money + secret. Until then photo anonymisation runs reject-only (RUL-033) |
| **By 27 Aug** | **Ship the deploy backlog** — the live site on 29 Aug is whatever has SHIPPED | Deploys reserved to David (RUL-037) |
| **27 Aug** | Turn on **Paystack 2FA** (reminder already set) | Account security |
| **Launch flip** | Activate **Resend $20/mo 50k tier** (pre-approved, B7 — execution not a new decision) | Spend |
| **Launch flip** | Set `LAUNCH_SPECIAL_DEADLINE=2026-09-01` on **both** MarketSquare and CityLauncher | Config both sides |
| **Once** | One smallest-pack **Paystack** buy with tab-close → closes the detached-credit E2E | Real money on the live rail |
| **Once** | One real **Didit** ID check → closes RG-0136 and reveals the true billing shape | Real money |
| **1 Sep 09:00** | Say go on the **Travelpayouts tours** resubmission (already scheduled) | Commercial |
| **Before 1 Sep** | Decide what replaces **Fable** — RUL-013's time-box expires that day | Ruling change |
| **Month 1** | Appoint the **accountant** (R2,000/mo + R500 software, RUL-023) | Engagement + spend |

---

## MONEY

| Service | State | Cost | Blocks 29 Aug? |
|---|---|---|---|
| **Paystack** (business 1777715) | LIVE + approved, intl + Apple Pay on. Webhook secret armed, RG-0091 passing. **`sk_live` install never independently confirmed.** 2FA not set up | 2.9% + R1 | No (B1 cleared) — but 2FA and the E2E close-out remain |
| **FNB business account** | Open | — | No |
| **CIPC** | Company done (2026/340128/07). **Provisional patent not filed** (~R900, A7) | R900 one-off | No |
| **Accountant** | **Not engaged.** RUL-023 says month 1, "not optional and not deferrable" | R2,500/mo | No |
| **Paddle** (MoR, phase 2) | Account not opened; pre-check never done | 5% + $0.50 | No |

## AI PROVIDERS

| Service | State | Blocks 29 Aug? |
|---|---|---|
| **OpenAI** (designated BASE lane) | **CONTRADICTORY — see Watch-outs.** Price card says active; baseline says preconditions NOT DONE | G6 allows formal deferral — but the deferral must be *recorded* |
| **Anthropic API** (failover) | **No key on the server, by decision** (SPEND-GUARD-1). Failover has never been exercised despite ten incidents 12–19 Aug | No, but DW-054 is an open FAIL |
| **Anthropic subscription** (Fable) | Active — **and time-boxed: ends 1 Sep, does not renew by default** (RUL-013) | Expires *on* full-launch day |
| **Gemini** | Dark, key not bought. Funds land ~25 Aug (RUL-033) | Indirectly — reject-only mode until then |
| **Scaleway** (EU last resort) | Configured, free tier, price unobservable | No |

## IDENTITY · EMAIL · SIGN-IN

| Service | State | Blocks 29 Aug? |
|---|---|---|
| **Didit** (DHA ID check) | Armed 21 Aug (`/id-verify/status` READY). Front end shipped 21 Aug. **No real query has ever run** — RG-0136 OPEN | No (never a blocker by RUL-039) |
| **Resend** | **Sending live** on the **free tier**. `mail.trustsquare.co` verified, root domain not. Its own health probe 422s every ~5 min on a malformed sender — *noise now, outage-mask later* | Operationally yes — it carries sign-in |
| **Gmail SMTP** (fallback) | Live, sending **from a personal address** | Presentation risk at public launch |
| **support@trustsquare.co** | Inbound live via Cloudflare worker; outbound via `mail.` with Reply-To. A5 still cites the dead Brevo plan | Partly satisfied |
| **Google OAuth** | ✅ **LIVE** — verified 21 Aug: `/auth/providers` → `google:true`, start endpoint 302s. RG-0111 LOCKED. *Only residue:* confirm the consent screen is **Published**, not left in Testing — in Testing only listed test users can sign in | No |
| **Apple Sign-In** | **OUT by ruling (RUL-030). Do not re-propose.** | — |
| **n8n** | Self-hosted, running (verified 2 Jun) | No |
| **WhatsApp / Meta** | **Not a dependency.** Only open question is AL-8: the SEV-1 wake channel | No |

## INFRASTRUCTURE

| Service | State | Cost | Blocks 29 Aug? |
|---|---|---|---|
| **Hetzner CPX32** | Live. **Single point of failure** | **EUR 15.49/mo grandfathered — RUL-025: do NOT rescale, any rescale reprices to EUR 35.49 permanently** | No |
| **Hetzner Object Storage** | Live, daily 3AM backup, 14-day retention | EUR 5.99 | No |
| **Cloudflare** (DNS/CDN/WAF/R2/email) | Live. **WAF deliberately open** (RUL-034). One stale cache token | Free | No |
| **SSL** | Cloudflare Origin CA, long-dated | Free | No |
| **GitHub** | Live. **Repo ahead of live — deploy debt** | Free | **Yes, in effect** (bar G3) |
| **Domain registrar** | ⚠️ **UNKNOWN — recorded nowhere** | Unknown | **Potentially catastrophic** |
| **External uptime monitor** | **Not built, no vendor named.** Due 22 Aug | — | Bar G4 |

## DATA FEEDS

**Live:** Travelpayouts (partner 758984; `data_flights` dark; tours declined 5 Aug — do not resubmit unchanged), Numista, JustTCG, and the free keyless set (OSM, Scryfall, Wikidata, Frankfurter, FX per RUL-022).
**Dark / deferred:** Duffel, AeroDataBox, Mapbox, GeoNames.
**Closed:** Google Places (**OUT — silent ~$360 bill, never re-propose**), Amadeus (portal dead 17 Jul), BrickLink (no ZA ops).
**Unknown:** eBay keyset was "pending ~1 day" on 7 Jun — no later entry says it arrived.
**Held:** ~14 paid property/vehicle/collectible vendors, all `false` until David enables with a ceiling.

---

## DOCUMENTS

| Document | State | Gate? |
|---|---|---|
| **EULA v1.15** | PUBLISHED pre-counsel. **v1.13–v1.15 were unshipped as of 21 Aug** — §3.5A is what the ID-verify feature depends on | Ship it. Counsel (A6) is **NOT a gate** (RUL-020) |
| **Privacy Policy** | `privacy.html` exists; A1 still lists it open | Bar G7 |
| **Privacy UK/US/AU supplements (D4)** | **Never drafted.** Matters because RUL-019 made launch worldwide | Bar G7 · David confirms scope, Claude drafts |
| **IP Brief v6** | DRAFT, counsel-gated, must land with the EULA | Not in the bar |
| **WhitePaper v3.11** | DRAFT (v2 is the published prior-art defence) | No |
| **CC-002 pricing/AI canon** | Parked, 71 days against a 7-day threshold | Land it or formally defer |

---

## WATCH-OUTS — contradictions on disk, stated not resolved

1. **Which AI lane is actually serving?** Baseline and RUL-002 say OpenAI base / Anthropic failover; `bea_main.py` still labels Anthropic "ACTIVE"; the server carries no Anthropic key. One `GET /ops/selfcheck` settles it.
2. **A10 was marked ARMED the same day RUL-019 said the pastes were still owed.** The ruling register is append-only and was never amended, so a future session reading it alone will believe `sk_live` is outstanding. `PAYSTACK_SECRET_KEY` is never independently confirmed installed anywhere.
3. **`.env` files prove nothing** — the service reads systemd, not `/var/www/marketsquare/.env` (established 21 Aug).
4. **`AGENT_BRIEFING` v1.9 is stale** on Paystack ("test mode, live pending CIPC") — treat its other rows with the same caution.
5. **"READY" is not "works"** — the Didit probe is a presence check. No real query has run.
6. **Resend's own monitor cries wolf every 5 minutes.** A monitor that always alarms will not tell you when Resend actually stops on 29 Aug.
7. **`LAUNCH_DEADLINE-1` is unsatisfied on the CityLauncher side** — that `.env` has no `LAUNCH_SPECIAL_DEADLINE` at all.
