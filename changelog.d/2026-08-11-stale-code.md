## 2026-08-11 — STALE-CODE-1: two runs today were read as tests while the box ran older code

- **What happened, twice:** the B4 Tier 2 `NOT READY` at 06:42 (server on `9cc3725`, one commit
  behind BRAIN-PATH-1) and the 0/2 live run at 08:10 (server on `127b6a6`, one behind
  CAND-FIX-1). Both times `git pull` reported **"Already up to date"** — which is true and
  useless: it compares the box to the *mirror*, not to the fix just written and not yet pushed.
- **Why it is dangerous rather than annoying:** the second occurrence produced output identical
  to the previous run. That is exactly how a stale test passes for a real one — nothing looked
  wrong, and the only tell either time was a stale wording spotted by eye.
- **The fix:** every run now prints the code it is actually executing —
  `code  c758b83  DIRTY-WORKTREE  maintenance-loop: CAND-FIX-1...` — short SHA, an uncommitted-
  changes marker, and the subject line. Stated *before* anyone reasons about the result.
- It reads `SELF_REPO`, the agent's own checkout captured **before** any `--repo` override,
  because the question is always "which agent is running", never "which sandbox is being
  patched". The first cut got this wrong and reported the rehearsal's temp sandbox.
- **Ledger RG-0059 LOCKED** — asserts the stamp exists, pins to `SELF_REPO`, flags a dirty
  worktree, and that `SELF_REPO` is captured before the override rather than after.
- Same family as UA-EDGE-1, BRAIN-PATH-1, GUARD-SPLIT-1, PHASE-AWARE-1 and CAND-FIX-1: a thing
  that reported plausibly while telling you nothing. Sixth of the day.
