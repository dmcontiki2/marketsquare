# AWAITING DAVID — CCP Run 2026-06-10 (CC-001 + CC-002)

Items requiring David's decision, approval, or go-live action. Logged in lieu of asking (unattended run). Each item: file, exact question/action, recommended answer, what was done meanwhile.

Format: `AD-NN · [CC-00X] · file · question · recommendation · interim action`

---
(populated during the run)
**AD-01 · [CC-001] · Patents\ + BACKLOG.md A7** — BACKLOG A7 says the CIPC self-file pack is "thrice-checked ready (IP Brief v6 · Patent Strategy v4 · Provisional Spec, claims C1–C13)". **No IP Brief v6 and no Provisional Spec file exists anywhere in the tree** (searched all 4 repos, Records\, company\, docs\). Question: does the pack live outside the repo (Claude Chat export / iponline draft), or must v6 + Provisional Spec still be written? *Recommendation:* treat A7 as desynced; use today's staged `TrustSquare_IP_Brief_v6_DRAFT` as the v6 starting point. *Meanwhile:* I drafted v6 (staged, never filed) and flagged A7 in the matrix.

**AD-02 · [CC-001] · CHANGE_REGISTER.md term map** — Register's canonical triple is "…release-on-**decline**" (intros); the already-shipped AI ledger + AI_FUNCTIONS_SPEC use "…release-on-**failure**" (AI runs). Question: confirm Codex v4.8 should state ONE HOLD mechanism with two release triggers (decline for introductions, failure for AI delivery) rather than two separate models. *Recommendation:* yes — single mechanism, release = "service not delivered" (decline / failure / 48-h timeout). *Meanwhile:* v4.8 draft + all staged copy written that way, consistently labelled.

**AD-03 · [CC-001] · bea_main.py:3853 (AI coach)** — Legacy seller listing-coach still direct-charges: "mark free use on first call; charge 1T on subsequent calls" — a charge-at-call, not a commit→settle HOLD. Question: must the coach path migrate to the ai-commit/ai-settle HOLD ledger under CC-001, or is first-free+1T direct charge exempt (cheap synchronous Haiku call, delivery≈instant)? *Recommendation:* migrate for canon consistency (failure must never charge), but as a separate gated code task — not bundled into today's doc sweep. *Meanwhile:* listed as pending row in MATRIX_CC-001 class 3; no code change staged.

**AD-04 · [CC-001] · Solar_Council_Codex_v4_8_DRAFT.docx** — Codex amendments are POLICY §12 never-automated. The v4.8 DRAFT (HOLD model cells + new §12 Tuppence HOLD + version-history row) is staged for your review. Action: review → accept → rename to canonical → then update the v4_7 pointers (CLAUDE.md ×5, protocol §4, Master View). Note: MS CLAUDE.md still points at v4_5 — two versions stale regardless of this change.

**AD-05 · [CC-001] · EULA charge wording exists in THREE generations** — deployed eula_clean/raw + app say *charged on acceptance*; `MarketSquare_EULA_v1_6_Draft.docx` says *charged at request* (the IP-Brief-v5-era CPA s63 fix, never deployed); CC-001 canon is the HOLD. Staged: `MarketSquare_EULA_v1_7_DRAFT.docx` recasting §5/Definitions to commit→burn→release. Counsel flag: the HOLD makes the CPA s63 "buyer receives nothing on decline" concern moot (hold released) — stronger position than v1.6's burn-at-request framing. Your call which generation goes to counsel.

**AD-06 · [CC-002] · "3 free AI sessions credited" onboarding copy (marketsquare.html ×4, ms.js ×2, bea_main ai_sessions credit)** — Sessions are retired; what replaces the signup incentive copy? *Recommendation:* "AI listing help included — in-app guidance is free" (no counted allowance; matches canon). Staged copy uses this; reword if you prefer.

**AD-07 · [CC-002] · buyer daily Introduction-session limits (3/20/50 per day)** — Old buyer tiers had daily intro-session caps. The 5-tier model defines slots+Tuppence but **no daily session limits**, and the live PLANS page shows none. Confirm: limits fully retired (no replacement)? Staged EULA/docs assume retired.

