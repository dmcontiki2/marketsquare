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
| L7 | **Paystack live mode** — paste `sk_live_` + webhook secret into `.env` once CIPC registration approved | Server |
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
| F4 | **International payments for US/UK/AU launch — cheap, NO US entity, NO travel · David proceeding 5 Jun 2026.** Stale assumption corrected: a SA (Pty) Ltd does NOT need a foreign entity. Lead path = **Merchant of Record (Paddle / Lemon Squeezy)** — seller of record, accepts US/UK/AU cards, handles all foreign VAT, pays out to SA (Payoneer/Wise/PayPal), one integration, ~5% + $0.50/txn (replaces the ~$100/mo foreign-entity line) and sidesteps the Stripe-direct + Paystack/CIPC blockers. Alternatives: SA multi-currency gateway (PayGenius/Peach ~4%, self-handle VAT) or a remote UK Ltd -> Stripe (lowest fees, more admin). Pre-checks: confirm the MoR allows selling intro-credits; confirm SA "export of services" VAT with accountant; sell Tuppence in $5-$20 bundles to amortise fixed per-txn fees. Claude offered a fee-math one-pager. | Payments |
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
| L9 | **Secrets rotation + editor access model.** Rotate `MS_API_KEY` / `MS_ADMIN_PASSWORD` / `MS_JWT_SECRET` (the three surfaced in a Cowork chat transcript 2 Jun — not a live breach: stored correctly server-side, app not yet public, Paystack test mode, 4 trusted editors — but treat as to-rotate). Kill the `96315` reuse (admin password shares the client-side `/support` gate code); replace client-side page gates with real auth (cf. `/orchestrator` Basic Auth). Move secrets from inline systemd `Environment=` lines to a `chmod 600` EnvironmentFile. Design per-editor accounts + FIDO2 hardware-key (dongle) + password for all 4 editors. JWT secret first (forging risk; rotation invalidates outstanding magic-link tokens); API-key rotation also updates the admin app + n8n. **Deferred by David to avoid halting the build — execute at/near launch with Claude's guidance. The orchestrator loop must FILE this, never auto-action it (security setting).** | Security |

---

## 🚀 Launch-Readiness Track — owner plan · 2 Jun 2026 · Orchestrator-managed
*Scope: Pretoria (Tshwane) public launch. External blockers (L1/L3/L4/L5/L6/L7/L9 + Overpass) deliberately set aside — see the 🔴 and 🔒 sections above; they are FILE-only for the loop and do not gate this track. Rendered view: `LAUNCH_READINESS_PLAN.html`.*

**Lane key (maps to ORCHESTRATION_POLICY §4–§5):** `AUTO-SHIP` = nightly Fixer, verified + non-gated · `STAGE` = verified but hits Gate 1 (regulatory) / Gate 2 (financial), awaits `approve <id>` · `ATTENDED` = design/feature/structural, FILE'd + built in an attended session (loop never executes) · `CONTENT/OPS` = supply/photos/onboarding/config.

### P0 — launch gates within our control
| # | Action | Lane | Gate | Wave |
|---|--------|------|------|------|
| H2/H3 ✅ | Introduction notification loop — **DONE / verified 2 Jun.** Found fully built in a prior session but never run; switched on + tested end-to-end (3 branded, anonymity-safe emails confirmed delivered to inbox). No code change. | DONE | — | A |
| M1/M2 | Money-path proven in test mode — test-card top-up→webhook→Tuppence credit; subscription subscribe/verify/activate | ATTENDED | — | A |
| S5 | Gate test/auto-approve payment endpoints behind a fail-closed prod flag | STAGE | Gate 2 | A (on `approve S5`) |
| M0 | `GET /listings` pagination (`?page=&page_size=` + `total`) + FEA infinite scroll | ATTENDED | — | A/B |
| M5/M6 | Reach 60 founding sellers (37 more from 23/60); real Maroushka content + interior photos for units 314/109/308 | CONTENT/OPS | — | Continuous (lead now) |
| RM-5 | Revive CityLauncher ("the gem") — finish + first real run of the orchestration brain (durable dead-source memory, Sonnet checkpoint-strategist, server-side saturation scheduler, MX email-verify). OSM-first runs now; wide SERP scale waits on the parked Overpass blocker | ATTENDED | — | A |

