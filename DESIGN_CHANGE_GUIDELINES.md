# DESIGN CHANGE GUIDELINES — the stringent Path B gate (11 Aug 2026)

**Status:** canon. Closes OPEN item (1) of the 5 Aug 2026 LAUNCH BOUNDARY REDRAW
(MAINTENANCE_AGENT.md). Item (2), binding the designer role, remains David's call.

**What this gates:** every design-change dossier in the shared design backlog —
fed by BOTH agents (Maintenance via recurrence rule 3; Feedback-Triage via
design-change items). The gate sits on the BACKLOG, on neither agent. Path A
mechanical fixes are NOT gated here (total autonomy, mechanical gates only).

**When it activates:** AT LAUNCH (1 Sep 2026). Pre-launch, improvement vs design
change stays deliberately undifferentiated — the tester pool of three is the
control. The scoring below may be used pre-launch as a checklist, not a gate.

## The ten criteria — each PASS/FAIL, all ten must pass

A dossier failing ANY criterion returns to its feeder with the failing number(s)
named. No partial credit, no "mostly". The scorer writes one line per criterion.

1. **EVIDENCE.** ≥2 independent reports, OR recurrence ≥3 (rule 3), OR a measured
   number (not an opinion). Every source cited by reference (TS-nnnn / F-nnn).
   One person's taste — including ours — is not evidence.
2. **PROBLEM BEFORE SOLUTION.** The user problem stands stated on its own; any
   proposed solution rides separately. (F-013's lesson: a reporter's wrong
   diagnosis buried a real fault. Adjudicate the problem, not the prescription.)
3. **SCOPE + BLAST RADIUS NAMED.** Files, screens and flows listed. Anything
   touching payment, auth/session, schema, anonymity or legal is NOT a Path B
   item at all — it exits to the escalation lane before scoring.
4. **CONSISTENCY WITH THE SYSTEM.** Reuses existing patterns (colors, controls,
   spacing, tone). Nothing may look like a control and not be one — the
   TS-0001/0002/0003 class is the founding precedent of this gate. A genuinely
   new pattern requires its own justification line and doubles the review.
5. **REVERSIBILITY.** The one-deploy revert is stated. User-visible changes ride
   a launch switch or dark launch where feasible. No irreversible design change
   ships without David's own tick.
6. **MEASUREMENT.** Name the before/after check that will prove it helped —
   a metric, a retest by the reporting user(s), or a named live probe. "Looks
   better" is not a measurement.
7. **MOBILE + ACCESSIBILITY.** Judged on a phone first: touch targets, muted
   playback (captions), and nothing meaningful below the fold of its sheet
   (MAINT-B1b addendum 7's lesson: invisible success reads as failure).
8. **BATCHED, NEVER HOTFIXED.** Design changes ride a batch on a normal deploy.
   A design change has no 2 a.m. emergency lane by definition — if it feels
   urgent, it is either really a fault (Path A) or really an escalation.
9. **COPY DISCIPLINE.** Labels describe state (past tense); imperative verbs are
   reserved for real controls. No placeholder tokens anywhere a user or an
   operator will read (the PASTE_IT_HERE rule).
10. **THE GATE ITSELF.** Designer approval recorded IN the dossier — name, date,
    one line of reasoning — before any build starts. Until the designer role is
    bound (open item 2), David is the gate by default.

## Dossier template (what the feeder files)

    DOSSIER: <short name>            DATE: <yyyy-mm-dd>   FEEDER: Maintenance|Feedback
    PROBLEM: <the user problem, solution-free>
    EVIDENCE: <TS-/F- refs, counts, measurements>
    PROPOSED DIRECTION (optional): <sketch>
    SCOPE: <files/screens/flows>     REVERT: <the one-deploy undo>
    MEASUREMENT: <the before/after proof>
    SCORE: 1..10 each PASS/FAIL + one line
    GATE: <approver name, date, one line>  — absent = not approved, do not build

## Why stringent

The fault lane optimizes for speed under mechanical gates; the design lane
optimizes for coherence under human judgment. Blurring them is how a marketplace
drifts into a different app one hotfix at a time. Ten hard criteria and one
named approver keep the drift at zero while still letting evidence move the
design forward every batch.
