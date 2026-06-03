# MarketSquare · Feature & Fix Backlog
*Updated Session 62 · 18 May 2026*
*Prioritised by: launch-blocking first, UX polish second, future features third.*

---

## 🔴 Launch Blockers — must fix before public launch

| # | Item | Area |
|---|---|---|
| L1 | **Counsel EULA review** — South African attorney must review and fill all `[COUNSEL REQUIRED]` sections before app goes public | Legal |
| L2 | **Company registration number** — insert Trustsquare (Pty) Ltd reg number into EULA Section 2 and app footer | Legal |
| L3 | **NCC direct marketer registration — counsel to confirm first** — counsel must advise whether TrustSquare (Pty) Ltd is required to register as a direct marketer with the NCC under the CPA. Transactional intro emails to opted-in users are likely exempt; CityLauncher cold outreach may not be. Section 6.6 EULA updated to remove false "is registered" claim and replaced with a compliant placeholder pending counsel confirmation. If registration is required, obtain reg number and insert into Section 6.6. | Legal |
| L3a | **support@trustsquare.co mailbox** — OPEN (verified S100): no real mailbox exists. Triage replies currently send from `dmcontiki2@gmail.com` via Gmail SMTP; MX is Cloudflare forward-only; SPF/DKIM half-set for Brevo. Fix plan in `SUPPORT_MAILBOX_SETUP.md`: (A) add Cloudflare routing address, (B) Brevo SMTP send from support@, (C) one BEA env/code edit (ready), (D) verify SPF/DKIM pass then close. Used in EULA §5.4/6.5/6.6/7.x/13/14/15 — EULA undeliverable until done. | Ops |
| L4 | **Privacy Policy page** — draft and publish trustsquare.co/privacy (required by EULA Section 9.1 and POPIA) | Legal |
| L5 | **FSCA guidance on Tuppence** — confirm Tuppence classification as non-virtual-asset with FSCA or comply if reclassified (EULA Section 12) | Legal |
| L6 | **POPIA consent timing** — counsel must confirm whether magic link email collection constitutes prior consent or whether EULA gate must move earlier in the flow | Legal |
| L7 | **Paystack live mode — go-live env flip (no code change)** — when Paystack approves live mode, set on the server and restart the BEA: `PAYSTACK_SECRET_KEY=sk_live_…` + `PAYSTACK_WEBHOOK_SECRET=…` (live webhook signing secret). The S5 fail-closed gate `_payment_grants_allowed()` (live since 2 Jun) auto-resumes grants the instant a `sk_live` key is present — no code deploy. Verify: one small real transaction credits Tuppence via the webhook + idempotent `/payment/verify`. State now: `sk_test` + `ALLOW_TEST_PAYMENTS` unset → grants correctly fail-closed. (CIPC reg already done; the blocker is Paystack's live-mode approval — the "last letter".) | Server / Ops |
| L8 | **IP Brief v3 + Patent Strategy v2 — Session 80 (Opus)** — Update `TrustSquare_IP_Brief_v2_May2026.docx` and `TrustSquare_IP_Patent_Strategy_v1.docx` to reflect: (1) A8 no-punitive-Tuppence principle; (2) corrected commitment-signal argument (buyer's irreversible 1T spend, not seller penalty); (3) new features (AI5 Batch Cards, AI4 Yield Calc, World Heritage linking); (4) updated pack tiers. Produce lawyer-ready handoff summary. Full briefing in `SESSION_80_OPUS_IP_BRIEF.md`. **Must be done before submitting to patent attorney.** | Legal / IP |


---

## 🟠 High Priority — needed for a solid user experience at launch

| # | Item | Area |
|---|---|---|
| H1 | **Local Market listings — parity with standard listings** | Buyer app |
| | · Cards should look identical to Property/Tutors/Services cards (photo, title, price, suburb, Trust badge) | |
| | · Detail screen should match the standard detail screen layout (photo carousel, full description, seller stats) | |
| | · Browse page LM banner should use same grid as other categories, not a separate layout | |
| | · LM intro flow should feel the same as standard intro (not a separate code path visually) | |
| H2 | ✅ **DONE (verified 2 Jun)** · n8n email notifications — buyer emailed when seller accepts or declines intro | BEA + n8n |
| H3 | ✅ **DONE (verified 2 Jun)** · Seller-facing intro notifications — seller emailed when new intro request arrives | BEA + n8n |
| H4 | **Maroushka + Dave phone test** — lightbox, back buttons, My Requests tab live test | Testing |
| H5 | **Showcase photos** — add `thumb_url` to demo listings 40–51 (royalty-free images) | Buyer app |
| H6 | **Tutors & Services edit parity** — confirm all structured fields save and display correctly after edit | Buyer + Admin |
| H7a | **Yield calculator — full breakdown display** — the BEA already returns `monthly_rent_estimate` and `market_context` but the FEA discards them. Render the full workings: implied purchase price, annual rent, the gross yield formula, net deduction estimate, benchmark comparison, and a 2–3 sentence AI context. Add a mandatory disclaimer line: "Indicative only — not financial advice. Purchase price is estimated from area benchmarks. Verify with a registered property practitioner." Cost stays 1T, value delivered becomes fully transparent. | BEA + Buyer app |
| H7b | **Yield calculator — country-aware benchmarks** — system prompt currently hardcodes SA yield ranges. Once multi-country listings exist, detect country from `geo_city_id` and apply country-specific gross yield benchmarks and net cost deduction norms (SA: subtract 2–3.5%; UK: subtract 2–5%; US: subtract 3–6%). Also localise the financial advice disclaimer to the listing's jurisdiction. | BEA |
| H7 | **Rental yield badge on Property listings** — seller enters monthly rental income (optional field); app computes gross yield = annual rent / asking price and displays as a badge on card and detail view. Zero seller effort, instant signal for investment buyers. Display as "X.X% Yield (gross)" with tooltip explaining the calculation. | Buyer app + BEA |

---

## 🟡 Medium Priority — polish and completeness

| # | Item | Area |
|---|---|---|
| M0 | **`GET /listings` pagination** — replace `LIMIT 200` hardpoint with proper offset pagination (`?page=1&page_size=50`) + `total` count in response. FEA: infinite scroll loads next page when buyer reaches bottom of grid. Required before multi-city rollout — a city with 500+ listings will otherwise be truncated. | BEA + Buyer app |
| M1 | **Paystack test card end-to-end test** — run full buy flow with test card, confirm Tuppence credited via webhook | Buyer app |
| M2 | **Subscription flow test** — test Global wishlist tier subscribe/verify/activate | Buyer app |
| M3 | **SA corporate tax rows B30:D30 in cost model** — fill once P&L is finalised | Cost model |
| M4 | **Local Market — wishlist feed integration** — LM listings appearing in "For You" home screen feed with LM badge | Buyer app |
| M5 | **Founding seller count** — currently 23/60, need 37 more before public launch | Content |
| M6 | **Maroushka re-listings** — real founding seller content via admin tool | Admin |
| M7 | **City selector bug audit** — verify geo selectors work on mobile Safari and Chrome Android | QA |
| M8 | **Content / photo pass** — (1) Replace Unsplash category shopfront photos with royalty-free alternatives (Wikimedia Commons or Pexels API) — current hotlinking is outside Unsplash commercial terms and images are being quality-degraded. (2) Add `max-height` cap on `wd-hero` for desktop so Heritage hero images don't over-stretch on wide screens. (3) Review all `w=800&q=80` Unsplash params across the codebase. Do as a dedicated session before public launch. | Buyer app |

---

## 🔵 Future Features — post-launch Wave 1

| # | Item | Area |
|---|---|---|
| F5 | **Subscription tier redesign — upgrade model for multi-unit sellers** — current model has fixed slot limits per tier plus one-off bundle purchases. Problem: a seller with 39 permanent listings (e.g. Maroushka/Kronborg) should not be re-buying monthly top-ups. Proposal: replace bundle purchases with permanent tier upgrades billed as subscription increases (Hetzner-style). Two design options: (A) Fixed tier steps — add "Professional" (50 slots) and "Business/Estate Agent" (unlimited) tiers at fixed monthly prices; or (B) Per-slot pricing above base tier — Premium includes N slots, each additional slot costs R X/month added to subscription. Key principle: Tuppence per-intro cost stays separate from slot cost — never mix them. Decision needed before implementation: per-slot vs tier steps, and whether downgrades are allowed. Discuss at start of Session 90. | Payments + BEA + Admin |
| F1 | **Adventures category** — Experiences + Accommodation sub-classes, Trust Score signals | All |
| F2 | **Collectors category** — catalogue reference, condition, edition/year fields | All |
| F3 | **Wave 1 cities** — New York · London · Sydney onboarding and CityLauncher campaigns | All |
| F4 | **Stripe international payments** — needed for Wave 1 non-ZAR buyers (IoM or Singapore entity required) | Payments |
| F5 | **Paystack recurring subscriptions** — automate Global wishlist tier renewal (currently manual) | BEA |
| F6 | **Referral system** — Trust Score +5 for verified referrals | BEA + Admin |
| F7 | **Automated git commits from sandbox** — remove need for David to run PowerShell git commands | DevOps |
| F8 | **Self-funding property filter** — buyer-side filter: "Show only self-funding properties" (yield >= bond repayment on standard 20yr bond at prime+1). Requires yield badge (H7) to be live first. Investment buyers can one-tap filter to deals where rent covers bond from day one. | Buyer app |

---

## ✅ Completed this sprint (Sessions 26–31)

- Local Market full implementation (BEA + buyer + admin) ✅
- Trust Score Hub (BEA endpoint + admin UI) ✅
- Wishlist Feed with Web Push ✅
- Edit-after-publish with version control ✅
- 4-level ge
---

## 🤖 AI Tuppence Services — Session 73+ Build Queue
*Added Session 72 · All items require Tuppence balance check before execution · All non-refundable*

### Tier 1 — Core AI Services (Session 73)

| # | Item | Cost | Model | Area |
|---|---|---|---|---|
| AI1 | **AI Listing Rewrite** — seller pays to rewrite title + description in current market language and buyer psychology. Available from admin listing edit screen + seller's live listing card. BEA: `POST /listings/{id}/ai-rewrite?email=` | 1T | Haiku | BEA + Admin |
| AI2 | **"Why am I not getting intros?" Seller Audit** — Claude reviews listing title/description/price/trust score/photo count and returns 3 specific improvement actions. BEA: `POST /listings/{id}/ai-audit?email=` | 1T | Haiku | BEA + Admin |
| AI3 | **"Is this a fair price?" Buyer Check** — buyer pays before requesting intro to get a market comparison for the specific listing with plain-English verdict. BEA: `POST /listings/{id}/price-check?email=` | 1T | Sonnet | BEA + Buyer app |

### Tier 2 — Category Intelligence (Sessions 74–75)

| # | Item | Cost | Model | Area |
|---|---|---|---|---|
| AI4 | **Property Yield Calculator** — seller enters purchase price / estimated value; Claude calculates gross yield, net yield (after rates/levies/maintenance estimate), compares to suburb averages, returns "Is this a good investment?" verdict. Feeds into the self-funding property filter (F8). BEA: `POST /listings/{id}/yield-calc?email=` | 1T | Haiku + static suburb yield table | BEA + Buyer app |
| AI5 | **Batch Card Listings — Collectors** — seller uploads photos of up to 20 cards in one session. Vision AI identifies each card (name, set, condition, estimated value), creates a separate draft listing per card, pre-fills all fields. Seller reviews and approves each before publishing. Major time-saver for estate sales and collector portfolios. BEA: `POST /listings/batch-cards?email=` | 2T per batch | Sonnet Vision | BEA + Buyer app |
| AI6 | **Batch Coin Listings** — same pattern as AI5 but coin-aware. Identifies denomination, mint year, condition grade, suggests Rand value using SA numismatic price ranges. Auto-suggests missing shots (reverse, edge, certificate) per coin. BEA: `POST /listings/batch-coins?email=` | 2T per batch of up to 10 | Sonnet Vision | BEA + Buyer app |
| AI7 | **Estate Agent Portfolio Import** — agent uploads PDF or photo set of current portfolio (or pastes spreadsheet). AI extracts each property's details (area, beds, baths, price, description), creates a draft BEA listing per property, flags any needing additional info/photos. Single-session flow for an agent's full portfolio. BEA: `POST /listings/portfolio-import?email=` | 3T per portfolio | Sonnet Vision | BEA + Admin |

### Tier 3 — Platform & Financial Tools (Sessions 75–76)

| # | Item | Cost | Model | Area |
|---|---|---|---|---|
| AI8 | **Listing Activity Log** — automatic timestamped event log per listing (created, photo added, intro requested/accepted/declined, price edited, relisted, expired). Scrollable timeline in admin dashboard. No AI cost — pure DB reads. Builds seller trust and platform auditability. | Free | None | BEA + Admin |
| AI9 | **Seller Financial Statement Export** — accountant-ready PDF/CSV for a date range: Tuppence purchases, intro fees, subscription payments, AI service spend, net platform cost. Formatted with TrustSquare logo, seller name, CIPC reg no. Strengthens "platform service credit, not financial instrument" legal position. BEA: `POST /users/{email}/statement?from=&to=` | 1T | ReportLab/WeasyPrint | BEA + Admin |
| AI10 | **Monthly Seller Performance Report** — automated monthly email: listings viewed, intros received/accepted, trust score movement, AI-generated recommendation for next month. n8n scheduled job on 1st of each month. Included in Standard/International tiers; 1T for free sellers. BEA: `POST /users/{email}/monthly-report` | 1T (free on paid tiers) | Haiku | BEA + n8n |

### Implementation notes
- All Tuppence deductions: write negative delta to `tuppence_ledger` table; check balance first — return HTTP 402 if insufficient
- Batch endpoints: process photos in parallel where possible; return partial results if some fail
- Portfolio import: accept multipart/form-data with up to 50 photos or a CSV attachment
- Financial statement: use existing `transactions` + `tuppence_ledger` tables; no new schema needed
- Activity log: new `listing_events` table (listing_id, event_type, detail, created_at) — lightweight append-only
- All AI services must have DEMO_MODE guards returning mock responses


---

## 🔒 Security — near-launch (added 2 Jun 2026 · David-deferred · HUMAN-ONLY — do NOT auto-action)

| # | Item | Area |
|---|---|---|
| L9 | **Secrets rotation + editor access model.** Rotate `MS_API_KEY` / `MS_ADMIN_PASSWORD` / `MS_JWT_SECRET` (the three surfaced in a Cowork chat transcript 2 Jun — not a live breach: stored correctly server-side, app not yet public, Paystack test mode, 4 trusted editors — but treat as to-rotate). Kill the `96315` reuse (admin password shares the client-side `/support` gate code); replace client-side page gates with real auth (cf. `/orchestrator` Basic Auth). Move secrets from inline systemd `Environment=` lines to a `chmod 600` EnvironmentFile. Design per-editor accounts + FIDO2 hardware-key (dongle) + password for all 4 editors. JWT secret first (forging risk; rotation invalidates outstanding magic-link tokens); API-key rotation also updates the admin app + n8n. **Deferred by David to avoid halting the build — execute at/near launch with Claude's guidance. The orchestrator loop must FILE this
---

## TVS follow-ups (filed Session 110 · 3 June 2026)

- **TVS-COMPS · internal-comps 1T tier gated off (latent).** `_comp_count()` and the new `_comp_amounts()` query a non-existent `status` column (the real column is `listing_status`, NOT NULL default 'live'); the query errors and is caught, so comp_count is always 0 and the blue 1T internal-comps chip never surfaces (property/vehicles). At launch this happens to match the spec (ZA property = 0T area guide only), so nothing is user-visibly broken. Before enabling: (1) fix the column to `COALESCE(listing_status,'live') != 'paused'` in both functions; (2) add a **sensible attribute match** — split for-sale vs rental by `listing_type` (and ideally beds/size band) so a fair-price comps median never mixes sale prices with rents; (3) re-confirm the min-8 density gate per matched set. Product decision (what counts as a 'comparable') deferred to David per Codex.
- **TVS-FEEDS · collectible 1T feeds config-only.** LEGO/coins/TCG (BrickLink/Numista/JustTCG) resolvers are built but dark until their API keys are set in env (B7-safe). Set `BRICKLINK_TOKEN` / `NUMISTA_API_KEY` / `JUSTTCG_API_KEY` to light them.
- **TVS-0TYIELD · optional.** 0T area-yield reuses one cheap Haiku narration; could be made strictly zero-cost with a templated sentence (like the 0T price-check).
