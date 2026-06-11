# MarketSquare · Feature & Fix Backlog
*Updated S131 · 7 June 2026 — launch-blocker re-triage (see 🔴/🟧/🟨)*
*Prioritised by: launch-blocking first, UX polish second, future features third.*

---

## 🔴 Launch Blockers — must fix before public launch

*Re-triaged 7 Jun 2026 (S131) per founder decisions: self-filed CIPC provisional + alternative PSP in parallel. 11 reds → 1 true external blocker · 7 self-executable actions (🟧) · 3 founder-call optionals (🟨) · 1 done. Reasoning: CityLauncher CHANGELOG S131 + chat 7 Jun.*

| # | Item | Area |
|---|---|---|
| B1 | **Payments live mode — the one true external gate** — the launch special requires $40/$100 paid plans in launch month, so a live PSP must exist at launch. Unblocked-in-principle: CIPC reg done (2026/340128/07) · patent-pending once the provisional is filed (A7) · mechanism publicly disclosed on trustsquare.co. ACTION NOW: submit Paystack live application AND run the alternative PSP application in parallel — first to approve wins; then paste `sk_live_` + webhook secret into `.env` (was L7) and build A6 card-on-file. | Payments |

---

## 🟧 Pre-Launch Required Actions — self-executable (re-marked from blockers, S131)

*Must EXIST at launch (several are legally required artifacts) but WE produce them — no external dependency, so they are work items, not gates.*

| # | Item | Area |
|---|---|---|
| A1 | [LEGAL-REQUIRED artifact] **Privacy Policy page** — draft + publish trustsquare.co/privacy (POPIA + EULA §9.1). AI-draft → David approves → publish. (was L4) | Legal |
| A2 | [LEGAL-REQUIRED mechanics] **POPIA consent timing** — wire consent capture at signup / magic-link entry; outreach opt-out already engine-enforced (opted_out sync + one-email rule). (was L6) | Legal |
| A3 | **EULA finalisation** — fill remaining `[COUNSEL REQUIRED]` sections with best-effort founder-approved text so the EULA exists and is deliverable at launch; counsel review itself moved to O1. (was L1) | Legal |
| A4 | **Company reg number into EULA §2 + app footer** — number EXISTS: Trustsquare (Pty) Ltd 2026/340128/07; insert + display (ECTA s43 expects it shown). (was L2) | Legal |
| A5 | **support@trustsquare.co mailbox** — plan ready in SUPPORT_MAILBOX_SETUP.md: Cloudflare route → Brevo SMTP from support@ → one BEA env/code edit → verify SPF/DKIM. EULA §5.4/6.5/6.6/7.x/13/14/15 depend on it. (was L3a) | Ops |
| A6 | **Card-on-file at signup — enforce what the copy promises** — zero-amount auth / R1 refundable tokenization at onboarding, store token for upgrades. Gated by B1 going live; copy-ahead-of-code acceptable pre-launch only. (was L10) | Onboarding |
| A7 | **File CIPC provisional patent — self-file, ~R900** — thrice-checked pack ready (IP Brief v6 · Patent Strategy v4 · Provisional Spec, claims C1–C13 incl. Tuppence HOLD). Filing = patent-pending + de-risks PSP onboarding. Supersedes L8 (IP Brief v3 / Strategy v2 — that refresh is DONE). | IP |
| A8 | ✅ **DONE — L9 closed: items 1–3 interim 6 Jun (ms.js v154) · items 4–5 Session 129 (launch_redemption.py + v155)** — billing/PLANS Tuppence canon + Founders redemption. | BEA + Buyer app |

---

## 🟨 Founder-Call Optionals — risk notes, never gates (S131)

| # | Item | Area |
|---|---|---|
| O1 | [RISK NOTE] **Counsel EULA review** — optional comfort pass over the A3 text; founder's call on timing/spend. (was L1's counsel half) | Legal |
| O2 | [RISK NOTE] **FSCA guidance on Tuppence** — optional comfort letter; the no-refund / no-deposit / burn-on-service design is the load-bearing protection (EULA §12). (was L5) | Legal |
| O3 | [RISK NOTE] **NCC direct-marketer registration** — registry believed non-operationalised; the real obligation (POPIA s69 consent/opt-out mechanics) is already enforced in the outreach engine. Counsel confirm = optional. (was L3) | Legal |

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

