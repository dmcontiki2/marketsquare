# TrustSquare · Session 44 — Start Prompt
# Paste this into Cowork at the start of the session.

Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.

## State going into Session 44
- **Legal entity:** Trustsquare (Pty) Ltd · Reg 2026/340128/07 · live
- **Platform:** TrustSquare at trustsquare.co · BEA v1.3.0 · clean slate
- **Listings:** 0 live · 70 demo_ listings across all 7 categories
- **Trust scores:** Recalculated from actual signal points — defensible
- **All demo listing bugs fixed:** Local Market chip, cat normalisation, home tile count, seller CV availability

## Session 44 Goal: End-to-end seller onboarding test

Publish a real listing in each category and verify the full flow works correctly.

### Flow to test per listing
1. Open admin app → fill in listing details for the category
2. AI coach note fires after key field filled (subject / trade_type / etc.)
3. Trust score calculates correctly from entered credentials
4. Submit → draft preview shows correctly
5. Tier picker → EULA → Publish
6. Listing appears in buyer app alongside demo listings
7. Detail view: chips, trust badge, photos all correct

### Categories to test (in order)
1. **Property** — private seller, verify Established tier (~44), no PPRA tip
2. **Tutors** — AI note fires on subject fill, SACE + police clearance chips show
3. **Services** — AI note fires on trade_type, Red Seal + insurance chips show
4. **Adventures** — FGASA chip shows, TGCSA if accommodation
5. **Collectors** — authentication cert chip, amber colour
6. **Cars** — NATIS chip, private seller declaration visible
7. **Local Market** — photo uploads, home tile slideshow updates

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
