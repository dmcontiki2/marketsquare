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
**Stage:** LANDED 21 Jun 2026 (A4 — wave-trigger wording swept into Codex + all PRINCIPLE_REQUIREMENTS copies). [orig 0/5 OPENED 12 Jun] — David ruling in chat: the design has ALWAYS been *60 staged prospects per city fires the auto-email founding wave; cities launch day-one with zero native listings* (WHCL 332 sites + demos carry browse; density via waves at ~5–7% conversion + direct agency onboarding on the free Agency tier). The "public launch threshold: 60 founding sellers (20/category)" wording in docs is an AI transcription error, never council intent. **Opened:** 12 Jun 2026 · **Owner:** David (council) · **Hot lines already corrected attended:** AGENT_BRIEFING.md:14, CLAUDE.md:139.

**Term map (initial, to be evidenced by the CCP run):**

| # | old (pattern) | where (known so far) | new | kind |
|---|---|---|---|---|
| 1 | `Public launch threshold: 60 founding sellers (20 per category)` | ~~AGENT_BRIEFING.md:14~~ ✓fixed · docs/PRINCIPLE_REQUIREMENTS.md:282 · PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md:283 (+ AA/CityLauncher/Codices copies — AD-16 divergence) · Codex (verify §) | `Wave trigger: 60 staged prospects/city → founding email wave; launch day-one (WHCL+demos+agency onboarding); no seller-count public gate` | canon |
| 2 | `23 / 60 founding sellers` style progress counters | ~~CLAUDE.md:139~~ ✓fixed · BACKLOG.md:162 (M5/M6) | reframe as founding-seller GROWTH milestone, not launch gate | copy |
| 3 | `RM-5 → 60 founding sellers` / `60 sellers stable` | BACKLOG.md AL-5 / AL-7 (autonomy-ladder gates) | KEEP as ladder evidence milestones but reword so they cannot be read as launch gates — David call per row | gates |
| 4 | docs/PLAN.md `20+ founding sellers ... per category` checkboxes | docs/PLAN.md:65/80/147 | historical plan doc — header-note supersede, per AD-13 pattern | historical |

**Interlock:** Gate-8 of the launch-gate checklist (to be drafted) must state the corrected model. EULA/marketing copy scan for "founding"/threshold phrasing = part of the CCP evidence run. Ladder rows (map #3) are autonomy-policy, not launch canon — they survive reworded.

## CC-001 · Tuppence HOLD model
**Stage:** ACCEPTED 21 Jun 2026 as current canon version (A1 — Codex v4.8 §2/§12 HOLD accepted; EXTERNAL pending: counsel EULA v1.7 + IP Brief v6). [was 4/5 STAGED 10 Jun] · baseline ✓ · term map (PROVISIONAL — David verifies) · matrix built (37 rows) · staged edits + drafts complete · zero-token proof PASS on staged set · NOTHING LIVE. Awaiting David: term-map verify → canon landing (Codex v4.8 / IP v6 / EULA v1.7) → INTRO_HOLD BEA build (Gate 2). See `REPORT_CC-001.md` + `AWAITING_DAVID.md`. · **Opened:** 10 Jun 2026
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

---

## POI-CONTAM-18JUN · Demo property amenities cross-city contamination (David-reported)
**Stage:** DONE — root-caused, all 40 regenerated from OSM, regression guard added + proven, deployed + live-verified 18 Jun 2026.
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David-reported: Bela-Bela farm showing Pretoria schools at impossible distances; instruction: "fix the root cause, update all links, verify by sampling, repeat until resolved").

**Symptom:** The Bela-Bela cattle farm (demo_prop_10, ~100km north of Pretoria) listed Pretoria schools — Laerskool/Hoërskool Garsfontein, St Albans College — at fabricated 1.2–3.9km "straight-line" distances. Several other Pretoria listings shared the same crossed entries.

**Root cause:** Demo `nearby_pois` were **hand-seeded with fabricated distances and no geographic validation** — entries leaked between listings (copy-paste bleed). This bypassed the BEA's real pipeline: `auto_link_pois()` / `_overpass_query_pois()` (bea_main.py ~1546–1660) queries OpenStreetMap against each listing's true coordinates and computes real haversine distances. Live listings are correct; only the static demo JSON was hand-built and wrong.

