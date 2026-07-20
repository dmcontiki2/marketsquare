# PRINCIPLE_REQUIREMENTS.md
**Solar Council · TrustSquare Platform**
Version 1.5 — CURRENT (18 July 2026). Single canonical copy; identical mirrors live in MarketSquare/docs, AdvertAgent/, CityLauncher/, Codices/. Supersedes v1.4 (21 Jun 2026) and all earlier per-folder copies.
Source of truth: Solar_Council_Codex_v4_8.docx (CANON, adopted 21 Jun 2026) · AGENT_BRIEFING.md v1.9 (18 Jun 2026) · PRICING_CANON.md (pricing authority). Third Pillar principle (H1–H6, adopted 18 Jul 2026) · CC-001 HOLD accepted; CC-002 pricing/AI PARKED (A7 follows PRICING_CANON); CC-003 launch threshold applied; EULA v1.7 baselined (A6).

This file is read-only. No agent or Cowork task may modify it.
Place a copy in the root of every project folder (MarketApp, AdminApp, CityLauncher, AdvertAgent).
When the Codex is updated, regenerate this file from Claude Chat and replace all copies.

---

## PART A · Product Principles (Locked — council review required to change)

### A1 · Tuppence is the only transaction currency
- 1 Tuppence (1T) = USD $2. Fixed. Not configurable.
- The requester pays (the service consumer — the buyer, for introductions). Tuppence follows the HOLD (CC-001): committed on request → burned on delivery (seller accepts / AI result delivered) → released in full on decline, 48-h expiry, or AI failure. A release frees an un-spent hold — it is never a refund.
- Seller earns zero commission. TrustSquare earns from intro fees + subscriptions only.
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
- CC-003: 60 staged prospects/city = founding-wave trigger (NOT a 60-seller public gate). Cities launch day-one (World Heritage layer + demos + agency onboarding).
- Density: 80 total / 20 per category (full promotion).
- Never launch a city below threshold. Never hardcode these numbers — they are governance rules.
- Applies to: CityLauncher KPI · admin tool count · city wave cascade · +1 Dashboard KPI page.

### A7 · Subscription tiers (Simpler Model — supersedes the Session 91 / CC-002 5-tier draft)

> **Pricing authority:** the live code constants + `MarketSquare/PRICING_CANON.md` are the single source of truth; this section is a derived summary. If it ever disagrees, fix it here — not the canon. Verify: `python scripts/check_pricing_canon.py`.
- SELLER tiers (listing slots): Free $0 · 2 · 0T | Starter $5 · 10 · 2T | Pro $20 · 30 · 10T | Agency free+verified · 10 base. Source: `bea_main.py _SELLER_SUB_TIERS`.
- BUYER tiers (wishlist/search reach): Free $0 (local) | Global $5/mo (national+global). Source: `_buyer_tier` → free|global; `WISHLIST_GLOBAL_USD = 5`.
- Listing slots are a CAP (meter display, not a wallet): Free 2 / Starter 10 / Pro 30.
- Monthly Tuppence to paid seller tiers (price ÷ 2 at 1T = $2): Starter 2T · Pro 10T (Founders ×1.2 rounded up: Pro 10→12T). The old multi-tier subscription family is fully retired (no grandfathering).
- "AI uses" / AI-session allowances are RETIRED: in-app AI guidance is free; advanced AI functions are Tuppence-priced per use through the HOLD ledger (/tuppence/ai-commit + /tuppence/ai-settle).
- AI-class access by tier (S3 — Free-Tier AI Cost Risk Report, 16 Jun 2026; PRICING_CANON.md §5): the PAID-FEED AI class (Sonnet + a contracted data feed) is reserved for $20 Pro; Free / Starter / Agency are blocked at /tuppence/ai-commit (403, no hold placed). Cheap Haiku / free-data AI stays open to everyone. Closes the ~$39,166/yr Year-1 free-tier cost leak. Source: `ai_service_tiers.PAID_FEED_FUNCTIONS` / `PAID_FEED_ALLOWED_TIERS`.
- Monthly grant is NON-ROLLING (S3): granted Tuppence (monthly_allocation + founders_bonus) does not accumulate — unspent grant is swept (grant_expiry row) before each new allocation; purchased/earned Tuppence is never swept. See A8 (this is a grant reset, not a penalty). Source: `launch_redemption.grant_monthly_tuppence`.
- Daily Introduction-session limits are retired [AD-07 — David confirm].
- Applies to: FEA plans screen + wallet · BEA verify_seller_subscription + launch_redemption.py · EULA tier disclosure · support FAQ.

