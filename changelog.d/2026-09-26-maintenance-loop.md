## 2026-09-26 — Maintenance loop: RG-0391 assertion corrected, RG-0485 locked

- **RG-0391 (QUICK-READY-6) — assertion corrected, not weakened.** The morning board read one REGRESSION:
  the Quick manifest's start_url is `/quick/` and quick.html links `quick.webmanifest?v=2`. Both were the
  deliberate QUICK-SCOPE-1 change (SEAM-1, 25 Sep; RG-0477 asserts the `/quick/` scope) — the older entry
  still pinned `start_url=/quick.html` and an unstamped link. It now guards what actually keeps an installed
  tile alive: the manifest `id` stays `/quick.html`, start_url sits inside its own scope, any `?v=N` stamp is
  accepted, and the live `/quick/` + `/quick.html` checks stay. Probed live: /quick.html 200, /quick/ 200,
  manifest 200. Correction noted in the entry's ref.
- **RG-0485 (MAP-FIRST-VIEW-1) promoted OPEN -> LOCKED** the run it printed READY TO LOCK.
- Fault queue: 0 new, 0 fix-shipped, 26 verified, 12 closed. Shadow agent saw 0, acted on 0; heartbeat
  probed on /dashboard/maint (run 20260926T054242Z). Backup lane OK (users=123, listings=126), screen walk OK.
- No escalations in the last 24 h (no brief written). Ledger after: every locked fix holding, 19 open.
  Rulings: 148 checked, 0 FAIL.
