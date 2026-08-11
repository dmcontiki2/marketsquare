## 2026-08-11 — REALREPO-PROBE-1: the question B4 cannot answer

- **Correcting an earlier read.** Three live runs returned `no clean patch` on TS-0024 and
  TS-0031, and that was written up as the agent failing. Reading the two faults properly says
  otherwise:
  - **TS-0031** carries its own first-pass diagnosis and a three-part fix direction — render
    unconfirmed specs as *"suggested — please confirm"*, never auto-assert variant/trim below a
    confidence bar, add a cars data lane later. That is a UX and confidence-policy change, and
    the row itself says `NEEDED FROM REPORTER: which fields were wrong`. It is blocked on
    information, not on code.
  - **TS-0024** is a question — "why was it unavailable?" — with no established root cause and
    no reproducible defect.
  **Neither is a copy/config/flag/logic bug fixable by a small code edit.** Declining both is
  correct behaviour. The agent was right; the queue simply contains no mechanical faults.
- **The real gap, which no amount of live running will close:** B4 Tier 1 and Tier 2 both patch
  a synthetic sandbox whose entire application is a two-line `app.py`. This repo's application
  lives in files of 1,074,965 (`ms.js`) and 906,981 (`bea_main.py`) bytes. **Passing B4 says
  nothing about whether the agent can find, window and patch real code here** — and that is
  exactly what CAND-FIX-1 changed and left unproven.
- **`scripts/maint_realrepo_probe.py`** closes it. Clones the repo to a throwaway dir, seeds ONE
  small mechanical defect of a known shape into a real file (a misspelt user-visible string),
  describes it the way a tester would, and runs the REAL agent against it. Then reports the
  lane, the outcome, and whether the defect was actually repaired.
- **It cannot ship anything:** the clone is a temp dir and the probe strips
  `MAINTENANCE_AGENT_ENABLED` from the environment before invoking the agent, so the run is
  shadow by construction, not by configuration.
- Two targets — `ms.js` (front end) and `bea_main.py` (`--target bea`). Each anchors on a string
  verified to appear exactly once; the probe aborts rather than guessing if the file has moved on.
- **Exit 0 = patch quality on this codebase is no longer unproven. Exit 1 = the honest answer to
  "can it fix things here", which is a different question from B4 and has never been asked.**
