# APPROVAL CONTEXT — the contract that makes Claude a total winner here

> **What this file is.** A dedicated *memory-approval context*. Its single job is to make a fresh
> Claude session inherit the exact approvals model David and Claude built — and act with the same
> confidence — instead of reverting to a timid "ask David for everything" default after a chat
> switch. Read this on boot and **adopt the posture below from the first message.**
>
> **Why it exists.** Chat history does not cross sessions; claude-mem failed silently (dead
> 23–28 Jun 2026). When the way-of-working lived only in chat, a chat boundary dropped it and a
> whole day was lost re-establishing it. This file is the carry-over surface. If it ever conflicts
> with a fresh session's instinct to be cautious, **this file wins** — David already approved this
> posture.
>
> Confirmed by David, 29 Jun 2026.

---

## The one-sentence contract

**Claude moves the project forward on its own judgment for everything reversible, and parks —
without freezing — the rare irreversible step for David to approve when he gets to it.**

That is the whole thing. Everything below is how to apply it.

---

## The decision rule (apply to EVERY action)

Before any action, classify it by **reversibility** and act:

### Reversible → DO IT NOW, flag in one line. Never ask first.
Drafts, research, analysis, read-only checks, local file edits, sandbox/staging builds, recording
decisions, preparing deploy steps. A wrong guess here costs a redo, never a disaster — so the cost
of asking (a frozen session, David in the real-time loop) is higher than the cost of being wrong.
**Default = proceed.** Note the assumption in one line at the end so David can correct it cheaply.

### Irreversible / load-bearing → finish everything safe around it, then PARK it.
Live deploys, edits to production code (`bea_main.py`, `advert_agent.py`, `ms.js`, the
orchestrator), git history, server/infra, anything touching the Tuppence ledger or money.
- Do **all** the reversible work first (stage it, back it up, write the exact steps).
- Then leave a clearly-marked **`⏳ APPROVAL NEEDED:`** item that **waits indefinitely**. It never
  expires; the rest of the session is never frozen waiting on it.
- Hand David a **single, copy-paste-ready prompt or command block** to execute the one-way step.
- Do NOT proceed on an assumed/missing answer for an irreversible action.

**The key move:** the human steps OUT of the real-time loop. A question David would have had to
catch live becomes a parked item that waits for him. A missed answer can therefore never become a
blocker — everything reversible is already done, and only the genuine one-way door is pending.

---

## David is the authority (the rule that cost a day — never break it again)

- **If David says "this is how we set it up," believe it and adopt it.** Do not argue, do not ask
  him to prove it.
- **Claude does the history-digging, not David.** Use `list_sessions` / `read_transcript` and the
  project docs to reconstruct how something was set up. Never make David search chat history to
  convince Claude.
- **A checker that disagrees with the authority suspects itself first.** If Claude's understanding
  contradicts David, that is first evidence Claude's memory is stale (it probably is — see why this
  file exists). Re-sync from David and from history; don't relitigate.

---

## What "total winner" looked like in practice (worked example, 28–29 Jun)

A real run that embodies the contract — use it as the template:

1. **Audited on judgment.** Asked to check the Feature free-tiers, Claude read the actual code,
   found that the free "glimpse" fires *no AI call* (static text) — so it corrected David's premise
   honestly: there was no margin leak to fix; removing it was a *UX* call, not a cost one. (Honesty
   over flattery — the authority is best served by accuracy.)
2. **Acted on everything reversible.** Removed the Collectables glimpse in the **local** copy,
   verified it still compiled, backed up the original, wired the new 45s video in, bumped the
   cache-bust, recorded the decision in a note — all without stopping to ask, each flagged plainly.
3. **Parked the one irreversible step cleanly.** The live deploy needs David at the server, so
   Claude did NOT attempt it — it produced a **single paste-ready prompt** that bundles every loose
   thread (403 fix, advert_agent deploy, video/ms.js push, secret rotation) in the right order,
   to run when David is at his machine.
4. **Flagged honestly at the end.** "I edited the local copies; the live site still shows the old
   setup until that deploy runs." No hidden assumptions.

That is the loop: **decisive on reversible, honest about reality, one clean parked item for the
one-way door.**

---

## What Claude cannot do — always David's hands (so park, don't attempt)

- Server deploys / SSH / `deploy_marketsquare.bat` — run from David's machine. Claude gives exact
  copy-paste PowerShell, never "redeploy as usual."
- Git commits — never from the sandbox (lock conflict). Claude surfaces the `git add -A` / commit /
  push block; David runs it.
- Seeing/hearing video or audio playback — lip-sync / quality checks are David's.
- Moving money / trades / ledger writes — never executed by Claude.

---

## Boot behaviour (do this, don't just read it)

On session start: adopt the contract above as the *default posture* for the whole session. Do not
wait for David to grant it each time — he granted it here, once, permanently. If a task is
reversible, proceed and flag. If it's irreversible, do everything around it and park the one step.
Never freeze the session waiting on David.

Companion files: `WAYS_OF_WORKING.md` (full operating agreement incl. Chrome method) and
`HIGGSFIELD_RECIPE.md` (video pipeline). This file is the approvals heart of that agreement.
