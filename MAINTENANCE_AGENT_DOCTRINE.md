# Maintenance Agent Doctrine — the three-tier ratchet
*(Born 24 Aug 2026 from David's direct concern: "the one area where we can't fail
at, maintenance" — and from the recorded fact that even attended sessions needed
2–3 tries on novel faults during 19–24 Aug. Written 24 Aug 2026, verified against
the on-disk machinery it cites.)*

## The founding observation (evidence ladder, generalized)
Every wrong fix attempt of 19–24 Aug was sourced from a REPRESENTATION (doc, code
pattern, cached state, memory). Every correction came from a PROBE. Therefore an
unattended agent that acts on representations WILL fail, invisibly, at 2 a.m.
The design goal is NOT first-try brilliance on novel faults — no human or AI has
that. It is: wrongness must be cheap, visible, and non-repeatable.

## Tier 0 — Machines (live today; no judgment involved)
- /pulse heartbeat · SERVER-BIT-1 10-min heartbeat · regression_ledger.py ·
  rulings_check.py · ONE_DEPLOY auto-rollback (server_deploy.sh health-check).
- Role: detect and contain without intelligence. Tier 0 is the floor that holds
  when everything smarter is asleep.

## Tier 1 — The unattended maintenance agent (playbook-only, NEVER clever)
- May execute ONLY pre-approved runbooks for KNOWN fault classes
  (examples already earned: stale .git/index.lock -> git_unlock; stale CDN edge
  -> purge + RG-0024 stamp check; dead service -> restart -> /health probe;
  poisoned scrape memory -> CT-MEM-1 requery).
- EVERY action is followed by a probe before "done" may be claimed (ledger rule).
- Anything NOVEL is forbidden unattended: contain (rollback to last green),
  then escalate to David with an EVIDENCE BUNDLE — what was probed, what was
  found, what was rolled back, which runbooks were tried. Never iterate blind
  on production.
- An agent that never guesses cannot fail three times in the dark.

## Tier 2 — Attended sessions (David + Claude)
- Where novel faults are actually solved, with the human present.
- EXIT CRITERIA for every attended fix (already standing rules, restated as the
  ratchet's pawl): (1) occurrence fixed, (2) class fixed, (3) ledger/tripwire
  entry same session, (4) IF the fault could recur operationally -> a Tier 1
  runbook entry so next time no one needs to be awake.

## The ratchet
Tier 2 feeds Tier 1; Tier 1 leans on Tier 0. Coverage only grows. The unattended
agent's competence is the accumulated set of PROVEN fixes — never its cleverness.
This is why maintenance does not require winning first-try on novel problems,
and why the 2–3-try pattern of attended debugging is acceptable: attended
iteration is how runbooks are BORN; unattended execution is how they are REPLAYED.

## Standing constraints inherited
- RUL-037: technical decisions are Claude's within spec; money/deploy/delete/
  lockout-risk actions remain David's — Tier 1 runbooks must never contain them
  beyond the pre-approved auto-rollback.
- RUL-009 analogue: no unattended self-modification; the agent never edits its
  own runbooks — new runbooks come only from Tier 2 sessions.
- Evidence ladder: PROBED > EXECUTED > READ > RECALLED. Tier 1 may only speak
  PROBED. "The runbook ran" (EXECUTED) is not "the fault is fixed" (PROBED).

## The 80/20 iteration principle (David, 24 Aug 2026 — ratifying this doctrine)
David's words, near-verbatim: "We don't design to fail or pass, we design to
ITERATE TO A DEFINITE PASS — not to expect a pass or fail at first, but to
expect an ~80% outcome which can then be MEASURED and COMPARED, and then with
this knowledge to resolve the last 20%."
Design consequences, binding on every after-launch agent:
1. First attempts are expected to land ~80%. An 80% outcome is not a failure —
   an UNMEASURED outcome is. Every agent action must emit something a gauge can
   read (probe result, golden-set score, ledger assertion, count vs target).
2. The gap to 100% must be expressed as a MEASUREMENT, never a feeling
   ("13 shops missing emails", "2 of 6 golden answers wrong") — because the
   measurement IS the work order for the next iteration.
3. Iteration without a gauge is forbidden — that is the blind three-try pattern
   of 19–24 Aug. Iteration with a gauge is convergence, and converged fixes get
   locked (ledger) so the pass is DEFINITE and permanent.
4. Corollary for Tier 1: a runbook graduates from Tier 2 only once its gauge is
   defined — a runbook without a pass-measurement cannot be replayed unattended.
