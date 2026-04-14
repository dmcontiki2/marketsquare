# MarketSquare Platform · Master Project Plan
**Version 1.0 · 14 April 2026**
*Covers: MarketSquare FEA · Admin Tool · BEA · AdvertAgent · CityLauncher*
*Owner: David · Update this file when a gate is passed or a phase shifts.*

---

## Current Snapshot — What Is Live Today

| Component | State |
|---|---|
| trustsquare.co (buyer app) | ✅ Live — Property · Tutors · Services |
| trustsquare.co/admin.html | ✅ Live — 4-step wizard + dashboard |
| BEA API (port 8000) | ✅ Live — all core endpoints + /advert-agent/* |
| AdvertAgent wizard (4 stages) | ✅ Built — coach blocked pending ANTHROPIC_API_KEY |
| CityLauncher | ✅ Live — ZA pipeline working; Wave 1 prospects ready |
| Paystack | 🔜 Test mode only — live pending CIPC registration |
| n8n notifications | 🔜 Container running — workflow not yet built |
| PDF generation (AA Stage 4) | 🔜 Not built — WeasyPrint not yet installed |

---

## City Readiness (CityLauncher prospects.db — 14 April 2026)

| City | Prospects | Status |
|---|---|---|
| Pretoria ZA | 62 / 60 ✅ | **Ready to email — awaiting David approval** |
| Cape Town ZA | 65 / 60 ✅ | Ready to email |
| Johannesburg ZA | 63 / 60 ✅ | Ready to email |
| London UK | 63 / 60 ✅ | Parked — free scrape sources exhausted for UK |
| New York US | 60 / 60 ✅ | Parked — free scrape sources exhausted for US |
| Durban ZA | 58 / 60 | EA needs +2 |
| Sydney AU | 52 / 60 | Needs +8 across categories |
| Bloemfontein–PE | 8–54 / 60 | Partial — ongoing scrape |

---

## Launch Gates

Gates are hard stops. No phase advances until the gate passes.

### Gate 0 · Platform Stable *(target: 21 April 2026)*
- [ ] Magic onboarding link fixed and tested end-to-end
- [ ] ANTHROPIC_API_KEY set on Hetzner — AA coach live
- [ ] n8n email workflow built — buyer notified on intro accept/decline
- [ ] Maroushka re-listing round 2 complete via admin tool

### Gate 1 · AdvertAgent Revenue-Ready *(target: 5 May 2026)*
- [ ] PDF listing sheet generated on `/advert-agent/publish`
- [ ] AI coach live — free first session confirmed working
- [ ] Tuppence buy-pack flow wired through Paystack test mode
- [ ] Cross-device draft pickup code built (6-char sync)
- [ ] 3 sellers complete full AA flow end-to-end (David + Maroushka + 1 beta)

### Gate 2 · Paystack Live *(target: TBD — CIPC dependent)*
- [ ] CIPC registration completed (David action)
- [ ] Paystack live mode activated and tested
- [ ] Intro fee (1T = R36) charged live on seller acceptance
- [ ] AA buy-pack (1T for 8 sessions) charged live
- [ ] Buyer subscription tiers enforced (not just display)
- [ ] Test: full buyer journey — browse → intro → fee charged → identity reveal

### Gate 3 · Pretoria Public Launch *(target: within 1 week of Gate 2)*
- [ ] CityLauncher Wave 1 email batch — David approves prospect list
- [ ] 20+ founding sellers onboarded via magic links per category
- [ ] 60 active listings confirmed live (GET /listings?city=Pretoria count)
- [ ] Trust Scores seeded — at least 5 sellers with Established badge (40+)
- [ ] Basic PR — WhatsApp groups · LinkedIn · Pretoria expat communities

### Gate 4 · ZA Wave 2 *(target: 4 weeks after Gate 3)*
- [ ] Cape Town launched (65 prospects ready)
- [ ] Johannesburg launched (63 prospects ready)
- [ ] Durban topped up to 60 and launched
- [ ] Bloemfontein / East London / PE pipeline completed

### Gate 5 · Phase 2 Categories *(target: 3 months after Gate 3)*
- [ ] Adventures FEA screens + BEA category support built
- [ ] Collectors FEA screens + BEA category support built
- [ ] CityLauncher scraper targets for Adventures / Collectors defined
- [ ] 20 founding sellers per category in at least one city

### Gate 6 · International Wave *(target: 6 months after Gate 3)*
- [ ] London pipeline unblocked (paid source or partnership, or organic sign-ups)
- [ ] New York pipeline unblocked
- [ ] Paystack international / Stripe integration reviewed
- [ ] Currency localisation (GBP, USD) confirmed in FEA wallet + pricing

---

## Phase Plan

### Phase 0 · Fix & Stabilise *(now → Gate 0)*

| Task | Owner | Notes |
|---|---|---|
| Fix magic onboarding link | Claude Code | Reported broken for Maroushka + Dave |
| Set ANTHROPIC_API_KEY on Hetzner | David | SSH: echo to /etc/environment + restart |
| Build n8n intro notification workflow | Claude Code | Buyer email on accept + decline |
| Maroushka re-listing round 2 | Maroushka | Use admin tool with Technical/Casuals split |

### Phase 1 · AdvertAgent Complete *(Gate 0 → Gate 1)*

| Task | Owner | Notes |
|---|---|---|
| WeasyPrint install on Hetzner | Claude Code | pip install + libpango check; fallback reportlab |
| PDF listing sheet — /advert-agent/publish | Claude Code | Branded A4 with listing details + QR code |
| Paystack buy-pack flow | Claude Code | aaBuyPack() → POST /payment/initialize → verify → credit sessions |
| Cross-device pickup code | Claude Code | 6-char code: draft → BEA temp store → phone loads by code |
| AA end-to-end test — 3 sellers | David + Maroushka + 1 | Confirm coach fires, PDF downloads, pack purchase works |

### Phase 2 · Revenue Live *(Gate 1 → Gate 2)*

| Task | Owner | Notes |
|---|---|---|
| CIPC registration | David | Prerequisite for Paystack live mode |
| Paystack live mode activation | David + Claude Code | Config switch + test transaction |
| Buyer subscription enforcement | Claude Code | Add BEA session gating (A7 tiers) |
| Intro fee live charging | Claude Code | PUT /intros/{id}/accept → charges 1T via Paystack |
| Smoke test: full buyer journey | David | Browse → intro → pay → identity reveal |

### Phase 3 · Pretoria Launch *(Gate 2 → Gate 3)*

| Task | Owner | Notes |
|---|---|---|
| Approve Wave 1 prospect list | David | CityLauncher dashboard → review → approve |
| Send founding seller emails | Claude Code | n8n emailer fires after David approval |
| Onboarding support | David + Maroushka | Hand-hold first 10 sellers through admin tool |
| Launch announcement | David | WhatsApp, LinkedIn, community groups |
| Monitor + hotfix | Claude Code | Watch /listings count, intro flow, trust scores |

### Phase 4 · ZA Expansion *(Gate 3 → Gate 4)*

| Task | Owner | Notes |
|---|---|---|
| Fix scraped_urls city-scoping bug | Claude Code | Blocks re-running scrapers for smaller cities |
| Top up Durban, Bloemfontein, PE, Polokwane | Claude Code | CityLauncher scraper runs |
| Cape Town + Johannesburg email approval | David | Both at 60+ — ready to send |
| City-by-city launch cadence | David | One city per week recommended |

### Phase 5 · Phase 2 Categories *(parallel with Phase 4)*

| Task | Owner | Notes |
|---|---|---|
| Adventures FEA + BEA | Claude Code | Screens, intro model, BEA endpoints |
| Collectors FEA + BEA | Claude Code | Screens, item type logic, grading fields |
| CityLauncher scraper targets | Claude Code | Adventures: tour operators / guides; Collectors: dealers |
| Seed 20 founding sellers each | CityLauncher | Per canonical register D7 |

### Phase 6 · International *(Gate 4 onwards)*

| Task | Owner | Notes |
|---|---|---|
| London unblock strategy | David | Organic sign-up push vs paid scrape source |
| New York unblock strategy | David | Same — all free US sources exhausted |
| Currency localisation | Claude Code | GBP / USD in wallet + pricing |
| Paystack international or Stripe | David | Review fees + supported countries |

---

## Tools

### In Use (no action needed)

| Tool | Purpose | Cost |
|---|---|---|
| Hetzner CPX22 | App server | ~R70/month |
| Cloudflare R2 (EU) | Photo + backup storage | $0 (10 GB free) |
| SQLite (WAL) | Database | $0 |
| Redis | Session cache + rate limiting | $0 |
| nginx + FastAPI | Serving stack | $0 |
| GeoNames API | Geo seeding | $0 (dmcontiki2) |
| n8n (Docker) | Email automation | $0 self-hosted |
| Resend | Transactional email | $0 under 3,000/month |
| claude-haiku-4-5 | AA coach AI | Covered by AA subscription revenue |
| Playwright (headless) | CityLauncher scraping | $0 |

### Needed — Phase 0

| Tool | Purpose | Action |
|---|---|---|
| ANTHROPIC_API_KEY | AA coach API calls | David sets on Hetzner via SSH |

### Needed — Phase 1

| Tool | Purpose | Action | Cost |
|---|---|---|---|
| WeasyPrint + libpango | PDF generation on server | Claude Code installs via venv pip | $0 |
| reportlab | PDF fallback if libpango missing | Installed alongside WeasyPrint | $0 |

### Needed — Phase 2 (Gate 2)

| Tool | Purpose | Action | Cost |
|---|---|---|---|
| CIPC registration | Legal entity for Paystack live | David action — 4–6 weeks | ~R175 |
| Paystack live mode | Real money transactions | Activate after CIPC | R0 setup; 2.9% + R1.80/txn |

### Needed — Phase 6 (International)

| Tool | Purpose | Action | Cost |
|---|---|---|---|
| Stripe (TBD) | International payments | Review after Paystack live | 2.9% + $0.30/txn |
| Hetzner CPX32 upgrade | Scale at ~50k sessions/day | Upgrade when needed | ~R230/month |

### Never Permitted Without Explicit David Approval + Cost Ceiling (Rule B7)

- Google Maps API · Google Places API · Any cloud ML/AI API with per-request billing
- Any API requiring a credit card to activate a trial

---

## Testers

### Internal (always available)

| Tester | Role | What they test |
|---|---|---|
| David | Owner / product | Full buyer + seller + admin + AA flow |
| Claude Code | Build agent | Unit + regression on each deploy |

### Founding Sellers (live testing)

| Tester | Category | Status |
|---|---|---|
| Maroushka | Property | Active — completed Session 7 test, round 2 pending |
| Dave | Services (TBC) | Magic link reported broken — fix in Phase 0 |
| Wave 1 (20 sellers) | Property · Tutors · Services | Post-Gate 3 — recruited via CityLauncher emails |

### Beta Buyers (recruit before Gate 3)

| Type | How to recruit | What they test |
|---|---|---|
| 3–5 Pretoria buyers | David's network, WhatsApp groups | Browse → filter → intro request → payment (test mode) |
| 1 mobile-only buyer | Maroushka's network | Full mobile experience — filter, map, intro |
| 1 buyer from outside Pretoria | David | Subscription tier gate (starter needed for national view) |

### QA Protocol per Gate

1. **Gate 0** — David + Maroushka run through the magic link, seller profile, and intro flow
2. **Gate 1** — David + Maroushka + 1 beta seller complete AA stages 1–4, coach fires, PDF downloads
3. **Gate 2** — David processes a real R36 intro fee end-to-end before announcing live
4. **Gate 3** — 5 beta buyers attempt intros before the public announcement goes out

---

## Cost Model Summary

| Item | Monthly | Notes |
|---|---|---|
| Hetzner CPX22 | ~R70 | Scale to CPX32 (~R230) at ~50k sessions/day |
| Cloudflare R2 | R0 | 10 GB free; $0.015/GB over |
| n8n | R0 | Self-hosted Docker |
| Resend | R0 | Under 3,000 emails/month |
| claude-haiku-4-5 | Covered by 1T pack purchases | ~$0.001/1k tokens input |
| **Total fixed** | **~R70/month** | Well within B6 target |

Revenue kicks in at Gate 2: intro fees (1T = R36 per introduction accepted) + AA packs (1T = 8 coaching sessions).

---

## Open Risks

| Risk | Severity | Mitigation |
|---|---|---|
| CIPC registration delay | High | Gate 2 is blocked until done — David must prioritise |
| Maroushka / Dave not onboarding | Medium | Simplify with hand-holding session; fix magic link first |
| London / US scrape sources exhausted | Medium | Parked until revenue; consider organic sign-up funnel instead |
| Server storage / memory at scale | Low | CPX22 comfortable to ~50k sessions/day; upgrade path clear |
| libpango missing on Hetzner (PDF) | Low | reportlab fallback already planned |
| Haiku token cost spike (AA) | Low | Gated by session count; pack purchase covers cost |

---

*End of PLAN.md v1.0 · Update version and date when a gate passes.*
*Append major pivots to CHANGELOG.md, not here.*
