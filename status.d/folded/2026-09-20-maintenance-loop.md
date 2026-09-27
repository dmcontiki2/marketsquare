### Maintenance loop — 20 Sep 2026 (17:00–17:40Z)

Fault queue empty (0 seen, 0 acted); heartbeat posted and read back from
`/dashboard/maint`; no escalation brief. Live site healthy: `/health` 200,
`/flags` 200, ops gate 401+Basic, `/admin/device-ok` 401.

Three instrument fixes, all the same class — a checker that could not see, convicting
the app anyway. RG-0420 (origin 502 = blind, both in the device-ok leg and generally in
`_get()`); RG-0423 (the RG-0355 judge now reads until the file settles, after a parallel
session writing the same file produced a four-needle phantom red); RG-0417 repointed off
the `marketsquare.html` EULA copy that EULA-FORK-2 correctly deleted, onto `ms.js`'s
`_EULA_HTML` — the text the seller actually ticks. No assertion was weakened; each fix
was proven to still convict its real fault before shipping.

Board ends 412 entries · 388 holding · 22 open · 0 unverified. The two remaining reds are
the parallel lane's uncommitted work (RG-0157 untracked migration 045; RG-0425 Adventures
chip awaiting deploy) — left alone.

NOTE FOR THE NEXT SESSION: two sessions were writing this repo at the same time this
evening. `scripts/regression_ledger.py` changes made here were swept into commit a776d96
by the other lane before this run could commit them. Nothing was lost, but the
CHANGELOG-COLLISION-1 hazard now demonstrably reaches `.py` files, not just `.md` — read
before writing, and prefer a settled read when verifying.
