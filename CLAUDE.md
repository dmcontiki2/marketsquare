# MarketSquare — Project Intelligence

## What this project is
A **mobile-first local marketplace** connecting buyers with trusted, anonymous sellers via a Tuppence introduction currency. Deployed at **trustsquare.co**. Three core files:
- `marketsquare_v8_6b.html` — buyer-facing marketplace app (FEA) · served as index.html
- `marketsquare_admin_v1_1.html` — seller onboarding admin dashboard · served as admin.html
- `Solar_Council_Codex_v4_1.docx` — canonical product rules, design principles, and version history

**This is a marketplace app, not a game.**

## Agent roles
This project uses a multi-agent Claude Code workflow. Each agent has a lane:
- **Architect agent** — reads the Codex only, owns system design and rule arbitration
- **Frontend agent** — works on `marketsquare_v8_6b.html`, references Codex excerpts only
- **Admin agent** — works on `marketsquare_admin_v1_1.html`, references Codex excerpts only

Read `AGENT_BRIEFING.md` at the start of every session — it is the single source of truth for all three agents.

## Rules for every agent
- Never rewrite large sections without being asked
- Always check Codex rules before adding any business logic
- Prefer small, focused changes over sweeping refactors
- After every change: what changed, why, and what to watch
- Use /compact when context starts filling up

## Operating principles

**Uncertainty:** Make the best guess, implement it, then add a one-line flag at the end of the response. Never stop mid-task to ask.

**Change size:** Maximum one feature or one bug fix per task. If a change touches more than one file section, split it and complete each part fully before starting the next.

**Git commits:** Auto-commit after every completed task with a clear descriptive commit message. Do not wait for user approval.

**Definition of done:** Code works AND a one-paragraph summary has been appended to `CHANGELOG.md`. Only update `CLAUDE.md` for major structural changes, not routine tasks.

**Conflict resolution:** The Architect agent arbitrates all conflicts between agents using the Codex as source of truth. Only escalate to the user if the Codex cannot resolve the conflict.

## Server deployment
- Server: Hetzner CPX22 · 178.104.73.239 · Ubuntu 24.04
- Nginx serves from: /var/www/marketsquare/
- Deploy buyer app: `scp marketsquare_v8_6b.html root@178.104.73.239:/var/www/marketsquare/index.html`
- Deploy admin tool: `scp marketsquare_admin_v1_1.html root@178.104.73.239:/var/www/marketsquare/admin.html`
- Reload nginx after config changes: `nginx -s reload`

## Key technical notes (Session 3)
- BEA listing ids are strings: 'bea_N' — always use findListing(id) not LISTINGS[id]
- All onclick handlers interpolating listing ids must quote them: openDetail('${l.id}')
- normCat() in loadLiveListings() normalises BEA category strings to CATS keys
- Magic link URL params: ?magic=1&name=...&email=...&cat=...&city=...
- Placeholder listings have ids starting with 'ph_' — used to bypass paused filter in renderGrid()

## Current development status
- Launch city: Pretoria, South Africa · 23 / 60 founding sellers
- BEA v1.1.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- GitHub backup: github.com/dmcontiki2/marketsquare
- Paystack: test mode (live mode pending CIPC registration)
- Next milestone: Maroushka real listings · n8n email notifications · Hetzner Object Storage
