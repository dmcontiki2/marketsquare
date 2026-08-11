## 2026-08-11 — MAINT-CLOSE-1: B3 + B4-Tier-2 lane + guidelines + scheduling — the loop is complete to the arming line

Session goal (David): "start these open issues now and complete them" — the gap between the
Maintenance Agent's design and a board that clears itself with nobody watching.

**MAINT-B4-5 — degrade-not-die (a real class bug, found by rehearsing, fixed + locked RG-0049).**
The local mechanics test of migration 011 crashed the agent: `classify()` guarded the IMPORT of
ai_provider but not the CALL, so a missing dep (httpx), network blip or bad key killed the whole
run mid-queue — later faults got NOTHING, not even escalation. Fixed at class level: every
`ai_provider.complete()` call guarded (classify → design lane; propose → declined/escalate);
per-fault try/except in main() so one poisoned fault can never kill the queue. Proven: Tier 1
still READY exit 0; keyless Tier 2 now completes with all six faults actioned (SYN-MECH degrades
to PATH_B instead of "(none)"). RG-0049 (source-level, offline-safe) locks it; full ledger green.

**B4 Tier-2 lane — `migrations/011_maint_b4_tier2.py`.** The server-side rehearsal (real brain,
patch quality — the one thing Tier 1 cannot prove) now rides the ONE deploy as a one-time
migration: sandboxed + shadow (env strips MAINTENANCE_AGENT_ENABLED; MAINT_PHASE=postlaunch
because B4 rehearses the LAUNCH posture), 540s timeout, verdict JSON → reviewer-gated
`static/maint/b4_tier2.json` + full table in the deploy log. READY or NOT READY is DATA (exit 0
either way — DW-030's lesson); only a failure-to-run retries. Mechanics proven locally end-to-end.

**B3 — `scripts/escalation_brief.py` + tripwire.** Stage-7 format made machinery: ESCALATE items
from the agent's own run reports, categorized against the agent's refuse markers IMPORTED (drift
structurally impossible), each item = what → safest action (standing) → 2-3 options → ONE tick
line ("reply `REF 1/2/3`"). Stdlib, no key, runs anywhere. Selftest (marker coverage + collector +
format) green — and it caught its own first bug: categorizing on the outcome boilerplate
("escalated (safety/legal/cost)") mislabelled everything LEGAL; categories now read ref/title/why
only. Tripwire `test_escalation_brief_wired` added to test_maintenance_agent.py (predeploy-run).

**Guidelines — `DESIGN_CHANGE_GUIDELINES.md` closes OPEN item (1) of the 5 Aug boundary redraw.**
Ten pass/fail criteria (evidence ≥2 reports or recurrence ≥3; problem before solution; scope;
consistency — the TS-0001/2/3 "looks like a control" class is the founding precedent;
reversibility; measurement; mobile/a11y; batched-never-hotfixed; copy discipline; the recorded
gate line). Dossier template included. Activates AT LAUNCH; pre-launch it is a checklist.
Item (2) — binding the designer role — stays OPEN, David's decision; until bound, David is the gate.

**Scheduling — the B2b cadence, both phases.** Pre-launch brain: Cowork scheduled task
`maintenance-loop`, daily 07:31 (strict contract: ledger → shadow agent against the live queue →
apply green fixes by hand-rules → AIK-VERIFY-1 evidence → escalation brief → fragments → commit;
NIGHTLY-SHIP-1 ships). Post-arming cadence: `ops/maintenance/maintenance-agent.{service,timer}`
(05:20/11:20/17:20 UTC) installed ONLY by `MAINT_ARMING_RUNBOOK.md` — one paste block, nothing to
substitute, preconditions stated (b4_tier2.json ready:true + fresh backup), DISARM one-liner,
push-auth dry-run check included. Arming remains David's single act.

**What remains before the board clears itself:** next deploy runs 011 → read the Tier-2 verdict →
if READY, David arms (one paste). Designer-role binding open (David). Nothing else in B1–B4 is unbuilt.

**Rider — the gate caught two live items while this session was closing.** (1) Four adventures
map pages (na/bw/mz/ke) had NO fault-report widget — a tester there had no way to report; wired
`ts_report.js?v=5` before `</body>` on all four (same first-party pattern as the other 14 pages;
RG-0025-safe); `test_widget_is_wired_into_every_tester_page` green again. (2) PG-READINESS flags
`strftime` 38→39 in bea_main.py — that file is the ADVERTS session's in-flight edit, not touched
here (collision discipline); flagged flat for that session to write portably before the nightly's
strict gate holds it.

**GIT-LOCK-2 rider.** This session's own commit proved a gap in GIT-LOCK-1: the commit succeeded
but left a stale `.git/HEAD.lock` (FUSE blocks unlink from the sandbox) — same class as
index.lock, would block the next writer. `git_unlock.bat` extended from the instance to the
class: clears index.lock, HEAD.lock and packed-refs.lock, same no-git.exe-running guard. The
residue self-heals at the next bat-path git write (05:45 nightly at the latest).
