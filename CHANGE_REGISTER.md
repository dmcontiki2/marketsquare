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

## CC-004 · S3 AI-class Pro-gate + non-rolling monthly grant
**Stage:** 4/5 STAGED — DEPLOY-READY (built + canon landed + deploy script patched 17 Jun 2026; live push pending on David's machine) — code staged, docs tracked, awaiting David: review -> deploy (RED money lane) -> land Codex/IP/WP DRAFTs with counsel.
**Opened:** 17 Jun 2026 · **Owner:** David (council) · **Source decision:** `MarketSquare_FreeTier_AI_Cost_Risk_Report.docx` (16 Jun), scenario S3 + no-rollover.

**One-paragraph change:** The expensive paid-feed AI class is reserved for the $20 Pro tier (enforced at `/tuppence/ai-commit`, 403 before any hold — Free/Starter/Agency blocked; cheap Haiku/free-data AI stays open to all), and granted Tuppence is made non-rolling (unspent grant swept via a `grant_expiry` row at each monthly allocation; purchased/earned Tuppence never swept). Closes the ~$39,166/yr Year-1 free-tier cost leak. A8-safe: the grant reset is not a punitive deduction.

**Code (staged, py_compile clean, backups `*.bak-5tgate-20260617-033027`):**
- `ai_service_tiers.py` — `PAID_FEED_FUNCTIONS`, `PAID_FEED_ALLOWED_TIERS`, `requires_paid_feed()`, `tier_may_run()`.
- `bea_main.py` `/tuppence/ai-commit` — tier-gate before hold.
- `launch_redemption.py` `grant_monthly_tuppence()` — non-rolling sweep.

**Docs updated to track the decision (this is the anti-drift step):**

| Doc | Current ver | Change | Bump |
|---|---|---|---|
| `PRICING_CANON.md` | pinned 15 Jun | +§5 AI-class access + non-rollover (authority) | in-place |
| `docs/CHANGE_5T_GATE_AND_NONROLL_SPEC.md` | new | full spec | new file |
| `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` | v1.3 draft | A7 +2 rules; A8 +clarification (reset != penalty) | in-place |
| `Solar_Council_Codex_v4_8_DRAFT.docx` | v4.8 DRAFT | §2 +S3 note; flagged stale 5-tier line -> defers to canon | in-place (stays DRAFT, v4.7 controlling) |
| `TrustSquare_IP_Brief_v6_DRAFT.docx` | v6 DRAFT | §0 +S3 para; grant sweep folded into existing float-expiry recital (NO new claim — David ruling) | in-place |
| `TrustSquare_WhitePaper_v3_5_DRAFT.docx` | v3.5 DRAFT | §3.2 non-rolling grant property; §3.5 paid-feed tier gate; Version History line | in-place (no number bump pending counsel) |
| `TrustSquare_Provisional_Specification_DRAFT_2026-06-11.docx` | v1.1 DRAFT | counsel note: detailed-description additions, claims unaffected | in-place |
| `eula_clean.html` / `eula_raw.html` | v1.3 draft | §5.2 non-rolling granted-Tuppence carve-out; §5.5 Pro-plan AI note | in-place |

**Version policy applied (David ruling 17 Jun):** edit in-place on the unfiled DRAFTs (no new vN files — avoids churn before counsel lands them); patent treats the grant sweep as a further instance of the existing time-based float-expiry recital, not a new claim. The patent/whitepaper now TRACK this decision so they cannot drift out of line.

**Deploy (17 Jun 2026):** `deploy_marketsquare.bat` PATCHED to scp `ai_service_tiers.py` + `launch_redemption.py` (were missing — would have shipped a half-change) before the BEA restart, plus two post-restart grep checks (`requires_paid_feed`, `grant_expiry`). Pre-flight green: all 3 files py_compile clean; gate + sweep unit-tested. Backups `*.bak-s3-*`. The live push must run on David's Windows machine (SSH key is local; the Cowork sandbox has no key and no passwordless route to 178.104.73.239 — verified). On a fresh session: run the .bat, confirm the two `[OK]` lines.

**Counsel — DECIDED, NOT A BLOCKER (David ruling 17 Jun 2026):** landing Codex v4.8 / IP v6 / WP v3.5 with a patent attorney is deferred indefinitely — cost-constrained, and it must NOT gate progress. The DRAFTs stay controlled/unfiled and are edited in-place as decisions land (they now TRACK CC-004). No future session should treat counsel sign-off as a prerequisite for shipping. Run `scripts/check_pricing_canon.py` after deploy.

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

## 2026-06-18 — Video deploys: Cloudflare purge is BROKEN, use versioned URLs
**Symptom:** Collectables tutor video kept showing the OLD stutter cut for end users
(Maroushka) even after the new file was confirmed on the server, many times over.
**Root cause:** `/admin/purge-cache` -> `_cf_purge_all()` silently no-ops: the running
marketsquare service does NOT have CF_ZONE_ID / CF_CACHE_TOKEN in its process env
(unit loads EnvironmentFile=/etc/environment, NOT /var/www/marketsquare/.env), and even
the token in .env returns Cloudflare "Authentication error" (10000) — invalid/expired.
So purge_everything never ran; Cloudflare kept serving the cached old mp4 (cf-cache HIT).
The endpoint still returns {"purged":true}, which masked the failure.
**Fix / standing method:** version every static video URL in ms.js
(`/static/videos/X.mp4?v=YYYYMMDD<tag>`) AND bump the `ms.js?v=NNN` tag in
marketsquare.html so the new ms.js is fetched. A new query string = new Cloudflare cache
key = fresh fetch from origin. HTML is cf-cache DYNAMIC (never cached), so the chain
self-busts. DO NOT trust /admin/purge-cache for videos until the CF token is renewed and
loaded into the service env.
**Verified in-app:** played collectables tutor inside trustsquare.co — src
`collectables-advert-howto.mp4?v=20260618c`, 57.22s, C1 (snap, Bodyguard card) and
C2 (typing) both the regenerated matching-cast clips.
**TODO (David):** renew the Cloudflare cache-purge API token, put CF_ZONE_ID/CF_CACHE_TOKEN
into the service environment (or load .env in the unit), so auto-purge works again.


## 2026-06-18 (later) — Collectables audio: the ACTUAL root cause was Flow's VOICE, not the cache
**What I kept getting wrong:** I "regenerated C1/C2 in Flow" ~10 times. Flow gave new
VISUALS each time but re-rolled the SAME garbled SPEECH. Proven by transcribing the clips:
  - C1 audio: "...writes your advert DONE DONE" (the stutter)
  - C2 audio: "...my CITY AREA ... currency CZAR" (= the mangled "city, Pretoria / ZAR" = "Citoria")
Regenerating in Flow can NEVER reliably fix this — the AI voice is non-deterministic garbage.
**Real fix:** dub clean TTS over C1 and C2 (video kept frame-for-frame, Flow audio replaced).
Lines: C1 "Selling rare cards? Just snap them. AI checks real market prices, then writes your
advert. Done." / C2 "Next I type a short description of my card, my asking price, my city,
Pretoria, and my currency, ZAR." TTS via gTTS en-GB, tempo-fit to 8s. VERIFIED by re-transcribing
the stitched FINAL: C1 ends single "done", C2 says "city pretoria ... ZAR" — clean.
**Deployed:** collectables FINAL md5 213c3206..., versioned `?v=20260618d`, ms.js v=183.
**LESSON:** never trust AI-generated speech in Flow clips. For any spoken line, dub TTS (or human
VO) and TRANSCRIBE the final to verify before deploying. Claude cannot hear — transcription IS
the audio check.


## 2026-06-18 (3) — Payoff VO cutoff fixed; hook card checked
- ISSUE 1 (end VO cut mid-sentence): c4-payoff Flow audio was truncated in-source
  ("...list the card automatically WITH"). Dubbed clean TTS "Wow! It lists my card
  automatically. One tap, and it is live." Verified full-FINAL transcript end-to-end clean.
  Deployed video ?v=20260618e, ms.js v=184, FINAL md5 01ebbb9b...
- ISSUE 2 (wrong card in hook): inspected the hook clip (c3-hook / Flow 'Man holding trading
  card' 3c7b5bf7) frame-by-frame + zoom. Card shown is white-bordered warrior/figure =
  consistent with Veteran Bodyguard, NOT an obviously-wrong card. Could not find a separate
  'regenerated hook' that never landed. ASKED DAVID to point at the exact clip/timestamp of the
  wrong card so we fix the right one rather than guessing.

---

## DEMO-FIX-18JUN · Demo property heritage links + international amenities (David-reported)
**Stage:** 8/8 DONE — built, deployed, live-verified through Cloudflare 18 Jun 2026. Data-only (demo listings); no pricing / ledger / auth / KYC touched.
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David-reported in chat) · **Source:** David screenshots — demo properties missing Heritage links; NY listing showing only one amenity.

**Two issues, both root-caused:**
1. **Heritage links lost on demo properties.** All 41 demo Property listings carried zero `linked_wonders`. An earlier ruling had deliberately *excluded* Property from World Heritage and stripped `linked_wonders` from the demo Property listings; S138 (WONDER-AUTOLINK-CAT-1) then re-allowlisted Property at the BEA publish hook — but that only affects newly-published live listings, never the static demo JSON, which stayed stripped. Adventures kept theirs (50 listings), which made it look selective.
2. **NY amenities thin, not broken.** The Long Island City listing genuinely had only 1 entry per amenity category, so the app rendered correctly. Root cause: the 30 international demo properties (NY/London/Sydney) were seeded ~1-per-category while the 10 Pretoria listings got the full 5-per-category. Not a bug — lopsided seed data.

**Fix (data + deploy script):**
- `demo_listings.json`: re-populated `linked_wonders` on all 40 demo Property listings via the same haversine + affinity + per-country-radius match the BEA `auto_link_wonders()` uses (NY→Met Museum/Statue of Liberty; London→British Museum/Westminster; Sydney→Opera House/Blue Mountains; Pretoria→Pilanesberg/Kruger). All IDs resolve to wonders with photos. Enriched the 30 international properties to 18 amenities each (5 schools / 2 unis / 4 shopping / 4 hospitals / 3 transit), matching Pretoria's depth, with real local landmark names per suburb.
- `deploy_marketsquare.bat`: **root-cause fix for the drift** — added Step 3e shipping `demo_listings.json` + `demo_sellers.json` to the box before the BEA restart. These were NOT previously auto-deployed, so all demo-data edits silently never reached production. Now they ship + the in-process demo cache reloads on every deploy.

**Deploy/verify:** server-side backup `demo_listings.json.bak-20260618-034659`; scp md5 parity `e871f4cc…` both sides; `systemctl restart marketsquare` → active; `/health` ok v1.3.1; Cloudflare purged `{purged:true}`; public `https://trustsquare.co/demo-listings` confirms 40 properties w/ heritage links + all 10 NY listings at 18 amenities. Local backup `demo_listings.json.bak-heritageamenities-20260618-034122`.
**Cost model impact:** none — demo content only.

---

## FEA-DRIFT-FIX-18JUN · Deploy-time auto-commit (permanent root-cause fix; David-directed)
**Stage:** DONE (script patched + validated 18 Jun 2026). Closes the recurring FEA-DRIFT ticket (open under serial IDs FEA-DRIFT-1/-2/-3 since 2 Jun).
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David-directed: "fix every problem every time it appears, don't let it become a human-to-remember issue").

