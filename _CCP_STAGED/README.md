# _CCP_STAGED — how to apply (CC-001 → CC-002, in that order)

**Nothing here is live. The working tree's deploy files are untouched.** Staged copies are complete files; `diffs\` show exactly what changed. `BASELINE_2026-06-10.md` holds the rollback anchor (HEAD `e4c547aa` + sha256 manifest).

## Review order
1. `AWAITING_DAVID.md` (18 items) → 2. `REPORT_CC-001.md` + `REPORT_CC-002.md` → 3. the diffs → 4. the five DRAFT docs (Codex v4_8, IP Brief v6, Canon Addendum 2, Strategy C10-13 addendum, EULA v1_7) + `PRINCIPLE_REQUIREMENTS_v1_3_DRAFT.md`.

## Apply (after you approve — PowerShell, from C:\Users\David\Projects\MarketSquare)
**CC-001 first.** Copy each file in `_CCP_STAGED\CC-001\files\` over its original (`__` in names = path separator: `n8n_email_templates__intro_accepted.html` → `n8n\email_templates\intro_accepted.html`; `AdvertAgent__*` / `Codices__*` / `CityLauncher_emailer_templates__*` → those repos).
**Then CC-002** the same way — CC-002 copies of shared files (ms.js, marketsquare.html, marketsquare_admin.html, eula_clean/raw, support.html, AGENT_BRIEFING.md, AdvertAgent briefing) ALREADY CONTAIN the CC-001 edits (cumulative). If you apply both, CC-002's copy of a shared file is the final one. `bea_main.py` (CC-002 only) is **Gate 2** — deploy attended with smoke pre+post.

## What must NOT be applied blind
- `bea_main.py` (Gate 2 — attended deploy + smoke + restart)
- Canon docs: rename `*_DRAFT` only after you land them (Codex v4_8, IP v6, EULA v1_7, Addendum 2, PR v1_3)
- The intro HOLD itself is NOT in any staged file — it's a spec (`CC-001\INTRO_HOLD_BEA_SPEC.md`) for an attended build
- AD-15 wishlist-Global SKU: deliberately untouched

## Deploy note
After applying app files: standard scp set + BEA restart + CF purge per CLAUDE.md; eula_clean/raw provenance check first (AD-10); email templates also need their n8n-synced copies refreshed (class-7 note).
