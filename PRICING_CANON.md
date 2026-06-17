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

**Legacy (existing users only — never offered to new sellers):** Standard $12 · Professional $20 · Business $40 · Elite $100.

## 2 · Buyer subscription tiers — the wishlist/search reach axis
| Tier | USD/mo | ZAR/mo | Reach |
|---|---|---|---|
| Free | $0 | R0 | Local city |
| Global | $5 | R90 | National + global |

Two tiers only (`_buyer_tier` returns `free` | `global`). The old 3-tier **$0/$5/$15 "introduction sessions per day"** model is **retired** — it never existed in code.

## 3 · Introduction fee (independent of subscription)
**1 Tuppence = USD $2, fixed.** Buyers pay **1T per Introduction** regardless of tier. Subscriptions buy *slots* (sellers) and *reach* (buyers) — never introductions.

## 4 · Founders Badge ("Ruby Spark") — launch special
- Mints **only on the $20 Pro** subscription during the launch window (`QUALIFYING_TIERS = ("pro",)`; close `LAUNCH_SPECIAL_DEADLINE = 2026-08-01`).
- Advantage: **+20% Tuppence for life**, rounded up — **Pro 10 -> 12T**. Honoured on any paid plan after minting; survives downgrade/pause.
- One human, one badge; ID-hash bound; never re-minted. Full canon: `Patents/Canon_Addendum_1_FoundersBadge.docx` (rev 3).

## 5 · AI-class access by tier + non-rollover (S3 — adopted 16 Jun 2026, built 17 Jun 2026)
Source decision: `MarketSquare_FreeTier_AI_Cost_Risk_Report.docx`. The expensive **paid-feed AI class** (Sonnet + a contracted/consumption data feed) was leaking ~$3,264/mo (~$39,166/yr at Year-1 scale) when free/granted Tuppence funded it. The fix is **not** to drop monthly Tuppence from the plans (that would breach principle **A8** — Tuppence is purchase/grant only, never removed as a deterrent), but two enforcement rules:

- **Paid-feed class is Pro-only.** A function in the paid-feed class (`ai_service_tiers.PAID_FEED_FUNCTIONS`) may be fired only by **Pro** (plus legacy `professional`/`business`/`elite` for existing users). **Free, Starter and Agency are blocked** with an upgrade message — enforced in code at `/tuppence/ai-commit` *before* any hold is placed, so a blocked call never charges. Cheap (Haiku / free-data / OSM) AI stays **open to everyone** — the conversion hook is preserved. Today all paid feeds are flag-OFF, so the gate is dormant-but-present; it activates automatically when a feed is contracted (B7 sign-off + ceiling still required).
- **Monthly grant is non-rolling.** Granted Tuppence (`monthly_allocation` + `founders_bonus`) does **not** accumulate: at each monthly grant, any *unspent grant* is swept to zero (a single `grant_expiry` ledger row) before the new allocation is credited. **Purchased and earned Tuppence is never swept.** A8-safe — a grant reset, not a penalty.

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
- April 2026 buyer 3-tier **$0/$5/$15** + "sessions per day".
- The 5-tier **$0/$12/$20/$40/$100** "one subscription family" (Standard/Professional/Business/Elite).
- Founders Badge on **$40 Business / $100 Elite**.

All superseded by the **Simpler Model (9-10 Jun 2026)** and pinned here on 15 Jun 2026. These appear only in changelogs/timelines/`_CCP_STAGED` as historical record.
