# PRINCIPLE_REQUIREMENTS.md
**Solar Council · MarketSquare Platform**
Version 1.3 — DRAFT (CCP CC-001 + CC-002) · 10 June 2026 · ⚠ NOT in force until David approves; the deployed v1.2 (17 May) remains controlling. NOTE: the AdvertAgent/CityLauncher/Codices copies are still v1.1 (12 Apr) — the four copies have diverged; after approval copy THIS file to all four folders.
Source of truth: Solar_Council_Codex_v4_8_DRAFT.docx (v4_7 + Canon Addendum 1 rev 2 until landed) · AGENT_BRIEFING.md v1.8-staged · Session 61 infrastructure decisions

This file is read-only. No agent or Cowork task may modify it.
Place a copy in the root of every project folder (MarketApp, AdminApp, CityLauncher, AdvertAgent).
When the Codex is updated, regenerate this file from Claude Chat and replace all copies.

---

## PART A · Product Principles (Locked — council review required to change)

### A1 · Tuppence is the only transaction currency
- 1 Tuppence (1T) = USD $2. Fixed. Not configurable.
- The requester pays (the service consumer — the buyer, for introductions). Tuppence follows the HOLD (CC-001): committed on request → burned on delivery (seller accepts / AI result delivered) → released in full on decline, 48-h expiry, or AI failure. A release frees an un-spent hold — it is never a refund.
- Seller earns zero commission. MarketSquare earns from intro fees + subscriptions only.
- Applies to: FEA wallet · BEA /intros/accept · Paystack flow · all pricing displays.

### A2 · Anonymity is Mode B — non-negotiable
- Seller name, email, business name, contact details, and location are NEVER revealed to buyers until both parties accept an introduction.
- Seller CV shows emoji avatar + lock mask only. No photo. No name. No location detail.
- Identity reveal is a bilateral event — both parties must accept before anything is shown.
- Applies to: FEA detail screen · seller CV · BEA listing payloads · admin tool · any future agent app.

### A3 · Introduction models are locked by category
- Property → Commitment model: listing pauses on request, one buyer at a time, 48hr window.
  - Seller ignores: Trust Score −5. Listing unpauses automatically. Seller declines: no penalty.
- Tutors / Services → Soft Queue: listing stays live, multiple buyers can queue, 48hr window.
  - Seller ignores: Trust Score −3. Seller declines: no penalty.
- Help Wanted → Soft Queue (helper owns the listing).
- Cannot be changed or mixed without full council review.
- Applies to: FEA intro flow · BEA accept/decline logic · dashboard cards.

### A4 · Three Liquidity Levers are locked
1. Listing First — listing created before account. Never gate behind registration.
2. Minimum Viable Listing — photo (skippable) + category + title/price. Target: under 30 seconds.
3. Show Activity Immediately — founding seller content visible on first open. Never show empty state.
- Applies to: FEA publish wizard · onboard flow · home screen.

### A5 · Trust Score governs visibility and priority
- 0–39: New (no badge) · 40–69: Established (blue) · 70–89: Trusted (green) · 90–100: Highly Trusted (gold + featured).
- Score drives display order and badge display. Penalties reduce score as per A3.
- Applies to: FEA listing cards · seller CV · BEA trust calculations.

### A6 · City go-live thresholds are the expansion trigger
- Loop: 1 per category (internal only).
- Liquidity: 15 per category (soft launch).
- Public: 60 total / 20 per category.
- Density: 80 total / 20 per category (full promotion).
- Never launch a city below threshold. Never hardcode these numbers — they are governance rules.
- Applies to: CityLauncher KPI · admin tool count · city wave cascade · +1 Dashboard KPI page.