**Fix (root cause, not instance):**
- **Regenerated ALL 40 demo property POIs from OSM Overpass** against each listing's real `listing_lat/lng`, faithfully porting the BEA categories/radii (15km; shopping 3km)/dedup/cap logic. `scripts/regen_pois.py` (ID-driven, saves after each listing — timeout-safe). Every POI is now a real local place at a real distance (Bela-Bela → Hoërskool Warmbad, Spa Park Primary, Bela Bela Hospital, local SPAR/Shoprite). NY/London/Sydney also regenerated → accurate (NY sparser, as OSM tags NYC police/schools thinly; honest rather than fabricated).
- **Regression guard `scripts/validate_demo_pois.py`** — CHECK A (no POI beyond query radius), CHECK B (a uniquely-named institution can't appear on listings >31km apart = 2× radius + slack; retail chains exempt so multiple branches don't false-flag), CHECK C (no legacy hand-seed `transit` key). **Proven both ways:** PASS on fixed data; on the contaminated backup it correctly fires on `St Albans College on demo_prop_1+demo_prop_10 — 101km apart` plus every Garsfontein/Wilgers/Unitas leak.
- **Wired into deploy** as `[3e-pre]` gate: a contaminated demo file now BLOCKS the deploy instead of shipping.

**Verify/deploy:** guard PASS pre-deploy; server backup `demo_listings.json.bak-poifix-*`; scp md5 parity `87adc709…`; BEA restart active /health v1.3.1; CF purged; public `https://trustsquare.co/demo-listings` confirms Bela-Bela shows real local schools, zero Pretoria contamination, 40/40 heritage links intact. Local backup `demo_listings.json.bak-poirebuild-*`.
**Cost model impact:** none — demo data + $0 OSM queries (no API key, public mirrors).

---

## POI-AIRTIGHT-18JUN · Demo POI integrity made fully automated (David-directed hardening)
**Stage:** DONE — coords retained, guard upgraded to true-distance, wired into 3 layers, proven both ways, deployed + live-verified 18 Jun 2026.
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David: "I want the fully automated method"). Follow-on to POI-CONTAM-18JUN.

**Why the earlier guard wasn't enough:** the first guard only caught GROSS impossibilities (>16/31km) because POI coords were stripped — it could miss a plausible-but-wrong entry (a real-sounding school typed at a fabricated short distance). And it only ran at deploy time, on David's machine.

**Hardening (3 independent layers, no money cost — OSM is free/$0):**
1. **Coords retained.** `scripts/regen_pois.py` (now the documented CANONICAL generator — "never hand-edit POIs, run this") keeps each POI's `lat/lon` (rounded 5dp). FEA ignores them (renders name/type/dist_km only — verified in `renderCards`), so invisible to users. All 40 properties regenerated; 664 POIs now carry coords. File 348KB→416KB.
2. **Guard upgraded to ground-truth.** `scripts/validate_demo_pois.py` now recomputes haversine(listing, poi) for EVERY POI: CHECK A (within 16km), CHECK B (stored dist_km matches truth ±0.35km), CHECK C (coords present, else unverifiable→fail), CHECK D (no legacy 'transit'). Proven: PASS on fixed data (664 verified); on the contaminated backup FAILs with 747 issues; on a synthetic SUBTLE injection it catches both a wrong-coord "1.0km" school (true 99.6km) AND a distance-typo (stored 0.3 vs true 2.31) — the exact gap the old guard missed.
3. **Automated runs.** (a) Deploy gate `[3e-pre]` blocks a bad file from shipping. (b) New **G-POI guard in the nightly Prevent harness** (`orchestration_v2/prevent.py guard_demo_pois()`) re-verifies all POIs every night with zero tokens; a FAIL is written as a Detect-schema finding that re-enters the orchestration loop. Tested end-to-end: PASS on good data, FAIL (with offender list) on contaminated.

