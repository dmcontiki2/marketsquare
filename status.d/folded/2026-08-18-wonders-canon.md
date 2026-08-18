## 2026-08-18 — Heritage catalog: canon fixed, one deploy click pending
- Root wonders.json 300 -> 319 staged (WONDERS-CANON-1; fork retired; RG-0102 LOCKED).
  gzip already live. On David's next deploy: 319 serves, migration 023 relinks, then
  promote RG-0101. Follow-ups open: dedupe assets/wonders_pending_32.json; tester-intake
  DANGER on 17 orchestration_v2 pages (blocking nightly strict gate since 17 Aug).
