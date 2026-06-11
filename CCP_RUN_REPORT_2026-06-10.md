# CCP RUN REPORT — 10 June 2026
**Fable unattended run · CC-001 (Tuppence HOLD) + CC-002 (Pricing + AI canon) · steps 0–5 executed STAGED · nothing live, nothing pushed, nothing merged, no live canon overwritten**

---

## 1 · Outcome per change

**CC-001 — Tuppence HOLD.** The commit-on-request → burn-on-delivery → release-on-decline/expiry model (payer = the requester) is staged across every artifact class: 27 staged file edits (app copy, deployed-EULA sources, support FAQ, three AGENT_BRIEFINGs, 18 email templates across two repos), five DRAFT canon/IP/legal docs (Codex v4.8 §12 + table cells; IP Brief v6 with claims C10–C13 and a CPA-s63 position that *improves* under the HOLD; Canon Addendum 2 superseding the published WhitePaper v2 statement without touching it; Strategy addendum; EULA v1.7), and a Gate-2 build spec for the intro ledger (`INTRO_HOLD_BEA_SPEC.md` — mirrors the live AI hold ledger, feature-flagged cutover). Discovery: charge wording existed in **three generations** (deployed charge-on-accept · v1.6-draft charge-at-request · HOLD) — all routed to one canon.

**CC-002 — Pricing + AI canon.** The live app was **already canon** ($0/12/20/40/100 · {6,10,20,50}T · slots 2/10/25/60/500 · packs 410). The drift was documentation and three retired code paths — all staged: 30 file edits (5-tier tables in both deployed-EULA sources + in-app EULA + ms.js mirror + support FAQ + 2 admin upsell cards; AI-uses/sessions retirement across briefings, onboarding copy, 14 outreach templates; a Gate-2 `bea_main.py` diff retiring the `ai_pack_sessions` payment path and registration session-credits — deploy-order-safe, ast-clean) plus `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md` and the Codex v4.8 §11 rewrite. Sequencing honoured: CC-002 staged files are cumulative on CC-001's.

## 2 · Coverage + zero-token proof

| | rows | edited-staged | verified | N-A (reason) | pending (David-gated) |
|---|---|---|---|---|---|
| MATRIX_CC-001.xlsx | 37 | 19 | 0 | 10 | 8 |
| MATRIX_CC-002.xlsx | 35 | 18 | 1 | 9 | 7 |

0 blank cells — every row dispositioned. All "pending" rows are POLICY-§12/Gate territory by design (canon landing, Gate-2 deploys, AD decisions). **Zero-token proof: PASS on both staged sets** — 5 Sensor passes total; mechanically caught: a `–`-escaped EULA sentence in ms.js, pandoc `odd/even` table rows in eula_raw, a second admin upsell card, AA wallet-card titles, and my own proof-pattern false positive ("burned … only upon Seller acceptance" is legitimate new wording — trap documented in the term map). 2 deliberate allowlisted hits = the wishlist-Global $5 SKU (AD-15). Identity-reveal "on acceptance" wording (FICA/anonymity) deliberately untouched — reveal timing ≠ charge timing.

## 3 · Test results
`node --check` staged ms.js (both stages): **clean** · `ast.parse` staged bea_main.py: **clean** (×3 after each patch round) · HTML tail integrity: **pass** (eula_clean/raw are fragments by design; tails byte-identical to originals) · docx round-trips: **clean** · xlsx recalc.py run on both matrices (Resolved-% formula live) · `smoke_test.py`: **N/A-blocked** — it is SSH/server-bound; running it would violate the no-live hard stop. It is the first item in the cutover checklist below.