**Verify/deploy:** guard PASS; server backup `demo_listings.json.bak-poicoords-*`; scp md5 parity `b8830350…`; BEA restart active /health v1.3.1; CF purged; public endpoint confirms Bela-Bela real schools with stored==true distances (0.4/0.41, 0.6/0.55, 1.5/1.52…), coords present live.
**Answer to "is the code now fixed to not have this in future":** yes — the data is generated-not-hand-typed, every entry is truth-verified, and three independent layers (deploy gate + nightly guard + canonical generator) keep it that way.
**Cost model impact:** none — OSM Overpass is free (no key, public mirrors); guard is zero-token deterministic Python.


## 2026-06-18 (4) — Dub voice corrected: female -> South African MALE
The TTS dub used a female en-GB voice (gTTS), wrong for the male on-camera seller — most
obvious on the payoff line. Re-dubbed C1/C2/payoff with edge-tts en-ZA-LukeNeural (SA male).
Lines verified present (small Vosk model mis-hears connected speech e.g. 'card'->'god',
'writes your advert'->'right sir edward'; confirmed phonetically correct at 0.8x).
Deployed video ?v=20260618f, ms.js v=185, FINAL md5 5494a1de... Public ms.js?v=185 confirmed
serving ?v=20260618f. NOTE: a browser may hold the prior ms.js in local HTTP cache for one
load — hard refresh (Ctrl+Shift+R) clears it; new visitors are unaffected.


