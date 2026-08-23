## 2026-08-22 — SESSION-COUNTER-1: the session badge was never a counter

**Raised by David**, who was certain the badge reading "Session 155" had been
overtaken "way past" that number, and who noted this had been "permanently
fixed" before. Both halves of that were correct.

**What it actually was.** `GET /dashboard/summary` did this, at `main.py:8545`:

```python
sm = _re2.search(r"Session (\d+)", status)
current_session = int(sm.group(1)) if sm else 0
```

That is a regex for the FIRST occurrence of the literal text `Session <digits>`
anywhere in STATUS.md — a 329 KB, 2,431-line, append-only prose file. The line
it landed on was **line 1650**, dated 1 Aug 2026, whose own text reads
*"SESSION COUNTER CORRECTED 150 -> 155"*. The badge was pinned to a paragraph
whose subject was a previous freeze of the same counter.

Nothing in the codebase incremented anything. **Freezing was the default, not
the failure mode.** The number could only move when a human hand-edited that
paragraph — which is why the two earlier "permanent" fixes (139→141 in Session
141, 150→155 in Session 155) each had a shelf life of exactly one session: both
corrected the NUMBER and left the MECHANISM.

**True number: 175**, derived from 20 distinct session-days of fragments between
2 and 22 Aug on top of the 1 Aug anchor. A floor, not an exact count.

**Fixed in two halves, both necessary:**

1. **Derive, don't transcribe.** `scripts/session_counter.py` computes the number
   from the `status.d/` and `changelog.d/` fragments that STATUS-COLLISION-1 and
   CHANGELOG-COLLISION-1 already make the only legal way to record a session. The
   act that proves a session happened is now the act that advances the count, so
   it cannot freeze while work continues. Written to `SESSION_COUNTER.json`,
   shipped by the manifest, recomputed by `deploy_marketsquare.bat` before the
   compilers archive the fragments.
2. **Carry the as-of date.** The badge renders `Session N · as of <date>` and
   greys to UNVERIFIED when the value did not come from the derived counter. A
   bare number can lie indefinitely; a number beside its own date confesses the
   moment it stops moving. This is RG-0133's rule (no instrument paints a state
   nothing measured) applied to the header badge.

**RG-0154** asserts the mechanism, not the number — OPEN until the release
reaches the server, then READY TO LOCK. Any future reinstatement of the prose
scrape, or any drift between the counter and the fragments on disk, trips it red.

Touched: `main.py`, `bea_main.py`, `dashboard.server.html`, `dashboard.html`,
`scripts/session_counter.py` (new), `SESSION_COUNTER.json` (new),
`ops/autodeploy/deploy_manifest.txt`, `deploy_marketsquare.bat`,
`scripts/regression_ledger.py`.
