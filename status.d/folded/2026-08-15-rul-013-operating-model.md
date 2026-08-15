- **RUL-013 recorded (David, 15 Aug 2026) — the fault-resolution operating model, both phases.**
  PRE-LAUNCH (to 1 Sep): the maintenance agent does NOT surface failures or reports to David;
  testers are the fault source and AI resolves without him; escalations route to the FIX AGENT
  (Fable) under standing pre-approvals with laptop resources open. POST-LAUNCH: source becomes user
  complaints; maintenance agent handles most; fix agent handles 98% of the remainder; David on
  STANDBY for the residual ~2% for the FIRST TWO MONTHS, with Claude's support — reviewed after that
  window, not assumed. Written to RULINGS.md and reflected in MAINTENANCE_AGENT.md;
  `rulings_check.py` gained the assertion, so it is a guarantee rather than a note (13 rulings,
  0 FAIL, 0 WARN).
- **Extends RUL-005 and inherits its condition, which today made pointed reading.** RUL-005 replaced
  the human veto with mechanical gates, on the express condition that "any gate that stops asserting
  re-arms the veto". Three gates had silently stopped asserting: the drift monitor (permanent
  phantom red, DRIFT-CACHEBUST-1 + DRIFT-FILEMAP-1), the tester-intake maint-scope guard (failing on
  CORRECT code since the 13 Aug ruling), and the DANGER verdict they jointly produced on every
  deploy. All three are honest again as of today — so the condition RUL-005 attaches to more
  autonomy is satisfied NOW, but it was quietly unsatisfied for weeks while autonomy was assumed.
- **Recorded honestly: the Fable hand-off is intent, not mechanism.** There is no Fable lane —
  `ai_active` accepts only anthropic|openai|scaleway and no Fable provider exists in the register.
  The server agent runs unattended and cannot summon a Cowork session, and per-session laptop grants
  can never be held by an unattended run (the fault that stalled the photo run at image 1 of 54).
  So pre-launch behaviour in PRACTICE is: PATH_A fixed autonomously and silently as ruled; the
  ESCALATE class accumulates for the next fix session. Better than David reading every report — but
  not yet "AI fixes it without me". Three concrete steps to close it are named in MAINTENANCE_AGENT.md
  and the gap note is itself asserted, so it cannot vanish while the gap remains.
- **NOT delegated in any phase:** the deterministic REFUSE guard. Legal, currently-costly and
  trust-core surfaces still stop for a human. Autonomy is over the fixable class, never the refuse class.