**AD-08 · [CC-002] · Codex §11.2 "2 Tuppence per batch of 20 extra slots"** — predates the 5-tier slot-cap model (Master View already flags it). Options: (a) retire §11.2 (slots purely a tier CAP), (b) re-price batches per tier. *Recommendation:* (a) retire — CAP semantics + upgrade path replace it; Elite 500 covers volume sellers. v4.8 DRAFT marks §11.2 [SUPERSEDED — David confirm].

**AD-09 · [CC-002] · Codices cost variants (Cost_Breakdown_GlobalLaunch/MultiCity/Updated.xlsx in Codices\)** — still carry $5/$15 5-listing models. *Recommendation:* move to `Codices\_ARCHIVE\` as superseded snapshots (don't edit numbers in historical models). Not done this run (cross-repo archive = your call).

**AD-10 · [CC-001/2] · eula_clean.html / eula_raw.html provenance** — these deployed-EULA sources were edited directly (staged). If they're generated from a docx/script pipeline (scripts/tuppence_purge.py touches EULA strings), the pipeline source must be the edit point instead — confirm provenance before applying the staged versions.

**AD-11 · [CC-001] · Patents\Claim_Visuals_Illustrative_v2.html** — needs a C10–C13 panel (HOLD ledger state machine) before filing. Not staged today (visual design work, David-owned per §12). v6 Brief DRAFT contains the claim language to illustrate.

**AD-12 · [CC-002] · listing durations per new tier** — v4.7 §11.1 durations (30/60/120d + fade totals 44/74/134d) are defined for the 3-tier model. Five tiers need five duration values; bea_main slot backfill defines slots only. v4.8 DRAFT carries [DAVID: durations] placeholders pending your numbers.

**AD-13 · [CC-002] · historical spec docs in docs\ (LISTING_STATE_MACHINE, Architecture_Blueprint_v1, SELL_FLOW, SESSION_NOTES, PLAN)** — carry old tiers/sessions as point-in-time records. *Recommendation:* leave as historical (matrix marks them legit-with-note) EXCEPT LISTING_STATE_MACHINE.md which reads as a live reference — flag for a header note "superseded by Codex v4.8 §11" rather than a rewrite.

**AD-14 · [CC-001] · CHANGE_REGISTER "claims C10–C13 (reverse-auction = lead)"** — The parenthetical is ambiguous: no reverse-auction concept exists anywhere in the tree. C10–C13 are drafted in IP Brief v6 DRAFT as the HOLD-ledger claims (C10 lead method + C11 decline-release + C12 dual-trigger + C13 atomic/idempotent enforcement). Question: was "reverse-auction = lead" a different intended C10 framing (e.g., lead-marketplace/reverse-auction distinction)? If so, supply wording — the v6 §1 drafts are placeholders for counsel either way.

**AD-15 · [CC-002] · Wishlist "Global" subscription ($5/month) — marketsquare.html:1120 + bea_main.py:4947-4990 (PR-16/PR-18)** — This is a SEPARATE buyer-side SKU (wishlist global-match tier with its own Paystack flow), not the seller tiers. Question: does the $5 wishlist-Global SKU survive under the 5-tier canon, get re-priced, or fold into a tier? *Recommendation:* fold into Standard+ (any paid plan ⇒ global wishlist matching) and retire the standalone SKU — one subscription family is cleaner and the SKU predates the canon. *Meanwhile:* left untouched in staged files (allowlisted in the proof, 2 hits); do NOT deploy a removal unattended — it's a live Paystack path.

**AD-16 · [CC-001/2] · PRINCIPLE_REQUIREMENTS copies have DIVERGED** — MS docs\ copy is v1.2 (17 May); AdvertAgent, CityLauncher, Codices copies are still v1.1 (12 Apr) — the "replace all copies" regeneration step was missed in May. Staged master: `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` (HOLD A1 + 5-tier A7). After you approve: copy it over all four (the matrix rows track them).

**AD-17 · [CC-002] · AdvertAgent_Pricing_Model.xlsx still models the RETIRED pack economy** ("$2 per 8-use pack", "uses per paid pack", "free uses granted — lifetime"). Question: archive it, or rebuild around per-use HOLD pricing (the AI_FUNCTIONS_SPEC §5 measured economics make a rebuild straightforward)? *Recommendation:* archive to AdvertAgent\_ARCHIVE\ and treat AI_CostModel.xlsx (already per-use, 7 Jun) as the living model. NOTE: AI_CostModel's "packs amortize the R1" cell refers to Tuppence TOP-UP bundles (Paystack fixed-fee amortisation) — different sense, legit, leave.

**AD-18 · [CC-002] · Tier→reach mapping undefined for the 5-tier model** — v4.7 mapped reach Free=local / Starter=country / Premium=global; the 5-tier canon defines slots+Tuppence but no reach column anywhere I can find. bea_main.py:7891 enforces multi-city = paid; staged copy says "paid subscription (from $12/month)" without naming reach per tier. Supply the reach column for Codex v4.8 §11 ([DAVID] placeholders are in the draft).

---

# DAVID'S DECISIONS — 2026-06-28 (logged from session)

> Context discovered this session: the live pricing model is the **Simpler Model** (pinned in `PRICING_CANON.md` 15 Jun 2026) — Sellers Free/Starter $5/Pro $20/Agency; Buyers Free/Global $5. The **five-tier $0/$12/$20/$40/$100 model that CC-002's term map was built around (10 Jun) is RETIRED.** Several decisions below follow from that: items framed around 5 tiers are stale by definition.

**AD-01 — REVIEW NEEDED (David).** David: is the IP-pack desync still valid or overridden by later analysis / just background noise? → ACTION: verify against latest IP work before closing; not auto-closeable. Carried to tomorrow's patents/whitepaper/EULA review.

**AD-02 — RESOLVED.** Confirmed: **Release-on-decline** = the introduction declined by the seller; **Release-on-failure** = AI guidance cannot provide guidance / cannot get info. Principle: **if the AI can't add value, do not subtract tokens.** → Single HOLD mechanism, two release triggers, as staged. Canon wording stands.

**AD-03 — RESOLVED (deferred to gated code task).** Migrate the legacy AI-coach charge path (bea_main.py:3853) to the commit→settle HOLD for consistency, **as a separate gated code task — NOT in the doc sweep.** Logged as a code task; no change staged today.

**AD-04 — DECISION: accept old version as-is.** David: accept the existing/old Codex version as-is (do not require the v4.8 DRAFT rename gate to block). → NOTE: Codex amendments are POLICY §12 (David-only). Recorded as "accept current"; tomorrow's review may revisit alongside patents/EULA.

**AD-05 — DEFERRED to tomorrow.** EULA generation choice folded into tomorrow's patents/whitepaper/EULA review (see AD-11).

**AD-06 — DECISION: remove (replace retired copy).** David's view: old functionality already replaced → remove. ⚠️ VERIFIED THIS SESSION: the "3 free AI sessions" copy is **still live** (marketsquare.html ×4; ms.js still credits ai_sessions:3). So this is a real live-app + code edit, not dead text. → Replacement copy agreed: "AI listing help included — in-app guidance is free." Flagged as a GATED code/app edit (touches live buyer app + credit path) — not applied unattended.

**AD-07 — RESOLVED: fully retired, no replacement.** Buyer daily intro-session limits (3/20/50) are old, already replaced. Verified absent from live front-end. Docs/EULA correctly assume retired. Closed.

**AD-08 — DECISION: remove.** Retire Codex §11.2 "2 Tuppence per batch of 20 extra slots" and all old/historical references already superseded. Slots are purely a tier CAP. (Codex edit itself is §12 David-only; doc-side references cleared.)

**AD-09 — DECISION: remove if already in latest baseline.** Codices cost variants ($5/$15 5-listing models) → archive/remove as superseded; the latest baseline is authoritative. (Cross-repo file moves staged for David's git step.)

**AD-10 — DECISION: remove the staleness.** Agreed — clear the stale EULA-provenance ambiguity; treat deployed eula_clean/raw as the edit point.

**AD-11 — DECISION: use accepted visual if applicable.** If the claim visual is already accepted and still applicable, use it. Patents, whitepaper, and EULA to be reviewed together TOMORROW for any needed changes.

**AD-12 — RESOLVED: not relevant.** "Five durations" is moot — **we no longer have 5 tiers.** Drop the 5-tier duration requirement. Durations follow the Simpler Model tiers only.

**AD-13 — DELEGATED to Claude's judgment.** David: use judgment to make the right calls on these obviously-old relics; do NOT keep them for David to track from memory. → Claude to classify/clear historical docs; LISTING_STATE_MACHINE.md gets a "superseded by current Codex §11" header note.

**AD-14 — CLOSED: not important.** Auctions ("reverse-auction = lead") placed on hold for future design/possible use. Close.

**AD-15 — DECISION: remove.** Wishlist is not yet fully developed → remove the standalone $5 wishlist-Global SKU references. ⚠️ Any LIVE Paystack path removal stays a gated task (not unattended).

**AD-16 — APPROVED.** David approves the latest PRINCIPLE_REQUIREMENTS version. (Canon-pointer check already shows mirrors identical — verify draft vs current before any propagate.)

**AD-17 — DECISION: remove/update.** AdvertAgent_Pricing_Model.xlsx (retired pack economy) → archive and/or update to latest per-use model as required.

**AD-18 — DAVID OWES INFO (boundaries needed).** Tier→reach boundaries have drifted out of clear views over time. David: we DO need to capture the boundaries clearly where they don't exist. → ACTION: Claude to draft the current reach boundaries from live code (`_buyer_tier`, multi-city gate at bea_main.py:7891, PRICING_CANON §2) for David to confirm — NOT invent new ones.

---

# REACH BOUNDARY — Heritage/Experiences exemption (David, 2026-06-28)

**STATUS: design intent — NOT yet in running code (gap pinned so it isn't lost).**

David's rule: the **Features in Heritage, Tours, Experiences, and Adventures are meant to be seen by everyone** — these four categories are "free for all."

**Boundary (confirmed both axes):**
- **City axis:** OVERRIDDEN — listings in these 4 categories are visible across all cities, not limited to the buyer's home city (no `listing_cities` extension needed; they show nationwide/global by category).
- **Tier axis:** OVERRIDDEN — visible to **Free buyers identically to Global** ($5) buyers; no wishlist/reach paywall applies to these categories.
- Net: **Heritage / Tours / Experiences / Adventures = unconditional visibility** (no city gate, no tier gate). All OTHER categories keep the standard reach: Free = home city; Global $5 = national + global.

**Code reality today (verified this session — the gap):**
- `GET /listings` (bea_main.py ~1420) applies the SAME reach to every category — Branch A (home city) + Branch B (extended cities via `listing_cities`). **No category exemption exists.**
- "Heritage" in code = the World Heritage auto-link/badge feature + `heritage_verified` flag — NOT a reach rule.
- `experiences` is folded into "Adventures" for display (ms.js normCat).
- PRICING_CANON.md / canon.yml / requirements: **no Heritage/Experiences reach rule written anywhere.**

**To implement (gated code task — not done unattended):**
1. Add a category-exemption set (e.g. `ALWAYS_VISIBLE_CATEGORIES = {heritage, tours, experiences, adventures}`) checked in `/listings` to bypass the city filter for those categories.
2. Ensure the buyer-tier/wishlist reach gate also skips these categories.
3. Pin the rule in PRICING_CANON.md §2 (buyer reach) + canon.yml as a named exemption, and in Codex §11 reach text.
4. Confirm the exact category KEYS first (normCat folds experiences→Adventures — decide if exemption keys on raw category or normalised family).

**Open sub-question for David (minor):** since `experiences` normalises into the `Adventures` family in the FEA, confirm the exemption keys on the four raw category strings, or on the Adventures display-family as a whole.
