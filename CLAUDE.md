# MarketSquare — Project Intelligence

## What this project is
A browser-based trading game built on the Solar Council universe. Three core files:
- marketsquare_v8_6b.html — player-facing UI and game logic
- marketsquare_admin_v1_1.html — admin/moderation dashboard
- Solar_Council_Codex_v4_0.docx — the canonical game rules, lore, and design principles

## Agent roles
This project uses a multi-agent workflow. Each agent has a lane:
- Architect agent: reads the Codex only, owns game logic and rule decisions
- Frontend agent: works on marketsquare_v8_6b.html, references Codex excerpts only
- Admin agent: works on marketsquare_admin_v1_1.html, references Codex excerpts only

## Rules for every agent
- Never rewrite large sections without being asked
- Always check Codex rules before adding game logic
- Prefer small focused changes over sweeping refactors
- After every change summarise: what changed, why, and what to watch
- Use /compact when context starts filling up

## Operating principles

**Uncertainty:** Make the best guess, implement it, then add a one-line flag at the end of the response. Never stop mid-task to ask.

**Change size:** Maximum one feature or one bug fix per task. If a change touches more than one file section, split it and complete each part fully before starting the next.

**Git commits:** Auto-commit after every completed task with a clear descriptive commit message. Do not wait for user approval.

**Definition of done:** Code works AND a one-paragraph summary has been appended to CHANGELOG.md. Only update CLAUDE.md for major structural changes, not routine tasks.

**Conflict resolution:** The Architect agent arbitrates all conflicts between agents using the Codex as source of truth. Only escalate to the user if the Codex cannot resolve the conflict.

## Current development status
- Files loaded: all three present in project root
- Multi-agent workflow: being established
- Next milestone: to be defined in session