---

## PART B · Sovereignty Stack Principles (Core — no exceptions)

### A8 · Tuppence deductions are purchase-only — never punitive (CORE PRINCIPLE)
- Tuppence is NEVER deducted from any wallet as a punishment, penalty, or deterrent.
- The only valid reasons to deduct Tuppence are: (i) buyer pays an Introduction fee; (ii) seller or buyer purchases an AI service; (iii) seller purchases a Boost.
- Negative behaviour (ignoring intros, declining without reason, no-shows, bad referrals) is penalised exclusively via Trust Score reduction and, in severe or repeat cases, Banishment (account suspension or permanent ban).
- This principle is non-negotiable. No agent, architect, or future feature may introduce a Tuppence-deduction penalty under any framing (fee, bond, deposit, resubmission cost, etc.).
- CLARIFICATION (17 Jun 2026): the non-rolling monthly grant reset (A7 / PRICING_CANON §5) is NOT a punitive deduction. It zeroes only UNSPENT GRANTED Tuppence at the moment a fresh grant is credited — a grant that resets rather than rolls over. No purchased or earned Tuppence is ever swept, and nothing is deducted in response to behaviour. A8-compliant by construction.
- Rationale: punitive deductions create fear, erode trust, and undermine the platform's commitment-signal model. Trust Score is the correct instrument — it is visible, recoverable, and proportionate.
- Applies to: BEA all endpoints · FEA all flows · admin tool · future agent features · EULA · any legal documentation.


### B1 · No SaaS. No cloud lock-in. Self-hosted always.
- Server: Hetzner CPX22 → **CPX32 from 25 May 2026** · 178.104.73.239 · Ubuntu 24.04.
  - CPX32: 4 vCPU · 8 GB RAM · 160 GB NVMe · €15.49/month (upgraded from CPX22 €9.49/month).
- Stack: FastAPI BEA + SQLite (WAL) + Redis + nginx. No managed databases. No external services.
- Target infrastructure cost: **€15.49/month from 25 May 2026** (previously ~€9.49/month).
- Hetzner Volume (100 GB block storage, ACTIVE, €0.052/GB/mo ~€5.20) — disk/DB headroom · + Hetzner Object Storage bucket for backups (~€5.99/mo). Both in the cost model (≈€11/mo combined).
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
- DB backups: daily 3 AM cron → Hetzner Object Storage bucket · 14-day retention (~€5.99/mo).
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
- **Active (in cost model):** Hetzner Volume (100 GB block storage) · €0.052/GB/mo (~€5.20) + Hetzner Object Storage bucket for backups (~€5.99) ≈ €11/mo. Volume survives server rebuild; expand when disk >80% full.
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
- `Solar_Council_Codex_v4_8.docx` is the canonical rules document (adopted 21 Jun 2026).
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

## PART H · The Third Pillar — AI Sovereignty and Access Equity (Core — adopted 18 July 2026)

**Context:** MarketSquare is built and deployed from South Africa, a region structurally excluded from the select group of users who have early or reliable access to frontier AI. US export controls, geopolitical restrictions, and commercial gatekeeping create a fundamental inequity: builders and founders in Africa, Asia, Latin America, and other underserved regions cannot reliably build on the same AI infrastructure as Silicon Valley. Restrictions like the June 2026 Claude Fable 5 / Mythos 5 suspension (temporary) and the ongoing Mythos 5 US-only limitation illustrate the risk.

