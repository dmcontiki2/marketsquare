## 2026-09-20 — maintenance-loop: four false-RED classes closed, one assertion repointed

**Fault queue: empty.** The shadow maintenance agent ran clean against the live site
(`MS_BEA_URL=https://trustsquare.co`, SHADOW, kill switch OFF): 0 faults seen, 0 acted,
report `.maint_agent/run_20260920T170421Z.json`, heartbeat confirmed on
`GET /dashboard/maint` (run `20260920T170419Z`). Email lane census only: 24 total,
6 held in 30d. Escalation brief: none written — no escalations in 24h.

**The whole session's work came from the board, not the queue, and all of it was one
shape: an instrument that could not see, printing a verdict anyway.**

- **UPSTREAM-BLIND-1 (RG-0420, new, LOCKED).** The 17:04Z board printed
  `1 previously-fixed issue HAVE COME BACK. Do not deploy over this` on RG-0342, reason
  `/admin/device-ok answers 502 -- the enrolled-device check is not fail-closed`. An
  immediate re-probe answered 401 with `{"detail":"Not an enrolled device."}`, `/health`
  200, `/dashboard.html` 401+Basic. Nothing had rotted; the app was restarting when that
  leg read it. Two halves fixed: (a) the device-ok leg re-probes a 5xx once and then
  judges it against `/health` — app alive + device-ok 5xx is still a **FAIL**, app not
  answering reads blind; (b) the GENERAL half in `_get()`, added when RG-0001, RG-0004
  and RG-0007 all crashed on `<HTTPError 502>` in the next board while `/health` answered
  200 three times running. `_status()` is deliberately untouched, so every entry asserting
  "this endpoint must not 5xx" still convicts. Proven by forcing all three branches.
- **SELFREAD-DIAG-1 (RG-0423, new, LOCKED).** RG-0355 reported all FOUR of its needles
  missing at once, then judged HOLDING twice minutes later. Four guards do not vanish and
  return together. Cause named, not guessed: this file was being appended to by a parallel
  session mid-run (RG-0421/RG-0422 appeared in it while the shards ran, and this entry's
  own first number collided), and that lane had just shipped **SAFE-READ-1** for a measured
  9%-of-a-file short read through the virtiofs mount. `inspect.getsource()` is not immune —
  it re-reads through linecache. The RG-0355 judge now reads via `safe_read.settled_read`
  (two consecutive agreeing reads) and every FAIL names which read path it used and how
  many characters came back. Nothing softened: all-four-missing still reads REGRESSION.
- **FADE-90-2 (RG-0417 repointed).** The entry convicted `marketsquare.html`'s embedded
  EULA of losing the one-window fade clause. That copy was deleted on purpose hours earlier
  by EULA-FORK-2 (RG-0400) — the acceptance box now renders `ms.js`'s `_EULA_HTML` at
  runtime. The assertion was wrong, not the app: it now reads the clause out of the text
  the seller actually scrolls and ticks. A "has the fourth copy come back?" leg was written
  and then **removed** — it keyed on `marketsquare.html` not mentioning `_EULA_HTML`, which
  the page mentions precisely because the fix landed, so it could never fire. A guard that
  cannot fire is worse than no guard. That property stays RG-0400's.

**Board:** 412 entries · 388 holding · 22 open · 0 unverified. Two reds remain and both
belong to the parallel lane's in-flight work, not to this run: RG-0157 (untracked
`migrations/045_journal_read_for_msdeploy.py`) and RG-0425 (Adventures country chip, their
fix not yet deployed). Not touched, not committed here.

Not deployed and not pushed — the nightly TSL ships committed work through the gates.
