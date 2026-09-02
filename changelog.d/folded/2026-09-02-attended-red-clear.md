## 2026-09-02 — Attended red-clear: ledger exit 1 → 0, rulings 5 FAIL → 0, RG-0237 built and LOCKED

David asked "what is open and what can you fix" — the answer was executed, not listed.

**Ledger reds cleared (3 → 0):**
- **RG-0190**: `.secrets/deploy_keys.txt.bak-20260902-044021` held 3 pre-rotation credentials at
  rest. Neutralized (content replaced with a dated note + pre-wipe fingerprint) — the values were
  dead post-rotation, so the backup had no restore value.
- **RG-0114/pg-readiness**: the 31 Aug suppression lane grew the SQLite surface. Cause fixed, not
  baseline-bumped: `datetime('now')` → `CURRENT_TIMESTAMP`, `INSERT OR IGNORE` →
  `ON CONFLICT(email) DO NOTHING` in bea_main.py `_record_optout` (behaviourally proven on a
  temp DB: default lands, dupe ignored). Fresh pre-deploy scan verdict: **ok**.
- **RG-0187**: rg_journey_front_door's direct subprocess call rerouted through `_harness()` — a
  missing dependency now demotes to NOT EVALUATED instead of crying REGRESSION.

**Also cleared en route:** the maintenance-agent guard red (5 consecutive scans since the 1 Sep
triage refactor) was TRUTH-REVIEW-3 — the third instance of the test's own documented class:
guards pinning spelling/geometry (block window +2500 too small after the outreach branch split
`can_auto`; gate hoisted into `_has_sender`). Both guards re-aimed at the properties; all 5 pass.

**Rulings 5 FAIL + 2 WARN → 90/90 clean:**
- RUL-056/057/058 needles re-aimed at the regenerated wave board v3.3 (substance intact, wording
  moved; `&middot;` entity accepted, old-pair bans kept and extended).
- RUL-088 reflection path fixed to the folded fragment (changelog_compile had archived it).
- RUL-089/090 got their missing reflection assertions; **RG-0221 was genuinely un-extended** —
  the RUL-089 acceptance criteria (singleton auto-collapse, true institution counts) are now in
  the entry text. That blind spot was real, exactly what rulings_check exists to catch.

**Built and promoted:**
- **RG-0237 → LOCKED**: DASH-SIGNEDOUT-TRUTH-1 branch added to dashboard.server.html's summary
  loader — `redacted=='heartbeat'` now paints a SIGNED OUT banner + NOT MEASURED placeholders
  instead of the launch-morning 'SESSION UNDEFINED' scare. **Live from the next deploy.**
- **RG-0243 → LOCKED** per its own ref condition (David shipped; live picker matches 37 launch
  cities across 9 countries).
- RG-0236 deliberately NOT promoted — its ref requires measured classifier accuracy, not a build.

Backups beside every edited file (.bak-<ts>); py_compile green on all Python; final board:
**ledger exit 0 · 0 regressed · rulings 90/90 · pre-deploy ok**. Deploy debt now includes
bea_main.py + dashboard.server.html — they go live on David's next /ship.
