## 2026-08-18 — WONDERS-CANON-1: the two-catalog fork found and killed (corrects this morning's entry)

- David's deploy landed gzip (verified live: 541 KB catalog travels as 149 KB) but served
  300 sites, not 351 — the repo carried TWO files named wonders.json. Root (300, photo-
  verified schema of 19 Jun, the one the manifest ships) and assets/ (332, older schema,
  NEVER shipped, growing since May — its 32 strays include duplicate sites under second
  ids: Stonehenge, British Museum, the Met). HERITAGE-RAIL-1 merged into the wrong one.
- Fix at class level: root reconciled 300 -> 319 (the 19 approved rail sites only; zero
  changes to the original 300 — verified field-identical). The 32 strays are quarantined
  in assets/wonders_pending_32.json pending a dedupe pass (OPEN follow-up). The fork
  assets/wonders.json is RETIRED by rename (.superseded-20260818). Ledger RG-0102 (LOCKED)
  trips if the fork file ever reappears, if root loses a rail id, or shrinks below 319.
- Migration 023's guard corrected: refuses on missing rail IDS (not a count tied to the
  dead 351 figure). This morning's "332 -> 351" wording described the fork, not the truth:
  the shipped catalog goes 300 -> 319 on the next deploy.
