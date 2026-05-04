# MarketSquare · Session 41 — Start Prompt
# Paste this into Cowork at the start of the session.

Read STATUS.md and AGENT_BRIEFING.md first — they are the source of truth.

## Session 41 Goal: Cross-category testing + any fixes found

We are testing a fresh listing in every category to verify the full sell flow and listing detail view work correctly end-to-end. For each category below, I will publish a test listing and you will help diagnose and fix anything that looks wrong.

### Categories to test (in order)
1. **Tutors** — AI market note fires after subject filled, trust score ≥ 40, credential chips show in detail view
2. **Services** — AI note fires after trade_type filled, trust score correct, chips show
3. **Collectors** — amber chips show in detail view, trust score correct
4. **Cars** — blue chips show, private seller gets no PPRA/agent tip, trust score correct
5. **Local Market** — list with a photo → home tile crossfade animates (needs 2+ LM listings with photos)
6. **Photo captions** — on any new listing, add a caption to at least one photo → verify frosted-glass overlay appears in detail view

### Known state going into this session
- Property listings working well (tested Session 39/40)
- Featured row cards: consistent layout, trust badge floats over photo ✓
- For You cards: same layout as Featured, price formatted with R symbol ✓
- Photo captions render as bottom-right frosted pill ✓
- Photos preserved on PUT (AI description save no longer wipes photos) ✓
- For You tap opens correct listing ✓

### Files and deploy
- marketsquare.html → `scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html`
- bea_main.py → `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` + `ssh root@178.104.73.239 "systemctl restart marketsquare"`
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
