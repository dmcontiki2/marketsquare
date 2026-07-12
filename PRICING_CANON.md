# TrustSquare — PRICING CANON (single source of truth)

**This file is the one authoritative statement of TrustSquare pricing.** If any other document, draft, or older version disagrees with this file, **this file wins** — fix the other source, never this one. Run `scripts/check_pricing_canon.py` to confirm everything is in line.

_Pinned: 15 Jun 2026 · Owner: David._

---

## The ultimate authority is the running code
This doc mirrors these constants for humans; the **code is the final word**, and the check script verifies the two never drift:

| What | Authority (file -> constant) |
|---|---|
| Seller tiers (price, slots) | `bea_main.py` -> `_SELLER_SUB_TIERS` |
| Seller monthly Tuppence | `launch_redemption.py` -> `TIER_TUPPENCE_MONTHLY` |
| Buyer tier + price | `bea_main.py` -> `_buyer_tier`, `WISHLIST_GLOBAL_USD`, `WISHLIST_GLOBAL_ZAR` |
| Founders Badge minting tier | `launch_redemption.py` -> `QUALIFYING_TIERS` |
| AI paid-feed class + tiers | `ai_service_tiers.py` -> `PAID_FEED_FUNCTIONS`, `PAID_FEED_ALLOWED_TIERS` |

---

## 1 · Seller subscription tiers — the listing-slot axis
| Tier | USD/mo | ZAR/mo | Listing slots | Monthly Tuppence |
|---|---|---|---|---|
| Free | $0 | R0 | 2 | 0 |
| Starter | $5 | R90 | 10 | 2T |
| Pro | $20 | R360 | 30 | 10T |
| Agency | free + verified | R0 | 10 base (grows with Trust Score) | 0 |


## 2 · Buyer subscription tiers — the wishlist/search reach axis
| Tier | USD/mo | ZAR/mo | Reach |
|---|---|---|---|
| Free | $0 | R0 | Local city |
| Global | $5 | R90 | National + global |

Two tiers only (`_buyer_tier` returns `free` | `global`). An earlier per-day “introduction sessions” buyer model was retired — it never existed in code.

### 2a · Trip-planning reach exemption (David, 28 Jun 2026)
**Travel-planning categories are borderless — visible to EVERYONE from ANY city on ANY tier (no city gate, no tier gate).** Rationale: a buyer planning a trip is by definition not local to the destination (a US user planning the Aussie deserts must see those listings), so a local barrier would defeat the Feature. The standard reach in the table above (Free = home city, Global = national+global) applies to **all other** categories.

Exempt categories (raw `l.category` keys): `adventures`, `adventure`, `experiences`, `adventures_experiences`, `accommodation`, `adventures_accommodation`, `tours`, `heritage` — i.e. the whole Adventures/travel family (experiences ≡ adventures) plus Tours and Heritage. Accommodation is **included** (trip lodging is part of planning).

### 2b · Online-mode reach exemption (David, 6 Jul 2026)
**Listings with `mode` Online/Both (tutors + online-capable services) are borderless — visible to EVERYONE from ANY city on ANY tier.** Same principle as 2a: reach follows whether the buyer can USE the thing from where they are — an online chess trainer is as usable from Sydney as from Pretoria. Physical listings are unchanged (Free = home city, Global = everywhere): **the Global tier's value is reach for the physical world.** Future (logged, demand-driven, NOT built): a "ships nationwide" seller toggle could extend the same principle to shippable goods (collectors); until then physical categories stay tier-gated by design.

**Authority:** `bea_main.py` `GET /listings` → Branch D (`include_branch_d`, mode IN online/both; active on the mixed feed + services/tutors requests; GROUP BY id dedupes).

**Authority (2a):** `bea_main.py` `GET /listings` → `TRIP_PLANNING_CATEGORIES` (Branch C unions these from all cities; result deduped `GROUP BY id`). Verified 28 Jun 2026: cross-city trip rows visible to a Pretoria buyer, no duplication, non-travel categories do not leak across cities.

## 3 · Introduction fee (independent of subscription)
**1 Tuppence = USD $2, fixed.** Buyers pay **1T per Introduction** regardless of tier. Subscriptions buy *slots* (sellers) and *reach* (buyers) — never introductions.

