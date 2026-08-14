# Pre-permissions — the whole list, granted once, not piecemeal

**Why this file exists (David, 14 Aug 2026):** a per-session, human-gated grant sitting in the
inner loop of a long run is a guaranteed stall — the only question is at which item. David asked
for the COMPLETE set up front so he can grant once and go to bed. Asking for them one at a time,
as each becomes the next blocker, is the failure mode this file kills.

**Rule for every session:** read this file at boot, request EVERYTHING in section A in ONE batch
while David is at the keyboard, verify each responds, then start work. Never start a run with an
unverified grant. Never discover a missing grant at item 1 of 54.

---

## A. Grants needed BEFORE any unattended / overnight run — request as one batch

| # | Grant | Needed for | Persists? |
|---|-------|-----------|-----------|
| A1 | Folder: `C:\Users\David\Projects` | everything — repo, scripts, docs, assets | auto-mounted, no action |
| A2 | Chrome extension connected (claude-in-chrome) | Higgsfield photo runs; live-site verification through the reviewer gate | per session |
| A3 | computer-use grant: **Chrome** | driving Higgsfield, reading live pages | per session |
| A4 | computer-use grant: **Command Prompt / Explorer** | running the `.bat` files (deploy, media_push, commit, rotate) | per session |
| A5 | Chrome site permission: auto-download on `higgsfield.ai` | photo runs download without a click each time | granted 13 Aug, persists |
| A6 | Chrome download location set to `C:\Users\David\Projects\MarketSquare\_incoming` | kills the Downloads-folder grant permanently (see B1) | one-time Chrome setting |

## B. Grants ELIMINATED — do not request these again

| # | Was | Killed by |
|---|-----|----------|
| B1 | Folder: `C:\Users\David\Downloads` (per-session, needed by `claim_super.py` / `claim_photos.py` on EVERY image) | **GRANT-KILL-1, 14 Aug 2026** — both scripts now read `MarketSquare/_incoming`, which is inside the always-mounted Projects tree. Falls back to the old Downloads mount if present. Requires A6 set once in Chrome. |

## C. Stays David-only, permanently — never pre-granted, never batched away

Secrets and key material · deploys and releases · anything that spends money · anything sent to a
real customer · deletions. These are meant to interrupt. They are not the problem this file solves.

**Terminal-paste exposure (David, 14 Aug 2026):** pasting raw terminal/SSH output into chat has put
credential-adjacent material in front of Claude. That is a workflow fault, not David's. Standing
correction: when Claude needs server output, it asks for the SPECIFIC lines, or the command is run
through a script that redacts before it is ever read. Never "paste the whole thing".

---

## D. The one-line boot check every session runs

    ls -d /sessions/*/mnt/Projects && ls -d MarketSquare/_incoming

Both present = photo/claim lane is live. If either is missing, request the batch in section A
BEFORE generating anything — not after.
