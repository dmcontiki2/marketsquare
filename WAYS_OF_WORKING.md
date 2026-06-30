# WAYS OF WORKING — David & Claude operating agreement

> **Purpose.** This file is the durable operating agreement between David and Claude. Chat
> history does NOT carry across a new session; claude-mem can fail silently (it was dead
> 23–28 Jun 2026). The ONLY thing that reliably survives a chat boundary is what is written
> to a file a new session reads at startup. So this file exists to make the way-of-working
> carry over **without David having to re-establish it every time**.
>
> A new session must **read this and adopt it on boot** — not revert to asking David to
> re-explain how approvals, Chrome, and the video pipeline were set up.
>
> Reconstructed 29 Jun 2026 from the 24–28 Jun video sessions, `HIGGSFIELD_RECIPE.md`,
> `MORNING_REPORT_28JUN.md`, `SESSION_HANDOFF_2026-06-29_videos.md`, and the CLAUDE.md
> approvals rules. Confirmed by David.

---

## 1. The approvals model — already agreed, do NOT re-litigate it

David is a single point of failure on real-time questions, so the process is designed *around*
that. Every action is classified by **reversibility** and acted on accordingly:

- **Reversible work** — drafts, research, sandbox/isolated builds, local file edits, docs,
  analysis, read-only checks. → **Proceed on best judgment and flag the assumption in one line
  at the end.** Do NOT stop mid-task to ask. A wrong guess costs a redo, never a disaster.

- **Irreversible / load-bearing work** — live deploys, edits to production code
  (`bea_main.py`, `advert_agent.py`, `ms.js`, the orchestrator), git history, server/infra
  changes, anything touching the Tuppence ledger or money. → **Finish all safe work around it,
  then park a `⏳ APPROVAL NEEDED:` item that waits indefinitely.** Never freeze the session
  waiting on it. David approves when he gets to it.

**A new session adopts this immediately.** It does NOT revert to "ask David to do everything."
That reversion is the specific failure this file prevents.

> The approvals contract has its own dedicated memory context: **`APPROVAL_CONTEXT.md`** — read it
> on boot and adopt its posture from the first message. It holds the one-sentence contract, the
> decision rule, and the worked "total winner" example.

---

## 2. David is the authority — when he says "this is how we set it up," believe it

This is the rule that cost a full day after a chat switch (28 Jun): a fresh session dropped the
operating agreement, reverted to asking David to do everything, and then *did not believe David*
when he explained how it had been set up — forcing him to dig through chat history to prove it.

The rule, going forward:

- **If David states how a process was established, that is the source of truth.** Adopt it.
- **Claude does the history-digging, not David.** Claude has `list_sessions` / `read_transcript`
  and the project docs. Reconstruct the agreement from history yourself; never make David prove
  it to you.
- **A checker that disagrees with the authority suspects itself first.** If Claude's
  understanding disagrees with David, the disagreement is first evidence that Claude's memory is
  stale — re-sync from David and from history, don't relitigate.

---

## 3. Chrome way-of-working (browser automation)

Drive Chrome via the **Claude-in-Chrome MCP**, not pixel coordinates.

- **Click by element-reference** (`find` → element `ref`), NOT fixed coordinates. This is *the*
  fix that made clicks reliable regardless of zoom/layout/view. It was the single unlock that
  turned a miss-prone run into a zero-miss run.
- **Verify state after every submit** (e.g. "Processing" appears) before moving on.
- The **"fullscreen renderer" Chrome view shifts buttons** and breaks fixed-coord clicks — turn
  it off, or use element-ref.
- **David must be logged in** to the target site (e.g. Higgsfield) in the controlled tab.
- **No-API tools (Higgsfield):** assets come down via the browser **Download** button into
  `C:\Users\David\Downloads`, which must be connected via `request_cowork_directory` — it is NOT
  mounted by default. Once connected it is at `/sessions/<id>/mnt/Downloads`.

---

## 4. The Higgsfield video pipeline (proven, David-approved)

Full, current detail lives in **`feature-videos/production-kit/cast/HIGGSFIELD_RECIPE.md`** —
read it before touching any video work. Summary of the proven path:

1. Assets → find cast portrait → "..." → **Open** (the menu has no "use as reference"; open the
   detail view first).
2. Click the yellow **"Turn to video"** — opens Create Video with that portrait attached.
3. **Clear the sticky prompt** (the box keeps the previous clip's text): click in, `Ctrl+A`,
   retype. The reference swaps via Turn-to-video, but the PROMPT does not.
4. Settings: **Kling 3.0**, **5s**, **9:16**. Cost = **10 credits/clip**.
5. **Generate** via element-ref → verify Processing → plays in ~1–2 min (720p).
6. **Wait for ALL queued clips to finish before zip-download** — downloading mid-render misses
   clips. Queue up to **8 in parallel** (plan allows it). **Do not buy boosts.**
7. Download → file by timestamp (newest `hf_*.mp4`) → `cp` to the clip folder with a meaningful
   name → ffprobe (expect 720x1280, H.264/AAC, ~5s) → ffmpeg stitch.
8. **Clear the sticky reference** (× on the thumbnail corner) when switching characters, or the
   new face gets contaminated by the old reference.

---

## 5. What Claude cannot do — always David's hands

- **Server deploys / SSH / `deploy_marketsquare.bat`** run from David's machine. Claude provides
  exact, copy-paste-ready PowerShell — never "redeploy as usual."
- **Claude cannot see or hear video/audio playback.** Lip-sync, voice, and clip-quality checks
  are David's.
- **Git commits never run from the sandbox** (index.lock conflict). Claude surfaces the
  PowerShell block (`git add -A` / commit / push); David runs it.
- **Money actions** (trades, transfers, ledger writes) are never executed by Claude.

---

## Maintenance

When the way-of-working changes, update THIS file in the same session (same spirit as the
canon/demo-mode rules). It is the carry-over surface — if it drifts, the next session inherits
the drift.