*Auctions & Offers track **PARKED until further notice** (David, 7 Jun 2026) — the full 13-item AU-* backlog, decisions and status are preserved verbatim in `PARKED_AUCTIONS.md` (same folder) for revival; dashboard panel intentionally removed (the /dashboard/summary parser keys on the section header). Canon/docs remain in `\Projects\Codices` + the auction memory files.*

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


## 🪜 Autonomy Ladder — Orchestrator-managed track (added 6 Jun 2026 · post-S129 · canonical doc: AUTONOMY_LADDER.docx)
**Current rung: 2 — Shadow autonomy · Destination: Rung 7 — Karoo posture.** Autonomy is earned by evidence gates, never assumed; every rung reversible; rung advancement is a weekly-review decision by David — the loop reports gate metrics in the daily brief but NEVER auto-advances a rung.

| # | Gate (the evidence) | Rung | Lane |
|---|---|---|---|
| AL-1 | **Rung 2→3 exit:** 3 consecutive clean parity nights — shadow plan ≡ what the live loop shipped/would ship, zero false-criticals, conductor cost $0 (Sonnet checkpoint excepted). On pass → table CUTOVER-1 at the next review. | 2→3 | AUTO-REPORT |
| AL-2 | **Rung 3 entry = CUTOVER-1** (already filed under Orchestration v2 Phase 5 — same item, not a duplicate). Needs David's go. | 3 | ATTENDED |
| AL-3 | **Rung 3→4 exit:** 14 nights fix-precision ≥95% (fix counts only if it survives 7 days) · zero out-of-scope ships · one clean rollback drill · doc-writeback hardening item (filed 4 Jun) CLOSED. | 3→4 | AUTO-REPORT |
| AL-4 | **Rung 4→5 exit:** 30-day rolling precision ≥97% · MTTR <12h · ledger-anomaly counter still at zero (never resets) · demo-mode sweep clean across 4 cities. | 4→5 | AUTO-REPORT |
| AL-5 | **Rung 5 gates (all blocking, jointly):** scaling-KPI capacity watcher LIVE · money-path M1/M2/S5 passed · security hardening executed (🔒 section above — HUMAN-ONLY items stay David's) · escalation page-drill passed · CPA s63 cure live · launch-code redemption + Ruby Spark badge mint in BEA · RM-5 → 60 founding sellers. | 5 | MIXED |
| AL-6 | **Rung 6 — launch month:** AUTONOMY FREEZE (no new authority granted) · every incident harvested into ORCHESTRATION_POLICY.md/Codex · zero Sev-1 mis-pages. | 6 | ATTENDED |
| AL-7 | **Rung 7 declaration:** joint 8+1 sign-off per AUTONOMY_LADDER.docx §3 — 60 sellers stable, revenue ≥ run-rate infra+AI cost, 6 green weeks, repeated page drill, one full quarter of weekly reviews with no missed-escalation finding. | 7 | ATTENDED |
| AL-8 | **Wake-David channel decision** (call vs WhatsApp vs email) for SEV-1 — one-line David decision, then encode in ESCALATION POLICY (ORCHESTRATION_POLICY.md §12). | — | DAVID |

## S130 filed (7 Jun 2026) — CityLauncher engine live-run gaps
| ID | Item | Lane |
|---|---|---|
| DDG-IP-1 | DuckDuckGo 403/connect-timeout from the Hetzner IP — source_health ladder cooling it (10m→24h); decide: drop ddg server-side or proxy. OSM + bing carrying. | LOW |
| PLAYWRIGHT-1 | playwright not installed in server system python — browser-tier jobs (pool cap 4) cannot run; OSM-first unaffected. Install playwright + chromium when a browser-only source is needed. | MED |
| LAUNCH-DEADLINE-1 | LAUNCH_SPECIAL_DEADLINE provisionally 2026-08-01 BOTH sides (BEA launch.conf + CityLauncher .env) — re-set to the true end-of-launch-month before LAUNCH_SPECIAL_ENABLED=1 / redemption flags flip. Same value both sides. | GATE |

## S130-flags resolved (7 Jun 2026, David decisions)
| ID | Decision |
|---|---|
| DDG-IP-1 | **ACCEPTED — no spend.** source_health ladder cools ddg to 24h retries by design; no proxy (independence/cost rule). Revisit only if bing also degrades. CLOSED. |
| PLAYWRIGHT-1 | **WON'T-DO server-side.** Every browser-tier source is unusable from Hetzner anyway (Property24 IP-blocked · Gumtree dead_permanent · GMaps key disabled). Replacement: **local Property24/GMaps run on David's machine** (`run_za_estate_agents.py`, runs now during discovery) → INSERT OR IGNORE to server (unique-email index verified, 0 dupes). CLOSED. |
| CUTOVER-1 | **GO tomorrow morning if tonight = 3rd consecutive clean shadow night** (Jun 6 + Jun 7 clean: smoke 39/39, guards 3/3, $0). Attended, reversible. Scheduled morning check will verify night 3 + present the runbook. |

## LAUNCH-FLIP CHECKLIST (one page — execute at launch-month lock, supersedes LAUNCH-DEADLINE-1 as a lone item)
Run the clean-refresh pass first (re-scrape launch city + free MX re-verify), then flip in this order:
1. `LAUNCH_SPECIAL_DEADLINE=<true end of launch month>` — BOTH sides, same value (BEA `marketsquare.service.d/launch.conf` + CityLauncher `.env`).
2. Re-enable Sonnet layer if wanted: uncomment `ANTHROPIC_API_KEY` in CityLauncher `.env` (S131 disabled it for $0 discovery).
3. Activate Resend $20/mo 50k tier (B7-approved S131, ceiling $20/mo).
4. CityLauncher: `LAUNCH_SPECIAL_ENABLED=1`.
5. BEA: `LAUNCH_REDEMPTION_ENABLED=1` + `TUPPENCE_MONTHLY_ENABLED=1` + `LISTING_VELOCITY_ENABLED=1`; `systemctl daemon-reload && systemctl restart marketsquare citylauncher-strategist citylauncher-scraper`.
6. `POST /launch/sync-registry` after first issuing run; verify `/launch/status` shows codes + gates true.
7. First email wave still HALTS at AWAITING_APPROVAL — David approves manually.

## TVS data quick-wins (S130, David-approved) — real variables for Fair Price / Yield, $0, no scraping
| ID | Item | Lane |
|---|---|---|
| DATA-KEYS-1 | **NUMISTA ✅ + JUSTTCG ✅ DONE (7 Jun — both keys live; both S110 stub resolvers were dead-on-arrival and rebuilt + live-verified: Numista v3 /types chain w/ VF-grade estimates · JustTCG per-variant NM baseline + full band). eBay registered, keyset pending (~1 day, chased by tomorrow's scheduled session). BrickLink CLOSED WON'T-DO (7 Jun): BrickLink ceased ALL South African operations 12 Dec 2025 — registration impossible from ZA; API also requires a running seller store + static-IP tokens. LEGO lane is covered by the eBay asking-band fallback (already wired — lego lights when the eBay keyset lands); bricklink resolver stays in code, dark, harmless. Acceptance rule added: a resolver isn't done until a key has run a live call through it.** Original: **David: 4 free signups** → set in BEA env: `BRICKLINK_TOKEN`, `NUMISTA_API_KEY`, `JUSTTCG_API_KEY`, `EBAY_APP_ID`+`EBAY_CERT_ID`. Resolvers already wired + credential-gated; chips light on restart, zero code. | DAVID |
| EBAY-1 | ✅ **DONE (S130)** — official eBay Browse API asking-price band resolver (free tier): `ebay_asking_band()` in tier_resolvers + collectible fallback in `_fair_price_resolve` (lego/coins/tcg/cards/comics/watches) + `ebay_browse` FREE provider registered (feature_flags.py + ai_service_tiers + json). Honest wording: "ASKING prices, NOT sold". Dark until EBAY keys (B7-safe); live-verified chips unchanged without key. | DONE |
| GV-ROLL-1 | **ZA property fair-price baseline from the official Tshwane GV2025 municipal valuation roll** (public per MPRA; propertyvaluations.tshwane.gov.za — search portal + Downloads; roll valid 1 Jul 2025 → 30 Jun 2029, so ONE manual download serves 4 years — no scraping, no loops, $0). Build: ingest bulk roll → suburb-aggregate table (median municipal valuation × property category) → `za_municipal_valuation()` resolver, provenance "Tshwane GV2025 (official)" + disclosed market-adjustment band. Joburg/CT rolls same pattern at wave time. | NEXT SESSION |
| TVS-CALC-1 | **Calculator mode + thin-comps band (canon adjustment, David-approved 7 Jun):** (a) when the benchmark variable is missing, the function does NOT hide — user supplies the variable (e.g. expected rent), system supplies validated math + official cost bands + a plausibility check against whatever thin data exists, output labeled "your assumption"; (b) `internal_comps_estimate` below min-8: with 3–7 comps return a WIDE band with N disclosed ("thin data — based on N comparable listings") instead of None. Touches resolver + bea waterfalls + FEA chip states; flag the canon change in Codex at next absorption. | NEXT SESSION |

## 🤖 AdvertAgent — advanced AI functions (added S132 · 7 Jun 2026)

| # | Item | Area |
|---|---|---|
| AI-1 | **FEA integration** — ✅ DONE S133 (wallet entry + screen, demo-blocked, dry-run-default-ON $0 testing). REMAINING: real user auth on /ai/ + hide dry-run toggle at launch | AdvertAgent |
| AI-2 | Promote stubs in revenue order: weekend_itinerary (3T, intro-flywheel; needs Adventures listings) → property_dossier (5T) → offer_advisor (2T) | AdvertAgent |
| AI-3 | G1 wording amendment at council review — buyer-side AI services under A8(ii) | Governance |
| AI-4 | API rate-limit tier review before launch volume (serial worker is the stopgap; 2 parallel web-search runs 429 today) | AdvertAgent |
| AI-5 | Wallet UI: AI feature spend must render under "AI feature credits — not used for introductions" (Briefing §5) when FEA wiring lands | AdvertAgent |
| AI-6 | nginx housekeeping: sites-enabled/marketsquare.bak_gate loads as a duplicate server block (pre-existing warn) — move out of sites-enabled | Infra |
| AI-7 | **Featured Local Slots** (DESIGNED, awaiting decision — AdvertAgent/Featured_Local_Slots_Design_Brief.docx) — subscriber-promoted local listings (3 mini-cards) at foot of relevant AI reports, 50/100T, area-bound, density scales by city. Needs 2 council rulings (ad-free brand · business-vs-A2 anonymity) + design-first clean build post-launch when subscriber inventory exists. $0 AI cost (revenue generator). | AdvertAgent |

---

## 🔁 Change-Control Protocol — standing process + active changes (added 10 Jun 2026 · David-approved)
**Big cross-cutting changes (canon / pricing / IP / business-process) now run through the Change-Control Protocol** so nothing gets dropped across the 60+ artifacts in five repos + the live server. Canonical: `CHANGE_CONTROL_PROTOCOL.md`. Active tickets + term maps: `CHANGE_REGISTER.md`. Reusable matrix: `TRACEABILITY_MATRIX_TEMPLATE.xlsx`. The guarantee = a **term map** a grep drives to **zero** (replaces human recall); the **Sensor/Fixer/Orchestrator** roles run the step-5 dry-run **attended + fully gated** (a canon change is exactly what the nightly loop must NOT auto-run — POLICY §7/§12).

| # | Item | Stage | Lane |
|---|---|---|---|
| CCP-0 | **Adopt the protocol** — `CHANGE_CONTROL_PROTOCOL.md` v1.0 written + wired here + into ORCHESTRATION_POLICY §7.1. | ✅ DONE 10 Jun | — |
| CC-001 | **Tuppence HOLD model** (commit-on-request → burn-on-delivery → release-on-decline; payer = service consumer; Codex→v4.8, IP Brief→v6, claims C10–C13). Term map DRAFT in `CHANGE_REGISTER.md`. | 4/5 STAGED (Fable 10 Jun — matrices+edits+drafts done, proof PASS; David: verify term map + land canon) | ATTENDED (Gate 1+2, §12) |
| CC-002 | **Pricing + AI canon** ("AI uses"/sessions retired; in-app AI FREE, advanced AI per-use Tuppence; tiers $0/12/20/40/100; allocs 6/10/20/50T @ 1T=$2; slots 2/10/25/60/500 cap). Term map DRAFT in `CHANGE_REGISTER.md`. | 4/5 STAGED (Fable 10 Jun — staged incl. Gate-2 bea diff; David: verify + land) | ATTENDED (Gate 2, §12) |
| CC-SEQ | **Sequencing call:** land CC-001 (sets the charge mechanism) before CC-002 (pricing copy refers to it); or run together with one merged term map / single Sensor pass. Decide at Step 1. | David call | DAVID |