### P1 — credible first impression + cost discipline
| # | Action | Lane | Gate | Wave |
|---|--------|------|------|------|
| RM-1 | Home-page redesign implement (value-prop hero + first-run explainer, lift sub-12px type floor, emoji→SVG, desktop frame) | ATTENDED (design) | — | C |
| H1 | Local Market parity (cards/detail/intro identical to standard categories) | ATTENDED (design) | — | C |
| H7a/H7b/H7 | Yield tools fully visible — render full breakdown (H7a), country-aware benchmarks (H7b), gross-yield badge on Property cards (H7); unlocks F8 | ATTENDED | — | B/C |
| RM-4 | AI-independence — Sensor/Orchestrator to server cron, Sonnet sparse checkpoints, retire Haiku (~70–90% maintenance-token cut). **Cost model impact: large standing reduction.** | ATTENDED (build) | — | A |
| M8/H5 | Content & photo pass — royalty-free shopfronts, cap `wd-hero` height, audit `w=800` params; `thumb_url` on demo listings 40–51 | CONTENT/OPS + design | — | C |
| RM-6 | Email overhaul — 9 templates onto steel-blue/Syne brand; badges match `trustTier()`; inherits RM-1's look | ATTENDED (design) | — | C (after RM-1) |

### P2 — foundation (makes scaling a config change)
| # | Action | Lane | Gate | Wave |
|---|--------|------|------|------|
| RM-2 | BEA modularization M1 → `core_spend.py` (build-ready), then M2+ | ATTENDED (FILE'd — loop never restructures) | — | B |
| RM-3 | FEA streamline — `ms.js` → 14 classic-script files; drop dead `PROP_PHOTOS`/`PROSPECTS` | ATTENDED (build) | — | B (after M1) |
| A11Y-1/2/3 | Accessibility — focus ring, `aria-live`, admin alt-text/labels | ATTENDED (design) | — | C |

### Continuous — nightly auto-ship lane (already queued; no action needed)
JS-2 → SCAN-8 → SCAN-9 → SCAN-10 → SCAN-11 → SCAN-12 → HTML-1 → HTML-2, plus the ADMIN_KEY backstop (`/admin/purge-cache` + `/admin/refresh-pois` unauthenticated while `ADMIN_KEY` unset). All `AUTO-SHIP`, one/night (~8 days). S5 is the only `STAGE` item in this lane.

---

## TVS follow-ups (filed Session 110 · 3 June 2026)

- **TVS-COMPS · internal-comps 1T tier gated off (latent).** `_comp_count()` and the new `_comp_amounts()` query a non-existent `status` column (the real column is `listing_status`, NOT NULL default 'live'); the query errors and is caught, so comp_count is always 0 and the blue 1T internal-comps chip never surfaces (property/vehicles). At launch this happens to match the spec (ZA property = 0T area guide only), so nothing is user-visibly broken. Before enabling: (1) fix the column to `COALESCE(listing_status,'live') != 'paused'` in both functions; (2) add a **sensible attribute match** — split for-sale vs rental by `listing_type` (and ideally beds/size band) so a fair-price comps median never mixes sale prices with rents; (3) re-confirm the min-8 density gate per matched set. Product decision (what counts as a 'comparable') deferred to David per Codex.
- **TVS-FEEDS · collectible 1T feeds config-only.** LEGO/coins/TCG (BrickLink/Numista/JustTCG) resolvers are built but dark until their API keys are set in env (B7-safe). Set `BRICKLINK_TOKEN` / `NUMISTA_API_KEY` / `JUSTTCG_API_KEY` to light them.
- **TVS-0TYIELD · optional.** 0T area-yield reuses one cheap Haiku narration; could be made strictly zero-cost with a templated sentence (like the 0T price-check).

---

## 🔍 Audit Function — day-one feature · FOR REVIEW (flagged 3 Jun 2026)
**David-flagged as important + nearly forgotten** — an "Audit function" intended in the app from day one. Believed to (a) potentially form part of the **patents**, (b) be a **major attraction**, (c) carry substantial prior thinking ("a lot of great ideas") **not yet written down**. **Status: TO DEFINE** — needs a full review discussion to capture the concept before it can be specced or placed on the live ops dashboard. Next: David to brain-dump (what it audits · who uses it · the trust/anonymity + patent-novelty angle · the attraction), and/or recover from his previous laptop (Genesis-era archive) + the Solar Council Codex / old planning docs. Parked here so it is never lost again. (See memory project_audit_function.md.)

---

## 🔨 Auctions & Offers — concept captured · open actions (added 3 Jun 2026)
**Recovered Genesis-era feature, now designed.** Concept doc + live-sim cost model live in `\Projects\Codices` (`TrustSquare_Auctions_and_Offers_Concept.html`, `TrustSquare_Auction_Cost_Model.xlsx`), indexed in `SOLAR_COUNCIL_MASTER_INDEX.md`. Model locked: intro-auction (not a sale) · real-money bids + real-escrow surety settle off-platform · Tuppence = simple burns (airtime always / winner-intro on success only) · data-theatre, **no video** (video = curated external links only) · one engine, many formats/modes incl. "make an offer". Chosen deploy = **server-primary behind `/orchestrator` auth, local folder as backup, one `scp` push**. **All items ATTENDED — design/build, the orchestrator loop never executes these.** (See memory project_auction_feature.md.)

| # | Open action (the gap, so nobody has to remember it) | Area | Lane |
|---|---|---|---|
| AU-DEPLOY | ✅ **DONE (3 Jun)** — `/auctions` live behind its OWN dedicated Basic-Auth (realm "TrustSquare Auctions (secret)", `.htpasswd_auctions`, user `david`); verified 401 unauthed (origin + Cloudflare); update via one `scp` to `/var/www/marketsquare/auctions.html` | Server/Ops | DONE |
| AU-BACKUP | Server-hosted canon has **no version history** (the gap of the scp-only choice) — add a periodic snapshot/backup (git or Drive) for rollback | Ops | ATTENDED |
| AU-ENTRY | ✅ **DECIDED (4 Jun)** — free to browse; to BID you HOLD the intro fee (a reservation, released if you don't win) — not a fee, weeds tyre-kickers, guarantees no flop. Adds a transactional hold ledger primitive (Financial-gate). Confirm at the Day-0 gate. | Design | DECIDED |
| AU-OFFER | "Closest offer" semantics: **highest** vs **closest-to-a-private-seller-target**; define a seller minimum-offer floor | Design | ATTENDED |
| AU-VERIFY | Define the platform-vetted **independent-verifier panel** + how results report to the app; seller pays the verifier directly (off-platform, $0 to platform) | Design/Ops | ATTENDED |
| AU-FORMATS | v1 = English-ascending + make-an-offer; stage Dutch / sealed / reverse later | Build scope | ATTENDED |
| AU-PATENT | Fold auction claims (intro-not-sale · real-escrow/Tuppence bond · anonymous-via-app-auth · deferred offer-triggered intro) into the pre-filing supplement; prior-art check vs Whatnot + Pingsby | Legal/IP | ATTENDED (ties L8) |
| AU-COSTMODEL | Cost-model placeholders to set: real verification cost/rate; **load-test** max websocket conns/box (8,000 est.) | Cost model | ATTENDED |
| AU-ARCH | ✅ **DONE (3 Jun)** — architecture decided + documented: auctions = a BEA router (`auctions.py`) on the transactional ledger; live-bid theatre = a separate stateless realtime gateway ("BEAA") only at v2 (Redis pub/sub, extractable); lazy `auctions.js` on the FEA. Splits RM-2/RM-3 pulled forward, incremental (strangler), auctions first — no dev freeze. Diagram + A3 Word doc in `\Projects\Codices`. | Architecture | DONE |
| AU-NAV | **OPEN** — FEA entry point for auctions. Recommendation: NOT a permanent bottom tab (usually-empty early = dead weight that trains users to ignore it); use an event-aware entry — a "Live / Starting soon" banner on Home + an understated "Auctions" entry in Browse that badges when active — linking to a new dedicated auction page (lobby: Live / Upcoming / Results → live room). "Make an offer" stays an inline button on every listing (no nav). Graduate to a real tab once a city has auction density. Decision pending David. | Design/FEA | ATTENDED |
| AU-TIERS | **OPEN** — one engine, tiers = presets of 7 dials (lead time · format/tempo · verification · hold-to-bid · registration · airtime): Quick (card "drop": photos+AI+short countdown+soft-close, NO seller video) → Standard → Premium → Regal (Sotheby's-style: weeks+preview, specialist+provenance(+guarantor), value-scaled refundable escrow, formal registration+paddle). Universals: proxy max-bids · soft-close · reserve · win=intro · Tuppence on win · off-platform · no platform video. Visual + A3 in `\Projects\Codices`. | Design | ATTENDED |
| AU-SCOPE | **OPEN** — local vs global. Rec: GLOBAL discovery by default (liquidity = attractor), but each lot carries a bidding-REACH (local/national/global) the seller sets, defaulted by category — cards & art global; livestock/property/vehicles regional. Constraint is settlement/logistics (cross-border escrow, shipping, customs), not discovery; stays within geo invariant #5. Decision pending David. | Design | ATTENDED |
| AU-SELLER | ✅ **DECIDED (4 Jun)** — trust floor (Quick 75 / Std 80 / Prem 88 / Regal 92) + subscription floor (Quick ≥ Standard $12 · Std ≥ Professional $20 · Prem ≥ Business $40 · **Regal ≥ Elite $100**). Free-tier EXCLUDED for now (revisit from history). Premium/Regal also require an actual real-money surety (escrow). | Design | DECIDED |

> **NGINX-HYGIENE — ✅ RESOLVED (3 Jun):** stale `marketsquare.bak-*` files moved out of `/etc/nginx/sites-enabled/` to `/root/nginx-backups/`; "conflicting server_name" warnings now zero; `nginx -t` clean + reloaded.


## 🌍 Wave 1/2 City Readiness — gaps (filed Session 113 · 4 Jun 2026)
**Done this session:** all Wave 1 (New York, London, Sydney) + Wave 2 (10 US, 10 UK, 10 ZA incl. the 3 newly-added) cities are seeded in the geo hierarchy with accurate centre coords and are selectable in the buyer app; `renderMap` now auto-centres on the selected city (`ms.js` v141). Remaining open actions so nothing relies on memory:

| # | Open action (the gap) | Area | Lane |
|---|---|---|---|
| W12-ADMIN | Admin seller-onboarding region/city picker is hardcoded `country=ZA` (`populateRegions` -> `/geo/regions?country=ZA`; city list -> `/geo/cities?country=ZA`). Add a country selector feeding region->city so non-ZA Wave 1/2 prospects can be assigned a `geo_city_id`. Magic link carries the city *name* but geo resolution for non-ZA is the gap. | Admin + BEA | ATTENDED |
| W12-SUBURBS | International cities (US/GB/AU) have no suburb hierarchy — the suburb panel shows "All suburbs" only and free-tier suburb gating stays ZA-only. Seed suburbs per city (GeoNames country dumps) if/when suburb-level precision is wanted for intl launches. | Data/BEA | ATTENDED |
| W12-WAVE3 | Wave 3 AU cities (Melbourne, Brisbane, Perth, Adelaide, Gold Coast, Newcastle, Canberra, Wollongong, Hobart) not seeded — out of the Wave 1/2 scope; seed via `seed_wave12_cities.py` pattern when Wave 3 approaches. | Data | ATTENDED |
| W12-VISUAL | In-app visual click-test of the city picker + map alignment was deferred (Chrome extension offline this session) — run the walkthrough + screenshot once Chrome reconnects. | QA | ATTENDED |
| W12-FORYOU | **Demo part DONE (S119): For You feed hidden in demo mode** so real listings no longer bleed into demo prospect cities. **Remaining (live):** the feed (`wlLoadFeed` → BEA `/wishlist/feed` + `/wishlist/showcase`) is not geo-scoped, so a live Houston/Phoenix buyer would see Pretoria recommendations. Add a city/country scope to those endpoints (or filter returned cards by active city/country). | BEA | ATTENDED |


## 🔧 Orchestrator loop — doc-writeback hardening (open action · filed 4 Jun 2026)
**The overnight loop's BACKLOG/STATUS/CHANGELOG writeback keeps truncating files** (the large-file write hazard). `BACKLOG.md` was silently truncated and caught + restored TWICE this run (Sessions 117 & 118), losing rows each time until restored from the committed copy; STATUS Live State was clobbered once too. Risk: a session's `git add -A` could commit a truncated doc if not caught.

| # | Open action | Area | Lane |
|---|---|---|---|
| LOOP-1 | Harden the loop's doc-writeback with safe-write + verify: write to a temp file, assert it still ends correctly (tail + expected length / anchor) before replacing the real file; on failure, abort the writeback and leave the prior file intact. Mirror the `open/read/str.replace/write` + verify discipline used for the big HTML/JS files. | Orchestrator/Ops | ATTENDED |
| LOOP-2 | Interim guard until LOOP-1 ships: every session runs `GIT_OPTIONAL_LOCKS=0 git status` and confirms BACKLOG/STATUS/CHANGELOG are intact (not truncated) before surfacing the commit — restore any truncated doc from `git show HEAD:<file>` first. | Process | ATTENDED |

## 🧪 Demo-mode sweep — remaining items (filed Session 122 · 5 Jun 2026)
First parallel-subagent demo audit; the 3 HIGH + key MED were fixed in S122. Remaining (lower priority):

| # | Open action | Area | Lane |
|---|---|---|---|
| DEMO-1 | Local Market tile count is written by TWO functions (`renderCatCounts` lm-branch + `initLMHomeTile`) with different filter rules, and ignores the active-suburb filter the 6 standard tiles honour; also the no-live count fallback drops the suburb filter. Latent today (numbers agree) but real. Unify into one predicate incl. suburb. | FEA | ATTENDED |
| DEMO-2 | World Heritage coverage gaps: 5 `_wfCountryMap` countries (BO/CD/IR/LY/PT) have no dropdown option (unreachable); confirm "332 vs 304" sites; latent dropdown-sync guard in `selectDemoCity`. | FEA/Data | ATTENDED |
| DEMO-3 | Demo data cosmetics: `area` can be far from `city` (a "Pretoria" listing showing "📍 Mozambique"); `city_country` vs `country` field inconsistency. Demo-only. | Data | ATTENDED |
| DEMO-4 | **Immediate fix DONE (S122):** every dead-image demo listing reassigned a working category-related photo (verified). **Permanent fix still open:** self-host the demo images on R2 so they never rot or rate-limit again (external Unsplash links die + throttle). Also: the bulk image-scanner must use low concurrency to avoid Unsplash rate-limit false-positives. | Data/Ops | ATTENDED |
| DEMO-5 | 27 dead Unsplash URLs sit in the **secondary `photos[]` gallery** of 34 demo listings (hero is fine; only seen on gallery swipe — falls back). Several look fabricated (e.g. `…3531b543weak`). Replace with verified URLs; rolls into DEMO-4's permanent R2 self-host fix. | Data | ↪ ROUTED → DEMO-4 (R2 self-host) · S125 Fix |
| DEMO-6 | `renderAdvGrid` hardcodes the price suffix by type (`/night` for accommodation, `/person` otherwise) and ignores the data's `per` field → `demo_stay_2` (`per:"/person/night"`) is mislabeled `/night`. Read `l.per`. Cosmetic, 1 listing. | FEA | ✅ DONE · S125 Fix (ms.js v153) |
| DEMO-7 | `renderCatCounts` excludes `ph_` placeholders but not `l.paused`. Latent (today the only paused demo rows ARE the placeholders) — add `&& !l.paused` so a future non-placeholder paused demo listing can't inflate a tile count. | FEA | ✅ DONE · S125 Fix (ms.js v153, both count paths) |

## 🔁 Orchestration v2 — Phase 2 Triage (shipped Session 124) · open gaps
**Phase 2 (Triage) is built, deployed behind `/orchestrator/v2/` and ran its first live triage** (S123 sweep → 3 green to Fix, 3 resolved, 6 dismissed). Engine `triage.py` (deterministic, zero-token) + `triage_board.html` + `ignore.json` + cockpit wiring. Open actions so nothing relies on memory:

| # | Open action (the gap) | Area | Lane |
|---|---|---|---|
| TRIAGE-IN-1 | **Detect should emit a findings-JSON.** Detect still runs through Claude and writes prose, so Triage had to reconstruct the S123 findings (`detect_findings_S123.json`). Add a poka-yoke: Detect's final step writes findings in the Triage input schema (sev/slice/symptom/root_cause/file/area/root_token/match_terms/proposed_lane/confidence) so the Detect→Triage handoff is a file, not a reconstruction. | Orchestration | ATTENDED |
| ORCH-POLICY-1 | **Reconcile ORCHESTRATION_POLICY §5 with the v2 lanes.** §5 says verified security-class fixes auto-ship; the approved Phase 0 v2 lanes put secrets/security/permissions in RED (human-only). v2 governs — update §5 to match, and **re-lane the ADMIN_KEY backstop** (`/admin/purge-cache` + `/admin/refresh-pois` unauth while `ADMIN_KEY` unset) off the "Continuous nightly auto-ship lane": under v2 it adds auth/permissions → RED, not green. | Policy/Orchestration | ATTENDED |
| TRIAGE-WB-1 | **Triage→BACKLOG safe-append when automated.** When Triage runs unattended (Phase 5), new amber/red items must be appended to BACKLOG with the LOOP-1 temp-write + tail/length verify + atomic swap discipline — the same large-file truncation hazard that truncated `triage.py`/`ignore.json` via the Edit tool this session (rebuilt via bash-python str-replace + verify). Ties to LOOP-1. | Orchestration | ATTENDED |

## 🛡️ Orchestration v2 — Phase 4 Prevent (shipped Session 126) · open items
**Prevent is built + deployed behind `/orchestrator/v2/`** (`prevent.py`): regression guards (G-DEMO6/G-DEMO7/G-PHOTO) + the gentle demo-image monitor (M-IMG). A guard FAIL / monitor alert is emitted as a Detect-schema finding so it re-enters Triage → Fix (the loop closes). First run: 3/3 guards pass; M-IMG 3/30 dead, 0 false positives, 498 watched.

| # | Open action (the gap) | Area | Lane |
|---|---|---|---|
| PREVENT-HOMESTATS | `renderHomeStats` (`const live = LISTINGS.filter…`, ms.js ~2263) has the SAME ph_-excluded-but-not-paused pattern that DEMO-7 fixed in `renderCatCounts`. Left out of DEMO-7's scope deliberately. Add a guard + the `if (l.paused) return false;` fix (a clean future Detect → Triage → Fix item, or fold into a shared count-filter helper). | FEA | ATTENDED |
| PREVENT-SMOKE-DEPLOY | Process poka-yoke for the S125 deploy drift: add `smoke_test.py` to the standard deploy set so the server test never lags the committed one again (it asserted a stale `Adventures` category → false fail). One line in the deploy checklist / a guard that the served smoke matches HEAD. | Ops/Orchestration | ATTENDED |

## ⚙️ Orchestration v2 — Phase 5 Automate (shipped Session 127) · cutover pending
**The 5-stage arc is built end-to-end and runs itself nightly in SHADOW.** `orchestrator_v2.py` (deterministic, zero-token) on server cron 03:50 SAST runs Detect→Triage→Fix→Prevent, writes the cockpit "since last night" panel, deploys nothing, leaves the old loop untouched. First pass clean (smoke 39/39, guards 3/3, $0). Plan + commands in `automate.html`.

| # | Open action (the gap) | Area | Lane |
|---|---|---|---|
| CUTOVER-1 | **The controlled cutover (the last switch).** After a shadow parity night: (1) turn on a v2 Fixer — a Sonnet-checkpoint scheduled task that consumes the green work order from `orchestrator_v2_report.json` under the lane gates (verify-or-revert + smoke); (2) retire the 3 old Claude loop tasks (`trustsquare-orch-sensor`/`-fixer`/`-orchestrator`); (3) flip the conductor cron to `orchestrator_v2.py --live`. Fully reversible at every step; nothing fires without David's go. Retires the old patched loop (and moots LOOP-1). | Orchestration/Ops | ATTENDED — needs David's go |
