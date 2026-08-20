## 2026-08-20 — maintenance-loop (daily B2b session)

- **Fault queue: empty.** Shadow agent run `2026-08-20T05:33:22Z` saw 0 faults
  (mode SHADOW, kill switch OFF as designed — arming is David's act alone).
  Heartbeat confirmed live: `GET /dashboard/maint` returns this run's timestamp
  over plain HTTP (no cookie needed — migration 018 has landed). Register state:
  35 faults total — 26 verified, 7 closed, 2 duplicate, **0 new, 0 fix-shipped**.
- **RG-0090 and RG-0120 promoted OPEN -> LOCKED** — both printed READY TO LOCK on
  the pre-run ledger. RG-0090 (edge-cache leak of the gated document) passes while
  the gate is down per RUL-029; locking it means a future re-arm re-activates the
  assertion instead of quietly losing it. RG-0120 (seller photo order/cover, the
  Maroushka fault) is proven in repo AND live, with the buyer-facing
  `[photos:...]` prefix rewritten by `PUT /listings/{id}`.
  Evidence: `scripts/regression_ledger.py` exit 0 after the change, both entries
  reported `[ ok ]` under LOCKED state.
- **RG-0125 (migration chain jam) diagnosed to the boundary, NOT fixed.**
  `023_relink_wonders_railexp.py` failed on the 05:00:38Z deploy and stranded
  every later migration. Ruled OUT by direct probe: the catalog refuse path (all
  19 HERITAGE-RAIL-1 ids are present in both the repo `wonders.json` and the live
  `GET /wonders`, 319 entries) and the import refuse path (MIGRATE-IMPORT-1 CWD
  guard present; `main`, `database`, `_load_wonders`, `auto_link_wonders`,
  `_derived_radius_km` and the `listing_status` column all exist). Remaining
  candidate is a runtime exception whose text is only on the server. POSTDEPLOY-
  EYES-2 (committed at HEAD, `tee`s each migration's own output into
  `post_deploy_status.json`) will name it on the next deploy — no further guessing
  this session, and DEFERRED.txt was deliberately NOT touched (deferring is
  David's call under DEFER-1).
- Escalation brief: none written — no escalations in the last 24h.
- Ledger: green before and after (exit 0). 4 known defects remain open:
  RG-0075, RG-0101, RG-0121, RG-0125.
