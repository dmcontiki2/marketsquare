# PRINCIPLE_REQUIREMENTS.md
**Solar Council · MarketSquare Platform**
Version 1.0 · 11 April 2026
Source of truth: Solar_Council_Codex_v4_4.docx · AGENT_BRIEFING.md v1.3 · STATUS.md 10 Apr 2026

This file is read-only. No agent or Cowork task may modify it.
Place a copy in the root of every project folder (MarketApp, AdminApp, CityLauncher, AdvertAgent).
When the Codex is updated, regenerate this file from Claude Chat and replace all copies.

---

## PART A · Product Principles (Locked — council review required to change)

### A1 · Tuppence is the only transaction currency
- 1 Tuppence (1T) = USD $2. Fixed. Not configurable.
- Buyer pays only. Charged only after seller explicitly accepts an introduction.
- Seller earns zero commission. MarketSquare earns from intro fees + subscriptions only.
- Applies to: FEA wallet · BEA /intros/accept · Paystack flow · all pricing displays.

### A2 · Anonymity is Mode B — non-negotiable
- Seller name, email, business name, contact details, and location are NEVER revealed to buyers until both parties accept an introduction.
- Seller CV shows emoji avatar + lock mask only. No photo. No name. No location detail.
- Identity reveal is a bilateral event — both parties must accept before anything is shown.
- Applies to: FEA detail screen · seller CV · BEA listing payloads · admin tool · any future agent app.

### A3 · Introduction models are locked by category
- Property → Commitment model: listing pauses on request, one buyer at a time, 48hr window.
  - Seller ignores: 1T fee to resubmit. Seller declines: 1T fee to resubmit.
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

### A7 · Buyer subscription tiers (preliminary)
- Free: $0 · 3 sessions/day · local city only.
- Starter: $5/mo · 20/day · country scope.
- Premium: $15/mo · 50/day · global.
- Preliminary as of April 2026. Final values confirmed before Paystack live mode activation.
- Applies to: FEA plans screen · BEA session gating (not yet built).

---

## PART B · Sovereignty Stack Principles (Core — no exceptions)

### B1 · No SaaS. No cloud lock-in. Self-hosted always.
- Server: Hetzner CPX22 · 178.104.73.239 · Ubuntu 24.04.
- Stack: FastAPI BEA + SQLite (WAL) + Redis + nginx. No managed databases. No external services.
- Target infrastructure cost: ~$10/month fixed.
- Never add a managed service or SaaS dependency without council review.

### B2 · Server is the single source of truth
- SCP files down before editing. SCP back + `systemctl restart marketsquare` after.
- Use `deploy_marketsquare.bat` for all four deployment steps.
- Never edit a local copy and assume it matches the server.

### B3 · Credentials never in chat windows
- API keys, passwords, and tokens are entered directly into SSH terminal only.
- Admin key stored in systemd drop-in at /etc/systemd/system/marketsquare.service.d/env.conf → /etc/environment.
- Must move to .env before any public exposure.

### B4 · Photo and backup storage: Cloudflare R2 (EU)
- Bucket: marketsquare-media. $0 egress. Env vars: HETZNER_S3_* in /etc/environment.
- DB backups: daily 3 AM cron → R2 backups/ · 14-day retention.
- Script: /usr/local/bin/backup_dbs_to_r2.py.

### B5 · Geographic data is database-driven, never hardcoded
- 4-level hierarchy: geo_countries → geo_regions → geo_cities → geo_suburbs.
- Seeded from GeoNames (username: dmcontiki2). All geo served via BEA /geo/* endpoints.
- `activeCity` is always {id, name}. `activeSuburb` is {id, name} or null.
- BEA geo API param is `country` — NOT `country_iso2`. This is a known drift point.
- South Africa pre-seeded. Other countries added via POST /geo/countries.

### B6 · Infrastructure costs are monitored — $10/month target
- Any agent change affecting infra, pricing, scaling, or storage triggers a "Cost model impact:" entry in CHANGELOG.md.
- Next server tier if needed: Hetzner CPX32 · ~$17/month.
- CPX22 comfortable capacity: ~50,000 sessions/day · ~16,000 free-only users before upgrade.

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
- `Solar_Council_Codex_v4_4.docx` is the canonical rules document.
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
| Codex version | Solar_Council_Codex_v4_4.docx |
| AGENT_BRIEFING version | v1.3 · 11 April 2026 |
| BEA geo param | `country` (NOT country_iso2) |
| Photo storage | Cloudflare R2 (EU) · marketsquare-media |
| Env vars location | /etc/environment |
| n8n restart | `docker restart n8n` |
| GeoNames username | dmcontiki2 |
| Target infra cost | ~$10/month |
| Public launch threshold | 60 sellers / 20 per category |
| City expansion trigger | 60-seller KPI per city |

---

*End of PRINCIPLE_REQUIREMENTS.md v1.0*
*Next update: when Codex version increments or a new project is added.*
*Do not edit this file manually — regenerate from Claude Chat using Codex + session files.*