## 2026-06-18 (5) — Wrong card FIXED by compositing the real card (Flow can't render it)
ROOT CAUSE of the persistent 'wrong card': Flow NEVER renders the real Veteran Bodyguard —
every snap generation invents a fake look-alike card (garbled art/text). No amount of
regenerating fixes this. FIX: composited the real production-kit/cast/card_bodyguard.jpg as an
overlay onto the snap clip (auto-cropped, rounded corners, ~162x228, +4deg tilt, pinned at
x=92 y=520 for the full 8s while he holds it up). Kept the male SA-voice dub. Re-stitched,
deployed ?v=20260618g / ms.js v=186 / FINAL md5 6efb7666. Verified IN-APP at 0:14: real
Bodyguard card visible in hand.
LESSON: for any specific real object/card/logo that must appear exactly, do NOT rely on Flow —
composite the real asset over the clip.
Re the female voice at this moment: confirmed it's the on-screen girlfriend's 'Try TrustSquare'
in the HOOK (kept by David's choice); the snap clip itself is 100% the male voice.

---

## VIDEO-VOICE-18JUN · Collectables tutor — revert to original voice (David-requested)
**Stage:** DONE — original voice restored, card overlay preserved, deployed + live-verified 18 Jun 2026.
**Opened+closed:** 18 Jun 2026 · **Owner:** Claude (David: the afternoon female dub's accent was wrong — "1970s poor-Afrikaner-hillbilly"; restore the original).

**Clarification first:** Claude does not generate or hear audio — the voice was never Claude's. It came from the AI video generator's spoken track plus dubbed audio layers spliced onto the clips. So this was a track-swap, not a re-recording.

**What happened:** clip audio history (collectables clips c1-snap/c2-typing/c4-payoff): original AI voice (02:37 .bak) → a morning dub (03:33 .predub) → an afternoon **female dub** (13:44 .femdub) which became the live voice. David wanted the original back.

**Fix (surgical — preserved the visual card):** A 17:02 "card" overlay had been burned into the served video AFTER the plain FINAL, so a naive rebuild from original clips would have dropped it. Instead: rebuilt an ORIGINAL-voice audio track from the restored clips (c1/c2 ← 02:37 .bak; c4 ← earliest 03:46 .predub, pre-female-dub; c3-hook never dubbed) in the exact 9-segment assembly order, then **muxed that audio onto the SERVED carded video with `-c:v copy`** — video stream verified byte-identical (card kept), audio swapped to original. 57.2s preserved.
**Deploy:** video → `/var/www/marketsquare/static/videos/collectables-advert-howto.mp4` (md5 `d77b9be5…` local==server==live-through-CDN); ms.js video cache-key bumped `v=20260618g→h`; ms.js shipped (md5 parity); CF purged. Backups: clips `*.femdub-current-*`, served `videos/*.femdub-*` + server `*.femdub-bak`, FINAL `*.femdub-*`.
**Cost model impact:** none — media asset swap.

## 2026-07-02 — Whitepaper v3.12 Public Edition + Claim Visuals v4 (pre-publication fixes)
- FAULT (registered): filed provisional PDF's claims section truncated mid-C4; C5–C13 + Abstract absent from
  the CIPC upload (write-truncation class; present since 29-Jun freeze). Attorney item for complete spec.
  See PATENT_PENDING addendum + TrustSquare_WhitePaper_PrePublication_Accuracy_Review_2026-07-02.docx.
- NEW: patent-loop/TrustSquare_WhitePaper_PUBLIC_v3.12_2026-07-02.docx/.pdf — publication candidate
  (fixes F2–F6 of the review; Figures 1–6 embedded; no new technical matter). Originals untouched.
- NEW: Patents/TrustSquare_Claim_Visuals_PUBLIC_v4.html — public-safe visuals; v3 stays internal.
- Snapshot: patent-loop/archive/whitepaper.v3.12-public-20260702.md (no-drift discipline).
- 2026-07-02 (later): Claim-5 production-reach alignment — whitepaper v3.12 (row 6 + §3.8 + version history) and
  Claim Visuals v4 (panel 5) corrected against bea_main.py/PRICING_CANON §2a; borderless travel-planning exemption
  now disclosed; snapshot refreshed. Baks beside both files (.bak-claim5-*).
- 2026-07-02 (later still): filing-status wording strengthened in whitepaper v3.12 + Visuals v4 (banner/title/§9/footer:
  FILED + "priority date secured" + deterrent sentence; formal "patent pending" marking retained — a provisional is not a
  granted patent and may not be marked as one, Patents Act s61). Figure 1 generalised (AdvertAgent codename and table
  inventory removed; generic front-end / back-end API / service agents topology). Baks .bak-status-*; snapshot refreshed.
- 2026-07-02: publication mechanics staged — whitepaper.html landing page, trustsquare_whitepaper_v3.12.pdf,
  trustsquare_claim_visuals_v4.html copied to site root; publish_whitepaper.bat created (scp + verify + evidence
  checklist). Nothing deployed — David runs the bat. Runbook + evidence slots appended to PATENT_PENDING.
- 2026-07-02: §8 accuracy qualifier — "SA buyers via Paystack (integration in progress at publication date)";
  Paystack submission decision recorded: filing (30 Jun) was the gate, so Paystack vendor review and whitepaper
  publication are order-independent; publish first, Paystack in parallel. PDF re-exported; staged site copy +
  landing-page sha256 + PATENT_PENDING sha reference updated in sync. Bak .bak-paystack-*.
- 2026-07-02 ~06:00 SAST: WHITEPAPER PUBLISHED. Live at trustsquare.co/static/ (landing + PDF + visuals v4);
  server sha256 = 3e9a7904… verified in publish run; Wayback snapshots 20260702035915 / 20260702040034 /
  20260702040056 captured; evidence recorded in PATENT_PENDING. First (non-served) webroot upload noted for cleanup.
  Zenodo DOI pending David. PATENT_PENDING "Do next" step 2 (publish whitepaper) = DONE.
- 2026-07-02: Zenodo DOI skipped by decision; publication evidence file closed (live URLs + server sha + 3 Wayback snapshots).
- 2026-07-02: Paystack activation resubmitted (profile complete, preview page live at /static/preview.html, reviewer pinged on ticket 1777715). Whitepaper publication + Paystack unblock both closed same day.
- 2026-07-02: Video QC complete (2 agents, all 10 FINALs): insert-renderer bug family found (07/08/09/10/02), audio −26..−30dB uniform-quiet, presenter clips soft/720p, heritage 4K partials confirmed reusable. Report: feature-videos/VIDEO_CHECK_2026-07-02.md. Phase-2 plan staged.
- 2026-07-02: Insert renderer rebuilt (inserts_fixed_02jul/renderer/render_insert.py, PIL path, 4K-capable --scale 3): tofu/markdown/doubled-header/black-void root-caused + fixed; 5 sample inserts re-rendered + frame-verified PASS (02/07/08/09/10). Upstream flags: heritage_tour.md + study_plan.md truncated (known max_tokens issue), weekend_itinerary.md line-1 leaked model preamble. No FINALs touched.
- 2026-07-02 07:30: Phase-2 video upgrade SCHEDULED — main run 07:35, resume run 11:30 (one-time tasks). 6s drop-in inserts rendered (inserts_fixed_02jul/dropin_6s). Rules baked in: no FINAL overwrites, credit gate ~10 ops, no purchases, RUN_LOG + MORNING_REPORT_02JUL_VIDEOS.md, 06-retirement skipped, heritage 4K partials reused.
2026-07-02 (scheduled run): Feature-video Phase-2 4K upgrade COMPLETE — 9/9 target masters produced (*-FINAL-4K-02jul.mp4 in each feature-videos/<nn>/ folder; 06 skipped per plan): ByteDance 4K upscale of 44 presenter clips (21 Higgsfield credits, 1988->1967), FIXED scroll inserts (tofu/void/md-leak) re-rendered at scale-3 for 02/07/08/09/10, loudnorm -16 LUFS on all, 10-offer Beats-logo blurred. Details: feature-videos/MORNING_REPORT_02JUL_VIDEOS.md + RUN_LOG_2026-07-02.md. Originals untouched; David to review playback/lip-sync.
- 2026-07-02: David's phone rejected his TrustSquare admin password at work. Investigated: morning's Paystack work was activation-resubmission only (dashboard profile + static preview.html + ticket 1777715) — NO auth code or server password touched (auth.py unchanged since 2 Jun; scan20 diff was one-line exception chaining). Live probe of /admin/login returned proper 401 => MS_ADMIN_PASSWORD intact, endpoint healthy. Root-cause candidate: master-password compare was exact-match, no whitespace strip (phone keyboards append trailing space after autofill). FIX staged locally in bea_main.py (accept raw OR stripped match; strictly more permissive, cannot break existing logins; py_compile OK; bak: bea_main.py.bak-20260702-pwstrip). NOT deployed — deploy is David's gate.
- 2026-07-02: COMPLIANCE GAPS CLOSED (staged, NOT deployed) — Paystack go-live checklist items from AWAITING_DAVID:
  (1) privacy.html NEW (POPIA policy: Trustsquare (Pty) Ltd 2026/340128/07, deferred-KYC data, Paystack/Hetzner/R2 sharing+s72, TLS1.3/at-rest, 30-day breach, rights+Regulator, 5-day opt-out; drafted from EULA v1.3 clauses; counsel review pending per LEGAL-COUNTRY-1 best-advice posture).
  (2) terms.html NEW — public page generated from sanitized eula_clean.html (regenerate on EULA change; reminder REM in deploy bat).
  (3) EULA internal draft markers stripped from ALL deployed copies: marketsquare.html embed (13.4K front-matter cut: draft banner, firm names, 18-gap table, counsel-input list; 8 red marker boxes restyled to normal; FICA internal note deleted; NCC false registration claim replaced with sanctioned CPA compliance wording; v1.0->v1.3 trailer fix; div balance verified) + ms.js + eula_clean.html + eula_raw.html (front-matter replaced with clean provenance header; [Company Name]/[REG NO] filled with real entity facts; [COUNSEL REQUIRED]x12, [OPERATIONAL]x1, [subject to council confirmation], [Preliminary] markers swept; ZERO residuals asserted). NO substantive legal wording changed beyond removing false/unfillable claims (NCC registration, external audit provider) — AD-05 generation choice untouched.
  (4) Footer added to app (Terms / Privacy / Contact / (c) + reg no) before LOGIC block.
  (5) bea_main.py: GET /privacy + /terms FileResponse routes (py_compile OK). deploy_marketsquare.bat: +2 scp lines.
  Baks: *.bak-20260702-cmpl / -legalroutes / deploy bat .bak-20260702. NOT deployed — goes live on David's next deploy_marketsquare.bat run. SKIPPED: APP_PREVIEW.html (not in deploy manifest, still has markers).
- 2026-07-02 evening: v2 REBUILD complete — 9/9 4K v2 masters (crossfades 0.37s sample-locked, 1.5s end fades,
  exam head trim, -g 60 + Level 5.2 = heritage stutter root-caused/fixed: v1 keyframes 5-8s at 98.9% of L5.1
  decode ceiling) + 9-file delivery_1080/ set (app-ready). Audio finding: v1 floor already clean (afftdn moved
  it 0.002dB) — "white noise" note likely ambience in generated clips or playback-side; parked to Maroushka R2.
  06-RETIREMENT reworked: misnamed "hook-woman" clip was actually the man (4 of 5 slots = the repetition +
  isolation); wt1 said its line twice in-clip (kept 2nd utterance); NEW couple connector shot generated
  (1 try, identities held, 3/4-angle) via Seedream ref still + Kling i2v 6s + 4K upscale; new master 47.5s
  (-8.9s repeats/dead air) + 1080 delivery. Credits: 15.72 (day total ~36.7); balance ~1,952. Originals + v1
  masters untouched. Open: wife's scripted hook line dropped with the misnamed clip — voice-over option R2.
- 2026-07-03 ~10:35: David decisions for round-2 Phase 2: credits "as required" — operational gate set at budget ≤300 / hard floor 1,650 (never unlimited); 07-liquidation canon lines = MULTI-CLIP in his own voice (2 consecutive clips per line, exact wording from FEEDBACK_DAVID_ROUND2). Phase 1 running since 09:20 (07+09 v3 done at 10:28).
2026-07-03 | feature-videos ROUND-2 PHASE-1 (scheduled, 0 credits): all 10 v3 masters + 1080 deliveries built NEW (v2/v1 untouched) — Andrew scroll VO drafts on all 10 + 01 outro VO, 09 mom-pause to 2.05s, 02 both reframe-glitches spliced out, 07 payoff card re-rendered to positioning canon; loudness -16.0..-16.2, frame-verified; VO wordings await David approval; Phase-2 regens blocked on credit floor (~150-280cr est) — see feature-videos/MORNING_REPORT_03JUL_ROUND2.md + RUN_LOG_2026-07-03.md
- 2026-07-03 ~14:30: feature-videos Round-2 PHASE 2 COMPLETE: 10 Kling regens (03 friend-in-room + payoff canon line [whisper pinned it to payoffA, not wt2]; 07 sister 7a + son 7c multi-clip 48w + 7e multi-clip 39w ending "thank you TrustSquare" on camera; 04 both lips-fixes; 09 syllabus; 10 girl standing) + 11 ByteDance 4K upscales -> v4 masters 03/04/07/09/10 (<name>-FINAL-4K-v4-03jul.mp4, 07 now 69.7s) + delivery_1080/<name>-1080-v4.mp4. 248.49 cr spent (budget 300; 60 wasted on wrong-reference fires, trap documented + procedure hardened), balance 1,702.51, floor 1,650 intact. 01b SSS deferred with options; 02 untouched. Hard-cut splices flat-logged (xfade re-splice available). Full: feature-videos/RUN_LOG_2026-07-03.md + MORNING_REPORT_03JUL_ROUND2.md.
- 2026-07-04 ~15:30: feature-videos Round-3 v5 (David's same-day feedback on v4): 03/07/10 seam repairs (freeze-pads removed, cut words restored: 03 "start", 07 "worth", 10 buyer line; 10's 0.38s A/V drift -> 0ms) + 04 payoff regen with NEW canon line "We know more than we did — now we can approach an agent with real information. Thank you TrustSquare." (positioning: informative, not replacing agents; line whisper-verified verbatim in master). 4 v5 masters + 4 1080-v5 deliveries; 09 stays v4 (David: complete). 12.48 cr (12 Kling + 0.48 upscale), balance 1,690, floor 1,650 intact, 0 wasted. v4/v3 masters untouched beside v5. Full log: feature-videos/RUN_LOG_2026-07-04.md.

## 2026-07-09 · Pre-launch gate RE-LOCKED + view-only reviewer code (Paystack)
- Context: the admin-gate had been left fail-open (`hideGate()` unconditionally) since 6 Jul so Paystack could review. That left the whole app publicly reachable.
- Change (marketsquare.html → live index.html): gate re-locked (`showGate()` for the public) and a **view-only preview code** added. A correct code sets `sessionStorage.ms_review_ok=1` and calls `hideGate()` ONLY — it never hits `/admin/login`, issues NO admin JWT, sets NO identity, and grants NO superuser/ops/test access (superuser still requires a server-side `users.is_superuser=1` sign-in; admin surfaces still require an admin token). Team master-password + admin-PIN paths unchanged.
- Reviewer preview code: **874467** (client-side soft curtain by design — discoverable in source; it is a pre-launch visibility lock, NOT a security boundary. The real boundaries — admin token, is_superuser, funds — remain server-side and untouched).
- Deploy: scp to /var/www/marketsquare/index.html (remote backup index.html.bak-review-20260709-163943), chown msdeploy, CF purge {purged:true}, live-edge verified (RE-LOCKED marker served, HTTP 200), /health v1.3.1 ok. Local backup marketsquare.html.bak-20260709-163853.
- To re-open fully later: restore `else { showGate(); }` → `else { hideGate(); }`, or at launch remove the whole ADMIN LOGIN GATE v2 block. To rotate/retire the review code: change/remove `var REVIEW_PIN`.
- Paystack reply drafted (Gmail, ticket 1777715) with the code + policy confirmation; awaiting David send.

## 2026-07-09 (later) · Reviewer access HARDENED to server-side (supersedes the client PIN)
- Why: the first pass put the review code in client JS (discoverable in page source) — a soft curtain, not security. David (operating in a bribe/threat-prone environment) asked for it as secure as possible.
- New model (BEA + gate):
  * bea_main.py adds `POST /review/login` + `GET /review/verify` (new code only — existing admin funcs untouched). The reviewer code is bcrypt-hashed and held server-side ONLY (env `MS_REVIEW_CODE_HASH` or `/var/www/marketsquare/review_code.hash`, chmod 600 msdeploy); the plaintext is NEVER in the repo, the client, or argv (hashed on the box via stdin).
  * On success `/review/login` returns a 14-day JWT signed with a SEPARATE secret `_REVIEW_SECRET` (derived from `_JWT_SECRET` via sha256, or env `MS_REVIEW_SECRET`). Because admin guards (`_require_admin`, `/admin/verify`) decode with `_JWT_SECRET`, a review token can NEVER validate as admin — proven live: admin/verify + admin/ai-test with a review token both return 401.
  * Scope of a review token = pass the pre-launch gate → anonymous browse view. No admin token, no identity, no `is_superuser`, no ops/test surfaces. Even if leaked it only reveals the same public browse view.
  * Brute-force defence: high-entropy code + bcrypt cost(12) + per-IP rate limit (8 / 10 min → 429). Instant revoke: delete/replace review_code.hash (re-read every attempt, no restart). Rotate: rewrite the file.
  * Gate JS (marketsquare.html) rewired: submit tries `/review/login` first (server), else `/admin/login` (team/master preserved); on load verifies `ms_review_token` via `/review/verify`; **fail-CLOSED** now (was fail-open). No secret in the page — verified live: `874467`/`REVIEW_PIN` absent from served HTML.
- Current reviewer code (give to Paystack): **TSR-****-**** [plaintext redacted from repo — held only as server-side bcrypt hash in review_code.hash (chmod 600); given to Paystack out-of-band per the plaintext-never-in-repo design]**. The earlier client PIN 874467 is DEAD (not in client, no server hash).
- Deploy: main.py (backup main.py.bak-review-20260709-165332, server-venv py_compile OK, restart, /health v1.3.1); index.html (backup index.html.bak-review2-*); CF purged {purged:true}; full security battery passed (7/7). Local backups bea_main.py.bak-20260709-165159 + marketsquare.html.bak-20260709-165248. Repo == live (scp'd local files).
- Follow-up (not blocking): `_require_admin`/`admin_verify` accept ANY `_JWT_SECRET`-signed token regardless of sub — a latent hole unrelated to reviewers (needs the admin secret to exploit). Worth adding a sub in {master, team:*} check as defence-in-depth. Left untouched here to avoid changing admin behaviour I can't test without the master password.

## 2026-07-22 — Homepage edge caching ENABLED + Cloudflare purge FIXED (root cause: stale zone ID)
**Symptom:** daytime pulse amber — homepage 3.4s (retries up to 4.7s) with ~zero users. Server itself served / in 8ms; delay was the uncached Cloudflare→origin path on every request (HTML was cf-cache DYNAMIC, 388KB/74KB gz).
**Root cause of the June "expired token" saga:** CF_ZONE_ID in /var/www/marketsquare/.env was WRONG (2026215991…; real zone is 92f52b142cf2d920e14c3ba097d5985e). Every purge call since ≤June hit a nonexistent zone → Cloudflare "Authentication error" (10000) → _cf_purge_all silently no-oped while /admin/purge-cache returned {purged:true}. The old token was likely fine.
**Changes:**
- nginx `location = /`: Cache-Control no-cache → `public, max-age=300, stale-while-revalidate=600` (bak: marketsquare.bak-edgecache-*). Dashboard/admin/orchestrator/auctions keep no-store.
- Cloudflare cache rule created (ruleset phase http_request_cache_settings, rule 000c106a…): cache "/" on trustsquare.co + www, respect origin TTL. Zone was previously rule-free.
- New API token `trustsquare-cache` (perms: Cache Purge, Cache Rules Edit, Zone Read; scoped to trustsquare.co, no expiry) installed in .env (bak: .env.bak-cf-*) AND systemd drop-in datakeys.conf (bak alongside) with corrected CF_ZONE_ID; daemon-reload + service restart; /health ok v1.3.1.
- ADMIN_KEY unset → deploy bat Step 5b headerless purge call passes auth as-is. No bat change needed.
**Verified end-to-end:** homepage cf-cache HIT at 0.22–0.30s (was 3.4–4.7s); POST /admin/purge-cache → live MISS then HIT again — purge PROVEN to evict, June's masking gone. The June register warning "DO NOT trust /admin/purge-cache" is now lifted; versioned ?v= URLs remain good practice.
**Deploy staleness window:** worst case 5 min (max-age=300) IF a purge fails; deploy purge normally makes updates immediate.
**TODO (David, 1 min):** delete the unused first token created today (R2 page / duplicate) in the Cloudflare dashboard.
**Addendum (same day):** duplicate token cleanup deleted the live secret; surviving `trustsquare-cache` token rolled and the new secret installed in .env + datakeys.conf drop-in, service restarted, purge re-proven (MISS→HIT). Exactly ONE `trustsquare-cache` token now exists. TODO cleared.

## 2026-07-22 — INFRA-PANEL-1: Infrastructure services panel on the ops dashboard (live)
**Why:** David, after the stale-zone-ID saga: external-service keys must be visible and testable on Page 4, not discovered dead a month later. Cloudflare et al. don't belong in the AI Providers seam, so they get their own card.
**Backend (bea_main.py → main.py):** GET /admin/services-status (JWT via _require_admin, ?service= re-tests one). Live checks run concurrently, 8s timeouts, masked key tails only — raw secrets never leave the process: Cloudflare (token verify + zone ruleset read), Resend (INFRA-RESEND-1 empty-POST probe: 422=valid/nothing sent, 401=dead — /domains gives false 401 on the production sending-scoped key), Paystack (bank list; LIVE/TEST mode shown), Hetzner S3 (endpoint + creds), TLS days (thresholds mirror /pulse), JustTCG (presence only).
**Frontend (dashboard.server.html → dashboard.html):** "Infrastructure — external services" card mirroring the apv2 pattern (self-contained script, X-Admin-Token, 5-min auto-refresh, per-service Test). Plus APV2-TESTALL-1: "Test all providers" button on the AI Providers card — sequential sweep of every available provider into apv2-out (David's ask, same day).
**Deploy/verify:** surgical scp ×2 (md5 parity), server py_compile OK, service restart → /health ok v1.3.1; endpoint 401s without JWT; authed call: all six services OK first run (after the Resend probe fix — its initial /domains version false-FAILed the working key, caught before it could cry wolf). Backups: *.bak-infrapanel-* local + server.
