---
name: start
description: >-
  Boots up David's MarketSquare project in one go: confirms the Projects folder is
  connected, runs the torn-mount guard, checks claude-mem memory health and refreshes
  the Cowork memory digest, runs deploy_marketsquare.bat (pushes the site live to the
  Hetzner server), reads and summarizes STATUS.md, and opens marketsquare.html in Chrome.
  Use when David types /start, or asks to "start", "boot up", "spin up", or "kick off"
  his MarketSquare session, or to deploy-and-open MarketSquare.
---

# /start — Boot up MarketSquare

Run David's MarketSquare startup sequence end to end, in order. Give a one-line status
after each step. Project root: `C:\Users\David\Projects\MarketSquare` (inside the connected
`C:\Users\David\Projects` folder).

## Step 1 — Confirm folder access

Confirm `C:\Users\David\Projects` is connected (David's settings normally grant it). Verify
by listing `C:\Users\David\Projects\MarketSquare`. If it isn't accessible, request it with
`request_cowork_directory` before continuing.

## Step 2 — Torn-mount guard (run BEFORE trusting any bash read or write-back)

The bash sandbox reaches the Projects folder over a virtiofs/FUSE mount that can serve a
persistently truncated (torn) copy of a large file for an entire session (MOUNT-READ-1). Catch
it before it can corrupt anything. Copy the detector OFF the mount first (so its own code can't
be torn), then run it:

```bash
cp /sessions/<id>/mnt/MarketSquare/mount_check.sh /tmp/ && chmod +x /tmp/mount_check.sh
/tmp/mount_check.sh /sessions/<id>/mnt/MarketSquare
```

Exit 0 = mount whole (report "mount clean" in one line and continue). Exit 1 = torn file(s)
listed — STOP, tell David which files are torn, and do NOT write-back those files from bash this
session (use the Read/Edit file-tools, which hit the true Windows file, or pull the authoritative
copy from the server). Do not proceed to a live deploy with a torn mount.

## Step 3 — claude-mem health + refresh the Cowork digest

claude-mem gives the Claude Code CLI automatic memory; Cowork reads it via a small capped digest
file. Do two quick things:

a) **Health ping** — confirm the claude-mem worker is up:

```bash
curl -s http://localhost:37777/api/health
```

Expect `{"status":"ok"}`. If it fails, note in one line that claude-mem's worker isn't running
(David can fix later with `npx claude-mem repair` in PowerShell) — this is non-blocking, continue.

b) **Refresh the digest** — rebuild the capped Cowork-readable memory summary. The helper copies
the live DB read-only, so it's safe while claude-mem is active:

```bash
cd /sessions/<id>/mnt/MarketSquare
python3 claude_mem_digest.py --db /sessions/<id>/mnt/.claude-mem/claude-mem.db --project MarketSquare --limit 10 --out /sessions/<id>/mnt/MarketSquare/CLAUDE_MEM_DIGEST.md
```

If `C:\Users\David\.claude-mem` isn't connected, request it with `request_cowork_directory` first.
Then read `CLAUDE_MEM_DIGEST.md` and fold a one-line "last session recap" into the Step 5 summary
so David sees where he left off. If the DB isn't found (plugin hasn't run yet), say so in one line
and continue — non-blocking.

## Step 4 — Run the deploy script

Run `C:\Users\David\Projects\MarketSquare\deploy_marketsquare.bat`.

- This is a LIVE deploy: it scp's the local files to the production server and restarts the
  backend (trustsquare.co). Tell David in one line that you're deploying live before running.
- It's a Windows batch file — run it on the desktop, not in the Linux sandbox:
  - `request_access` for File Explorer (and the console window the script opens).
  - Open File Explorer to `C:\Users\David\Projects\MarketSquare` and double-click
    `deploy_marketsquare.bat`. Launching by double-click needs no typing — and terminal/console
    windows block typing anyway, so never try to type into the console.
  - Watch the console with screenshots. It prints numbered steps (`[1/6]`…). It `pause`s and
    prints `ERROR:` on failure — if you see that, stop and report the failing step. Continue
    only once it completes successfully.

## Step 5 — Read and summarize STATUS.md

Read `C:\Users\David\Projects\MarketSquare\STATUS.md`. It is large — do NOT dump it. Read the
top section first (most recent status usually lives there) and give David a 3–5 line summary:
current state, anything flagged or awaiting him, and the next steps. Include the one-line
"last session recap" from the claude-mem digest (Step 3) so he sees both the documented status
and what was actually worked on most recently.

## Step 6 — Open the app in Chrome

Open the local buyer app in Chrome with the Claude-in-Chrome tools (not computer-use —
browsers are read-only there). Navigate to:

`file:///C:/Users/David/Projects/MarketSquare/marketsquare.html`

Confirm the page rendered. (If David asks for the live site instead, open `https://trustsquare.co`.)

## Finish

Recap in 3–4 lines: mount-guard result, claude-mem/last-session recap, deploy result, the
STATUS.md summary, and what you opened.

## Guardrails

- Run the steps in order. The torn-mount guard (Step 2) is a gate: if the mount is torn, stop
  before deploying and before any bash write-back.
- The claude-mem health/digest step (Step 3) is non-blocking — a failure there is reported but
  never halts the boot.
- If the deploy errors, stop and report before opening anything.
- Only run `deploy_marketsquare.bat`; don't run other `.bat` files without asking.
- Never type into terminal/console windows — launch the batch file by double-click.
- This command deploys to production. If David seems to want only a local preview, point him
  to `start_marketsquare.bat` instead and confirm before deploying.
