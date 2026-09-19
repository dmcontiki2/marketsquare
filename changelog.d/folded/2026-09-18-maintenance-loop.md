## 2026-09-18 — maintenance-loop: quiet queue; one ledger red owned by the locked design lane (RG-0253 window artefact)

**Fault queue: empty.** PROBED via /admin/faults: 0 new, 0 triaged, 0 fix-shipped, 0 escalated
(26 verified, 12 closed). No tester fault work this run. Shadow maintenance agent ran foreground
(MS_BEA_URL=https://trustsquare.co): mode SHADOW, phase postlaunch, 0 seen / 0 acted, run cost
$0.0000. Report `.maint_agent/run_20260918T071450Z.json`. Heartbeat PROBED on GET /dashboard/maint:
run=20260918T071448Z (this run), brain NOT_EVALUATED:remote, arming NOT MEASURED (off-box vantage,
RG-0398 wording as designed). Email lane census: 24 total, 6 held in 30d (legal 1, other 5,
spam 1, support 7) — counts only. Escalation brief: no escalations in 24h, no brief written.

**Regression ledger BEFORE (3 shards + combine, 263.8 s): 385 entries · 367 holding · 1 REGRESSED
· 17 open · 0 unverified.** The red is **RG-0253** (first-time seller: register before EULA stamp),
source leg only at that point — the live leg (served ms.js v=685) PASSED.
**AFTER (284.6 s): 386 entries · 368 holding · 1 REGRESSED · 17 open.** Same entry, now red on BOTH
legs: between the two runs the design lane committed HUB-EULA-1 (a051975, RG-0396) and the deploy
ref shipped — live ms.js moved v=685 → v=686 and now carries SEAM-PROOF-1 too. PROBED on the live
v=686: `_sobGoLiveInner` present, register@869 precedes eula@1174 — the property HOLDS live and in
repo; only the assertion cannot see it.

Cause, PROBED in the working tree: the design-review lane's uncommitted **SEAM-PROOF-1** (18 Sep)
wraps `sobGoLive()` around a new `_sobGoLiveInner()` and moves the register→EULA fetch pair into
the inner function, which begins 5,202 chars after the `async function sobGoLive` anchor. The
assertion reads a 6,000-char window from that anchor, so it now finds neither call (`reg@-1
eula@-1`) and reports a regression. Inside `_sobGoLiveInner` the order is intact: register@869
precedes eula@1174. **The property holds; the instrument's window is too short for the new shape.**

Not fixed by this lane, deliberately: `ms.js`, `bea_main.py` and `scripts/regression_ledger.py`
are under the WORK-LOCK-1 stand-off (RUL-140) held by "Fable design-review lane (session 01LTt5)"
since 03:33Z — `work_lock.py check` exit 3, lock 3.7 h old, not stale. Per the lock contract the
finding is recorded here and the owner ships it. What the owner needs to do now (SEAM-PROOF-1 is
already live): re-anchor RG-0253 on `_sobGoLiveInner` (or widen its window past the wrapper) so
the assertion follows the function it polices — until then the board prints "Do not deploy over
this" for a fix that has not rotted, and the nightly TSL gate reads red.

Also on record (not this lane's): the 05:45 nightly TSL was **BLOCKED** — `TSL_READY.flag` reads
"DEPLOY DRIFT: bea_main.py, ms.js local-ahead of live; gate not clean (rc=2)"; the CM gate asked
for the ship to be recorded first (CHANGELOG newest folded entry 2026-09-16; 09-17/09-18 fragments
sit unfolded in changelog.d/, which the deploy compiles).

No file under the lock was touched. No push, no deploy (NIGHTLY-SHIP-1 carries committed work).
