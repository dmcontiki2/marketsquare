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
| Maintenance | Complaint→fix pipeline, majors first, one-word daily ship gate | MAINTENANCE_AGENT.md · triage: Haiku via BEA; fix sessions: Claude scheduled task | **RULED 29 Jul — building B1–B4, rehearsed by ~22 Aug** |
| Pulse/Monitor | Site heartbeat, amber/red alerts | /pulse skill + server mailer | live |
| BIT Tester | Functional + negative self-test each deploy | trustsquare-bit-agent/bit_cycle.py | live (deterministic engine) |
| Outreach/Emailer | Wave sends, gated | wave_runner.py + emailer.py (--no-ai default) | built, gated for wave-1 |
| Feedback Triage | Tester/seller feedback → register → fixes | /feedback, /fixback, /fix skills | live, session-invoked |
| Video Pipeline | Launch clips generate/QC/package | /launch-series, /video-qc, /youtube-pack | live, session-invoked |
| (further agents) | — | to be defined with David | discussion tonight |

Roster changes and engine re-bindings are recorded HERE, dated, David-ruled.