The Third Pillar is MarketSquare's answer: a resilient, self-hosted AI inference layer that cannot be banned, restricted, or gatekept based on geography, geopolitics, or regulatory fiat. It is built on principles of access equity and sovereignty.

### H1 · The Third Pillar is open-weight model fallback, not API dependency
- Primary inference: Claude Haiku / Sonnet (Anthropic API) — cost-optimal, fast, best-in-class.
- Third Pillar fallback: open-weight frontier model (currently Kimi K3, 2.8T parameters, released 27 Jul 2026) — self-hosted on EU/US-neutral infrastructure.
- Never depend solely on a single closed-source API provider (Anthropic, OpenAI, or otherwise). If export controls block Claude or Mythos, or OpenAI faces regional restrictions, Kimi K3 remains accessible.
- The model weights are downloaded and owned by MarketSquare. No API routing through China or any single provider.
- Applies to: MarketSquare's AI inference strategy · AdvertAgent AI backend · any future agent feature.

### H2 · Self-hosted infrastructure must be EU or neutral ground
- Host Kimi K3 (and any future open-weight fallback) on European infrastructure: Latitude.sh, Nebius, OVHcloud, or equivalent.
- These providers are subject to EU regulatory framework and are less likely to discriminate by geography.
- Never host on US-controlled infrastructure (which is vulnerable to US export controls).
- Never host on Chinese infrastructure (to avoid dependency on or routing through Chinese state entities).
- Applies to: GPU infrastructure procurement · vendor selection · cost modeling.

### H3 · Availability is the measure — cost efficiency is secondary
- The Third Pillar exists to ensure that MarketSquare can always serve its users, especially in regions outside the Silicon Valley/US commercial ecosystem.
- Cost must be managed but never at the expense of availability.
- Target: access a frontier-class open-weight model within 5 seconds of inference request, with 99.5% uptime.
- If open-weight hosting becomes expensive, that is a cost of sovereignty — it is justified.
- Applies to: SLA targets · infrastructure budgeting · feature availability decisions.

### H4 · This principle serves global equity, not just MarketSquare's margin
- The Third Pillar is a hedge against AI being weaponized as a tool of selective access, where "selected" means the wealthy, connected, geographically privileged few.
- By proving that a frontier model can be self-hosted and reliably accessed by founders in South Africa, we prove that access is possible for anyone with the infrastructure.
- This is not altruism; it is a direct response to structural inequality.
- Applies to: product strategy · infrastructure investment · public narrative about MarketSquare's role.

### H5 · Open-weight model adoption follows this sequence
1. **Wait for provider adoption** (Jul–Aug 2026): Major cloud providers (Latitude.sh, Nebius, OVHcloud) will announce hosted Kimi K3 inference.
2. **Vet providers** (Aug–Sep 2026): Select 1–2 providers with strong uptime SLAs, transparent pricing, and neutral jurisdiction.
3. **Integrate fallback** (Sep–Oct 2026): Wire Kimi K3 as inference fallback in AdvertAgent + any AI-dependent feature. Primary stays on Claude Sonnet.
4. **Self-host if needed** (Q4 2026+): If provider options are insufficient or unstable, evaluate self-hosting Kimi K3 on dedicated GPU infrastructure.
- Applies to: MarketSquare AI roadmap · AdvertAgent inference strategy · quarterly architecture reviews.

### H6 · Export control and geopolitical monitoring is ongoing
- Kimi K3 is Chinese-developed (Moonshot AI), but the open-weight release is not subject to US export controls.
- However, export control regimes change quickly (demonstrated June 2026).
- Every monthly AI-Watch (automated monitoring, weekly digest) includes a section on frontier model availability and geopolitical risk.
- If China restricts open-weight model exports or US designates Kimi K3 as a dual-use technology, the Third Pillar pivots to the next available model (likely GLM or Qwen from Alibaba, or DeepSeek from China, or any model that can be legally hosted).
- Applies to: MarketSquare AI-Watch task · quarterly security/sovereignty reviews.

---

## PART G · Advert Agent Project Principles (New — April 2026)