## 4 · Branch / diff location + rollback
No branch and no commits were made (sandbox git-lock rule; a live `.git/index.lock` was in fact present and not removable from the sandbox — confirming the rule). Staged-files pattern per the brief: **`_CCP_STAGED\`** — `BASELINE_2026-06-10.md` (HEAD `e4c547aa` + sha256 manifest), `CC-001\files+diffs` (27), `CC-002\files+diffs` (30, cumulative), `README.md` (apply order + what must never be applied blind). **Verified at close: every baseline deploy/canon file in the working tree is byte-identical to the baseline manifest.** Rollback today = delete `_CCP_STAGED\` + the `*_DRAFT` files + the two MATRIX files. David may tag: `git tag ccp/CC-001/baseline e4c547aa` + `git tag ccp/CC-002/baseline e4c547aa`.

## 5 · AWAITING DAVID (18 items — full text in `AWAITING_DAVID.md`)
1. **AD-01** BACKLOG-A7's "ready" IP pack (Brief v6 + Provisional Spec) doesn't exist in the tree — desync or external?
2. **AD-02** one HOLD, two release triggers (decline/failure) — confirm unification wording
3. **AD-03** AI coach still direct-charges (first-free → 1T) — migrate to HOLD ledger?
4. **AD-04** land Codex v4.8 (then update v4_7 pointers; MS CLAUDE.md still says v4_5)
5. **AD-05** EULA: which generation goes to counsel (v1.7 HOLD recast recommended)
6. **AD-06** replacement copy for "3 free AI sessions" (staged: "AI listing help is included — in-app guidance is free")
7. **AD-07** confirm daily intro-session limits fully retired
8. **AD-08** Codex §11.2 extra-slot batches — retire or re-price (recommend retire)
9. **AD-09** Codices cost-model variants → `_ARCHIVE`
10. **AD-10** eula_clean/raw provenance (generated?) before applying
11. **AD-11** Claim Visuals needs a C10–C13 panel pre-filing
12. **AD-12** listing durations per 5 tiers ([DAVID] placeholders in v4.8 draft)
13. **AD-13** historical spec docs: leave as records; header-note LISTING_STATE_MACHINE
14. **AD-14** "(reverse-auction = lead)" register note — clarify intended C10 framing
15. **AD-15** wishlist-Global $5 SKU vs tier canon (fold/retire/keep — live Paystack path, untouched)
16. **AD-16** PRINCIPLE_REQUIREMENTS copies diverged (v1.1 ×3 vs v1.2) — v1_3 DRAFT staged as master
17. **AD-17** AdvertAgent_Pricing_Model.xlsx still models retired packs — archive or rebuild
18. **AD-18** tier→reach mapping undefined for 5 tiers (needed by Codex §11 + admin upsell copy)

## 6 · Paste-ready PowerShell (review first — DO NOT run before reading AWAITING_DAVID; commits the run's artifacts only, deploys nothing)
```powershell
cd C:\Users\David\Projects\MarketSquare
if (Test-Path .git\index.lock) { del .git\index.lock }   # stale sandbox-era lock — safe to clear when no git op is running
del ".~lock.MATRIX_CC-001.xlsx#", ".~lock.MATRIX_CC-002.xlsx#" -ErrorAction SilentlyContinue   # LibreOffice junk from recalc
git add -A
git commit -m "CCP run 10 Jun: CC-001+CC-002 staged (matrices, term maps, _CCP_STAGED diffs, DRAFT canon docs, reports) - nothing live"
git push
```
Note: `Solar_Council_Codex_v4_8_DRAFT.docx` + `MarketSquare_EULA_v1_7_DRAFT.docx` are **gitignored** (`*.docx` rule; only `Patents\*.docx` are tracked) — they exist on disk but won't enter the commit. Add `git add -f` lines or a `.gitignore` exception if you want them versioned.

## 7 · Cost model impact
**Cost model impact: none.** HOLD is revenue-timing-neutral (burn at accept = current charge timing; declines were never revenue). CC-002 numbers were already live canon (S129); the MS cost xlsx is Session-90 new-model (verified clean). Only AD-08/AD-15 decisions could move the model — flagged, not changed.

---
### Cutover checklist (when you land it — attended)
1. Verify term maps (Step-2 gate) → 2. land Codex v4.8 / IP v6 / EULA v1.7 (rename from _DRAFT) → 3. apply `_CCP_STAGED` per its README (CC-001 → CC-002) → 4. `smoke_test.py` green pre+post → 5. deploy set + BEA restart + CF purge → 6. build INTRO_HOLD per spec behind `INTRO_HOLD_ENABLED` → 7. n8n-synced template copies refreshed → 8. matrices: flip edited→verified as each surface is live-checked → 9. close CC-001/CC-002 in CHANGE_REGISTER with final coverage %.

*Run log: `PROGRESS_LOG.md` · Detail: `REPORT_CC-001.md`, `REPORT_CC-002.md`*
