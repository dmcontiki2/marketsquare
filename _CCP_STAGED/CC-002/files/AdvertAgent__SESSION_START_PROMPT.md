# AdvertAgent · Session Start Prompt
# Paste this into Claude Code at the start of every session.

Read STATUS.md first, then AGENT_BRIEFING.md, then CLAUDE.md. They are the source of truth.
Also read PRINCIPLE_REQUIREMENTS.md Part G (G1–G4) — the founding constraint set for this project.

## What this project is
A seller-facing AI listing coach embedded inside trustsquare.co. Helps sellers write better
listings and improve Trust Score before publishing. Optional — sellers can publish without it.
Code lives in the MarketSquare files, not here. This folder holds docs and principles only.

## Code lives in MarketSquare
- `C:\Users\David\Projects\MarketSquare\marketsquare.html` — all #screen-aa-* screens + aaDB
- `C:\Users\David\Projects\MarketSquare\bea_main.py`       — /advert-agent/* endpoints

## Key BEA endpoints
- `POST /advert-agent/status`    — check free session + pack balance
- `POST /advert-agent/coach`     — AI coaching call (Haiku, gated by subscription)
- `POST /advert-agent/publish`   — PDF + pending draft creation
- `POST /advert-agent/buy-pack` — **410 Gone** (packs retired 6 Jun 2026; per-use HOLD via `/tuppence/ai-commit`+`ai-settle`)

## The 4-stage flow
| Stage | Screen              | AI call? | Cost                  |
|-------|---------------------|----------|-----------------------|
| 1     | #screen-aa-detail   | No       | Free                  |
| 2     | #screen-aa-photos   | No       | Free                  |
| 3     | #screen-aa-coach    | Yes      | Free (1st) then 1T/8-pack |
| 4     | #screen-aa-publish  | No       | Free                  |

## Tuppence language rules — CRITICAL
Two distinct uses of Tuppence — NEVER conflate them:
- Introduction Fee: paid by BUYER on seller accepting intro (governed by A1)
- AI features: in-app guidance FREE; advanced AI features paid by SELLER per use in Tuppence (AI-uses packs RETIRED 6 Jun 2026; governed by G1)

Mandatory copy:
- Pack button: RETIRED — packs gone; advanced AI per-use in Tuppence
- Wallet card: "AI feature credits" (canon CC-002)  ← legacy titles retired
- Subtitle:      "Not used for introductions"
- Stage 3 zero: "Top up Tuppence — advanced AI is priced per use"
- Free badge:   "1 free coaching session included"  ← NOT "Free"

## Known open issues (as of Session 7 · 14 April 2026)
1. ANTHROPIC_API_KEY not yet set in /etc/environment on Hetzner — coach endpoint not live
2. PDF generation: /advert-agent/publish returns pdf_url: null — WeasyPrint not integrated
3. (RETIRED) buy-pack flow — endpoint 410; per-use HOLD pricing replaces packs (CC-002)
4. Cross-device pickup code: drafts in IndexedDB on device only, no sync yet

## Operating rules reminder
- One task at a time, complete fully before starting next
- NEVER call Claude API without confirming active subscription (G2)
- NEVER compromise seller anonymity — every feature must preserve A2
- Secrets always from `.env` — never hardcoded
- AI model is `claude-haiku-4-5-20251001` — do not change without pricing review
- Surgical edits only — no large rewrites
- Check Codex before adding business logic
- Auto-commit after each completed task
- Append to CHANGELOG.md — done = working code AND changelog entry

## Deploy (changes go to MarketSquare files — deploy via MarketSquare)
```
cd C:\Users\David\Projects\MarketSquare
deploy_marketsquare.bat
```

## Session end checklist
1. Update STATUS.md — move completed tasks, write next task
2. Append one paragraph per completed task to CHANGELOG.md
3. Git commit: "Session N complete"
4. Push to GitHub
