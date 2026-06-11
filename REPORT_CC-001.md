# REPORT — CC-001 · Tuppence HOLD model
**CCP step-7 closeout (staged scope) · 10 June 2026 · Fable unattended run · NOTHING LIVE, NOTHING COMMITTED**

## What changed (all staged, zero working-tree edits to deploy files)
The charge model **commit-on-request → burn-on-delivery → release-on-decline/expiry** (payer = the requester) replaces "charged on seller acceptance" across every artifact class. Charge-timing wording existed in **three generations** (deployed: charge-on-accept · EULA v1.6 draft: charge-at-request · canon target: HOLD) — all routed to the HOLD.

**Staged edits — `_CCP_STAGED\CC-001\files\` (27 files) + `diffs\`:** ms.js (7 copy spots + FAQ label + 4 EULA-mirror sentences incl. a `–`-escape variant the Sensor caught on pass 2) · marketsquare.html (1) · marketsquare_admin.html (accept dialog) · eula_clean.html + eula_raw.html (§5 recast ×4 sentences each) · support.html (4 FAQ answers) · AGENT_BRIEFING.md (MS, CX, AA) · 10 n8n + 8 CityLauncher email templates (intro_accepted/declined deduction wording; "pays…to request" → "commits…" — the sweep caught 4 outreach templates beyond the known set).

**New DRAFT canon/IP/legal docs (never overwrite live):** `Solar_Council_Codex_v4_8_DRAFT.docx` (HOLD cells in §2 tables, endpoint row, new §12 HOLD section, version history; also carries CC-002 §11) · `Patents\TrustSquare_IP_Brief_v6_DRAFT.docx` (claims **C10–C13** drafted; Claim 2 Element-2A redraft flag; CPA s63 position improved by hold-release-on-decline; §1 corrections) · `Patents\Canon_Addendum_2_TuppenceHOLD_DRAFT.docx` (supersedes the published WhitePaper v2 charge-timing statement — v2 itself untouched) · `Patents\TrustSquare_IP_Patent_Strategy_v4_C10-13_Addendum_DRAFT.docx` · `MarketSquare_EULA_v1_7_DRAFT.docx` (§5 + Definitions HOLD recast) · `_CCP_STAGED\CC-001\INTRO_HOLD_BEA_SPEC.md` (Gate-2 code plan — intro ledger mirrors the live AI hold ledger; feature-flagged cutover).

## Coverage (MATRIX_CC-001.xlsx, 37 rows, 0 blank — 100% dispositioned)
18 **edited-staged** · 10 **N-A with reason** (incl. server copies = hard-stop blocked; WhitePaper v2 = published, Addendum routes it; payments.py/smoke/dashboards/memory-class = zero hits) · 9 **pending = David-gated** (Codex/v6 canon landing + pointer updates that must wait for it; intro-HOLD code build; AI-coach decision AD-03; PRINCIPLE_REQUIREMENTS copies after approval; Claim Visuals panel). Strict verified+N-A = 27%; actioned-this-run = 76%; the 24% pending is **all** POLICY-§12/Gate territory by design.

## Zero-token proof
Re-grep of all 15 old-form search terms across the **staged set + 5 DRAFT docs**: **ZERO survivors** (PASS; 2 Sensor passes — pass 1 caught the ms.js escape-variant). Identity-reveal "on acceptance" wording (FICA/anonymity) deliberately untouched — reveal timing is not charge timing. Full term map with false-positive traps: MATRIX Term Map tab + CHANGE_REGISTER.md.

## Tests
`node --check` staged ms.js: **clean**. HTML staged copies: tail-integrity verified (eula_clean/raw are fragments by design — tails byte-identical to originals). Docx drafts: python-docx round-trip **clean**. `smoke_test.py`: **N/A-blocked** — it is SSH/server-bound (`--local` means "on the box"); running it violates the no-SSH hard stop. Verify-at-cutover step listed for David.

## Branch / rollback
No branch/commits (sandbox git lock rule) → staged-files pattern per brief. Baseline anchor: HEAD `e4c547aa` + sha256 manifest in `_CCP_STAGED\BASELINE_2026-06-10.md`; David may tag `ccp/CC-001/baseline e4c547aa`. Rollback today = delete staged folder + DRAFT files (working tree untouched).

## Cost model impact
None — burn timing equals current revenue timing (accept); declines were never revenue; release ≠ refund.

## AWAITING DAVID
AD-01…AD-05, AD-10, AD-11, AD-14 (see `AWAITING_DAVID.md`).