*The Advert Agent is a new, separate project. It is a paid-subscription AI support function embedded inside the TrustSquare app. Core principles are established here as the project foundation. Full AGENT_BRIEFING.md to be written at project kickoff.*

### G1 · The Advert Agent is a seller-facing paid subscription feature
- It operates inside the TrustSquare app (FEA) as a support/assistant function for sellers.
- It is NOT a buyer-facing feature. It is NOT a general AI chatbot.
- Revenue model: paid subscription (tier and pricing TBD at kickoff).

### G2 · The Advert Agent must respect all product principles
- Anonymity (A2) applies absolutely — the agent must never expose seller identity to buyers.
- It cannot override Tuppence flows (A1), introduction models (A3), or Trust Score (A5).
- It operates within the sovereignty stack (B1) — no external AI API costs passed to users without a clear subscription model.

### G3 · The Advert Agent is a separate Cowork project
- Folder: `C:\Users\David\Projects\AdvertAgent\`
- It has its own AGENT_BRIEFING.md, STATUS.md, CHANGELOG.md, and CLAUDE.md.
- It does not share files with TrustSquare or CityLauncher projects.

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
| Codex version | Solar_Council_Codex_v4_8.docx (CANON, 21 Jun 2026) |
| AGENT_BRIEFING version | v1.9 · 18 June 2026 |
| BEA geo param | `country` (NOT country_iso2) |
| Photo storage | R2 primary (marketsquare-media) + Hetzner /media/ mirror — write-to-both |
| Photo failover | `r2Fallback()` in marketsquare.html — auto-retries via /media/ on onerror |
| Env vars location | /etc/environment |
| n8n restart | `docker restart n8n` |
| GeoNames username | dmcontiki2 |
| Server tier | CPX22 until 24 May → CPX32 from 25 May 2026 · €15.49/month |
| Hetzner storage | 100 GB Volume ~€5.20 + Object Storage bucket (backups) ~€5.99 ≈ €11/mo |
| Founding-wave trigger | 60 staged prospects/city (CC-003) — not a public seller gate |
| City expansion trigger | 60-prospect wave KPI per city (CC-003) |

---

*End of PRINCIPLE_REQUIREMENTS.md v1.5 — CURRENT (18 July 2026)*
*Next update: when Codex version increments or a new project is added.*
*v1.4 changes: header→CURRENT/v1.4; source→Codex v4.8 CANON + briefing v1.9; launch threshold (A6 + Quick Ref)→CC-003 wave-trigger; C5→v4.8; EULA v1.7 baselined (A6). CC-002 pricing PARKED — A7 follows PRICING_CANON.*
*v1.5 changes: added PART H — The Third Pillar (AI Sovereignty and Access Equity, H1–H6, adopted 18 Jul 2026), merged forward from the Codices mirror where it had been added without propagation (canon QA 2026-07-20 catch); header→v1.5/18 Jul 2026.*

---
## [A6 · 21 Jun 2026] EULA v1.7 baselined as the accepted current version; counsel finalization (the clause below + FAIS/NCA review) is the remaining external action.

## [COUNSEL REQUIRED] AI Price Estimate Disclaimer — EULA Addition (Session 77)

The following clause needs to be added to the EULA (after Section 11 — Tuppence):

**Section X — AI Price Estimates**
AI-generated price suggestions (including vision-draft suggested prices, AI market analysis, yield calculator estimates, and "Is this a fair price?" results) are informational estimates only. They are not financial advice, valuations, or offers. They are generated from AI training data reflecting general South African second-hand market conditions and may differ materially from:
(a) international retail or official list prices;
(b) live market prices at time of listing;
(c) import duties, scarcity premiums, or local supply/demand conditions.

TrustSquare makes no warranty as to the accuracy of AI price estimates. Users rely on them at their own discretion. Each AI price call costs Tuppence and is non-refundable regardless of the estimate provided.

[COUNSEL REQUIRED: confirm this covers FAIS AI-advice exclusion and NCA pricing disclosure requirements]
