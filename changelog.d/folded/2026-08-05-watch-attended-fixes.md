## 2026-08-05 — WATCH-FIX-1: attended sweep clears the RED (4 fixes + 1 hygiene)

- RG-0023 regression HEALED: fix_support_public.bat (root@ + scp, one-shot from 6 Jul) retired to _to_delete/retired-deploy-bats-20260802/; support.html already in the deploy manifest. Ledger exit 0.
- RG-0030 promoted OPEN -> LOCKED (tester fault channel assertions now guard against rot).
- CLAUDE.md TP-DRIVE-1/RG-0025 paragraphs corrected to post-breach state (DW-014 re-introduction hazard removed).
- run_daily_checks.py seeds its own host key (DW-015 false-unreachable fixed).
- bea_main.py: dead base_score assignment dropped (ruff F841; rides next deploy).
Register: DW-007/011/014/015/017 CLOSED with evidence; 13 items remain open.
