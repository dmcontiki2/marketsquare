# TrustSquare · Feature & Fix Backlog
*Updated S140 · 18 June 2026 — added the Deferred items list (surfaced in the daily brief)*
*Prioritised by: launch-blocking first, UX polish second, future features third.*

---

## 📌 Deferred items — the one durable "do it later" list (READ THIS IN THE DAILY BRIEF)

**Standing rule (from the Approvals & blockers principle in CLAUDE.md):** nothing is left dangling in a chat thread. If a small item genuinely can't be done in the moment, it lands HERE with a date, and it is surfaced every morning until it's done or explicitly dropped. Do-it-now is always the default; this list is only for the true exceptions. Clear an item by deleting its row (and noting it in CHANGELOG if it shipped).

| Added | Item | Why deferred | Reversible? |
|-------|------|--------------|-------------|
| 10 Jul | **Reinstate the wonders data audit** — recreate the deleted trustsquare-wonder-data-audit scheduled task (weekly Wed 07:30, cron 30 7 * * 3; read-only wonders-vs-Wikidata week-over-week delta into AUDIT_PROGRESS.md, never edits data) when the heritage / wonder numbers are next expanded. Removed 10 Jul 2026 — stable a long period, low value while the dataset is static. | Only worth running when heritage data is actively growing again | Yes — recreate the task (David’s call) |
| 18 Jun (S140) | **Tier-2 render check for video faults** — `human_view_verify.py` has the render hook stubbed; wiring true render verification needs David's Chrome (Claude-in-Chrome extension) live, which can't run headless in the sandbox. | Needs David's browser session; not sandbox-doable | Yes |
| 18 Jun (S140) | **Commit the S140 fix set** — `git add -A` + commit + push from PowerShell (sandbox can't commit; MOUNT/index.lock rule). Covers: human-view verify gate, approvals/blockers + mount/self-verify rules, deferred-items list, `mount_check.sh`, `.gitignore` `.bak-*` fix, CHANGELOG MOUNT-READ-1 entry. | Commit must run Windows-side, not sandbox | Yes |
| 7 Jul | **Pre-launch: demote the 3 family testers from superuser → tester-scoped rights** — David jnr `davidconradie1234@gmail.com` · Maroushka `miconradie1@gmail.com` · Maurice `conradiedm@gmail.com`. ⚠️ TWO steps or it silently reverts: (1) remove their emails from `SUPERUSER_EMAILS` in bea_main.py (~line 614 — the startup seed re-flags anyone listed, on every BEA restart) and deploy; (2) `ssh root@178.104.73.239 "sqlite3 /var/www/marketsquare/marketsquare.db \"UPDATE users SET is_superuser=0 WHERE LOWER(email) IN ('davidconradie1234@gmail.com','miconradie1@gmail.com','conradiedm@gmail.com')\""`. Superuser also auto-restores slot_limit 500 (~line 1098) — set their tester slot caps when defining the rights matrix (David's launch-time call: which of console-view / imports / rename / intros-inbox testers keep). | Launch-gated by design — they need full access until launch | Yes |
| 14 Jul | **SUPPORT-FROM-ROOT** — send support replies From support@trustsquare.co exactly (EULA wording). Today: From support@mail.trustsquare.co + Reply-To support@trustsquare.co (inbound-proven, launch-acceptable). Resend free plan = 1 domain and mail.* holds the slot → either upgrade Resend (~$20/mo) or swap slot to root + update SUPPORT_FROM_EMAIL / DEMAND_FROM_EMAIL envs + re-verify DNS. | David chose stay-as-is 14 Jul (cost/benefit); revisit post-launch | Yes |

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
| CC-003 | **Launch-threshold canon correction** — 60 staged prospects = WAVE TRIGGER; day-one launch w/ WHCL+demos+agency onboarding; purge “60 founding sellers = public threshold” doc error (David ruling 12 Jun, in chat). Hot lines fixed attended (AGENT_BRIEFING:14, CLAUDE.md:139); rest via CCP evidence run. | 0/5 OPENED 12 Jun | ATTENDED (canon, §12) |
| CC-SEQ | **Sequencing call:** land CC-001 (sets the charge mechanism) before CC-002 (pricing copy refers to it); or run together with one merged term map / single Sensor pass. Decide at Step 1. | David call | DAVID |

## Filed by daily loop — 12 June 2026
- [BASELINE-12JUN-1 · SEV-2 · ✅ RESOLVED S137 — APPROVED] 12 Jun 04:24Z cost-sweep deploy adjudicated (David-delegated, S137): content matches the approved Simpler-Model brief + P2 rails; prices byte-identical; SCAN-14 preserved; 9 sibling files identical; rollback would re-break starter/pro payment-init. Process breach remains open → COST-SWEEP-LANE-1. SCAN-16-LEDGER unblocked + shipped S137.
- [MOUNT-TEAR-1 · ✅ DONE S137] Mount bea_main.py healed from server post-ack (torn copy was a pure md5-proven prefix; restored, parity verified).
- [COST-SWEEP-LANE-1 · ops] "Nightly cost-compliance sweep" is a 4th agent lane outside ORCHESTRATION_POLICY — register it (cadence/gates/write-backs) or fold into the daily loop.
- [FEA-DRIFT-3 · ops] ms.js v168 / ms.css v127 / index 376196B attended-deployed 10–11 Jun, uncommitted+undocumented (3rd instance). fea baseline refreshed 12 Jun; the git sweep commit still owed.
- [GIT-INDEX-1 · ops] Sandbox git cannot parse .git/index (0xffff0000 → 0x00730000, 2 days). Temp-index workaround works; suspect Windows/sandbox git version skew.

## Filed attended — 12 June 2026 · launch-readiness (S137 chat, Claude → David)
- [GUIDED-PUBLISH-1 · HIGH · ✅ DONE S138] Publish endpoint: redundant admin-key Depends dropped (internal email-auth was already complete); hub now shows DRAFT + Publish button (dashPublish, demo-guarded); sobGoLive no longer sends the embedded admin key. CORRECTION: ms.js DID call publish in sobGoLive (earlier "zero /publish calls" was a grep artifact) — the real gaps were the key gate, the hub mislabel, and the client-side key. Auth matrix live-tested. FOLLOW-UP (open): guided handoff UX — surface the "Go live" step before the seller exits the flow.
- [SELLERHUB-STATUS-1 · MED · ✅ DONE S138] Hub status derived from `listing_status`; 📝 DRAFT badge + Publish CTA shipped (ms.js v171). PENDING/review-state chips can follow with the 7-state machine work.
- [WONDER-AUTOLINK-CAT-1 · ✅ DONE S138 — David ruling] Wonder AUTO-link allowlisted to Property+Adventures at publish; 27 listings / 135 auto-links cleaned (flag-filtered, manual picks preserved); picker stays open to all categories.
- [WONDER-AUTOLINK-MAX-1 · LOW · canon-conformance] Codex wonder auto-link table: MAX 3 links per listing, affinity-weighted, never overwrite manual picks, dismissible opt-out — live code attaches 5 (listing 243 has 5). Bring auto_link_wonders to canon (≤3 by affinity score). Today's category allowlist already matches the Codex affinity row (Property/Tours/Adventures).
- [PREVENT-PUBLISH-1 · ops] Add a Prevent guard + negative KPI: "guided-flow listing reaches `live` after completion" — this bug is a textbook false-pass (smoke green, journey broken); exactly the abnormal-condition class David specified for launch KPIs (gate 6).
- [GATE1-PAY-ZA · launch] "Payments open" ZA checklist: CIPC → Paystack business activation → live keys (env only) → live-webhook signature verify + idempotent credit re-test → ONE real-card E2E (smallest Tuppence pack: ledger + dashboard + bank settlement) → CPA s63/no-refunds posture rides the HOLD (CC-001 EULA v1.7). Admin-heavy, no build.
- [GATE1-PAY-INTL · launch · LONG-LEAD — START NOW] International rail fork (interlocks PAYMENTS-F4): MoR (Paddle/FastSpring class, ~5–7%, tax/currency/chargebacks handled) vs own-entity+Stripe (~3%, but UK VAT from FIRST sale for non-established digital sellers, AU GST @ A$75k, US state nexus tracking) vs Paystack cross-border (interim/testing only — ZAR statements, elevated declines). Lean: MoR at launch. FIRST ACTION: MoR compliance pre-check that Tuppence qualifies (prepaid fee for a defined introduction service, never cash-out; HOLD charge-on-delivery). Per-city gate = local-currency charge, normal auth rates, tax handled, refund-law aligned (AU ACL guarantees, UK CCR digital cooling-off ↔ HOLD).
- [AGENCY-IMPORT-1 · build] Agency-feed bulk importer: Rightmove/Zoopla, MLS/RESO, REA-XML exports → listings via BEA, with anonymity scrub (location-revealing-photo rules already canon), R2 photo pipeline, per-agency review queue. Converts the David/Dave/Maroushka agency visits into same-week listings; upgrades day-one cities from "WHCL+demos" to "WHCL+demos+anchor agencies".
- [LAUNCH-GATES-1 · canon] Draft the eight-gate launch checklist as the council doc: 1 payments currency-true per city · 2 patent pending · 3 wave trigger = 60 staged prospects/city (CC-003 model) · 4 app baseline joint sign-off (David+Claude) · 5 server readiness joint sign-off · 6 agent team lined up + KPIs live incl. negative tests (false-pass AND false-fail) · 7 (+1) Launch Control dashboard live · 8 per-country legal pass (outreach law: AU Spam Act consent, UK PECR/GDPR, US CAN-SPAM; category law: NY property/brokerage priority; EULA per-country annex). Codex amendment after David review (§12 attended).
- [LAUNCH-CONTROL-1 · build · GOVERNING SPEC FOUND S138] Build the **+1 Dashboard** per **Codex v4.7 §8** (April 2026; E4 observe-only): Page 1 Live Health · Page 2 KPIs · Page 3 Pipeline Status (CityLauncher scrape / email queue / intro queue / n8n — fields+sources specified in the Codex table) · Page 4 David +1 Control Surface (David-only — the launch gate-board + halt/approve buttons live HERE). The session dashboard, CityLaunch and orchestrator /approve are partial slices to consolidate. Early abandoned prototype: archive/trustsquare_command.html. Gate-7 of the launch checklist = this build.
- [LEGAL-COUNTRY-1 · David+counsel] One counsel session per country BEFORE its emails fire: outreach legality (Sydney: Spam Act consent basis; London: PECR/GDPR; US: CAN-SPAM) + Property-category introduction/brokerage rules (NY first) + EULA annex (consumer guarantees vs no-refunds; HOLD is the structural answer). Reusable forever per country.
- [PITCH-AGENCY-1 · marketing · BUILD NOW, EXTERNAL USE GATED] Global estate-agency pitch deck + poster: build now, circulate ONLY after the provisional patent is filed (ZA/UK/AU/EU absolute-novelty — pre-filing public disclosure can destroy patentability). Mechanism internals (HOLD ledger, C10–C13 claim matter) stay OUT of marketing materials permanently — sell outcomes, not mechanisms. "Patent pending" badge goes on only after filing.

---
## BIT (Built-In Test) self-test layer — design + first slice (27 Jun 2026)
- **BIT_ARCHITECTURE.md** written: functional + negative BITs, false-pos-PASS / false-neg-FAIL discipline, S1–S4 severity ladder, four-phase recovery (Report→Mitigate→Resolve→Prevent), auto-fix allow-list gating, concurrent BIT-Agent shape (deploy-gate + systemd cycler + daily brief), baselined against the live app (FEA / ~130 BEA routes / 23 dBase tables / complaints channel).
- **bit/bit_runner.py + bit/bit_registry.json** built & self-test-verified (mock BEA): 8 baseline BITs, N-of-M confirm, quiet-when-healthy, severity-tagged board, READ-ONLY (no edit/charge/deploy).
- **TRUE POSITIVE found:** FEA advertises `/ai/example/<id>` for every AI feature but the BEA has **0** such routes (every other AI op is a real route). That is *why* the "See an example (free)" buttons error. Caught by B-FEA-EXAMPLE + B-FEA-CONTRACT. This is the failure the heartbeat monitor structurally cannot see.
- **NEXT (open):**
  - [BIT-GATE-1] Merge the contract/functional BITs into smoke_test.py so a UI-button-without-a-route blocks deploy.
  - [BIT-AGENT-1] systemd BIT-Agent service beside the BEA (mirror citylauncher-strategist.service) + `bit_state` table + +1 Dashboard "Live Health" panel — after David okays §7 shape.
  - [AI-EXAMPLE-FIX] Implement/mount the `/ai/example/<id>` route (today's feature fix). BIT now makes its done-ness checkable.

- **BIT canon landed (27 Jun 2026):** Codex v4.8 §13 + system block diagram embedded; budget tightened to <=2% (customer ceiling for this app, vs 5% electronics); placement = Hetzner same-box for now. BIT marked as an applicable article in STATUS.md + AGENT_BRIEFING.md. Article lives at ../trustsquare-bit-agent/.

- **BIT Fix-cycle complete (27 Jun 2026):** Codex repaired (was corrupt — rebuilt via python-docx, opens clean) and now carries §13 (BIT), §13.1 (4-actor Fix process), §13.2 (worked /ai/example example) + both diagrams (system block + full fail→detect→report→fix→pass cycle). Mitigator wire-call IMPLEMENTED + verified: guarded reversible flag-flip to POST /admin/flags (allow-list, safe-direction-only, record-first journal, auth+idempotent+rate-limit, --apply gate, --rollback). BIT article now 1.47% of core (<2%). One live prerequisite: the safe-state flags (ai_example_enabled, auth_fail_closed, tuppence_burn_enabled) must exist as launch_switches columns in the BEA for apply to take effect — until then the Mitigator plans/journals correctly and writes no-op.

- **BIT inputs landed (27 Jun 2026):** (1) Diagram loop closed correctly — added the Fix Orchestrator → Core App DEPLOY edge (PASS stays the terminal verdict, the deploy is what physically closes the loop); Codex re-embedded. (2) The 3 BIT safe-state flags are now IMPLEMENTED in the BEA: `ai_example_enabled` (default 1), `auth_fail_closed` (default 0), `tuppence_burn_enabled` (default 1) — added to launch_switches CREATE TABLE + idempotent ALTER migration + _FlagsUpdate model + _flags_payload (exposed under "bit_flags"). py_compile clean; migration verified idempotent; flip path verified. NOT yet deployed to the server — local bea_main.py only; deploy via deploy_marketsquare.bat when David is ready.

- **BIT live monitoring wired (27 Jun 2026):** (a) BEA: POST/GET `/dashboard/bit` added (no-auth obscure URL, mirrors /dashboard/summary; stores bit_status.json) — py_compile clean. (b) Agent: `bit_cycle.py` runs the registry every 15 min, POSTs the board to /dashboard/bit, and on FAIL files findings_bit.json + runs the (reversible) Mitigator; spec in trustsquare-bit-agent/SCHEDULED_TASK.md (cron */15). (c) Dashboard: BIT summary line in the ⚡ Server Health panel (green/amber/red dot, pass count, failing ids, last-run) + full 🧪 BIT SELF-TEST panel under the Ops view, both reading GET /dashboard/bit. renderBIT() verified under node for healthy+failing states; bit_cycle post verified against a mock BEA (HTTP 200). Budget 1.77% (<2%). NOT deployed — local bea_main.py + dashboard.html only; goes live with deploy_marketsquare.bat. Scheduler task `trustsquare-bit-cycle` still to be created in Cowork.

- **BIT monitoring deploy (gated on David — 27 Jun 2026):** dashboard.html is NOT in deploy_marketsquare.bat and the SERVER copy is source-of-truth (CLAUDE.md DASHBOARD VERSION GUARD). So the BIT panel was applied to the LOCAL dashboard only for reference; the SAFE deploy is `deploy_bit_monitoring.bat` which (1) pulls the live dashboard down, (2) runs apply_bit_panel.py on THAT copy (idempotent), (3) pushes it back + deploys bea_main.py (adds /dashboard/bit), (4) restarts + purges. Run from David's machine (SSH). Sandbox cannot reach the server. After deploy, create the `trustsquare-bit-cycle` scheduled task (cron */15) per trustsquare-bit-agent/SCHEDULED_TASK.md to start posting boards.

- **BIT baseline CLEAN (27 Jun 2026):** folded the BIT into deploy_marketsquare.bat as step [6c] (runs on every push, prints [OK]/[WARN]/[FAIL], posts to /dashboard/bit) — NO separate schedule to manage. Fixed three real defects found by actually running it: (1) bit_cycle didn't propagate BIT_BASE to bit_runner (tested the wrong host) — fixed; (2) unreachable site now reads UNKNOWN+exit0, not a false FAIL on a transient; (3) budget guard was counting runtime output (findings_bit.json) as source — now counts source only = 1.84% (<2%). Verified end-to-end: healthy mock → 8/8 PASS exit0; unreachable → UNKNOWN exit0. No open caveats. Deploy path: David runs deploy_marketsquare.bat (BEA + dashboard via deploy_bit_monitoring.bat the first time); [6c] reports BIT status in the deploy output thereafter.

- **Kill-switch / independence audit (27 Jun 2026 — Fable lesson applied):** DEPENDENCY_AUDIT.md records every external single-point-of-failure (D1 Claude inference HIGH/ironic, D2 BIT trigger on Claude HIGH, D3 Paystack, D4 Hetzner single host, D5 Cloudflare, D6 Gmail/SMTP, D7 feeds=already seamed/the model to copy). Core finding: we seamed the FEEDS but hardwired the BRAIN — Anthropic is in ~15 BEA call sites with no swap point. FIX designed + reference-built: AI_PROVIDER_SEAM.md + ai_provider.py — one module, abstract task tiers (haiku/sonnet/vision/triage), vendor chosen by AI_ACTIVE env, any-of fallback, spend-log preserved in the seam. Proven: flip AI_ACTIVE anthropic->openai changes the model in ONE place, zero call-site edits. ROLLOUT is staged + gated (route 1 low-risk site first, then ~14 one-at-a-time verify-or-revert; David lands each deploy). OPEN: D2 (move BIT trigger to Hetzner cron/systemd so it survives Claude-off) still to build; D3-D6 seams backlogged after D1.

- **RECONCILED + CLOSED (27 Jun 2026) — supersedes the three BIT-monitoring notes above:** The "create trustsquare-bit-cycle scheduled task / every 15 min via Cowork" idea was SUPERSEDED (David: don't add a thing to manage; don't depend on Claude). Final design, all built this session:
  1. BIT runs as deploy-gate step **[6c]** in deploy_marketsquare.bat (every push) — no Cowork schedule.
  2. BIT runs **independently on the Hetzner box** via systemd timer (trustsquare-bit-agent/deploy/trustsquare-bit.{service,timer} + install_bit_timer.sh; cron fallback provided) — every 15 min, system python3, NO Claude in the path. Survives Claude-off.
  3. Dashboard reads GET /dashboard/bit (BEA endpoint built; panel via deploy_bit_monitoring.bat).
  **D1 kill-switch fix DONE:** all 15 httpx Anthropic call sites in bea_main.py now route through _ts_ai_url()+_ts_ai_headers(); model strings resolve from ai_provider via AI_ACTIVE — swap Claude→another LLM in ONE place. 16th site (KYC, uses anthropic SDK) annotated for later migration. py_compile clean; recursion bug found-by-running + fixed.
  **STILL DAVID-ONLY (physical, not sandbox-doable):** (a) run deploy_marketsquare.bat (+ deploy_bit_monitoring.bat first time) to push BEA+dashboard; (b) run trustsquare-bit-agent/deploy/install_bit_timer.sh on the box once; (c) set AI_ACTIVE/OPENAI_API_KEY only if/when actually swapping providers. These need SSH/box access the sandbox does not have.

- **AI swap seam — deploy gap fixed (27 Jun 2026):** deploy_marketsquare.bat did NOT ship ai_provider.py, so the seam fell back to hardcoded Anthropic (AI_ACTIVE would silently do nothing). FIXED: added `scp ai_provider.py` (with the backend-module group, before BEA restart) + a Step-6 [OK]/[FAIL] verify line. The "switch" is the AI_ACTIVE env var in /etc/environment on the server (same place as ANTHROPIC_API_KEY) — there is intentionally NO UI toggle (swapping inference vendor is a rare deliberate act). To swap: add AI_ACTIVE=openai + OPENAI_API_KEY=... to /etc/environment, then `systemctl restart marketsquare`. ACTION: re-run deploy_marketsquare.bat once so ai_provider.py reaches the server and the switch becomes live (until then it defaults to anthropic).

- **Page-4 AI Provider switch — BUILT (27 Jun 2026):** David asked for a private-dashboard control to swap AI providers when one goes down / for testing. Built: (1) `ai_active` TEXT column in launch_switches (default 'anthropic') + idempotent ALTER; (2) `_ts_active_provider()` — seam reads the provider LIVE from the DB per-call (10s cache), so a switch takes effect with NO restart; (3) `/admin/flags` accepts `ai_active` (validated anthropic|openai, busts cache) and `/flags` exposes `ai_provider:{active,available}`; (4) Page-4 (launch-switch-view) "🔌 AI Provider" card — segmented Anthropic/OpenAI control, reuses tok()+X-Admin-Token, OpenAI shown but greyed "adapter pending" until its real adapter is wired. Verified: live switch flips the resolved endpoint with no restart; bad provider rejected (400); added JS passes node --check; bea_main.py compiles. DEPLOY: re-run deploy_marketsquare.bat (ships bea_main.py + ai_provider.py) AND push dashboard.html via deploy_bit_monitoring.bat (server is dashboard source-of-truth). OpenAI stays inert until its adapter is built (currently a stub).

- **Page-4 AI Provider card — DEPLOY GAP FOUND + FIXED (27 Jun 2026):** David's screenshot proved the card was NOT on the live Launch Switch tab. ROOT CAUSE (not timing): deploy_bit_monitoring.bat PULLS the server dashboard and patches it with apply_bit_panel.py ONLY — it never added the AI Provider card, so the card (built into LOCAL dashboard.html) could never reach the server. FIX: built apply_ai_provider_card.py (idempotent patcher, verified: applies card+JS to a server copy lacking it, node --check clean) and wired it into deploy_bit_monitoring.bat as step [2b/6] + a post-push [OK]/[FAIL] verify line; added the card check to check_deploy_current.bat. ACTION: re-run deploy_bit_monitoring.bat — now it applies BOTH the BIT panel AND the AI Provider card to the server dashboard. Then the card appears on the Launch Switch tab.

- **OpenAI adapter BUILT — switch is now testable (27 Jun 2026):** _openai() in ai_provider.py is now a REAL adapter: _to_openai_messages() translates the app's Anthropic content-block messages (text + base64 image) → OpenAI chat format (text + image_url data-url), calls /v1/chat/completions, parses choices[0].message.content + usage. Verified end-to-end against a mock OpenAI (translate text+image → call → parse → ok). Page-4 card: OpenAI now shows available ONLY when OPENAI_API_KEY is set (honest key-gate). Added /admin/ai-test (admin-only) + a "▶ Test active provider" button on the card that runs a tiny prompt through the ACTIVE provider via the FULL seam and shows the result — so David can A/B test live WITHOUT touching the 15 production call bodies (those still send Anthropic-shaped JSON; migrating them to complete() is the separate staged D1 rollout). HOW TO TEST: (1) deploy (deploy_marketsquare.bat + deploy_bit_monitoring.bat), (2) set OPENAI_API_KEY in /etc/environment + restart, (3) Launch Switch tab → OpenAI now selectable → click it → click "Test active provider" → see the OpenAI round-trip result. Switch back to Anthropic the same way.

- **First REAL feature runs on either provider — invisible swap PROVEN (27 Jun 2026):** Reframed: NOT "migrate Claude→OpenAI" — the goal is BOTH always live, app-invisible switching. /advert-agent/market-note converted to route through ai_provider.complete() via asyncio.to_thread (stdlib bridge; sync seam from async handler). Verified end-to-end against dual mocks: the SAME feature returns a valid 1-sentence note on BOTH Claude Haiku 4.5 AND gpt-4o-mini, with each provider's own token counts feeding the SAME spend-log. Feature code is provider-agnostic. Model equivalence map (task->model per vendor) lives in ai_provider.TASK_MODEL: haiku=Haiku-4.5↔gpt-4o-mini, sonnet/vision=Sonnet-4.6↔gpt-4o, triage=Haiku↔gpt-4o-mini (VERIFY current OpenAI model names+pricing before going live — they move). QUALITY/COST are a David call per feature (the Test button + this live feature let you eyeball both). Failover model chosen: active-provider instant manual swap (auto-failover + per-feature pinning available as later options). REMAINING 14 features still send Anthropic-shaped JSON directly — convert one-at-a-time through complete() the same way (each verify-or-revert, David lands each). This one (market-note) is the proven template.

- **Date-stamp + accuracy disclaimer on AI reports (27 Jun 2026 — liability fix):** A price/market figure with no date reads as "true forever" — exposure if someone re-runs months later when the number moved. FIX: one `_report_stamp(extra)` helper in bea_main.py (defined once beside _INDICATIVE_LABEL) returns as_of / as_of_iso / as_of_human / date_disclaimer ("This report is accurate as of <date>. AI estimates, prices and market figures change over time — may be materially higher/lower if re-run later. Indicative for the date generated, not a guarantee of current/future value." + feature-specific tail). Spread into the money-sensitive returns: market-note, value-tiers, price-check (+"re-run for a current figure"), yield-calc (+"benchmarks current at the date above"). FRONT-END: aiDateFooter(j) in ms.js renders "Report date: <date>" + disclaimer as a footer under BOTH the live AI result AND the free EXAMPLE preview (so the date shows even on the first sample). Verified: stamp emits real UTC date; bea py_compile + ms.js node --check clean. Pattern is reusable — apply _report_stamp() to the remaining AI reports as they're touched. DEPLOY via deploy_marketsquare.bat (bea + ms.js).

- **Report stamp upgraded to MINUTE precision + UTC + volatile-item warning (27 Jun 2026):** David's point — for spot-priced items (gold, bullion coins, FX) even minutes mean $thousands, so a date alone understates risk. FIX: _report_stamp() now stamps "DD Month YYYY, HH:MM UTC" (minute precision, explicit UTC) + as_of_time_utc field; wording changed to "snapshot for the exact time above … may be materially higher/lower if run even minutes later." New `volatile=True` mode adds: "spot price can move significantly within minutes; not a dealing price; re-check live market before any transaction." New `_is_volatile_item()` classifier (coin/numismat/bullion/krugerrand/gold/silver/platinum/sovereign/spot/ounce) auto-fires volatile for value-tiers (by tierkey/service) + price-check (by source/verdict/subject). FRONT-END aiDateFooter(): shows "Priced as of: <date HH:MM UTC>" and a PROMINENT amber banner for volatile items (not buried fine print). Verified: classifier correct (coins/gold/bullion=True, cards/property/watches=False); both fns top-level (call-time safe); bea py_compile + ms.js node --check clean. Deploy via deploy_marketsquare.bat (bea + ms.js).

- **THE FIX OF THE DAY — /ai/example route BUILT (27 Jun 2026, while David rested):** Root cause (confirmed): the FEA "See an example (free)" button calls GET /ai/example/<id> but NO such route existed in the BEA → every example button errored. AUDIT FINDING: the authoritative feature-id list (/ai/functions) is NOT in any local file (server-only/built elsewhere), so I could not enumerate every id with certainty. FIX built to be id-proof: GET /ai/example/{function_id} ALWAYS returns a valid {result} — real curated samples for the 9 known ids (collectables_advert, collection_liquidation, property_dossier, car_dossier, heritage_tour, expedition_dossier, weekend_itinerary, offer_advisor, study_plan) + a graceful generic sample for ANY other id (incl. empty/unknown/edge), so it can never error regardless of what /ai/functions serves. Free, no Tuppence, no auth; carries the date stamp. Verified standalone: all 9 known + 6 edge ids return valid non-error results → B-FEA-EXAMPLE + B-FEA-CONTRACT will PASS. bea py_compile clean, no truncation. Deploy: deploy_marketsquare.bat (ships bea_main.py→main.py; added a Step-6 [OK]/[FAIL] verify line for the route). DAVID TO RUN: deploy_marketsquare.bat — then the example buttons work. NOTE: server-only /ai/functions means I built id-proof rather than id-exact; once live, the BIT confirms green and any feature wanting a richer sample is a one-line add to _AI_EXAMPLE_SAMPLES.

- **Deploy verify-line bugs FIXED (27 Jun 2026):** David's deploy run showed two `bash: syntax error near unexpected token '('` + a [FAIL] /health. ROOT CAUSE: the two verify lines I'd added had literal parentheses in their echo text — "(AI swap seam)" and "(free example buttons fixed)" — which break the remote `ssh "..."` bash command (the OTHER working verify lines have no parens; that was the tell). The /health [FAIL] was a cascade/transient: curl hit /health during the BEA's mid-restart window. FIX: (1) removed parens from both verify lines (now "AI-swap-seam present" / "route present - free example buttons fixed"); (2) /health check now retries 5x over ~10s so a startup race can't show a false [FAIL]. Verified: no ssh-echo line contains parens; {function_id} braces match literally (single-quoted, no expansion); all 3 commands simulated clean in local bash. NOTE: the /ai/example FIX ITSELF was never the problem — bea_main.py imports clean, route registers, all helpers top-level. Re-run deploy_marketsquare.bat; the two syntax errors are gone and /health won't false-fail.

- **BEA crash root cause FOUND + FIXED + deploy hardened (27 Jun 2026):** The deploy crashed the BEA (site down, "Connection error" on admin login). David ran restore_bea_now.bat → site live on the 09:16 pre-change BEA. Crash diagnosed via diagnose_bea_crash.bat v2 (loads systemd env + reads journalctl). REAL CAUSE (from uvicorn logs): `NameError: name '_require_admin' is not defined` — my /admin/ai-test endpoint (line 8698) referenced _require_admin which isn't defined until line 9091 = forward reference, NameError at import, BEA won't boot. py_compile CAN'T catch this (valid syntax, undefined-at-runtime); sandbox can't catch it (no FastAPI to load the app). FIX: moved /admin/ai-test to AFTER _require_admin's def (now 9075; uses at 9088+9161, all after). Verified: forward-ref scan clean, app-load test got past all imports+decorators with zero NameError (only failed deep in geo-seeding against the fake DB stub — not a code bug). PROCESS FIX: built deploy_bea_safe.bat — backs up main.py→main.py.lastgood, BOOT-IMPORTS the new file under real venv+env before relying on it, health-checks with retries, and AUTO-ROLLS-BACK to main.py.lastgood if it doesn't come up (saving the bad one as main.py.CRASHED). A bad BEA push can never again leave the site down. NEXT: David re-deploys the /ai/example fix via deploy_bea_safe.bat (self-protecting) — the example buttons fix is intact in bea_main.py, just needs this corrected build live.

- **DEPLOY SUCCEEDED — /ai/example fix is LIVE (27 Jun 2026):** deploy_bea_safe.bat ran: [4] HEALTH-OK, [5] [OK] New BEA is live and healthy. The _require_admin NameError fix is deployed; the BEA booted clean. The [3] boot-test RuntimeError(MS_API_KEY) was a FALSE ALARM — my [3] harness sourced env manually and missed systemd's Environment= directive, so a bare python import hit auth.py's fail-closed. FIXED [3] to use systemd's real Environment= + EnvironmentFiles, and labelled it ADVISORY. CRITICAL CONFIRMATION: step [5] rollback gates ONLY on (systemctl is-active AND /health=ok), NEVER on [3] — so the healthy BEA was correctly KEPT, not rolled back. The safety logic worked. NET: site is up, /ai/example route is live → the FREE/PAY "See an example" buttons should now work. David to confirm by clicking one.

- **"Internal Server Error" on Preview/Free AI run — DIAGNOSED + CODE-FIXED (27 Jun 2026):** David's collectables "Preview sample · $0" showed "Unexpected token 'I', Internal S... is not valid JSON". This is NOT today's example bug and NOT the BEA — it's the SEPARATE AdvertAgent service (advertagent.service, port 8002, AdvertAgent/service/advert_agent.py). Same error was already diagnosed 26 Jun (BUGFIX_ai-commit-403.md): AdvertAgent's /ai/run calls back to BEA /tuppence/ai-commit which returns 403 (AA_BEA_KEY != MS_API_KEY, suspected hidden char), the 403 is unhandled -> 500 plaintext -> browser JSON-parse error. "See an example" works (no commit call); Free + 5T runs fail (both commit). ROOT FIX (code, in advert_agent.py): a $0 DRY-RUN must NOT place a Tuppence hold — was calling bea_commit for dry too. Now: dry_run -> hold_id=None (skip commit), and the dry worker skips bea_settle when no hold. So the free preview no longer 500s regardless of the key mismatch — it shows the fixture sample (if seeded) or a clean "no sample" message. py_compile OK. TWO THINGS STILL FOR DAVID: (1) deploy advert_agent.py to the server + restart advertagent.service; (2) the AA_BEA_KEY<->MS_API_KEY 403 still blocks REAL 5T paid runs — config fix (compare exact key bytes per the bugfix note's "NEXT SESSION" step); (3) confirm fixture_collectables_advert is seeded (seed_map_fixtures.py) so the preview shows real sample content.

- **Advert Coach follow-ons (3 Jul 2026 — STAGED, awaiting David deploy):** deploy_marketsquare.bat ships bea_main.py + ms.js v213 + marketsquare.html together; after deploy, run ONE real /listings/vision-draft with car photos (~$0.02) to QA coach_tips + the template-shaped description; FEA baseline refresh (monitor expects v213). Rollback = cp the .bak-advertcoach-20260703-105734 files back.

- **CARS-SPEC-1 (docs/CARS_LISTING_AND_VERIFICATION_BRIEF.md Parts A–C, 15 Jun):** structured car persistence (variant / service_history / drivetrain / kW etc. as Listing fields + columns), 2×2 Vehicle Specs panel on detail, per-section confirm + single liability attestation, gallery generalisation adv*→gal*. Bigger build — architect sign-off per the brief.

- **CARS-VERIFY-1 (brief Parts D+F):** "Verified by Lightstone/TransUnion" 2T deliver-then-charge tier — GATED on David: provider choice (TransUnion/Imagin8 pay-per-lookup recommended first) + the redistribution/caching licence question. Free own-listings comps (area_guide for Cars) can ship before any provider.

- **VEHICLES-SUBTYPE-1:** Cars→Vehicles elevation + sub-type selector (Car/Bike/Caravan/Trailer/Boat/Other), per-sub-type field sets (brief B0).

- **FORMAT-BRIEFS-2:** Property + Trips/Tours benchmark briefs (Property24/Private Property; GetYourGuide/Viator/SafariBookings) to deepen the v1 Advert Coach templates the way the cars brief did for WeBuyCars/weelee.

- **SOB-COPY-1:** guided-onboard step copy still says "uses 1 session" (AI sessions retired) — one-line copy fix next time ms.js is touched.

- **Advert Coach batch 2 (3 Jul 2026 — STAGED with batch 1, same deploy):** SOB-COPY-1 DONE (decision refined per David: replace retired "uses 1 session" with the true price — "free" — not just delete; 6 ms.js step-subs + 4 marketsquare.html sessions-copy spots) · CARS-VERIFY-1 FREE half DONE (make/model/year title-matched comps + honest tier gate; PAID half still gated on David's TransUnion/Imagin8-vs-Lightstone account decision) · VEHICLES-SUBTYPE-1 DONE in the AA wizard (Car / Motorcycle / Caravan & trailer / Boat / Truck-bus-tractor; chip mechanism generalised; follow-ons: SB_FIELDS manual-flow parity + Cars→Vehicles DISPLAY-rename decision) · FORMAT-BRIEFS-2 DONE (docs/PROPERTY_LISTING_FORMAT_BRIEF.md + docs/TRIPS_TOURS_LISTING_FORMAT_BRIEF.md, primary-sourced; coach cues deepened from findings) · CARS-SPEC-1 architect plan FILED (docs/CARS_SPEC_1_ARCHITECT_PLAN.md — 6 shippable tasks, visibility-invariant design) — EXECUTE next session on David's go. Deploy note: ms.js is now v214 (v213 was batch 1, never deployed separately — one deploy ships both).

## CARS-SPEC-1 staging build — 2026-07-04 (scheduled, $0, staged NOT deployed)
- [DONE-STAGED] VSPEC Tasks 1–5 per docs/CARS_SPEC_1_ARCHITECT_PLAN.md — see BUILD_REPORT_CARS_SPEC_1.md. Deploy + 1 Haiku vision QA + FEA baseline refresh = David.
- [OPEN] VSPEC-FILTERS (plan Task 6, optional): Variant/Fuel/Body/Drivetrain chips in the cars filter sheet (mapper columns already live-wired).
- [OPEN] Seller-hub attest affordance: dashPublish currently 409-guided only — no in-hub confirm/attest UI (sob flow has it).
- [OPEN] CARS-VERIFY-1 paid half: provider decision (TransUnion/Imagin8 pay-per-lookup recommended first) — HELD until live profitability per David 3 Jul.

- **Executive Tour Dossier v2 follow-ons (3 Jul 2026 — staged in AdvertAgent, awaiting deploy_advertagent_safe.bat):** FEA render of the new options-JSON "routes" + "addons" arrays as settable chips that adjust the estimated total client-side (degrades safely until built) · glimpse copy refresh to tease the executive selection ("4 packaged tours found R19k-23k · self-planned est. R14.6k — unlock the dossier") · apply the same market-scan + executive-selection + build-vs-buy pattern to expedition_dossier and weekend_itinerary when those stubs activate · ONE real QA run (~$0.72, Sonnet + 10 searches) after deploy needs David's explicit OK · pattern candidate for property_dossier and car_dossier too (compare listed agents/dealers vs private buy).

- **Exec Dossier worked example (3 Jul 2026):** AdvertAgent/EXAMPLE_ExecTourDossier_VicFalls_via_Zambia.html — full v2 render (SATMS compliance card · market-scan exec selection · settable routes/add-ons with live total · intro buttons · PDF button), all figures marked (est.). NEXT: seed it as `fixture_heritage_tour` via seed_map_fixtures.py so the FEA "See an example (free)" button serves THIS instead of the old sample; reuse its option-chip pattern when building the FEA routes/addons renderer.

- **Exec-selection pattern rollout (3 Jul 2026, later — staged in AdvertAgent):** Heritage + Weekend + Retirement now all v2 (market scan · section-0 executive selection · routes/addons JSON · branded PDF shell applies worker-wide). Vic Falls worked example SEEDED as the heritage fixture incl. real 8-stop route map + SATMS callout (server step: run seed_map_fixtures.py after deploy). REMAINING: expedition_dossier same pattern (next touch) · FEA render of routes/addons as settable chips · FEA full result_html example render (example view currently renders markdown + map + spliced figs).

## VIDEO-REPORTS-V2 regeneration — 2026-07-04 (scheduled, $0 subscription route, staged NOT deployed)
- [DONE-STAGED] All 10 video-matched feature reports regenerated in v2 format (session reasoning + WebSearch, NO Anthropic API spend — David chose the subscription route 4 Jul over the ~$6 server-key path): heritage_tour (4,573 w, exec selection + options + 18 round-trip waypoints CPT first/last) · weekend_itinerary (3,700 w, ≈R930 for two vs R1,000 cap proven) · retirement_planner (4,682 w, D7 €920+50% verified, Tavira rent-first vs Caldas buy, Monte da Palhagueira estate scan, SATMS cited to SARS) · collectables_advert (2,708 w, A/B/U price ladder, price_suggest 350) · property_dossier (3,202 w, 6 comps, yield bands) · car_dossier (3,701 w, verdict FAIR-with-conditions vs R420k, 1GD-FTV faults cited, SA-spec no-DPF correction) · expedition_dossier (4,977 w, SA–Russia visa waiver + NEW RuID pre-registration mandatory 1 Jul 2026 + SATMS, 19 waypoints Pretoria first) · collection_liquidation (3,483 w, 5 lots, R5k–27k band, commissions cited) · study_plan (3,135 w, official Nov 2026 NSC timetable verified: Maths P1 23 Oct/P2 26 Oct, PhysSci P1 30 Oct/P2 2 Nov) · offer_advisor (1,880 w, R3,400/4,000/4,500 numbers). All in AdvertAgent\video_reports_v2\, every file tail-verified whole, unverifiable items marked (est.)/not-verifiable inline.
- [OPEN → David] Double-click AdvertAgent\push_video_reports_v2.bat — scp's the 10 .md over the old-format reports on the server + chmod 644 + listing confirmation. Nothing remains to regenerate.

- **NO-0T canon (4 Jul 2026, David ruling):** Example + paid run only, platform-wide — /ai/glimpse retired to 410 (ships with the pending deploy_advertagent_safe.bat re-run alongside fixture enrichment) · FREE_SNAPSHOT 0T tier cancelled-never-built · FEA glimpse dead code (FREE GLIMPSE tag ~ms.js:13061, AI_SEL.glimpse branch ~13086) = SCAN-candidate for the loop's auto-ship cleanup lane (renders nothing today, zero urgency).

- **VIDEO-V2 pipeline (4 Jul 2026, David's catch: videos are the last stale shop window):** scheduled Sun 5 Jul 09:00 — build report-to-video pipeline (render report → headless scroll capture with holds on money moments → free TTS narration → ffmpeg), $0, repeatable per report regen so videos can never go stale again; decided length 75-90s fast-scroll (NOT full read-through — attention cliff); pilot = heritage_tour for David's voice/pacing approval, then 9 more are one command each; existing Flow clips reusable as intros later; deploy via deploy_marketsquare.bat videos/ upload after approval.

## VIDEO-REPORTS-V2 — 2026-07-04 19:3x scheduled re-run (verification pass, $0)
- [DONE] All 10 v2 reports from the 18:0x run verified on disk: tails whole, every ```json block parses, options carry routes+addons (heritage/weekend/retirement), heritage 18 waypoints Cape Town first AND last, expedition 19 waypoints Pretoria first, no free-run/glimpse copy anywhere, (est.) marking present. Nothing regenerated — nothing needed it.
- [DONE] push_video_reports_v2.bat UPGRADED to the amended 4-Jul-evening spec (old copy = .bak-20260704-193x): now [1] mkdir both server dirs → [2] scp to video_reports_v2/ (seeder source) → [3] scp to video_reports/ (legacy) → [4] remote python3 seed_map_fixtures.py (fixtures upgrade WITH images) → [5] listing confirmation. The 18:20 version only did the legacy push — fixtures would never have picked up the v2 files. SUPERSEDES the earlier [OPEN → David] line above.
- [OPEN → David] TWO clicks in order: (1) deploy_advertagent_safe.bat FIRST — deploy report on disk is still 27 Jun, so the server lacks the v2-override seeder + 410 glimpse retirement; (2) push_video_reports_v2.bat — pushes the 10 reports and re-seeds fixtures as the real v2 examples.
- [DONE] 2026-07-04 ~19:45 relay 2/4 (overnight resume pass): independent re-verification all-green — 10/10 v2 reports whole, all fenced json parse (heritage 18wp CT first+last, expedition 19wp PTA round trip, options blocks present), zero free-run copy, .bat still at seeder spec. Nothing regenerated, nothing changed. Relays 3-4 need only re-verify.
- [DONE] 2026-07-05 relay 3/4 (final overnight resume pass): 10/10 v2 reports re-verified programmatically — every fenced json parses, heritage 18 waypoints Cape Town first AND last, expedition 19 waypoints Pretoria round trip, exec-selection quartet each carry options+second json block, tails whole, zero free-run/0T copy, push_video_reports_v2.bat still at the 4-step seeder spec. Nothing regenerated, nothing changed. David's two clicks (deploy_advertagent_safe.bat then push_video_reports_v2.bat) remain the only open step.

- [DONE] 2026-07-05 ~02:40 relay 4/4 (report-to-video): pipeline BUILT in AdvertAgent\video_pipeline\ + 10/10 narrated videos produced to video_pipeline\out\ (heritage pilot self-check PASS, then batch; edge-tts en-ZA-LukeNeural, $0, all gates green; MarketSquare\videos\ untouched, nothing deployed). Morning click list in AdvertAgent\MORNING_REPORT_5JUL.md: [1] deploy_advertagent_safe.bat (deploy report still 27 Jun) → [2] push_video_reports_v2.bat → [3] watch heritage pilot, approve, copy mp4s into MarketSquare\videos\ + deploy_marketsquare.bat.

- **⛔ HOLD deploy_marketsquare.bat until video re-render (5 Jul morning):** David rejected the overnight pilot's voice — en-ZA-LukeNeural BANNED FOREVER (enforced in narrate.py code). videos\ state: heritage + collectables RESTORED to originals; the other 8 staged v2 files are Luke-voiced and CANNOT be deleted (FUSE blocks unlink) — a MarketSquare deploy now would push them over the good server copies. Rule: no deploy_marketsquare.bat run until the re-render (David's audition pick: Leah-SA vs Ryan-GB, files in AdvertAgent\video_pipeline\out\) overwrites all 10. Re-render also switches source to ENRICHED live examples (post AA-bat + push-bat re-seed) so videos show the reports' pictures; narration stays SUMMARY-style (David-confirmed). AA bat + push bat remain SAFE to run — different script, no videos.

- **✅ HOLD LIFTED (5 Jul ~08:15): deploy_marketsquare.bat is SAFE again.** All 10 videos in MarketSquare\videos\ are now the Ryan-GB picture-rich re-renders (10/10 md5-verified; Luke-voiced strays overwritten — hazard gone). Deploy ships them + auto-commits the weekend's repo state. Post-deploy QA: watch one video in-app (hard refresh), one real car vision-draft (~$0.01), heritage example shows Kruger v2 + images.

- **VIDEO-POLISH-1 (5 Jul, optional):** the 30-Jun polish layer (crossfades + ambient audio beds, commit b29a71f) is absent from the new narration-over-scroll renders. If David wants it back: assemble.py mixes a quiet ambient bed under the narration + optionally stitches the existing Flow intro clips (e.g. the in-house scene) ahead of the scroll — pure reuse, $0, one pipeline pass. Decide after watching the deployed set.

- **LAUNCH-AUTH-1 (6 Jul 2026, David's ruling — build WITH Paystack integration):** replace the closed-testing spend guard with real user auth: passwordless MAGIC-LINK sign-in on the user's email (Resend sends the link; email ownership = wallet ownership), short-lived session token in the FEA replacing trust-by-typed-email, wallet/spend endpoints require the session, keep is_superuser as the admin/tester layer. Rationale: the app is a wallet of paid-value tokens once Paystack lands — self-declared email is not auth. Interim (live 6 Jul): gates OFF for review + /tuppence/ai-commit 403s non-superusers, so only the 4 family accounts can spend. Post-review decision: re-lock gates or stay open to launch (one-line revert in marketsquare.html).

- **REACH-SHIP-1 (6 Jul, logged not built):** extend the online-mode reach principle (canon §2b) to shippable physical goods via a seller "ships nationwide" toggle (collectors first — cards ship globally). Demand-driven, post-launch; needs the toggle field + honest logistics copy. Physical categories stay tier-gated until then — deliberately, it is the Global $5 tier's value.

### SEARCH-HMI-1 — FEA dial-in surface (Step 1 front-end) · NEXT SESSION on David's approval
Server params live (q/sort/price/trust/make/model/years + facets=1). Build the FEA: debounced search bar → q; facet chips with true counts from facets=1; sort control (smart default); URL/state persistence; infinite scroll on existing pagination; result count always visible. Blueprint: MarketSquare/SEARCH_DIALIN_HMI_DESIGN.docx. DONE early (6 Jul, David-driven): search bar live (phase A) + Enter submit + deterministic sentence interpreter (price/rent-sale/typo-city/stopwords/relaxation). Remaining for the session: facet chips w/ counts (facets=1 wired to UI), URL state, infinite scroll. Steps 2–4 of FILTER_ENGINE_DESIGN (geo window, saved lists+alerts, Tuppence boost) stay staged post-launch.

### DEMAND-LOOP-1 — demand-driven seller acquisition (David's spark, 6 Jul) · POST-PAYSTACK, 1 session
Search-miss → realness score → match against RM-5 prospect pool (1,416/1,326 mx_ok, $0) → coded invite email (launch-code machinery + templates, anonymity-safe wording: item CLASS only, never who/price) → 8h priority countdown (demand_tickets table + sweeps) → on listing, wishlist ping to the requester. Build env-gated OFF with dry-run (zero sends); flip-on = David's gate, naturally with RM-5 un-pause. Groundwork LIVE 6 Jul: wishlist_signals.result_count captures every miss from today. [RISK NOTE] POPIA s69 posture inherited from approved RM-5 outreach. Patent-adjacent to C10–C13 — add a paragraph to the CIPC provisional. Design: MarketSquare/DEMAND_LOOP_DESIGN.docx (rev 2, David-ratified 6 Jul: anonymity + class wording + trigger CONFIRMED; NEW rulings — (1) shared suppression ledger across RM-5 + demand invites, one touch per email address, 90-day cool-down default, permanent on opt-out/bounce; (2) personalization exception: email may name the PROSPECT'S OWN scraped product, never the buyer — content exception only, frequency rule absolute). UPDATE 6 Jul (late): BEA pipeline BUILT + LIVE dark — capture/score/ticket always-on (production ticket #1 verified), matcher/composer/sweep gated (DEMAND_LOOP_ENABLED=0, DRYRUN=1). UPDATE 2 (6 Jul, late): email automation BUILT dark — house-style invite template (preview n8n/email_templates/demand_invite.html) + triple-gated Resend send path + startup RM-5 auto-import/ledger-seed (env DEMAND_RM5_DB). Flip-on now = 4 server envs (DEMAND_RM5_DB, RESEND_API_KEY, DEMAND_LOOP_ENABLED=1, DEMAND_LOOP_DRYRUN=0) + Resend domain verify + launch_codes ungate; remaining BUILD item: listed→wishlist-ping + FEA surface.


## LISTING-QUALITY-1 — per-listing quality score + publish gate (design SETTLED with David, 15 Jul 2026 — build next)
Settled design (do not re-open): deterministic per-LISTING quality score 0-100, computed from countable facts, NO AI call. Rubric v1 (Cars): photos 40 (main exterior 10, each covered slot side/interior/dash/rear/engine 6, cap 40) + Details section confirmed 20 + Condition (mileage + service history + 30-word description) 20 + Performance confirmed 10 + price & suburb 10. Shown LIVE in the sell flow as a meter with recovery hints ('Add an interior photo +6'). Publish gate at 50, enforced SERVER-SIDE in the publish endpoint beside the CARS-SPEC-1 attest gate (409 pattern); below 50 saves as DRAFT with the shortfall itemised — never a hard reject that discards work. Explicit exclusions (David): score never renders on the public advert; never touches trust_score_breakdown / the seller's 40-point base (per-listing, not per-person — David 15 Jul). Ranking: SLIGHT tie-breaker weight only among published listings — must never hide or filter out low-quality listings (David 15 Jul: 'the effect must be very slight not to hide bad ones permanently'). Companion build: Cars guided-flow restructure — real example advert as visual guide (not emoji placeholder), sequenced photo slots (main shot first), spec template as Step 2 pre-filled from vision with per-section confirm (absorbs the attest cards into the flow); backend contract already carries everything (CARS-SPEC-1).


## LISTING-CONSISTENCY-1 — same-item photo-set check (designed 15 Jul 2026, build next)
David's abuse case: a Cars listing with 5 photos of DIFFERENT cars (colours/models), or off-topic photos. Per-photo defence now live (SUBJECT-MATCH-1 notes + MODERATION-1 reject in the anon gate). REMAINING: cross-photo consistency needs ONE multi-image call at publish: send all photo thumbs to Haiku — {"same_item": bool, "category_match": bool, "note": "..."} (~$0.005/listing). V1 WARN-ONLY: publish succeeds, FEA shows "your photos appear to show different vehicles — buyers distrust mixed sets", quality-score flag, ops log. Enforcement (block) only after false-positive rate is known. Wire into PUT /listings/{id}/publish beside the attest gate; skip when <2 photos.


## STRIPE-GLOBAL-1 — SHELVED (David, 16 Jul 2026: 'till we are generating a financial income stream') — international payments entity + Stripe registration
TRIGGERS to unshelve: ZA MRR ~$500/mo sustained, OR real blocked international demand, OR first international city going transactional. Registration lead time is days — nothing is lost by waiting. Original prep below stays current:
Budget already in the model: 'International entity (Stripe)' $1,100 Yr-1. Paystack stays for ZA (live, proven 14 Jul); Stripe serves non-ZA buyers/sellers.
KEY FACTS FOR THE REGISTRATION SESSION:
- Stripe does NOT generally support South African merchant entities — this is WHY the model budgets a foreign entity. Two realistic routes: (a) Stripe Atlas — Delaware C-Corp/LLC, ~$500 once + ~$100/yr registered agent + Delaware franchise tax; bundled EIN + Stripe account + banking intros (Mercury). (b) UK Ltd — ~£50 formation + agent, UK Stripe account; simpler accounting, no US tax filings. VERIFY current terms on the day — both change.
- Needed on the day: passport/ID, entity name choices, business description (marketplace/introductions — note Stripe's marketplace rules may steer toward Stripe Connect), website (trustsquare.co), support email (live), director/shareholder details.
- Watch items: SARB exchange-control implications of a foreign entity owned by a ZA resident (accountant/lawyer question — the Yr-2 accountant line exists); US/UK tax filing obligations (Delaware franchise tax + IRS 5472 even at $0 revenue); Stripe fees ~2.9%+30c vs model's 2.5% processing line (delta is rounding).
- RIDES THE SAME MILESTONE: live forex display (server-side daily cached rate, free feed — decision 15 Jul), multi-currency price lines already locale-gated in TQTY-1 (US shows $ only), Tuppence stays USD-anchored $2 — display converts, price never does.


## MODEL-COST-GUARD-1 — the anti-silent-killer guard (David's standing demand, 16 Jul 2026)
Two rules, institutional: (1) The daily loop computes ACTUAL average $/photo from the spend logs and compares it to AI_PHOTO_COST_MODEL.xlsx's assumption — drift >20% goes in the morning brief as an amber line. (2) ANY change to an AI call site (prompt length, probe size, model, rounds, new call) MUST restate the unit cost in its CHANGELOG entry next to the quality claim — a quality upgrade without its price is an incomplete entry. Context: probe 896->1344 + verify loop + moderation clause moved photos from $4.80 to $13.89/1000 across five days with no budget restatement; David caught it, not the process.
