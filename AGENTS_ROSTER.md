# AGENTS — doctrine, roster, stand-up (29 Jul 2026, David's ruling)

## THE DOCTRINE (binding rule)
Agents are defined by ROLE and CAPABILITY — never by, or hardcoded to, an AI.
Every agent spec names: its role, its inputs/outputs, its capabilities, its
escalation rules, and a SWAPPABLE ENGINE BINDING. David can re-bind any agent to
a different AI (or a deterministic script, or a human) per context, without the
rest of the system noticing. In-app precedent: ai_provider.py (the AI-swap seam).
No agent spec may name a model as part of its identity; bindings live in one
place per agent and are configuration, not design.

## Governance — the daily stand-up
A scheduled cloud session runs DAILY as part of the daytime pulse report:
pulse verdict first, then per-agent: status · progress · current batch ·
blockers · any safety/legal/cost item (those FIRST, as solution list + tick
actions). Sources: this file + each agent's spec doc (via the connected
Projects folder, else the published copy at /static/agents_status.md).

## Roster
| Agent | Role | Spec / engine binding today (configuration, not identity) | Status — PROBED 2026-09-27 19:2xZ |
|---|---|---|---|
| Maintenance | Fault (NCR) lane: adjudicate→fix→verify→harden, majors first | Spec: MAINTENANCE_AGENT.md · runner: `scripts/maintenance_agent.py` · spine: server-resident, three runs a day (05:20Z / 11:20Z / 17:20Z) · brain: whatever `AI_BASELINE.json` binds, read live from `/dashboard/maint` as `brain_lane` / `brain_model` | **LIVE.** Heartbeat `20260927T172042Z` at 17:20:43Z (1.9 h, inside the 12 h bar), mode LIVE, phase postlaunch, armed true, live true, brain GREEN, lane `openai`, model `gpt-5.6-luna`, probe 200, seen 0 acted 0. 7 d spend **$0.00013 / 21 calls** against a $0.50/day budget. TOTAL AUTONOMY ruled 29 Jul (no veto; mechanical gates + auto-rollback + kill switch) |
| Pulse/Monitor | Site heartbeat, amber/red alerts | `/pulse` skill + this stand-up + server mailer | live — this run's pulse is logged in PULSE_LOG.md |
| BIT Tester | Build-integrity board: functional + negative self-test, on a timer and after each deploy | **TWO vantages, deliberately:** `bit/bit_runner.py` (edge, this stand-up) and the served `ops/bit/bit_runner.py` under `trustsquare-bit.timer` every 15 min on the box, both reading the same `bit_registry.json`. Cycle wrapper: `ops/bit/bit_cycle.py`. Deterministic engine, no model | live — 8/8 PASS, worst 0, failing `[]`, ran 19:05:19Z, base `http://localhost:8000`. The two copies are now held together by `scripts/test_bit_boards_agree.py` (BIT-BOARD-DRIFT-1) |
| QA Bot | Adversarial route walk as a deploy gate: every route × persona, fail-closed | `qa_bot/qa_bot.py`, run by `server_deploy.sh`; vantage chosen at run time by `choose_vantage()` | live and fail-closed. **Narrower than it reads:** the front-door canary cannot pass from on the box (the origin accepts only Cloudflare's ranges and the bot pins the name to 127.0.0.1), so runs fall back to the app's own loopback port and name nginx + the edge as not covered — QA-PIN-TRUTH-1, corrected at source 27 Sep |
| Outreach/Enrolment | Agency wave prep and enrolment links, gated | `POST /agencies/wave-prep` (admin-only, no loopback pass) · `scripts/wave_hygiene_witness.py` · `scripts/enrol_import.py` · `scripts/mint_enrol_link.py` · runbook AGENCY_WAVE_RUNBOOK.md | prep lane built and admin-gated. **NOT PROVEN by this stand-up:** no wave has been sent, and no send was probed |
| Feedback Triage | Voice-of-customer lane: listen→synthesize→prioritize→route; never fixes — fix-now routes to Maintenance by reference; design-change items feed the shared design backlog | `/feedback`, `/fixback` skills + FEEDBACK.md register | live, session-invoked — RULED a separate agent from Maintenance, 5 Aug 2026 |
| Design | Proposed direction for a design-change dossier, on demand | `/admin/maint/brain` `task="design"` (RUL-013's allocated lane); caller: PATH_B via DESIGN-ROUTE-1, filing into DESIGN_BACKLOG.md | wired and called since 26 Sep. **Envelope DECLARED, not measured** (`AI_BASELINE.json tiers/design`), and the dossier GATE line is written EMPTY on purpose — an absent gate means NOT APPROVED, DO NOT BUILD; binding the designer role is David's |
| Video Pipeline | Launch clips generate/QC/package | `/launch-series`, `/video-qc`, `/youtube-pack` | live, session-invoked. Not exercised this run |

**Every engine binding above is configuration.** Re-binding any of them is a config change, not a
roster change, and no row may name a model as part of its identity (the doctrine above). The
Maintenance brain's live binding is read from `/dashboard/maint`, not asserted here, precisely so
this file cannot go stale about it again.

**CORRECTED 2026-09-27 (stand-up, mechanical — SO-3/RUL-037). This table had not been touched since
5 Aug and four of its cells were false, each in the proxy-assertion class this project keeps
catching:** (i) the BIT row's engine binding was `trustsquare-bit-agent/bit_cycle.py` — **that
directory does not exist**; the real files are `ops/bit/bit_cycle.py` and the two `bit_runner.py`
copies. (ii) The Outreach row named `wave_runner.py + emailer.py`: **`wave_runner.py` exists
nowhere in the repo**, and the only `emailer.py` is `_verify_rig/letters/emailer.py`, a test rig —
so the row pointed at a rig and a file that was never written, while the real lane is the admin
`POST /agencies/wave-prep` route. (iii) The Maintenance row read *"building B1–B4, rehearsed by
~22 Aug"* five weeks after that date, and *"brain: Claude scheduled sessions for launch"* while the
live brain is the `openai` lane on `gpt-5.6-luna` — a model binding that was both hardcoded, which
the doctrine at the head of this file forbids, and wrong. (iv) The last row said *"discussion
tonight"*, written 5 Aug. Two agents that have been live for weeks — the QA Bot and the Design tier
— were not on the roster at all. Each status cell now carries the dated probe behind it, and where
a capability is unproven (the Outreach send) it says so instead of claiming "gated".

Roster changes and engine re-bindings are recorded HERE, dated, David-ruled.

- **5 Aug 2026 (David):** Maintenance vs Feedback-Triage RULED as TWO agents sharing ONE
  intake (REPORT tab / email / error log — the reporter never picks a lane; triage routes).
  Hand-over contract + full boundary: MAINTENANCE_AGENT.md, LAUNCH BOUNDARY REDRAW section.
  The designer approval gate sits on the shared design backlog both agents feed — on
  neither agent itself. Path A total autonomy remains Maintenance-only.
