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
| Agent | Role | Spec / engine binding today | Status |
|---|---|---|---|
| Maintenance | Fault (NCR) lane: adjudicate→fix→verify→harden, majors first (stale 'one-word gate' wording removed — retired by the 29 Jul evening ruling) | MAINTENANCE_AGENT.md · spine: server-resident (API-billed, swap seam); brain: Claude scheduled sessions for launch → re-bind to dedicated Hetzner worker when launch rush trickles (ruled 29 Jul) | **TOTAL AUTONOMY ruled 29 Jul (no veto; mechanical gates + auto-rollback + kill switch) — building B1–B4, rehearsed by ~22 Aug** |
| Pulse/Monitor | Site heartbeat, amber/red alerts | /pulse skill + server mailer | live |
| BIT Tester | Functional + negative self-test each deploy | trustsquare-bit-agent/bit_cycle.py | live (deterministic engine) |
| Outreach/Emailer | Wave sends, gated | wave_runner.py + emailer.py (--no-ai default) | built, gated for wave-1 |
| Feedback Triage | Voice-of-customer lane: listen→synthesize→prioritize→route; never fixes — fix-now routes to Maintenance by reference; design-change items feed the shared design backlog | /feedback, /fixback skills + FEEDBACK.md register | live, session-invoked — RULED a separate agent from Maintenance, 5 Aug 2026 |
| Video Pipeline | Launch clips generate/QC/package | /launch-series, /video-qc, /youtube-pack | live, session-invoked |
| (further agents) | — | to be defined with David | discussion tonight |

Roster changes and engine re-bindings are recorded HERE, dated, David-ruled.

- **5 Aug 2026 (David):** Maintenance vs Feedback-Triage RULED as TWO agents sharing ONE
  intake (REPORT tab / email / error log — the reporter never picks a lane; triage routes).
  Hand-over contract + full boundary: MAINTENANCE_AGENT.md, LAUNCH BOUNDARY REDRAW section.
  The designer approval gate sits on the shared design backlog both agents feed — on
  neither agent itself. Path A total autonomy remains Maintenance-only.