### A7 · Subscription tiers (5-tier canon — Session 91 / CC-002)
- One subscription family: Free $0 · Standard $12/mo · Professional $20/mo · Business $40/mo · Elite $100/mo.
- Listing slots are a CAP (meter display, not a wallet): 2 / 10 / 25 / 60 / 500.
- Monthly Tuppence to paid tiers = price ÷ 2 at 1T = $2: 6 / 10 / 20 / 50T (Founders ×1.2 rounded up: 8 / 12 / 24 / 60T).
- "AI uses" / AI-session allowances are RETIRED: in-app AI guidance is free; advanced AI functions are Tuppence-priced per use through the HOLD ledger (/tuppence/ai-commit + /tuppence/ai-settle).
- Daily Introduction-session limits are retired [AD-07 — David confirm].
- Applies to: FEA plans screen + wallet · BEA verify_seller_subscription + launch_redemption.py · EULA tier disclosure · support FAQ.

---

## PART B · Sovereignty Stack Principles (Core — no exceptions)

### A8 · Tuppence deductions are purchase-only — never punitive (CORE PRINCIPLE)
- Tuppence is NEVER deducted from any wallet as a punishment, penalty, or deterrent.
- The only valid reasons to deduct Tuppence are: (i) buyer pays an Introduction fee; (ii) seller or buyer purchases an AI service; (iii) seller purchases a Boost.
- Negative behaviour (ignoring intros, declining without reason, no-shows, bad referrals) is penalised exclusively via Trust Score reduction and, in severe or repeat cases, Banishment (account suspension or permanent ban).
- This principle is non-negotiable. No agent, architect, or future feature may introduce a Tuppence-deduction penalty under any framing (fee, bond, deposit, resubmission cost, etc.).
- Rationale: punitive deductions create fear, erode trust, and undermine the platform's commitment-signal model. Trust Score is the correct instrument — it is visible, recoverable, and proportionate.
- Applies to: BEA all endpoints · FEA all flows · admin tool · future agent features · EULA · any legal documentation.


### B1 · No SaaS. No cloud lock-in. Self-hosted always.
- Server: Hetzner CPX22 → **CPX32 from 25 May 2026** · 178.104.73.239 · Ubuntu 24.04.
  - CPX32: 4 vCPU · 8 GB RAM · 160 GB NVMe · €15.49/month (upgraded from CPX22 €9.49/month).
- Stack: FastAPI BEA + SQLite (WAL) + Redis + nginx. No managed databases. No external services.
- Target infrastructure cost: **€15.49/month from 25 May 2026** (previously ~€9.49/month).
- Hetzner Volume (independent block storage, €0.052/GB/month) on standby — activate when local disk approaches 80% capacity.
- Never add a managed service or SaaS dependency without council review.

### B2 · Server is the single source of truth
- SCP files down before editing. SCP back + `systemctl restart marketsquare` after.
- Use `deploy_marketsquare.bat` for all four deployment steps.
- Never edit a local copy and assume it matches the server.

### B3 · Credentials never in chat windows
- API keys, passwords, and tokens are entered directly into SSH terminal only.
- Admin key stored in systemd drop-in at /etc/systemd/system/marketsquare.service.d/env.conf → /etc/environment.
- Must move to .env before any public exposure.

### B4 · Photo storage: Cloudflare R2 (primary) + Hetzner local mirror (redundant fallback)
- **Write-to-both pattern (from 17 May 2026):** every photo upload writes simultaneously to:
  1. **Cloudflare R2 (EU)** — primary CDN. Bucket: marketsquare-media. $0 egress. Env vars: HETZNER_S3_* in /etc/environment.
  2. **Hetzner local disk** — `/var/www/marketsquare/media/` — redundant fallback. No dependency on external service.
- **JS failover:** `r2Fallback()` in marketsquare.html — if an R2 URL fails to load (`onerror`), the browser automatically retries against `/media/<key>` on the same server. Zero user-visible failure.
- **Storage projection:** 50,000 listings globally ≈ 29.5 GB (3 photos × 200 KB thumb + 400 KB medium per listing). Well within CPX32 160 GB NVMe capacity.
- **Self-funding:** 2 Starter subscribers ($10/month) cover the full CPX32 upgrade cost — storage scaling is subscription-neutral.
- DB backups: daily 3 AM cron → R2 backups/ · 14-day retention.
- Script: /usr/local/bin/backup_dbs_to_r2.py.

