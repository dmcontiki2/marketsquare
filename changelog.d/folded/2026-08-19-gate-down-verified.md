## 19 Aug 2026 — gate lowered on the live box, verified, and the board reconciled

`migrations/026_gate_down.py` applied to `/etc/nginx/sites-enabled/marketsquare`
(backup `marketsquare.bak-gatedown-20260819-041800`). **Verified from outside**, not reported:

- `/review/verify` → `{"valid":true,"scope":"review"}` — the client overlay half is down
- `/listings`, `/wonders`, `/` → 200 anonymously — the server half is down
- `/tuppence/balance`, `/tuppence/history`, `/users/{email}` → **401, app key still required**
- `/dashboard.html` → **401**, still behind its own auth

Lowering the review gate exposed **nothing private**. With the curtain gone, the app-key guards
(RG-0094) are now the only line rather than the second — which is exactly why RG-0029 was
repointed at them.

**Two ledger entries reconciled, neither weakened:**

- **RG-0029** asserted *"the gate ENFORCES at the origin"*. That premise expired by ruling, not by
  rot. Repointed to assert the three things that matter now: private reads still refuse
  anonymously, the dashboard stays shut, and every credential door (reviewer code, email link,
  6-digit code, admin password) is still **in the source, unused rather than deleted** — a lowered
  gate is not a demolished one, and it must stay re-armable.
- **RG-0092** carried a second clause — *"and the gate did not silently widen"* — which would now
  assert the opposite of standing canon. Retired with the reason recorded; it keeps the RUL-020
  legal-docs promise it was written for.

**A collision worth recording.** This session numbered the gate-down entry RG-0112 while a
concurrent session had already committed RG-0112/0113/0114 for the Postgres ratchet. Theirs was
first, so ours moved to **RG-0115**. The duplicate `@entry` silently shadowed a real assertion and
surfaced as a phantom "REGRESSION" against their PG fix — which was intact all along (working tree
verified byte-identical to their commit `08944fe`). Two sessions each taking `max+1` from their own
read of the file will collide; the ledger needs a duplicate-ID guard, logged as a follow-up.

**Board: 108 entries · 100 holding · 0 regressed.** RG-0115 promoted to LOCKED.
