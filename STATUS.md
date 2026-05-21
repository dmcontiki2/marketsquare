# TrustSquare - STATUS.md

## Live State
BEA v1.3.0 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 335 KB HTML shell
- Static assets: /static/ms.css?v=70 (103 KB) + /static/ms.js?v=70 (494 KB), cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 30-check post-deploy safety net
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- **NEW Session 70:** POST /listings/vision-draft live — photo-first AI onboarding endpoint

## Last Completed (Session 70)
- Designed Photo-First AI Onboarding complete flow (6 screens, data contract, error states) — documented in bea_main.py lines 7654–7774
- Implemented POST /listings/vision-draft endpoint: accepts 1–12 photos, calls Claude Vision (claude-sonnet-4-6), returns draft listing JSON
- Built category-aware vision prompt covering all 4 categories (Property, Services, Adventures, Cars) with SA price anchors
- Tested live endpoint 4/4 categories passing: Property 95% confidence · Services/Tutor 98% · Cars 85% · Adventures 97%
- All 30 smoke test checks passing; BEA version bumped to 1.3.0

## Last Completed (Session 69)
- Inserted company registration number 2026/340128/07 into EULA (all 6 placeholders replaced)
- [Company Name] → TrustSquare (Pty) Ltd in EULA Definitions, Section 1.3, and Operator definition
- [REG NO] → 2026/340128/07 in Platform definition and Section 1.3
- [COUNSEL REQUIRED: insert … address] placeholders replaced with registered address (3 instances)
- Generated 5 corporate stationery templates (Letterhead, Invoice, Quotation, Confidential Cover, Meeting Agenda/Minutes) as Word .docx files using CIPC + FNB details
- Added Edge browser sidebar suppression meta tags (edge-sidebar, edge-copilot, ms-edge-skia-disable)
- Designed Photo-First AI Onboarding concept — documented in Session 70 brief below
- All 30 smoke test checks passing; no JS/CSS changes, version remains ?v=70

## File anatomy (335 KB HTML shell after Session 70)
- HTML markup + ms-data + gate script: 335 KB  (sent every page load)
- /static/ms.css?v=70:               103 KB  (cached 1 year after first load)
- /static/ms.js?v=70:                494 KB  (cached 1 year after first load)
- On first visit: ~922 KB total transfer
- On repeat visits: 335 KB only (assets served from cache)

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=70

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 71)
Goal: Photo-First AI Onboarding — FEA Onboarding Screen (Session 2 of 3-session arc)

### Session 71 Build Plan
5. Build new `sob-photo-first` screen in `marketsquare.html`:
   - Photo upload UI: large camera icon, multi-file input (1–12 photos, accept="image/*")
   - "Skip photos — describe it instead" link (small, below camera button)
   - Animated "Building your listing…" overlay with 3 rotating messages
   - Draft card reveal: hero image carousel, editable title, editable description, price, tags
   - "Does this look right?" bottom bar with [Improve description] and [Looks good — publish it →]
6. Wire magic link ?cat= param as vision hint (category_hint in FormData)
7. Inline AI description improver: POST /advert-agent/market-note → show old vs new

### Key design references (from Session 70 flow doc)
- Endpoint: POST /listings/vision-draft
- Response shape: {draft: {category, title, description_draft, suggested_price, currency_prefix, tags, ...}, warnings, model_used}
- Loading animation: 3 messages cycling — "Reading your photos…" → "Identifying category…" → "Writing your listing…"
- Timeout: 45s server side (show progress bar with 40s client timeout — show fallback toast if exceeded)
- Full flow design: bea_main.py lines 7654–7774

## Blockers
- CIPC registration confirmed (2026/340128/07) - Paystack live mode still pending activation
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