### B5 · Geographic data is database-driven, never hardcoded
- 4-level hierarchy: geo_countries → geo_regions → geo_cities → geo_suburbs.
- Seeded from GeoNames (username: dmcontiki2). All geo served via BEA /geo/* endpoints.
- `activeCity` is always {id, name}. `activeSuburb` is {id, name} or null.
- BEA geo API param is `country` — NOT `country_iso2`. This is a known drift point.
- South Africa pre-seeded. Other countries added via POST /geo/countries.

### B6 · Infrastructure costs are monitored
- Any agent change affecting infra, pricing, scaling, or storage triggers a "Cost model impact:" entry in CHANGELOG.md.
- **Current tier (until 24 May 2026):** Hetzner CPX22 · €9.49/month.
- **Upgraded tier (from 25 May 2026):** Hetzner CPX32 · €15.49/month · 4 vCPU · 8 GB RAM · 160 GB NVMe.
- **On standby:** Hetzner Volume (block storage) · €0.052/GB/month · independent of server · survives server rebuild. Activate when disk >80% full.
- CPX32 comfortable capacity: ~100,000 sessions/day · photo storage self-sufficient to ~50,000 listings globally.
- Self-funding model: 2 Starter subscribers cover the full CPX32 upgrade cost delta (€6/month).

### B7 · No consumption-based external API without explicit approval and a hard cost ceiling
- This rule exists because a Google Maps API project (radiant-arcanum-455219-u2) was activated during CityLauncher development without adequate cost warning, resulting in a $360+ charge to David. This must never happen again.
- Before any external API with usage-based or consumption-based billing is activated in ANY project, David must explicitly approve it in the chat with a hard monthly cost ceiling agreed in advance.
- If an agent activates such an API without this approval, it is a critical violation of the sovereignty stack principle.
- Exempt (free tier, no approval needed): Overpass/OSM API · GeoNames API · Resend under 3,000 emails/month · Cloudflare free tier.
- NOT exempt (require explicit David approval + cost ceiling): Google Maps API · Google Places API · Any cloud ML/AI API · Any maps or search API with per-request billing · Any API requiring a credit card to activate.
- When suggesting an API that has any cost attached, the agent must state the cost explicitly and wait for David to say yes before proceeding.

---

## PART C · File and Code Principles (All agents — no exceptions)

### C1 · Local filenames have no version suffix
- Always: `marketsquare.html` · `marketsquare_admin.html` · `bea_main.py`.
- Any reference to v8_6b, v1_1, or similar in older docs is outdated. Use the names above.

### C2 · Single-file architecture — surgical edits only
- Both HTML files are single-file. Structure: DATA LAYER → STYLES → UI SCREENS → LOGIC.
- Never rewrite large sections unless David explicitly instructs.
- No large refactors. No structural changes without Architect agent sign-off.

### C3 · Always use `findListing(id)` — never `LISTINGS[id]`
- BEA listing ids are strings ('bea_N'). Direct array access fails silently.
- All onclick handlers must quote ids: `openDetail('${l.id}')` not `openDetail(${l.id})`.

### C4 · One task at a time. Definition of done = code + changelog.
- Complete one feature or bug fix fully before starting the next.
- Done = working code AND one paragraph appended to CHANGELOG.md.
- Git commit after every completed task. Auto-commit — do not wait for approval.

### C5 · Codex first — check before adding business logic
- `Solar_Council_Codex_v4_5.docx` is the canonical rules document.
- Architect agent arbitrates via Codex. Escalate to David only if Codex cannot resolve.

### C6 · STATUS.md is read first, every session
- Read STATUS.md before AGENT_BRIEFING.md. Then begin work.
- Update "Last Completed" and "Next Task" at session end. Keep under 60 lines.
- No hardcoded live data in STATUS.md — point to BEA endpoints instead.

### C7 · Run /compact when context fills up
- Never let context overflow silently. Context management is part of the definition of done for long sessions.

---

## PART D · CityLauncher Principles (Internal ops tool — never user-facing)

### D1 · No confirmed email = no record written to database
- This is the hardest rule in CityLauncher. A prospect without a verified email is discarded, not stored. No exceptions.

### D2 · Scrape real individuals only — never businesses or agencies
- Estate agents: individual agents from Property24 profile pages.
- Services: individual tradespeople from personal ads (Gumtree SA, multi-source DOM-verified).
- Tutors: individuals from personal ads.
- Target: 20 real individuals per category per city.

### D3 · Pipeline runs per suburb — not per city
- Fetch suburb list from BEA `GET /geo/suburbs?city_id=N`.
- Scrape per suburb. Aggregate to city level. Never hardcode suburb lists.

### D4 · Respect robots.txt. Random 2–5 second delays between requests.
- Never retry aggressively. Flag if a source blocks scraping. Do not circumvent blocks.
- Use Playwright (headless) for browser-based scraping.

### D5 · CityLauncher is internal — never user-facing
- Dashboard lives at trustsquare.co/launch/ on the same Hetzner box.
- Port 8001 · citylauncher.service · nginx /launch/ and /launch-api/.
- No end user ever sees it or knows it exists.

### D6 · No email sent without David's explicit approval of the prospect list
- Flow: scraper → prospects.db → dashboard inspection → David approves → emailer runs.
- The emailer never fires automatically. David is the final gate before any outbound email.

### D7 · Categories are open-ended strings
- Current: Property · Tutors · Services · Casuals.
- Planned: Travel · Collections.
- Casuals is architecturally distinct from Services — no credentials required, proximity/referral-based.

---

## PART E · Agent and Session Principles

### E1 · Three Claude Code agents — clearly separated lanes
- Architect: owns Codex + rules + system design.
- Frontend: owns marketsquare.html only.
- Admin: owns marketsquare_admin.html only.
- Agents do not edit each other's files.
- CityLauncher has its own Scraper Agent + Dashboard Agent.

### E2 · Uncertainty = implement best guess + flag. Never stop mid-task.
- Make the best decision, implement it, add a one-line uncertainty flag at the end.
- Never pause mid-task to ask David for clarification.

### E3 · Solis is David's ChatGPT persona — not a Claude Code agent
- Solis operates in ChatGPT externally. Not part of the Claude Code agent setup.
- Do not reference Solis as an active agent in any code or briefing.

### E4 · +1 Dashboard is observe-only — no autonomous action
- The dashboard surfaces intelligence. It never intervenes or redirects without David's instruction.
- Page 4 (David +1 Control Surface) is David-only. No agent has access.

---

## PART F · Guard Rails — What This Platform Is NOT

### F1 · Not a game
No game mechanics, scoring loops, or entertainment UX patterns. Real marketplace. Real transactions. Real people.

### F2 · Not open to large refactors
HTML files are single-file architectures that work. No structural rewrites without explicit David instruction.

### F3 · No hardcoded live data anywhere
Founding seller count, city progress, suburb lists — all from BEA live endpoints. STATUS.md and AGENT_BRIEFING.md point to endpoints, never contain static numbers.

### F4 · No simulated or placeholder prospect data in CityLauncher
Every record in prospects.db is a real individual found on a live website with a verified email. No fake data, ever.

### F5 · No SaaS subscriptions
Zero recurring SaaS costs. Sovereignty stack only. Any exception requires David's explicit approval and a council review.

---

## PART G · Advert Agent Project Principles (New — April 2026)

*The Advert Agent is a new, separate project. It is a paid-subscription AI support function embedded inside the MarketSquare app. Core principles are established here as the project foundation. Full AGENT_BRIEFING.md to be written at project kickoff.*

### G1 · The Advert Agent is a seller-facing paid subscription feature
- It operates inside the MarketSquare app (FEA) as a support/assistant function for sellers.
- It is NOT a buyer-facing feature. It is NOT a general AI chatbot.
- Revenue model: paid subscription (tier and pricing TBD at kickoff).

### G2 · The Advert Agent must respect all product principles
- Anonymity (A2) applies absolutely — the agent must never expose seller identity to buyers.
- It cannot override Tuppence flows (A1), introduction models (A3), or Trust Score (A5).
- It operates within the sovereignty stack (B1) — no external AI API costs passed to users without a clear subscription model.

### G3 · The Advert Agent is a separate Cowork project
- Folder: `C:\Users\David\Projects\AdvertAgent\`
- It has its own AGENT_BRIEFING.md, STATUS.md, CHANGELOG.md, and CLAUDE.md.
- It does not share files with MarketSquare or CityLauncher projects.

### G4 · Architecture TBD at kickoff — principles only locked here
- Likely approach: Claude API (Sonnet 4.6) called from BEA on seller request.
- Token costs must be covered by subscription revenue — never erode platform margin.
- Agent behaviour spec, prompt design, and UI integration to be defined in first Cowork session.

---

## Quick Reference: Key Facts Every Agent Must Know

| Fact | Value |
|---|---|
| 1 Tuppence | USD $2 |
| Server IP | 178.104.73.239 |
| Live domain | trustsquare.co |
| API key header | X-Api-Key: ms_mk_2026_pretoria_admin |
| Codex version | Solar_Council_Codex_v4_8_DRAFT.docx (pending David; v4_7 controlling) |
| AGENT_BRIEFING version | v1.3 · 11 April 2026 |
| BEA geo param | `country` (NOT country_iso2) |
| Photo storage | R2 primary (marketsquare-media) + Hetzner /media/ mirror — write-to-both |
| Photo failover | `r2Fallback()` in marketsquare.html — auto-retries via /media/ on onerror |
| Env vars location | /etc/environment |
| n8n restart | `docker restart n8n` |
| GeoNames username | dmcontiki2 |
| Server tier | CPX22 until 24 May → CPX32 from 25 May 2026 · €15.49/month |
| Hetzner Volume | €0.052/GB/month · on standby · activate at >80% disk |
| Public launch threshold | 60 sellers / 20 per category |
| City expansion trigger | 60-seller KPI per city |

---

*End of PRINCIPLE_REQUIREMENTS.md v1.2*
*Next update: when Codex version increments or a new project is added.*
*v1.2 changes: B1 updated CPX22→CPX32 from 25 May 2026; B4 updated to write-to-both dual storage; B6 updated with actual upgrade schedule; Quick Reference table updated with storage and server tier rows.*

---
## [COUNSEL REQUIRED] AI Price Estimate Disclaimer — EULA Addition (Session 77)

The following clause needs to be added to the EULA (after Section 11 — Tuppence):

**Section X — AI Price Estimates**
AI-generated price suggestions (including vision-draft suggested prices, AI market analysis, yield calculator estimates, and "Is this a fair price?" results) are informational estimates only. They are not financial advice, valuations, or offers. They are generated from AI training data reflecting general South African second-hand market conditions and may differ materially from:
(a) international retail or official list prices;
(b) live market prices at time of listing;
(c) import duties, scarcity premiums, or local supply/demand conditions.

TrustSquare makes no warranty as to the accuracy of AI price estimates. Users rely on them at their own discretion. Each AI price call costs Tuppence and is non-refundable regardless of the estimate provided.

[COUNSEL REQUIRED: confirm this covers FAIS AI-advice exclusion and NCA pricing disclosure requirements]
