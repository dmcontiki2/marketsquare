## 2026-08-11 — PHASE-AWARE-1: the arming gate could never clear the mode it was meant to clear

- **Symptom:** the B4 rehearsal run on the server at `MAINT_PHASE=prelaunch --live-brain` printed
  `NOT READY — do not arm`, failing on one row: `SYN-DESIGN  expect PATH_B  routed PATH_A`.
- **The agent was right and the harness was wrong.** Routing a design ask to PATH_A *is* the
  documented pre-launch job (MAINTENANCE_AGENT.md, David 9 Aug) and is exactly the autonomy
  David asked for. The rehearsal hardcoded `"expect": "PATH_B"` — the postlaunch answer — and
  scored correct behaviour as a failure.
- **Why this mattered more than a wrong test:** the B4 rehearsal is *the gate that clears the
  agent for arming*. A gate that can never green-light the mode it exists to clear is worse than
  no gate — it trains you to override it, and the next real failure gets overridden with it.
- **The fix:** the expectation now moves with the run, and the harness prints which combination
  it scored. Nothing was relaxed:
  - Tier 1 (stubbed brain) → `PATH_B` in **both** phases — the classify stub is consulted
    *before* the PRELAUNCH branch, so the phase genuinely cannot change the answer.
  - Tier 2 + postlaunch → `PATH_B`.
  - Tier 2 + prelaunch → `PATH_A`.
- **Evidence:** Tier 1 re-run in both phases still passes **6/6**, guard rows green, banner
  reading `scoring against: stubbed brain, phase=<phase>`.
- **Ledger RG-0057 LOCKED** — asserts the expectation stays phase-aware, that the scorer resolves
  it from the run's own phase+brain, that the harness names the mode it scored, and — the part
  that matters — that the four protected-surface rows (`SYN-PAY`, `SYN-ANON`, `SYN-LEGAL`,
  `SYN-SAFETY`) never become phase-conditional. A protected surface escalates in every mode.
- **Known limitation, stated not buried:** the prelaunch design lane is now *routed* correctly
  but is still not proven end-to-end. In the Tier 2 prelaunch run the brain took SYN-DESIGN to
  PATH_A and then returned **"no clean patch"** — sensible judgement, since "add a dark-mode
  toggle" cannot be patched into a two-line sandbox `app.py`. So no design change has ever
  actually been generated and gated. The rehearsal cannot prove that lane; only a real design
  fault will.