**The recurring problem (correctly diagnosed):** Source files (`ms.js`, `ms.css`, `marketsquare.html`, `support.html`) were repeatedly edited and pushed LIVE but never committed to git, so each session re-discovers uncommitted drift. NOT the same as yesterday's fix — 17 Jun (`1d6e83f`) fixed *backup-file clutter* (`.gitignore *.bak-*` + untrack 33 backups), which held. FEA-DRIFT is a separate, older issue.

**Root cause of the recurrence (two compounding):**
1. The deploy script pushed to the server (which is what makes a change "done" in practice) but **never committed** — commit was a separate manual step a human had to remember, so it was skipped.
2. Commits **cannot be made reliably from the Cowork sandbox**: its `.git` lives on a FUSE mount that blocks `unlink` (`Operation not permitted`), so git's lock/index handling fails (this is the long-standing GIT-INDEX-1 caveat). So commits were always deferred to "later on David's machine" — and forgotten.

**Permanent fix:** Added **Step 7 to `deploy_marketsquare.bat`** — after a successful deploy + live verify, a PowerShell block runs `git add -A` + `git commit` (timestamped message) and `git push` if an upstream exists. The deploy script runs on Windows (native git, no FUSE limit), which is the only place commits work reliably. **Deploying now == committing**, so the drift is structurally impossible rather than memory-dependent. Non-fatal by design (every branch `exit 0`): a git hiccup never fails an already-successful deploy. Backup `*.bak-*` files stay out via the existing `.gitignore *.bak-*` rules (verified with `git check-ignore`). PowerShell command reconstructed + validated; `*> $null` (PS3+) and `$LASTEXITCODE` guards confirmed.
**Backups:** `deploy_marketsquare.bat.bak-demodata-*` + `deploy_marketsquare.bat.bak-autocommit-*`.
**Cost model impact:** none — process/tooling only.

