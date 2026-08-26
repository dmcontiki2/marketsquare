## 2026-08-26 — maintenance-loop: CSP-SCRIPT-SRC-6 + POSTDEPLOY-EYES-3 (RG-0191)

**Fault queue:** drained. 0 new, 26 verified, 7 closed, 2 duplicate (35 total, probed
`GET /admin/faults`). Shadow agent ran clean — 0 seen, 0 acted — and its heartbeat is on
`/dashboard/maint` at 2026-08-26T05:35:32Z. No shadow patch was ready, so nothing was
applied from that lane. No escalations in 24h, so `escalation_brief.py` wrote no brief.

**The session's top item was the RG-0125 red:** `033_csp_verify_served.py` FAILED on the
04:05:08Z deploy and jammed the migration chain. Diagnosed to the migration's *measurement*,
not its rewrite — the fourth consecutive failure in the same organ:

| | what it got wrong |
|---|---|
| CSP-SCRIPT-SRC-3 | could not SEE the emitting file (discovery) |
| CSP-SCRIPT-SRC-4 | compared prose, not directives (staleness) |
| CSP-SCRIPT-SRC-5 | measured a 301, not the page (vantage) |
| **CSP-SCRIPT-SRC-6** | **polled for a STABLE answer, not the EXPECTED one (settling)** |

The settle loop exited when "the value stopped changing". A stale nginx worker still serving
the OLD policy answers with the SAME value every read, so the loop was satisfied on read 2 —
about one second after the reload — and returned exactly the value it had been asked to wait
for the reload to replace. `settle=15` bought nothing. A correct rewrite was then restored and
the chain jammed. **Class rule now on the books: poll for the EXPECTED state, never for a
stable one.** A steady wrong answer is indistinguishable from a settled right one.

**POSTDEPLOY-EYES-3, the second half of the same failure.** The one line naming the measured
value was line -4 of 033's output and `post_deploy.sh` captured `tail -n 3 | cut -c1-300` — so
the evidence existed and the report structurally could not carry it. Four consecutive reports
said "something else is emitting the header"; not one said what was actually served.

**Changed**
- `migrations/033_csp_verify_served.py` — `served_csp()` polls until `script-src` appears or
  the deadline is spent (settle 15s→45s), returns immediately on a first-read hit, and reports
  what IS served when the window runs out. The raise now LEADS with `MEASURED=` so a
  head-truncated report window cannot eat it. Loud-on-3xx (CSP-SCRIPT-SRC-5) intact.
- `ops/autodeploy/post_deploy.sh` — failing-migration capture widened from 3 lines/300 chars to
  12 lines/1200 chars, backslashes stripped alongside quotes for JSON safety.
- `scripts/prove_csp_settle.py` — NEW. Reproduces the old loop returning the stale value
  deterministically, proves the new one waits it out, proves it does not burn the window on a
  first-read hit, proves the redirect behaviour is not regressed, and asserts the report window.
  11/11.
- `scripts/regression_ledger.py` — RG-0191 added LOCKED (RG-0190 was taken; the ledger's own
  LEDGER-DUP-1 guard caught the collision and it was renumbered rather than forced).

**Ledger after: RG-0125 is STILL RED, and honestly so.** It asserts against the *last deploy
report*, which cannot change without a deploy — and this loop does not deploy. The fix is
committed for the 05:45 nightly TSL to carry. If 033 fails a fifth time, the report will for
the first time name the value it measured. 166 ok / 17 open / 1 red. Rulings: 57 checked, 0 fail.
