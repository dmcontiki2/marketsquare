## 2026-09-10 — SANDBOX-REPAIR-1 corrections: AGENT-RC-1 proven, two of my own defects fixed

Follow-up pass, 05:00–05:30 SAST, still shell-less (the sandbox is dead — KB5124008, see the 9 Sep entry).

**AGENT-RC-1 is PROVEN on the host.** The last two CityLauncher lines in `autodeploy_agent_log.txt`
say it exactly: `21:48:21.89 CL REQUEST seen` / `21:48:21.89 CL FAILED rc=` (old code — same second,
empty rc, flag kept, 74th consecutive re-deploy), then `22:20:53 CL REQUEST seen` /
`22:24:45 CL SHIPPED - request closed` (fixed code — real elapsed time, real verdict).
`CL_DEPLOY_RESULT.txt` carries the SHIPPED line. The 40-hour loop is closed.

**Two defects of mine, both caught by the fact board within ten minutes of my writing them:**

- *RG-0194 (line endings).* Three of the six scripts I added last night were LF-only on disk —
  `sandbox_repair_diag.ps1`, `sandbox_repair_sess.ps1` and `sandbox_repair_restart_app.bat`. The
  two `.ps1` files I never converted; the `.bat` I did convert, but the CRLF bytes did not reach
  the disk and I reported it done without re-reading them. Now CRLF, and this time **verified by
  re-staging the files and reading the bytes back** (2610 / 6883 / 425), not by trusting the write.
- *RG-0349 (my own new assertion).* It scanned the whole of `autodeploy_agent.bat` for the
  parse-time reads it forbids — and went red on the header comment that QUOTES those exact lines to
  explain the bug they caused. The fix on disk was correct the whole time. The scan now skips `::`
  and `rem` lines, and the entry's ref records the correction rather than hiding it (ledger rule:
  if an assertion is wrong, fix the assertion and say so). Proven both ways against the real file:
  the corrected scan finds no parse-time read in the code, and the old scan is shown to have matched
  only the comment. Class note: a CODE-PATTERN red that cannot tell code from the comment describing
  it is the RG-0117 mistake wearing a new hat.

**A third mistake, caught before it landed:** rebuilding `host_queue/ALLOWLIST.txt` I copied from a
staging snapshot taken hours earlier, which would have silently deleted every row added last night.
Nothing was committed — the fresh file was re-staged and the rebuild verified row by row (33 entries,
each of last night's present) before writing. The lesson is the one already in CLAUDE.md for SQLite
and CHANGELOG: on this bridge, re-read immediately before writing, every time.

**Also new:** `boards_host.bat` (allow-listed) runs `session_counter.py` — RG-0154's own designed
remedy — and `dashboard_provenance.py --check` on David's PC, because the queue's `run_py` lane
cannot pass a `--check` flag. Those two reds (RG-0154, RG-0155) are pre-existing and untouched by
this work; the run names what is actually wrong instead of quoting the ledger back at David.
