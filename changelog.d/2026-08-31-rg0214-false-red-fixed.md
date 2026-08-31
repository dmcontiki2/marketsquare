## 2026-08-31 — RG-0214's live half re-aimed: the launch-eve red was FALSE, and a leak guard was added

**Third-party launch sweep (T-1 to full launch, RUL-001).** The regression ledger opened the day at
**exit 1** on one red — `RG-0214: deploy report 2026-08-30T17:04:29Z carries no migration-035 step`,
run ending `Do not deploy over this`. A red board refuses a launch-day deploy, so this was the
highest-cost item on the board on the wrong morning.

**The red was false, and the fault was in the assertion, not the world.** RG-0214's live half searched
`/static/post_deploy_status.json` for a step whose *name* contains "035". That report aggregates the
whole post-deploy chain into **one** step — probed live: `seed=ok`, `ladder_seed=ok`, `migrations=ok`.
A per-migration step name has never existed in that format, so the check could only ever go red. The
asserted property was independently PROBED live (today's daily watch, three ways: the `MAP-LIVE-1`
nginx block with both exact-match locations under `auth_basic`; origin `127.0.0.1:8000` serving both
documents 200 at 64,667 B and 110,819 B; 401 anonymous at the edge).

**Fixed under RUL-037 (CTO call), per the never-weaken rule — the correction is written into the
entry's own ref, dated, with the reason.** The live half now asserts:

- the deploy report's migration chain step ran and did not fail, read in the report's **own**
  vocabulary (`migrations`) rather than a name that cannot exist;
- migration 035 still carries the self-proof clauses that make `migrations = ok` mean *proven* —
  both exact-match locations, `auth_basic`, and its "NOT claiming success" refusal path;
- **neither gated document answers 200 anonymously** — a guard the old assertion did not have. The
  information leak this entry exists to prevent is now asserted directly and probed live
  (`/orchestrator/defence_map.html` and `/orchestrator/watch_register.md` both **401**).

`py_compile` green; backup kept beside the file; board re-run **exit 0 · 214 entries · 197 ok ·
16 open · 0 REGRESSED · 0 UNVERIFIED**.

**DW-086 CLOSED the same day.** The daily watch diagnosed it correctly and correctly declined to fix
it (observe-only lane; `scripts/regression_ledger.py` is not a watch-owned path) and named an
attended CTO session as the owner. This was that session.

**Class lesson, carried in prose deliberately and not as a new meta-harness on launch eve:** an
assertion that names evidence which has never existed is a false-red generator, and the evidence
ladder cuts both ways — a *harness* can claim a rot that is not there just as a *file* can claim a
state that is not true. Every mechanical version of "no assertion may check for evidence that cannot
exist" is brittle enough to become a false-red generator itself; building that the night before full
launch trades a known small risk for an unknown one. Named in `THIRD_PARTY_LAUNCH_REGISTER.md`
watch-outs so a calmer session can decide it.

Also recorded: `post_deploy_status.json` aggregates migrations into ONE step (any future assertion
wanting to prove a *specific* migration must prove it another way), and day-name drift in the launch
dates — 29 Aug 2026 was a **Saturday** and 1 Sep 2026 is a **Tuesday**, while the docs say Friday and
Monday. The RUL-001 **dates** stand and are unchanged; RULINGS.md was deliberately not edited,
because amending a ruling's wording is David's call, not Claude's.

Files: `scripts/regression_ledger.py` · `DAILY_WATCH/OPEN_ITEMS.md` ·
`THIRD_PARTY_LAUNCH_REGISTER.md` (rewritten from today's probes).
