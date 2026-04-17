# MarketSquare · Session Start Prompt
# Paste this into Claude Code at the start of every session.

Read STATUS.md first, then AGENT_BRIEFING.md. They are the source of truth.

## Working files (local names → server names)
- marketsquare.html → index.html (buyer app)
- marketsquare_admin.html → admin.html (admin tool)
- bea_main.py → main.py (BEA backend)
- Solar_Council_Codex_v4_5.docx — canonical rules (upload to Claude Chat if needed)
- Cost_Breakdown_GlobalLaunch.xlsx — live cost model (upload to Claude Chat when flagged)

## Deploy (or use deploy_marketsquare.bat)
```
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
ssh root@178.104.73.239 "systemctl restart marketsquare"
```

## Operating rules reminder
- One task at a time, complete fully before starting next
- Use findListing(id) not LISTINGS[id] for BEA listings
- Quote all BEA listing ids in onclick handlers: openDetail('${l.id}')
- activeCity is {id, name}, activeSuburb is {id, name} or null
- Geo API param is `country` (not `country_iso2`)
- Check Codex before adding business logic
- Auto-commit after each completed task
- Append to CHANGELOG.md — done = working code AND changelog entry
- BEA FastAPI route order: `/listings/mine` MUST appear before `/listings/{id:int}` to avoid "mine" being cast to int
- Edit auth: PUT /listings/{id}?email= uses email match; NULL seller_email accepts any email and stamps it (no API key needed for sellers)
- listing_versions table archives full JSON snapshots — version_num increments per listing
- ⚠️ /dev/credit endpoint and Dev Tools nav tab MUST be removed before public launch

## Session end checklist
1. Update STATUS.md — move completed tasks, write next task
2. Append one paragraph per completed task to CHANGELOG.md
3. Git commit: "Session N complete"
4. Push to GitHub
5. If any cost model assumptions changed this session, note "Cost model impact:" in CHANGELOG.md
