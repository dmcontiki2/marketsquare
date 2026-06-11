# REPORT — CC-002 · Pricing + AI canon
**CCP step-7 closeout (staged scope) · 10 June 2026 · Fable unattended run · NOTHING LIVE, NOTHING COMMITTED**

## Headline
The live app was already canon (PLANS $0/12/20/40/100 · allocations {6,10,20,50} · slots 2/10/25/60/500 · packs 410-gone since S129/Addendum 1 rev 2). CC-002 was therefore a **documentation/EULA/FAQ/Codex sweep plus three retired-model code paths** — all staged. CC-002 staged files build **on top of CC-001's** (apply CC-001 first; every CC-002 diff also exists as `.vs-original`).

## What changed (staged in `_CCP_STAGED\CC-002\`)
**Tier surfaces → 5-tier canon (Free/Standard/Professional/Business/Elite, slots as CAP, monthly Tuppence):** eula_clean.html + eula_raw.html tier tables (raw uses pandoc `odd/even` rows — caught pass 2) · marketsquare.html in-app EULA block + preliminary-pricing note · ms.js EULA mirror (`—`-escape variant) · support.html "three tiers"→five (also fixed R0/$0 inconsistency) · marketsquare_admin.html ×2 city-reach upsell cards ("$5/month · Starter" → "from $12/month · paid plans") · bea_main.py:7891 402-message.

**AI-uses/sessions retirement:** AGENT_BRIEFING.md packs para + 5 endpoint rows · marketsquare.html AI-Pack upsell + "3 free AI sessions" onboarding copy ×4 (AD-06 wording) · ms.js `ai_pack_sessions` send line + `ai_sessions:3` ×2 + stale 3-tier comment + legacy wallet-block title · marketsquare_admin.html session counters → per-use line · 7 outreach templates ×2 repos ("AI Coach uses" dropped) · AA AGENT_BRIEFING + SESSION_START_PROMPT (pack buttons retired; wallet card title → "AI feature credits").

**Gate-2 code (STAGED DIFF ONLY — attended deploy):** `bea_main.py` retires the ai_pack_sessions payment path (initialize metadata + verify + webhook crediting blocks) and the registration-time free-sessions credit; nudge-seed strings updated. `ast.parse` clean; −1,357 bytes; deploy-order safe (pydantic ignores extra fields; FastAPI ignores unknown query params; packs un-buyable since 6 Jun so no in-flight pack payments can exist). Coach billing (first-free → 1T/use via `aa_free_used` + `_deduct_tuppence`) confirmed NOT session-based — retiring credits is internally consistent; `aa_sessions_remaining` column reads remain (harmless zeros; post-launch column-drop noted in diff).

**Docs:** `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` (A1 HOLD + A7 5-tier; discovered the four copies DIVERGED v1.1 vs v1.2 — AD-16) · Codex v4.8 DRAFT §11 rewrite + tbl9 5-tier (shared with CC-001) · memory `project_pricing_ai_canon` created (was referenced but missing).

## Coverage (MATRIX_CC-002.xlsx, 35 rows, 0 blank)
18 **edited-staged** · 1 **verified** (AI_CostModel.xlsx grep-clean) · 9 **N-A with reason** (server blocked; WhitePaper v2 via Addendum 1 rev 2; already-canon code; dashboards zero-hit) · 7 **pending = David-gated**: Codex landing, AD-08 §11.2 batches, AD-09 CX cost variants, AD-15 wishlist-Global SKU, AD-17 AA Pricing_Model.xlsx, AD-16 copy distribution, AD-13 historical docs.

## Zero-token proof
Final Sensor pass over all 30 staged files: **ZERO survivors**; 2 deliberate allowlisted hits = the wishlist-Global $5 SKU (a separate product, AD-15 — David decides; never guess-retire a live Paystack path). Three Sensor passes total (pandoc-variant table, en-dash escapes, second admin card — each caught mechanically).

## Tests
`node --check` ms.js clean · `ast.parse` bea_main.py clean · html tails verified · docx round-trips clean · `smoke_test.py` N/A-blocked (SSH/server-bound — hard stop), listed for cutover.

## Branch / rollback
Same model as CC-001: no commits; baseline HEAD `e4c547aa` (David may tag `ccp/CC-002/baseline`); rollback = delete staged folders + DRAFT files.

## Cost model impact
**Cost model impact:** none new today — pricing values were already live canon (S129); this change aligns documents to them. The MS cost xlsx is Session-90 new-model (verified). If AD-08 retires §11.2 extra-slot batches, remove that revenue line from any model that still carries it (none found in the MS xlsx).

## AWAITING DAVID
AD-06…AD-09, AD-12, AD-13, AD-15…AD-18 (see `AWAITING_DAVID.md`).
