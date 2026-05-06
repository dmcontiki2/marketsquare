# TrustSquare · Session 45 — Start Prompt
# Paste this into Cowork at the start of the session.

Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.

## State going into Session 45
- **Legal entity:** Trustsquare (Pty) Ltd · Reg 2026/340128/07 · live
- **Platform:** TrustSquare at trustsquare.co · BEA v1.3.0 · clean slate
- **Listings:** 0 live · 70 demo_ listings across all 7 categories
- **Onboarding flow:** Verified end-to-end across all 7 categories (Session 44)
- **BEA fixes (Session 44):** trust_score stamped on publish · ai_sessions credited on registration · POST /users idempotent
- **NightlyScraper:** Removed from Task Scheduler — scraper design to be revisited

## Session 45 Goal: Paystack subscription + AI coach verification

### Priority tasks
1. **Paystack test mode** — complete a subscription payment flow end-to-end (buyer Tuppence top-up)
2. **AI coach verification** — verify advert-agent/coach fires correctly per category using real listing data from admin app
3. **Admin credential upload flow** — test Document Hub with a real listing: upload ID doc, verify trust score updates
4. **Gate sbTriggerMarketNote** — gate the inline AI market note behind subscription tier for free sellers

### Files and deploy
- marketsquare.html → `scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html`
- bea_main.py → `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` + restart
- **NEVER use Edit/Write tool on marketsquare.html or bea_main.py** — Python replace only
- After every HTML change: extract scripts + `node --check` before deploying
- SSH: run `bash load_sandbox_ssh.sh` first

## Operating rules reminder
- One task at a time, complete fully before starting next
- findListing(id) not LISTINGS[id] for BEA listings
- Quote all BEA listing ids in onclick: openDetail('${l.id}')
- activeCity = {id, name}, activeSuburb = {id, name} or null
- Geo API param is `country` (not `country_iso2`)
- Check Codex before adding business logic
- Append to CHANGELOG.md — done = working code AND changelog entry
- Git commits: ask David to run from PowerShell

## Session end checklist
1. Update STATUS.md — completed tasks → Last Completed, write Next Session
2. Append one paragraph per fix to CHANGELOG.md
3. Ask David to git commit + push from PowerShell
4. If cost model assumptions changed: note "Cost model impact:" in CHANGELOG.md
