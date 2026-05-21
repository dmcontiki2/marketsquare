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
| L3a | **support@trustsquare.co mailbox** — confirm mailbox exists and is monitored before EULA published to production. Used in Sections 5.4, 6.5, 6.6, 7.x, 13, 14 and 15. Operational item, not legal — but EULA is undeliverable without it. | Ops |
| L4 | **Privacy Policy page** — draft and publish trustsquare.co/privacy (required by EULA Section 9.1 and POPIA) | Legal |
| L5 | **FSCA guidance on Tuppence** — confirm Tuppence classification as non-virtual-asset with FSCA or comply if reclassified (EULA Section 12) | Legal |
| L6 | **POPIA consent timing** — counsel must confirm whether magic link email collection constitutes prior consent or whether EULA gate must move earlier in the flow | Legal |
| L7 | **Paystack live mode** — paste `sk_live_` + webhook secret into `.env` once CIPC registration approved | Server |


---

## 🟠 High Priority — needed for a solid user experience at launch

| # | Item | Area |
|---|---|---|
| H1 | **Local Market listings — parity with standard listings** | Buyer app |
| | · Cards should look identical to Property/Tutors/Services cards (photo, title, price, suburb, Trust badge) | |
| | · Detail screen should match the standard detail screen layout (photo carousel, full description, seller stats) | |
| | · Browse page LM banner should use same grid as other categories, not a separate layout | |
| | · LM intro flow should feel the same as standard intro (not a separate code path visually) | |
| H2 | **n8n email notifications** — buyer emailed when seller accepts or declines intro | BEA + n8n |
| H3 | **Seller-facing intro notifications** — seller emailed when new intro request arrives | BEA + n8n |
| H4 | **Maroushka + Dave phone test** — lightbox, back buttons, My Requests tab live test | Testing |
| H5 | **Showcase photos** — add `thumb_url` to demo listings 40–51 (royalty-free images) | Buyer app |
| H6 | **Tutors & Services edit parity** — confirm all structured fields save and display correctly after edit | Buyer + Admin |
| H7 | **Rental yield badge on Property listings** — seller enters monthly rental income (optional field); app computes gross yield = annual rent / asking price and displays as a badge on card and detail view. Zero seller effort, instant signal for investment buyers. Display as "X.X% Yield (gross)" with tooltip explaining the calculation. | Buyer app + BEA |

---

## 🟡 Medium Priority — polish and completeness

| # | Item | Area |
|---|---|---|
| M1 | **Paystack test card end-to-end test** — run full buy flow with test card, confirm Tuppence credited via webhook | Buyer app |
| M2 | **Subscription flow test** — test Global wishlist tier subscribe/verify/activate | Buyer app |
| M3 | **SA corporate tax rows B30:D30 in cost model** — fill once P&L is finalised | Cost model |
| M4 | **Local Market — wishlist feed integration** — LM listings appearing in "For You" home screen feed with LM badge | Buyer app |
| M5 | **Founding seller count** — currently 23/60, need 37 more before public launch | Content |
| M6 | **Maroushka re-listings** — real founding seller content via admin tool | Admin |
| M7 | **City selector bug audit** — verify geo selectors work on mobile Safari and Chrome Android | QA |

---

## 🔵 Future Features — post-launch Wave 1

| # | Item | Area |
|---|---|---|
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

