## 2026-08-13 — The agent patches REAL code: probe PASS on bea_main.py and ms.js (RG-0067)

David's challenge — "how will we know the agent can work autonomously if we leave the live
test till after launch?" — answered by running the test, not describing it. Thirteen
real-repo probe runs in one sitting; four environment defects and three pipeline defects
found, fixed, and locked:

- PROBE-KEYS-1/2: the gitignored .secrets never reached the probe clone — brain keyless
  (PATH_B by default), then gate probes blind. Clone now provisioned like the real repo.
- WINDOW-AIM-1: the excerpt window aimed at the densest cluster of ANY token — generic
  words outgunned the distinctive one (defect at line 122, brain shown 1158-1298; sonnet's
  NObugfix was CORRECT). Rare tokens (≤2, then ≤8 hit lines) now steer; common ones pad.
- PROBE-EXHAUST-1: the probe harness itself ranked as the patch target — it quotes faults
  verbatim, so the brain was shown the seed DEFINITION, where the misspelling is correct.
  CAND-FIX-1's "own exhaust" class, new costume. Harnesses excluded from ranking.
- PATCH-FENCE-1 + --recount: sonnet fences its diffs and miscounts hunk headers; written
  verbatim to .proposed.patch = "corrupt patch at the closing fence". THE root of the
  MAINT-B4-6 "diffs slip" class. Fences stripped; git apply --recount --3way (proven by
  hand: rc=0, typo fixed).
- WINDOW-SPLICE-1: the rewrite fallback demanded "the COMPLETE file" while showing an
  excerpt labeled "the rest is NOT shown" — impossible; sonnet echoed the block. Windowed
  rewrites now ask for the corrected BLOCK and splice by line range under a bytes-match
  guard (also kills the latent garbage-filename write: rw path was the LABEL).
- PATCH-EVIDENCE-1: apply failures now keep the failing diff + git's stderr in the run
  report — "did not apply" was undiagnosable for two days.
- GATE-CREDS-1 (launch-critical): gate worktrees carry TRACKED files only — no .secrets —
  so from the moment 016 armed the origin gate, the ledger GATE crashed 401-red for EVERY
  patch, however perfect. The arming didn't just break intake (GATE-COOKIE-1); it silently
  blocked the entire fix pipeline's gate step. Worktrees now get the repo's .secrets.

Evidence: PROBE PASS both targets — bea_main.py (909,256 B) and ms.js (1,060,023 B) found,
windowed, patched, gates green, commit correctly withheld by shadow. "Patch quality on this
codebase is no longer unproven" — the last open question before the timer (STATUS.md, 11
Aug) is answered for both real-file classes. RG-0067 locks the whole pipeline with
deterministic no-API assertions.
