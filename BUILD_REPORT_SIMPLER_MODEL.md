# Build Report — Simpler Model (attended build · 10 June 2026)
Built attended with David in one Cowork session, against the real spec `MarketSquare_Simpler_Model_Options.docx` (Option A). **Nothing deployed, nothing committed, nothing charged — all reversible (timestamped `.bak` of every edited file).** Code verified syntactically; gated surfaces (pricing/tiers/ledger/EULA/canon) stay staged for David to land.

---

## A · Subscription tiers — DONE & verified
5-tier ($0/12/20/40/100) → **3 tiers + free agency**: Free / Starter / Pro / Agency = **$0 / $5 / $20 / free**, slots **2 / 10 / 30 / trust-graduated**, monthly Tuppence **Free PAYG / Starter 2T / Pro 10T**.
- `marketsquare.html` — PLANS screen rebuilt to the 4 cards; onboarding tier picker (`sob-tier-*`) now Free/Starter/Pro.
- `ms.js` — `_SUB_TIERS` rebuilt; `TIER_IDS` + accent logic; `sobSelTier` list. `node --check` ✓
- `bea_main.py` — `_SELLER_SUB_TIERS` now free/starter/pro/agency (legacy 5 tiers retained + labelled, so existing users don't break); `/subscription/tiers` serves the four; slot backfill knows Pro=30. `ast.parse` ✓
- Visual: `PLANS_PREVIEW.html` (your real `ms.css`).

## B · AI free-glimpse / paid deep-dive, capped 5T — DONE & verified
- `AdvertAgent/service/advert_agent.py` — ladder capped to **Free/2T/3T/5T** (Expedition 10→5, Collection 8→5; Property & Car 5→**3**); distinct prices now {2,3,5}. 8T/10T gone.
- **Free Level-1 glimpse**: `glimpse` field on Property + Car dossiers, new `GET /ai/glimpse/{id}` ($0 · no Tuppence hold · no model call), exposed via `has_glimpse`/`glimpse` in `/ai/functions`. Paid Level-2 = the existing run at 3T (hold/worker path untouched). `ast.parse` ✓

## C · One-photo-one-sentence onboarding — DEMO done
Interactive demo built and shown (photo + one sentence → drafted, **editable** Title / Category / Condition / Suggested price / Description → publish). Meets the demo-done bar (walk the flow, see a drafted listing). Live wiring into the seller-onboarding flow + the real $0-first vision draft endpoint = follow-on.

---

## Files changed (every one has a `*.bak-<timestamp>` beside it)
`marketsquare.html` · `ms.js` · `bea_main.py` (TrustSquare) · `service/advert_agent.py` (AdvertAgent).

## Follow-ons — logged, not blocking
- **FEA chip** to display the free glimpse ("Free Area Snapshot → Investor Dossier · 3T") in the app.
- **Agency trust-graduated cap** logic (base 10 set in the dict; the 10→100→500 graduation function by verification + Trust Score still to add, category-aware).
- **Existing-user migration** map (old Standard/Pro/Business/Elite → Starter/Pro/Agency) — stage, don't run live.
- **Open dials** (doc-flagged): free-L1 scope per feature; $0-first listing/snapshot data source; tier→reach mapping.
- **Doc/canon alignment** (Codex §11, EULA/PLANS copy, AdvertAgent pricing xlsx) — staged, David lands.
- **Launch special** → per-city window + any-paid-plan gate (separate gated build; see `CHANGE_REGISTER` / `project_launch_special`).

## Gates / safety
Everything here is Gate-1 (EULA) / Gate-2 (pricing, tiers, ledger) / §12 (canon) territory → **staged for David, nothing deployed, committed or charged.** Reversible: restore any file from its `.bak`, or discard the edits.

## To save progress (PowerShell — review, then run; deploys nothing)
```
cd C:\Users\David\Projects\MarketSquare
git add -A
git commit -m "Simpler Model build (attended 10 Jun): 3-tier + free agency, AI L1/L2 ladder cap, one-photo onboarding demo — staged, nothing live"
git push
cd C:\Users\David\Projects\AdvertAgent
git add -A
git commit -m "Simpler Model: AI ladder cap Free/2/3/5 + free Level-1 glimpse endpoint — staged"
git push
```
(The `*.bak-*` files can be deleted once you're satisfied.)

**Cost model impact:** subscription prices change ($12/$40/$100 tiers retired → $5 / $20 + free agencies); AI ladder capped at 5T (8T/10T dropped). The revenue bridge for this is already modelled — `MarketSquare_Revenue_Bridge.docx` (Option A, ~+11% at ~2× supply).
