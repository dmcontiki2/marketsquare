# TrustSquare — Session Continuity (zero manual git)

## The one line you paste to start any new chat
> **New TrustSquare session — baseline from the server and continue.**

That's all you do. I then fetch the current state myself (see below) and brief you back.

## How it works (no manual pushes, no manual saves)
- **Source of truth = the server.** STATUS.md / CHANGELOG.md / AUDIT_PROGRESS.md live at
  /var/www/marketsquare/ and are parsed by the BEA at GET /dashboard/summary (no auth, obscure URL).
- **Session END (automatic):** Claude updates those files locally, then `scp`s them to the server.
  SSH is something the sandbox can do — git is NOT involved, so there is no index.lock conflict
  and no PowerShell push step. Git remains a convenience backup you run whenever you like.
- **Session START (one paste):** Claude fetches https://trustsquare.co/dashboard/summary and is
  baselined — last session, what changed, next goals, blockers, audit progress, cost snapshot, tasks.

## The honest limit
A chat doesn't exist until you open it, so Claude cannot fetch state with *zero* input — the
irreducible minimum is the one line above. For a truly hands-off version, the scheduled morning
brief (below) fires on a clock and posts the brief to you proactively.

## Two ways to bootstrap (both enabled)
1. **Paste-line** (ad-hoc) — the line at the top of this file, any time.
2. **Scheduled brief** (hands-off) — a daily task pulls server state and posts a ready-made
   session brief each morning. You just read it.

## What Claude gives you at session start (the baseline brief)
- Current session number + last completed
- What changed last session (recent CHANGELOG)
- Next-session goals + any blockers
- Audit phase + open findings (from AUDIT_PROGRESS.md)
- The four cost metrics: per-user AI token cost · cost-vs-revenue margin per op ·
  monthly running cost @100 users · @100k users  (real-token actuals once C2/C3 land)
- Open task list

## Build status
- [READY] Server reachable via scp; /dashboard/summary live and already parses STATUS/CHANGELOG/BACKLOG.
- [PHASE 1] Enrich /dashboard/summary to also return AUDIT_PROGRESS + the 4 cost metrics + tasks.
- [PHASE 1] Add the scheduled morning-brief task.
- [PHASE 1] Add a session-end scp helper so the write-back is one deterministic step.
