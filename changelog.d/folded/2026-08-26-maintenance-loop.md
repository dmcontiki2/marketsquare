## 2026-08-26 — Maintenance loop: two instrument faults fixed, fault queue clean

**Fault queue: nothing to do.** 0 new, 0 triaged, 0 fix-shipped (26 verified, 7 closed,
2 duplicate, 35 total). The shadow agent ran clean in SHADOW mode, saw 0, acted on 0, and
posted its heartbeat to `/dashboard/maint` at 02:22:32Z. No escalation brief — no
escalations in 24h. So the session's work was the opening ledger's four reds, which per
the loop's contract ARE the top item when a LOCKED entry is red.

**Two of those four reds were the instrument lying, and both are now fixed at class level.**

### LEDGER-DEPS-1 — a missing dependency read as a rotted fix (RG-0187, LOCKED)
The loop's own opening run printed `RESULT: 5 previously-fixed issue(s) HAVE COME BACK.
Do not deploy over this.` RG-0181 ("its refusals no longer refuse") and RG-0182 ("the
dark/lit harness FAILS") were both `ModuleNotFoundError: No module named 'fastapi'`. Both
harnesses died on their import line having run ZERO assertions; `pip install fastapi`
turned them into 9/9 and 13/13 with not one byte of app code changed.

This is the THIRD instance of one shape — the instrument reporting itself as the app —
after LEDGER-OFFLINE-1 (7 Aug, no network) and GATE-CACHE-1 (14 Aug, a 429 credential),
and it now gets the same treatment: `NOT EVALUATED` → UNVERIFIED, loudly not a pass,
exit 2, never REGRESSION. A false red is worse than no answer — it invites the next
session to "fix" what is not broken and it blocks a deploy for nothing.

The narrowness is the point: the demotion covers third-party imports ONLY. A missing
**repo** module is a deletion and stays RED — a demotion that swallowed that would be the
silent green the ledger's preamble calls the worse failure. New `_harness()` /
`_missing_third_party()` helpers; all four subprocess-harness call sites (RG-0128,
RG-0177, RG-0181, RG-0182) now route through them, and RG-0187 trips red if a future
entry hand-rolls its own `subprocess.run`.

### CSP-SCRIPT-SRC-3 — a migration that could not SEE what it had to change (RG-0186, LOCKED)
RG-0125 was red: migration `033_csp_verify_served.py` failed on the 24 Aug deploy and
JAMMED the chain, so every later one-time server change would have been silently skipped.

The deploy report told the whole story: 033 said *"CSP declared in N file(s); 0 still lack
script-src"* and then measured a served policy of `frame-ancestors 'self'`. It restored
**0** files — there was nothing stale to restore. It rewrote everything it could see and
the emitter was not among them.

The defect was never the server. 033 searched a FIXED list of globs, none recursive
(`snippets/*` never reaches `snippets/security/*`) and all under `/etc/nginx`, so an
include one directory deeper — or by absolute path from outside the tree — was invisible.
A glob that misses the file is indistinguishable from a server that refuses the change,
and it fails identically forever.

Discovery now unions `nginx -T` (the fully-resolved config, which names every file nginx
really reads and therefore cannot miss an include) with a recursive walk of `/etc/nginx`
and the original globs. On failure it now PRINTS every file still declaring a CSP, so the
next failure is diagnosable instead of mute. 033's honesty — its refusal to claim an
effect it has not probed — is untouched and is now itself asserted; that honesty is the
only reason this was findable at all. Same lesson as 031's, one level up: **031 declared
success from a WRITE instead of a PROBE; 033 probed correctly but searched blind.**

### Evidence (AIK-VERIFY-1)
- `scripts/prove_ledger_deps.py` (new) — 10/10. Mutation-tests all four branches: a
  third-party death demotes, a real assertion failure stays red, a deleted repo module
  stays red, a pass is still a pass.
- End-to-end: with fastapi uninstalled RG-0181/RG-0182 reported **UNVERIFIED**; reinstalled,
  both returned **HOLDING**. The exact morning conditions, reproduced clean.
- `scripts/prove_csp_discovery.py` (new) — 10/10. Builds a fixture with the emitter nested
  one level below the old globs' reach; the old discovery misses it, the new one finds,
  classifies and correctly rewrites it without losing `frame-ancestors` or the neighbouring
  headers.
- Both new entries mutation-tested against a throwaway repo copy: **11/11 mutations go red**,
  and green when restored. Two of my own first-cut assertions were wrong and were corrected
  rather than worked around — one matched prose split across string literals, the other
  split on an `except` clause that occurs three times in the file and so could never fail.

### Also found
- **RG-0188 (new, OPEN)** — the SSH-LOCKOUT-1 self-heal has never been armed. RG-0099's
  failure message says "Fix: run `scripts/hetzner_fw_selfheal.py`", so the loop ran it, and
  it answered "NO TOKEN … Nothing changed." For nine days the class has been DETECTED but
  not CURABLE and nothing on the board said so. The script only ever ADDS the current IP and
  never removes a rule, so arming it cannot itself cause a lockout — but provisioning the
  token is David's (RUL-027).

### Files
- `scripts/regression_ledger.py` — LEDGER-DEPS-1 helpers; 4 call sites rerouted; RG-0186,
  RG-0187, RG-0188 added (181 entries).
- `migrations/033_csp_verify_served.py` — `nginx -T` discovery + recursive walk + failure inventory.
- `scripts/prove_csp_discovery.py`, `scripts/prove_ledger_deps.py` — new harnesses.
- `SESSION_COUNTER.json` — recomputed (derived, 179).
