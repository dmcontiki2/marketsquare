# CHANGE — 5T Pro-gate + non-rolling monthly grant (S3)

**Opened:** 17 Jun 2026 · **Owner:** David (council) · **Lane:** RED (money/Tuppence) · **Source decision:** `MarketSquare_FreeTier_AI_Cost_Risk_Report.docx` (16 Jun 2026), scenario **S3 + no-rollover**.

## Why
The Free-Tier AI Cost Risk Report priced the un-recouped exposure when free/granted Tuppence is spent on the expensive paid-feed AI class at **~$3,264/mo (~$39,166/yr)** at Year-1 scale. The decision was **not** to drop monthly Tuppence from the plans (that would breach principle A8 — Tuppence is purchase/grant only, never removed as a deterrent), but to:

1. **Tier-gate the paid-feed class to Pro** (S3) — Free and $5 Starter cannot fire it; only $20 Pro, whose 5T = $10 charge covers Sonnet-plus-feed cost.
2. **Make the monthly grant non-rolling** — reset each period so a free/cheap allowance can never be banked and burst.

Both were logged but never built. This change builds them.

## Decision (locked)
- **Gated class = the paid-feed AI class.** A function is gated when it draws on a contracted/consumption data feed (B7-class). Today all such feeds are flag-OFF, so the gate is dormant-but-present; it activates automatically the moment a feed is contracted. Free-data / Haiku / OSM-Nominatim functions are **never** gated.
- **Allowed tiers for the gated class:** `pro` only (plus legacy `professional`/`business`/`elite` for existing users until migration). `free`, `starter`, `agency` are blocked with a friendly upgrade message.
- **Non-rollover:** before each monthly grant, the unspent portion of the *previous* grant is expired. Purchased Tuppence and earned balances are **never** swept.

## Implementation
1. **`ai_service_tiers.py`** — add `PAID_FEED_FUNCTIONS` set + `PAID_FEED_ALLOWED_TIERS` + `requires_paid_feed()` / `tier_may_run()` (single source of truth for which functions are paid-feed-class). Empty-active today (feeds OFF) but lists the 5T paid-feed candidates so flipping a feed on auto-gates.
2. **`bea_main.py` `/tuppence/ai-commit`** — before the balance check, resolve the caller's `users.seller_tier`; if the function `requires_paid_feed` and tier is not allowed -> **HTTP 403** with upgrade message. The hold is never placed, so no charge and no leak.
3. **`launch_redemption.py` `grant_monthly_tuppence`** — non-rolling sweep, **balance-bounded, grant-spent-first**: `sweep = min(current wallet balance, previous grant's total amount)`. This can never remove more than the user holds (so purchased/earned Tuppence is never touched) nor more than the last grant (so a long-lived account does not drift over many months). Env-gated by the same `TUPPENCE_MONTHLY_ENABLED` flag; idempotent per period.
   - *Revised 17 Jun 2026 (caught in diff review): the first cut used a lifetime-sum formula (`sum(grants) - sum(all AI spend)`) that mis-attributed AI spend funded by purchased Tuppence and drifted over months. Replaced with the balance-bounded rule above; 8 ledger cases now pass incl. purchase-preserved + multi-month-steady.*

## Verify
- Gate: gated function + free/starter/agency -> 403; + pro -> hold placed. Non-gated function + free -> hold placed (cheap AI stays open to free). **PASS.**
- Sweep (8 cases): full-unspent, fully-spent, partial, purchase-preserved, mixed spend, multi-month steady, zero-balance edge, free-tier untouched. **ALL PASS.**
- `py_compile` clean on all three files; backups `*.bak-5tgate-*` / `*.bak-sweepfix-*`.
- `CHANGELOG.md` cost-impact entry; `PRICING_CANON.md` §5; `CHANGE_REGISTER.md` CC-004.

## Canon
`PRICING_CANON.md` §5 is the authority; principle-doc + EULA + Codex/IP/Whitepaper DRAFTs updated to track the decision (CC-004). No price changes — tiers, slots and monthly Tuppence are unchanged.

## Deploy
`deploy_marketsquare.bat` patched to scp `ai_service_tiers.py` + `launch_redemption.py` (were missing) before the BEA restart, with post-restart grep checks. Live push runs on David's machine (SSH key is local). RED lane.
