## 2026-08-05 — Maintenance vs Feedback-Triage ruled TWO agents (David)

David's rulings today, now canon in MAINTENANCE_AGENT.md (LAUNCH BOUNDARY REDRAW) and the
AGENTS.md roster:

- **Launch boundary redraw:** Path A (mechanical fixes) keeps total autonomy; Path B
  (design changes) now requires stringent design-change guidelines + a DESIGNER APPROVAL
  GATE. Pre-launch stays deliberately loose — the tester pool of three is the control.
- **Two-agent split confirmed:** Maintenance (fault/NCR lane: adjudicate→fix→verify→harden,
  immediate, majors first) and Feedback-Triage (voice-of-customer lane: synthesize,
  vote-count, route; never fixes) are separate agents sharing ONE intake — the reporter
  never picks a lane; triage routes (F-013/F-015 proved testers can't self-classify).
- **Hand-over contract:** items cross by reference, never copy. Feedback fix-now → a
  FAULT_REGISTER row citing the F-nnn; fix status flows back to close the F-row.
  NOT-A-FAULT adjudications revealing a wish route back as feedback. The designer gate
  sits on the shared design backlog BOTH feed — on neither agent.
- Open before launch: write the design-change guidelines; bind the designer role.