## 4 · Founders Badge ("Ruby Spark") — launch special
- Mints **only on the $20 Pro** subscription during the launch window (`QUALIFYING_TIERS = ("pro",)`). **Window posture (David, 6 Jul 2026): activated PER CITY, post-launch, on traction — each city's activation sets its own definitive deadline (the old 2026-08-01 was a placeholder, now removed from all app copy; machinery stays env-gated OFF until activation).**
- Advantage: **+20% Tuppence for life**, rounded up — **Pro 10 -> 12T**. Honoured on any paid plan after minting; survives downgrade/pause.
- One human, one badge; ID-hash bound; never re-minted. Full canon: `Patents/Canon_Addendum_1_FoundersBadge.docx` (rev 3).

## 5 · AI-class access by tier + non-rollover (S3 — adopted 16 Jun 2026, built 17 Jun 2026)
Source decision: `MarketSquare_FreeTier_AI_Cost_Risk_Report.docx`. The expensive **paid-feed AI class** (Sonnet + a contracted/consumption data feed) was leaking ~$3,264/mo (~$39,166/yr at Year-1 scale) when free/granted Tuppence funded it. The fix is **not** to drop monthly Tuppence from the plans (that would breach principle **A8** — Tuppence is purchase/grant only, never removed as a deterrent), but two enforcement rules:

- **Paid-feed class is Pro-only.** A function in the paid-feed class (`ai_service_tiers.PAID_FEED_FUNCTIONS`) may be fired only by **Pro** (plus legacy `professional`/`business`/`elite` for existing users). **Free, Starter and Agency are blocked** with an upgrade message — enforced in code at `/tuppence/ai-commit` *before* any hold is placed, so a blocked call never charges. Cheap (Haiku / free-data / OSM) AI stays **open to everyone** — the conversion hook is preserved. Today all paid feeds are flag-OFF, so the gate is dormant-but-present; it activates automatically when a feed is contracted (B7 sign-off + ceiling still required).
- **Monthly grant is non-rolling.** Granted Tuppence (`monthly_allocation` + `founders_bonus`) does **not** accumulate: at each monthly grant, any *unspent grant* is swept to zero (a single `grant_expiry` ledger row) before the new allocation is credited. **Purchased and earned Tuppence is never swept.** A8-safe — a grant reset, not a penalty.

**Class membership (6 Jul 2026):** 9 of the 10 AdvertAgent research features — `retirement_planner` ADDED (oversight; heaviest profile) and `offer_advisor` REMOVED (David 6 Jul: lightest profile, 2 searches — open to all tiers so Starter's monthly 2T buys one Offer Strategy brief, the $5 tier's monthly ritual) incl. `retirement_planner` (added 6 Jul — it was an oversight; Sonnet + 20 searches is the heaviest profile in the set). FEA presents a violet **PRO** chip on gated features so users see the tier before tapping Run.

**Authority:** `ai_service_tiers.py` -> `PAID_FEED_FUNCTIONS` / `PAID_FEED_ALLOWED_TIERS` / `tier_may_run()`; gate at `bea_main.py` `/tuppence/ai-commit`; sweep at `launch_redemption.py` `grant_monthly_tuppence()`. Spec: `docs/CHANGE_5T_GATE_AND_NONROLL_SPEC.md`. **No price, slot, or monthly-Tuppence values change** — tiers in 1-3 are unchanged.

---

## What DEFERS to this file (keep these in line — never let an old copy win)
Each restates pricing and is **derived**. If one disagrees, fix it to match here:
- `docs/PRINCIPLE_REQUIREMENTS.md` A7 — and its mirrors in `Codices/`, `AdvertAgent/`, `CityLauncher/`
- `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` A7
- `eula_clean.html` / `eula_raw.html` 6.2, and the in-app EULA (`marketsquare.html`, `ms.js`, `APP_PREVIEW.html`)
- `Patents/Canon_Addendum_1_FoundersBadge.docx`
- the 28 outreach templates (`n8n/email_templates/` + `CityLauncher/emailer/templates/`)
- `Codices/CODEX_EVOLUTION_AUDIT.md`, `CHANGE_REGISTER.md`, the Solar Council vision/master-view docs

## Verify before trusting any pricing claim
```
python scripts/check_pricing_canon.py
```
Exit 0 = code <-> canon <-> key docs agree. Non-zero = drift, with the exact mismatch printed.

---

### Retired history (NEVER treat as current)
- Earlier multi-tier seller/buyer subscription models and the per-day “introduction sessions” scheme were **fully retired — no grandfathering** (no existing users carried over).

All superseded by the **Simpler Model (9-10 Jun 2026)** and pinned here on 15 Jun 2026. These appear only in changelogs/timelines/`_CCP_STAGED` as historical record.
