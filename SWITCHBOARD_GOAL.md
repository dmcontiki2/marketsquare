# SWITCHBOARD GOAL — the contract for the Fable 5.1 session

*Written 2 Oct 2026 from David's brief. Visual plan: `SWITCHBOARD_PLAN_2026-10-02.html`
(also in Projects\Visuals). Ruling: RUL-195. Run it as ONE goal, the same way as ONBOARDING_GOAL.md (RUL-096).*

## The goal (one sentence)
Make every AI model and every agent that TrustSquare uses a **swappable plug-in behind a
server-side Switchboard in Europe**. Each job runs on the cheapest model that passes its test,
fails over automatically on outage or throttling, and uses Claude only as the last resort.
David watches and steers all of it from a **Cockpit Mod** inside Claude Code.

## David's intent (his words, 2 Oct 2026, condensed)
- Quick, easy, fluid.
- Cheapest current AI plug-in models, replaced only when a model is down or throttled.
- **Claude is never the first option.** Claude is the design and management tool, so putting
  it in the app's path is a conflict of interest. Models and agents are plug-ins.
- Redundancy: European server, plus a separate redundant one elsewhere later.
- "Do not be restricted by these guidelines… improve on my vision." The plan improves on the
  brief in three places: the cockpit/switchboard split, rules-become-rails, and a Johannesburg node.

## Key fact about the Mod (read before Phase 4)
A Claude Code mod is a plugin of function hooks that runs **inside Claude Code** on David's PC
(panes, a band above the prompt, status line, toasts, slash commands, and `tool.call` hooks
that can refuse an action). It is NOT a runtime for the live app. The app's AI must keep running
on the server when no PC is on. Load the `plugin-authoring` skill before writing it.

## Finish lines — each one PROBED, never self-reported
| # | Phase | Finish line |
|---|-------|-------------|
| 0 | Look before touching | Ledger (`--shard` runs + `--combine=3`) and `rulings_check.py` run; live `/health` probed; a dated "true today" list written to `status.d/`. |
| 1 | Claude to the bottom rung | In `AI_BASELINE.json` and the live seam, every tier's order is non-Claude base → other-vendor non-Claude → EU open-weight → Claude last. Reaching Claude ALERTS and is time-boxed. New ledger entry proves no tier starts with Claude or fails over to it first. **Claude is never the first option.** |
| 2 | Model Scout | Weekly SERVER job (not a paid session) reads every wired vendor's catalog and prices, runs the golden set per tier on the live seam, and posts "promote?" cards with scores and the full field. It never promotes by itself (RUL-009, 14 Aug ruling). The first card exists. |
| 3 | Agent passports | One registry (brain = tier ladder, permissions, cost cap, schedule, health probe) for QA Bot, maintenance agent, BIT agent, CityLauncher, AdvertAgent, SellerScraper, MinutesMaker and Genie. A grep finds no hard-coded model id in any agent. QA Bot's brain stays non-Claude (Claude never audits Claude). |
| 4 | Cockpit Mod | Mod loads in Claude Code: AbovePrompt band (ledger, AI spend today, serving lane, alarms), Switchboard pane, Agent pane, toasts on failover or cost cap, one-tap permission requests (promote, drill, request_deploy). `tool.call` rails refuse Edit/Write on large /Projects files, direct scp of app code (RG-0023) and any Claude-first lane change. A refused Edit is demonstrated. |
| 5 | Data off the box | The SQLite DB is continuously replicated to EU object storage (for example Litestream to an EU R2 bucket). A restore test rebuilds it and row counts match. The Paris standby (a different company) is designed and priced; spending waits for David. |
| 6 | Quick & fluid | Speed budgets become ledger checks: first screen < 1.5 s on a mid phone, AI text starts < 1 s (streaming), no blank spinner > 3 s (fallback shown), ≤ 4 taps to target. ms.js (1.68 MB) is split. Design polish uses the `impeccable` skill if installed; otherwise design-critique + accessibility-review. |

## Rules that bind this goal
- Every fix gets a regression-ledger entry in the same session. Scope is stated (most faults are a class).
- Deploy only via `python3 scripts/request_deploy.py` (RUL-092). Never scp app code.
- File writes on /Projects go through bash/python with guards, never Edit/Write (Projects CLAUDE.md).
- Model choice stays David's (RUL-009). The goal builds the machinery; promotions are his taps.
- **Cost fence (as RUL-096e):** work inside the subscription. Never enable or consume Usage Credits.
  On hitting the limit, stop cleanly, save state to `SWITCHBOARD_STATE.md`, and resume after the reset.
- Reserved to David: money (standby servers), deletions, sending to third parties, lockout risk (RUL-027),
  vendor choice with money or jurisdiction at stake, and changing a ruling.
- No China-hosted endpoints (Add. 6). Chinese-origin open weights only on EU hosts.
- Reports to David are in plain language (Projects CLAUDE.md), with a NICE .docx for documents.

## Anti-gaming
A phase is done only when its finish line is probed. A ladder that only exists in a file but not in
the live seam is NOT done. A mod that is written but not loaded is NOT done.
