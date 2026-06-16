# TrustSquare Change Register
*Active and closed changes run through the Change-Control Protocol (`CHANGE_CONTROL_PROTOCOL.md`).*
*One CHANGE-ID per big cross-cutting change. The term map here is the mechanical key for that change.*

---

## How to read a ticket
- **Stage** = the current CCP step (0 Freeze → 8 Clean-up).
- **Term map** = the old→new key. ⚠️ A term map marked **DRAFT** has not yet passed **Step 2 verification**
  (David confirms the exact old wording and completeness). **No grep / matrix runs until the term map is
  CONFIRMED** — an incomplete key produces an incomplete sweep, which is the exact failure the CCP prevents.

---

## CC-003 · Launch-threshold canon correction (60 prospects = wave trigger, not 60 sellers = public gate)
**Stage:** 0/5 OPENED (attended, 12 Jun 2026) — David ruling in chat: the design has ALWAYS been *60 staged prospects per city fires the auto-email founding wave; cities launch day-one with zero native listings* (WHCL 332 sites + demos carry browse; density via waves at ~5–7% conversion + direct agency onboarding on the free Agency tier). The "public launch threshold: 60 founding sellers (20/category)" wording in docs is an AI transcription error, never council intent. **Opened:** 12 Jun 2026 · **Owner:** David (council) · **Hot lines already corrected attended:** AGENT_BRIEFING.md:14, CLAUDE.md:139.

**Term map (initial, to be evidenced by the CCP run):**

| # | old (pattern) | where (known so far) | new | kind |
|---|---|---|---|---|
| 1 | `Public launch threshold: 60 founding sellers (20 per category)` | ~~AGENT_BRIEFING.md:14~~ ✓fixed · docs/PRINCIPLE_REQUIREMENTS.md:282 · PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md:283 (+ AA/CityLauncher/Codices copies — AD-16 divergence) · Codex (verify §) | `Wave trigger: 60 staged prospects/city → founding email wave; launch day-one (WHCL+demos+agency onboarding); no seller-count public gate` | canon |
| 2 | `23 / 60 founding sellers` style progress counters | ~~CLAUDE.md:139~~ ✓fixed · BACKLOG.md:162 (M5/M6) | reframe as founding-seller GROWTH milestone, not launch gate | copy |
| 3 | `RM-5 → 60 founding sellers` / `60 sellers stable` | BACKLOG.md AL-5 / AL-7 (autonomy-ladder gates) | KEEP as ladder evidence milestones but reword so they cannot be read as launch gates — David call per row | gates |
| 4 | docs/PLAN.md `20+ founding sellers ... per category` checkboxes | docs/PLAN.md:65/80/147 | historical plan doc — header-note supersede, per AD-13 pattern | historical |