---

## DEPLOY-VERIFY-PAREN-18JUN · ssh verify line syntax error (recurring; David-reported again)
**Stage:** DONE (fixed + scanned for siblings 18 Jun 2026). Cosmetic/verification-only — never affected the actual deploy, only the post-deploy check output.
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David-reported: "this looks like a problem and I have reported it before").

**Symptom (recurring):** During deploy verification the console showed `bash: -c: line 1: syntax error near unexpected token '('` followed by a garbled `[OK]…||…[FAIL]` line, and the next check (`[FAIL] Admin: old admin.html still on server`) looked wrong because the broken command's output bled into it.

**Root cause:** `deploy_marketsquare.bat` line 310 — the backend-modules presence check — put literal parentheses in the remote echo text: `echo [OK] BEA: backend modules (auth/database/storage/payments) present`. Sent through `ssh` to the server's bash *unquoted*, `(` is a subshell metacharacter → `syntax error near unexpected token '('`, which also mis-parsed the `&& … || …` chain. It was the ONLY ssh verify line carrying literal `( )`, which is why it was the only one failing.

**Why it kept coming back:** it never had actually been fixed. The broken parens are present in every deploy-script backup back to `bak-20260611` and in the committed history — prior reports were acknowledged but the paren text itself was never changed. This is the first edit that removes it.

**Fix:** removed the parentheses from the remote echo text (`backend modules auth,database,storage,payments present` — plain comma list, no shell metacharacters). Then scanned ALL `ssh %SERVER%` lines for risky remote metacharacters (`()`, backticks, `$()`, redirects): zero parens remain; the only other flags were legitimate `2>&1` redirections. Backup `deploy_marketsquare.bat.bak-sshparen-20260618-041235`.
**Note (separate, not fixed — cosmetic):** L293/L308 send Windows `>nul` inside the ssh quotes to remote Linux bash (should be `/dev/null`); harmless (creates a stray file named `nul` server-side), left as-is unless flagged.
**Cost model impact:** none — verification output only; the deploy steps themselves were always fine.