**Interlock:** Gate-8 of the launch-gate checklist (to be drafted) must state the corrected model. EULA/marketing copy scan for "founding"/threshold phrasing = part of the CCP evidence run. Ladder rows (map #3) are autonomy-policy, not launch canon — they survive reworded.

## CC-001 · Tuppence HOLD model
**Stage:** 4/5 STAGED (Fable run 10 Jun) — baseline ✓ · term map evidence-based (PROVISIONAL — David verifies) · matrix built (37 rows) · staged edits + drafts complete · zero-token proof PASS on staged set · NOTHING LIVE. Awaiting David: term-map verify → canon landing (Codex v4.8 / IP v6 / EULA v1.7) → INTRO_HOLD BEA build (Gate 2). See `REPORT_CC-001.md` + `AWAITING_DAVID.md`. · **Opened:** 10 Jun 2026
**One-paragraph change:** The Tuppence charge model is corrected to a **HOLD**:
**commit-on-request → burn-on-delivery → release-on-decline**, with the **payer = the service consumer**
(the party requesting the introduction). Canonicalised in Codex (→ v4.8), IP Brief (→ v6) and the
Provisional Spec, adding patent claims **C10–C13** (reverse-auction = lead). Ref memory
[[project_tuppence_hold_model]].

**Baseline (Step 0):** tag `ccp/CC-001/baseline` before any edit. Snapshot: Codex v4_7, IP Brief v5,
WhitePaper v3_4, Provisional Spec, `bea_main.py`, `payments.py`, EULA draft.

**Term map — EVIDENCE-BASED (Fable run 10 Jun 2026; whole-tree scan, 616 files / 4 repos). Still PROVISIONAL until David verifies (Step 2 gate).** Exact old wording discovered and cited file:line; full hit lists in `MATRIX_CC-001.xlsx` Term Map tab.

| # | old (exact, evidenced) | where (current artifacts only) | new | kind |
|---|---|---|---|---|
| 1 | `1T on acceptance` | ms.js 2719/2778/2990/3700/4607/10964/11030 · Codex tbl4r4 · AA:AGENT_BRIEFING.md 95 | `1T committed on request · burned on delivery` (short UI form) | copy |
| 2 | `1 Tuppence ($2) deducted only on seller acceptance` | ms.js 3703 · marketsquare.html 3870 | `1 Tuppence ($2) is committed (held) when you request — burned only when the introduction is delivered (seller accepts); released back to you if declined or expired` | copy |
| 3 | `Who pays \| Buyer only — on seller acceptance` + `When deducted \| Only after seller accepts introduction request` | Codex v4_7 tbl3r2+r3 | `Who pays \| The requester (the service consumer)` + `Charge model \| HOLD: commit-on-request → burn-on-delivery → release-on-decline` | rule |
| 4 | `Buyer pays only. Charged only after seller explicitly accepts an introduction.` | PRINCIPLE_REQUIREMENTS.md A1 L16 (×4 copies: MS docs/, AA, CL, CX) | `The requester (service consumer) pays — the buyer, for introductions. Tuppence is committed on request, burned on delivery, released on decline/expiry.` | rule |
| 5 | `Only the **buyer** pays, and only **after the seller accepts** the introduction.` | MS:AGENT_BRIEFING.md 27 (CX copy too) | same rule as #4 | rule |
| 6 | `Accept intro · charges 1T` | Codex tbl12r12 · MS:AGENT_BRIEFING.md 144 | `Accept intro · burns the buyer's 1T hold` | copy |
| 7 | `This will charge 1T to the buyer.` | marketsquare_admin.html 3074 | `This burns the buyer's 1T hold (committed at request).` | copy |
| 8 | `charged to the Buyer's balance only upon Seller acceptance … No charge arises on submission, decline` | eula_clean.html 511 / eula_raw.html (deployed EULA v1.4-line) | EULA v1.7 §5 HOLD recast (see `MarketSquare_EULA_v1_7_DRAFT.docx`) | rule |
| 9 | `no Tuppence was deducted (the charge only fires on acceptance)` | eula_clean.html 543+544 | `the 1T hold is released in full — a declined/expired introduction never burns Tuppence` | rule |
| 10 | `1 Tuppence has been deducted from your wallet` | n8n/email_templates/intro_accepted.html 83 (+ CityLauncher copy) | `The 1 Tuppence you committed when you requested this introduction has now been used` | copy |
| 11 | `No Tuppence was charged … introduction fees are only deducted when a seller accepts` | intro_declined.html 80 (+ CL copy) | `Your 1 Tuppence hold has been released back to your wallet` | copy |
| 12 | `credits are not deducted — you only pay when a seller actively confirms` (+2 variants) | support.html 312/370/383 (live FAQ) | commit/release framing, no "refund" word | copy |
| 13 | `pays a small Tuppence introduction fee (1T = USD $2) to request contact` | agency/cars/collectors_dealer/property_outreach.html (×2 repos) | `commits a small Tuppence introduction fee (1T = USD $2) to request contact — it is only used when you accept` | copy |
| 14 | `1T (USD $2) per Introduction request, charged to the Buyer` + Definition `charged at 1 Tuppence, which — if accepted —` | MarketSquare_EULA_v1_6_Draft.docx §5 + Definitions | EULA v1.7 HOLD recast | rule |
| 15 | `$2 per accepted introduction` | IP Brief v5 §1 | `$2 per delivered introduction (HOLD)` in v6 | rule |
| 16 | Codex `v4_7`/`v4.7` pointers | CLAUDE.md ×5 · CHANGE_CONTROL_PROTOCOL §4 · CX:Master_View | `v4.8` — **only after David lands canon** (today: v4_8 DRAFT staged) | version |
| 17 | IP Brief `v5` pointers | Strategy v4 · WhitePaper v3_4 · Claim Visuals v2 · BACKLOG A7 | `v6` — same staging rule | version |
| 18 | claim set ends at C9 (`9 claims`) | IP Brief v5 · Strategy v4 · Pre-Filing UPDATE · WhitePaper v3_4 | add **C10–C13** (drafted in `TrustSquare_IP_Brief_v6_DRAFT.docx`, David/counsel land) | rule |
| 19 | (guard — no old form) refund / deposit framing | everywhere | release-of-hold ≠ refund; never introduce refund/reversal language | rule |

**Term-map deltas vs the original DRAFT (flag per run brief):** charge-timing wording exists in **three generations** — deployed EULA/app/FAQ say *charged on acceptance*; EULA v1_6 draft says *charged at request* (the v5-era CPA fix, never deployed); canon target is the HOLD. Also: WhitePaper v3_4 carries **no** charge-timing sentence (reveal-on-acceptance wording is identity-reveal, NOT charge — left untouched), and IP Brief v5's Claim 2 element "outcome-independent" needs counsel redraft under HOLD (burn is delivery-conditional now) — see v6 DRAFT §2.

**Known hotspots (pre-grep, from memory/CLAUDE.md — NOT the full matrix):** Codex, IP Brief v5→v6,
Provisional Spec, `bea_main.py` ledger path, `payments.py`, EULA §12, `/support` refund FAQ, the public
mechanism copy, the Tuppence-ledger transactional write path (scale-shape invariant #2).
⚠️ **Gates:** almost entirely **Gate 1 + Gate 2 + POLICY §12** — attended, David approves every edit.

**Next action:** David verifies/extends the term map → then Step 3 grep + `MATRIX_CC-001.xlsx`.

---

## CC-002 · Pricing + AI canon
**Stage:** 4/5 STAGED (Fable run 10 Jun) — baseline ✓ · term map evidence-based (PROVISIONAL) · matrix built (35 rows) · staged edits complete incl. Gate-2 `bea_main.py` retired-paths diff · zero-token proof PASS (2 allowlisted AD-15 wishlist-Global hits) · NOTHING LIVE. Sequencing honoured: CC-002 staged files build on CC-001's. See `REPORT_CC-002.md` + `AWAITING_DAVID.md`. · **Opened:** 10 Jun 2026
**One-paragraph change:** "AI uses" / "AI sessions" are **retired**. In-app AI guidance is **FREE**;
advanced AI functions are **Tuppence-priced per use**. Subscription tiers become **$0 / $12 / $20 / $40 /
$100**; the **1T = $2** anchor sets monthly Tuppence allocations at **price ÷ 2 → 6 / 10 / 20 / 50T**; listing
**slots = 2 / 10 / 25 / 60 / 500** are a **CAP** (meter-vs-wallet display rule). Ref memory
[[project_pricing_ai_canon]].

**Baseline (Step 0):** tag `ccp/CC-002/baseline`. Snapshot: Codex v4_7, WhitePaper **v2 (PUBLISHED — do
NOT edit)** + v3_4, AdvertAgent specs + both xlsx, `bea_main.py`, `ai_service_tiers.py`, `tier_resolvers.py`,
`ms.js`, `marketsquare.html` PLANS page, Cost model xlsx.

**Term map — EVIDENCE-BASED (Fable run 10 Jun 2026). Still PROVISIONAL until David verifies (Step 2 gate).** Good news from the scan: the **live app is already canon** (PLANS $0/12/20/40/100 · tup 6/10/20/50 · slots 2/10/25/60/500 — ms.js 1063-66; `TIER_TUPPENCE_MONTHLY` in launch_redemption.py:48; MS cost xlsx is Session-90 new-model; Canon Addendum 1 rev 2 carries the AI canon). The drift is in **docs, EULA surfaces, support FAQ, Codex, three retired-model code paths**.

| # | old (exact, evidenced) | where (current artifacts only) | new | kind |
|---|---|---|---|---|
| 1 | `AI Coach uses` (in "purchase Tuppences or AI Coach uses") | 5 outreach templates ×2 repos (e.g. adventures_accommodation_outreach.html 117) | `Tuppence` only (drop the retired SKU) | concept |
| 2 | `AI Coach Credits … Tiered packs: 5T=40 uses · 10T=100 uses · 25T=320 uses` + `ai_pack_sessions` metadata | MS:AGENT_BRIEFING.md 29 | per-use canon sentence (Addendum 1 r10): in-app AI guidance free; advanced AI Tuppence-priced per use via HOLD | concept |
| 3 | `AI Pack (5T · 40 uses)` | marketsquare.html 3040 | advanced-AI per-use copy | copy |
| 4 | `3 free AI sessions` / `3 free AI sessions credited` / `ai_sessions: 3` | marketsquare.html 2604/2607/2802/2805 · ms.js 4238/4639 · bea_main.py 1205/2610-21 · docs/SELL_FLOW.md | RETIRED concept — replacement copy AWAITING DAVID (AD-06) | concept |
| 5 | `ai_pack_sessions` payment path (initialize/verify/webhook still credit "AI sessions") | bea_main.py 3115/3122/3131/3143-3167/3210-3249 · ms.js 916/661 | retire path (Gate 2 — **staged diff**, not live) | endpoint |
| 6 | `AI sessions remaining` / `Free AI session used` admin panel | marketsquare_admin.html 3783-84 | AI feature credits framing (wallet rule: "not used for introductions") | copy |
| 7 | `POST /payment/initialize?…&ai_pack_sessions=M` · `GET /advert-agent/status` "AA session balance" · `POST /advert-agent/buy-pack` rows | MS:AGENT_BRIEFING.md 146-151 + AA:SESSION_START_PROMPT.md 20/36/39/45 + AA:STATUS.md 100 | document 410-retired + per-use HOLD (`/tuppence/ai-commit`+`ai-settle`) | endpoint |
| 8 | Buyer tiers `Free $0 · 3 sessions/day` / `Starter $5/mo · 20/day` / `Premium $15/mo · 50/day` | Codex tbl9 · PRINCIPLE_REQUIREMENTS.md A7 L55-57 (×4) · eula_clean/raw.html 527-535 · marketsquare.html 2210-2214 · ms.js 11615 (EULA mirror) | RESOLVED 15 Jun — buyer model pinned to live code: Free $0 (local) / Global $5/mo (national+global), two tiers only (`_buyer_tier` → free|global; `WISHLIST_GLOBAL_USD = 5`). The 3-tier $0/$5/$15 "sessions/day" and the "$0/$12/$20/$40/$100" conflation are both retired. Aligned across A7 (×4), eula_clean/raw.html, marketsquare.html, ms.js | number |
| 9 | Seller tiers §11.1 `Free $0 ·2 / Starter $5 (R90) ·20 / Premium $15 (R270) ·50 listings` | Codex v4_7 §11.1 · support.html 343-344 · docs/LISTING_STATE_MACHINE.md · docs/TrustSquare_Architecture_Blueprint_v1.docx tbl5r5 | `Free $0·2 / Starter $5·10 / Pro $20·30 / Agency free·10base [RESOLVED 15 Jun — Simpler Model is current; 5-tier $12/$40/$100 superseded, legacy for existing users only]` — slots are a **CAP** (meter display, not a wallet) | number |
| 10 | `Upgrade to Global · $5/mo` (live button) | marketsquare.html 1120 | `Upgrade · from $12/mo` (staged; David verify microcopy) | copy |
| 11 | `2 Tuppence per batch of 20 extra slots` (§11.2) | Codex v4_7 §11.2 · LISTING_STATE_MACHINE 31/185 · Architecture_Blueprint · SESSION_NOTES ("1T = +20") | **UNRESOLVED — predates 5-tier slot-cap model (Master View flags it). AWAITING DAVID (AD-08)** | rule |
| 12 | stale 3-tier comment `'free' \| 'standard' \| 'professional'` | ms.js 4291 | 5-tier comment | copy |
| 13 | legacy keys `starter`/`premium` | launch_redemption.py 49 `_LEGACY_TIER_MAP` (intentional) · ms.js sob keys (migrated S129) | LEGIT survivor — compat map, keep | name |
| 14 | (anchor) `1T = $2` / allocations `6/10/20/50` / Founders `8/12/24/60` | consistent in all live code + Addendum 1 rev 2 | keep-verify rows (no drift found) | number |
| 15 | `Tuppence charged for AI use is cost-recovery…` | eula_clean/raw 473 · marketsquare.html 2182 · ms.js 11615 · EULA v1_6 | LEGIT under new canon ("per-use cost") — keep, noted | note |
| 16 | WhitePaper v2 `AI uses` + `$5 Standard / $15 International` + pack rates | **PUBLISHED — NEVER edit** | already superseded by Canon_Addendum_1 rev 2 (tbl r10 + allocations note) → N/A-covered | rule |
| 17 | CX:Cost_Breakdown variants (`$5/mo — 5 listings…`) | Codices Cost_Breakdown_GlobalLaunch/MultiCity/Updated.xlsx | superseded historical models → recommend `_ARCHIVE` (AD-09), not edit | number |

**Term-map deltas vs the original DRAFT (flag per run brief):** (a) old buyer-tier numbers were `$0/$5/$15` with **"Introduction sessions per day" 3/20/50** — a second, distinct "sessions" sense the draft didn't list; (b) `bea_main.py` ~3862 credit fn + "ms.js ×4" hotspots turned out **already canon** (S129 shipped them — the real ms.js targets are the legacy pack params + EULA mirror); (c) live PLANS page already shows the five tiers, so CC-002 is mostly a **docs/EULA/FAQ/Codex** sweep plus three retired code paths (rows 4, 5, 7).

**Known hotspots (pre-grep, from memory — NOT the full matrix):** `bea_main.py:~3862` (credit fn),
`ms.js` (×4 spots), `marketsquare.html:~1806` + the **PLANS page** T-numbers, AdvertAgent
`Pricing_Model.xlsx` + `AI_CostModel.xlsx`, `Cost_Breakdown_GlobalLaunch.xlsx`, the 16 email templates,
Codex, `/support` FAQ.
⚠️ **WhitePaper v2 is published defensive disclosure — supersede via Addendum №1 rev 2, NEVER silently
edit** (term map must route any v2 change to the Addendum, not the file).
⚠️ **Gates:** **Gate 2** (pricing/tiers/ledger) throughout + POLICY §12 — attended, David approves.

**Next action:** David verifies/extends the term map → then Step 3 grep + `MATRIX_CC-002.xlsx`.

---

## CC-002 ↔ CC-001 interaction note
Both touch the Codex and the IP/whitepaper line in the same window. Recommend **sequencing, not parallel**:
land **CC-001 (HOLD)** first (it sets the charge *mechanism* the pricing copy refers to), then **CC-002
(pricing/AI)** on top. Decide at Step 1; if run together, the two term map