# TrustSquare — Project Intelligence

## What this project is
A **mobile-first local marketplace** connecting buyers with trusted, anonymous sellers via a Tuppence introduction currency. Deployed at **trustsquare.co**. Core files:
- `marketsquare.html` — buyer-facing marketplace app (FEA) · served as index.html
- `marketsquare_admin.html` — seller onboarding admin dashboard · served as admin.html
- `bea_main.py` — FastAPI backend (BEA) · served as main.py on server
- `Solar_Council_Codex_v4_7.docx` — canonical product rules (controlling); `Solar_Council_Codex_v4_8_DRAFT.docx` — staged next version, pending CC-001/CC-002 landing
- `Cost_Breakdown_GlobalLaunch.xlsx` — live cost model · updated in Claude Chat when assumptions change

**This is a marketplace app, not a game.**

## Agent roles
This project uses a multi-agent Claude Code workflow. Each agent has a lane:
- **Architect agent** — reads the Codex only, owns system design and rule arbitration
- **Frontend agent** — works on `marketsquare.html`, references Codex excerpts only
- **Admin agent** — works on `marketsquare_admin.html`, references Codex excerpts only

Read `AGENT_BRIEFING.md` at the start of every session — it is the single source of truth for all three agents.

## Rules for every agent
- Never rewrite large sections without being asked
- Always check Codex rules before adding any business logic
- Prefer small, focused changes over sweeping refactors
- After every change: what changed, why, and what to watch
- Use /compact when context starts filling up

## Demo-mode wiring rule (AI-enforced)
Any new FEA feature that calls the BEA API **must** include a `DEMO_MODE` guard:
```javascript
if (DEMO_MODE) {
  // serve from LISTINGS / SELLERS arrays
} else {
  // call BEA API
}
```
The agent must verify **both branches** work before marking the task done. This is not optional and must not be delegated to the human to remember. When adding any new API call, immediately ask: *"Does this need a demo fallback?"* If yes, implement it in the same task. Run a post-change audit confirming demo listings still show correctly across all 4 cities.

## Demo data integrity rule (AI-enforced)
After any change to `LISTINGS` or `SELLERS`, run the audit script `/tmp/full_audit.py` on the server before closing the session. It checks: sellerIdx range, sellerIdx category match, currency prefix, trust score range (70–96), LM title presence. Zero issues required before CHANGELOG is written.

## Operating principles

**Uncertainty:** Make the best guess, implement it, then add a one-line flag at the end of the response. Never stop mid-task to ask.

**Approvals & blockers (David is a single point of failure on real-time questions — design around it):** Never let a missed answer freeze progress. Classify every action by reversibility and act accordingly:
- **Reversible work → proceed and flag.** Drafts, research, isolated/sandbox builds, docs, analysis, read-only checks, anything not touching live state. Make the best-judgment call, do it, and note the assumption in one line at the end. A wrong guess costs a redo, never a disaster. (This is the Uncertainty rule above — proceeding is the default.)
- **Irreversible / load-bearing work → finish all safe work first, then park a waiting APPROVAL item.** Live deploys, edits to production code (`bea_main.py`, `fix.py`, `ms.js`, the orchestrator, etc.), git history, server/infra changes, anything touching the Tuppence ledger or money. Complete every reversible thing around it, then leave a clearly-marked `⏳ APPROVAL NEEDED:` item that **waits indefinitely** — it never expires and the rest of the session is never frozen waiting on it. David approves when he gets to it; only that one one-way step pends. Do NOT proceed with an irreversible action on an assumed/missing answer.
- **Why this works:** the human moves out of the real-time loop. A question David must catch live becomes a parked item that waits for him, so a missed answer can never become a blocker — everything reversible is already done, and only the genuine one-way door is pending.
- **No floating "later"s — do it now or it goes on the one list.** Never leave a follow-up dangling in a chat thread. If it's reversible and small, do it immediately in the same session. If it genuinely can't be done now (needs David's browser, an external approval, a separate focused session), it goes on the single **`📌 Deferred items`** list at the top of `BACKLOG.md` with a date — nowhere else. That list is surfaced in every morning/daily-loop brief (wired via AGENT_BRIEFING.md) and shown until the item is done or explicitly dropped. One list, always visible, never a scattered TODO.

**Change size:** Maximum one feature or one bug fix per task. If a change touches more than one file section, split it and complete each part fully before starting the next.

**Sandbox mount is NOT authoritative — the file-tools and Windows/git are (MOUNT-READ-1 root cause, fixed S140):** The bash sandbox reaches the Projects folder over a virtiofs/FUSE mount that can serve a **persistently torn (truncated-mid-file) copy** of a large file for an entire session — bash `wc -l`/`cat` show a short prefix while the true Windows file is complete. This is the recurring MOUNT-TEAR / MOUNT-READ fault. Rules: (1) **Never treat a bash read of a project file as ground truth** — the Read tool and `git show HEAD:<file>` read the real Windows file; bash may not. (2) **Never report git/file state from the bash mount as authoritative.** When a sandbox check disagrees with Windows `git status` or the Read tool, the sandbox is the suspect — re-check via Read/`git show`, and trust *that*, not the bash mount. (3) **Never Python-write a large project file from bash** (`open(path,'w')`) — a torn in-memory copy will overwrite the good Windows file. Use the Read→Edit file-tools for doc/code edits (they hit the true file), reserving bash-Python writes for the big HTML/JS files per the HTML WRITE RULE, and always verify the tail after. (4) **Run `python3 mount_guard.py` (see orchestration)** at session start and before any write-back to detect a torn mount before it can corrupt anything.

**Self-verification — a checker that disagrees with the authority must suspect itself first (S140):** Any monitoring/verification step (git state, file state, a live-site check) must validate against the *authoritative source for that layer* — for git: Windows working tree / `origin`; for files: the Read tool / `git show`; for the live site: the CDN-served page. When my check and the authority disagree, that disagreement is first evidence that **my checker is stale or torn**, not that the human/authority is wrong. Re-sync from the authority and re-check; only a disagreement that survives a re-sync is a real finding. Never report a phantom diff as a real one (the S140 false-RED loop).

**Git commits:** Always ask David to run git add/commit/push from PowerShell — never commit from the sandbox. The sandbox and Windows share the same folder mount under different OS users; sandbox-created index.lock files block Windows git and vice versa, and neither side can remove the other's lock. At session end, sweep the whole working tree into a commit (see **Session end checklist** step 6) so commits never drift behind the live server — deploys and the overnight loop write files without committing, so the catch-up must be comprehensive (`git add -A`), not scoped to the session's files.

**Definition of done:** Code works AND a one-paragraph summary has been appended to `CHANGELOG.md`. Only update `CLAUDE.md` for major structural changes, not routine tasks.

**Session end checklist (mandatory — all six required, in order):**
1. Run smoke test: `python3 smoke_test.py` — ALL checks must pass before closing. Fix any failures before proceeding.
2. Append a Session entry to `CHANGELOG.md` (with `Cost model impact:` if AI volume/cost/concurrency/pricing changed).
3. Append a line to `AUDIT_PROGRESS.md` if any audit item moved.
4. Update `STATUS.md`: bump the Live State session number, add a new `## Last Completed (Session N)` block and a `## Next Session (N+1)` block. The first `Session (\d+)` match in this file is what `/dashboard/summary` reports as currentSession — keep it accurate.
5. **Baseline write-back (the dashboard is live-data-driven — do NOT hand-edit a DATA object).** `scp STATUS.md CHANGELOG.md BACKLOG.md AUDIT_PROGRESS.md root@178.104.73.239:/var/www/marketsquare/`. The BEA parses these at `GET /dashboard/summary`, so this single step refreshes the live dashboard for the next session. Then confirm: `curl -s https://trustsquare.co/dashboard/summary | python3 -c "import sys,json;print(json.load(sys.stdin)['currentSession'])"` shows the new number. Only re-deploy `dashboard.html` itself when its MARKUP/JS changed (respect the DASHBOARD VERSION GUARD below); routine session state needs only the scp of the four docs. This step is what lets David always view the latest — never skip it.
6. **Git sync — end every session with a clean tree (commits must never drift behind the live server).** Run `git status --short` from the sandbox. If anything is pending — this includes drift left by mid-session `scp` deploys and by the overnight orchestrator loop, both of which deploy without committing — surface a paste-ready PowerShell block and have David run it before closing:
   ```
   cd C:\Users\David\Projects\MarketSquare
   git add -A
   git commit -m "<session summary>"
   git push
   ```
   `git add -A` deliberately sweeps the WHOLE tree (not just this session's files) so loop/deploy drift never accumulates. Never commit from the sandbox (index.lock conflict — see **Git commits** above); the agent runs read-only `git status`/`git diff` and surfaces the commands, David runs the commit/push. Before surfacing, confirm no secret is staged (`ssh_hetzner_key` / any `.env` must stay gitignored). The session is not done until `git status` is clean and pushed.

**Conflict resolution:** The Architect agent arbitrates all conflicts between agents using the Codex as source of truth. Only escalate to the user if the Codex cannot resolve the conflict.

## Scale-shape invariants (design for it, don't plan for it)
These are not future work. They are how code is written *now* so that scaling later is a config change, not a rewrite. Each costs ~nothing today and saves a rip-out at traffic. Hold to them every session; if a change would violate one, flag it rather than silently breaking it. **We are NOT building shards, replicas, queues, or multi-region now — do not add that infrastructure on spec.** These rules only keep the door open.

1. **DB access through one thin layer, standard SQL only.** No SQLite-only pragmas or local-file assumptions leaking into route handlers. The SQLite→Postgres move must stay a connection-string swap + test, not a hunt across call sites.
2. **Money-touching writes are transactional now.** Wrap every Tuppence debit and intro-accept in an explicit transaction even though SQLite's single writer would let us skip it. The ledger path stays strictly consistent; this code must already be correct under concurrency before Postgres arrives. (See Tuppence no-refunds rule — correctness here is load-bearing.)
3. **No state on the box.** Requests carry their own auth; shared state lives in the DB/Redis, never in process memory or a local session file. This is what lets the BEA later run as N identical copies behind a load balancer with zero code change.
4. **Media is always a URL, never bytes in the DB or local disk.** Already true via R2 — keep it that way. A CDN in front later is then a DNS/config change, not a code change.
5. **Carry `city_id`; never assume a global pool.** Data is naturally geo-partitioned — always scope queries by city/region and never write logic that only works if all rows live together. Keeps city/region sharding cheap if it's ever needed.
6. **Reads tolerate staleness; the ledger does not.** Browse counts, listing feeds, geo lookups may be cached/eventually-consistent. Tuppence balance and intro state must read authoritative. Decide which bucket a new read falls in when you write it.

## Sandbox SSH setup (run at the start of every session before any SSH/SCP)
The sandbox does not persist SSH keys between sessions. At the start of every session, run this before any SSH or SCP command:
```bash
bash /sessions/<session>/mnt/MarketSquare/load_sandbox_ssh.sh
```
If it says "key not found", ask David to run `setup_sandbox_ssh.ps1` once from PowerShell — it copies `~/.ssh/id_ed25519` into the project folder as `ssh_hetzner_key` (gitignored, never committed).

## Torn-mount check (run at session start AND before any doc write-back — MOUNT-READ-1)
The bash mount can serve a torn (truncated) copy of large files all session (see the Sandbox-mount rule under Operating principles). Detect it before trusting any bash read or writing anything back. Copy the detector OFF the mount first (so its own code can't be torn), then run it:
```bash
cp /sessions/<session>/mnt/MarketSquare/mount_check.sh /tmp/ && chmod +x /tmp/mount_check.sh
/tmp/mount_check.sh /sessions/<session>/mnt/MarketSquare
```
Exit 0 = mount whole. Exit 1 = torn file(s) listed — do NOT Python-write those from bash; edit via the Read/Edit file-tools (they hit the true Windows file) or pull the authoritative copy from the server. A `[TORN]` on a file you were about to write-back means a bash write would overwrite the good Windows copy with a truncated one.

## Local environment
- **David's working directory:** `C:\Users\David\Projects\MarketSquare` — always cd here before any scp/git command
- **PowerShell rules:** never use `&&` in SSH commands — chain with `;` or split into separate commands. Never pass Python inline via SSH — always write a .py file, scp it, then run it.
- Git remote: github.com/dmcontiki2/marketsquare

## Server deployment
- Server: Hetzner CPX32 · 178.104.73.239 · Ubuntu 24.04 · 4 vCPU · 8 GB RAM (upgraded from CPX22 on 25 May 2026)
- Nginx serves from: /var/www/marketsquare/
- **Always cd to working directory first:** `cd C:\Users\David\Projects\MarketSquare`
- Deploy buyer app: `scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html`
- Deploy admin tool: `scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html`
- Deploy BEA: `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py`
- Deploy ms.js: `scp ms.js root@178.104.73.239:/var/www/marketsquare/static/ms.js` ⚠️ nginx serves from /static/ not root
- Deploy ms.css: `scp ms.css root@178.104.73.239:/var/www/marketsquare/static/ms.css` ⚠️ nginx serves from /static/ not root
- Restart BEA: `ssh root@178.104.73.239 "systemctl restart marketsquare"`
- Purge Cloudflare cache after deploy: token stored in server `.env` as `CF_CACHE_TOKEN` and `CF_ZONE_ID` — call via BEA: `curl -s -X POST https://trustsquare.co/admin/purge-cache` (endpoint requires POST — GET fails; corrected Session 129) or use the sandbox helper in bea_main.py `_cf_purge_all()`
- Reload nginx after config changes: `nginx -s reload`
- CityLauncher: /var/www/citylauncher/ · port 8001 · citylauncher.service · nginx /launch/ + /launch-api/

## Server Dependency Installation
BEA dependencies must be installed into the BEA venv, not system Python. Always use `/var/www/marketsquare/venv/bin/pip install <package>` — never `pip install` or `pip3 install` directly on the server. This tripped up the Session 25 build (pywebpush install).

## Key technical notes
- ⚠️ DASHBOARD VERSION GUARD — CRITICAL: Before updating or deploying `session_dashboard_live.html`, ALWAYS check the server's current version first: `ssh root@178.104.73.239 "strings /var/www/marketsquare/dashboard.html | grep currentSession"`. If the server version has a HIGHER `currentSession` than the local file, pull the server version down first before making any changes. Never deploy a dashboard with a lower session number than what is already live. The server is always the source of truth for the dashboard.
- Cost model lives in project root as .xlsx — edited via openpyxl in the sandbox
- ⚠️ HTML WRITE RULE: **NEVER use the Write tool or Edit tool on marketsquare.html or marketsquare_admin.html. These files are too large and WILL be truncated.** ALL changes must use Python `open(path,'r') / content.replace() / open(path,'w')`. After every Python write, verify with: `python3 -c "c=open('marketsquare.html',encoding='utf-8').read();print('OK' if c.rstrip().endswith('</html>') else 'TRUNCATED:'+repr(c[-60:]))"`. If truncated, restore using the git-anchor method in the session log.
- ⚠️ XLSX WRITE RULE: After ANY cost model change, Claude must remind David to run these three commands in PowerShell before ending the session — the sandbox cannot reliably write binary files to the Projects folder mount:
  ```
  cd C:\Users\David\Projects\MarketSquare
  git add Cost_Breakdown_GlobalLaunch.xlsx
  git commit -m "Cost model update"
  ```
- When any session changes infrastructure, pricing, city launch mechanics, subscription tiers, or revenue model: flag the impact in CHANGELOG.md with a line starting "Cost model impact:"
- BEA listing ids are strings: 'bea_N' — always use findListing(id) not LISTINGS[id]
- All onclick handlers interpolating listing ids must quote them: openDetail('${l.id}')
- normCat() in loadLiveListings() normalises BEA category strings to CATS keys
- Magic link URL params: ?magic=1&name=...&email=...&cat=...&city=...
- Placeholder listings have ids starting with 'ph_' — used to bypass paused filter in renderGrid()
- activeCity is an object {id, name} — use activeCity.name for display, activeCity.id for API calls
- activeSuburb is {id, name} or null — use activeSuburb.name for comparisons
- activeCountry is {iso2, name}, activeRegion is {id, name} or null
- Geo API query param is `country` (not `country_iso2`) — e.g. /geo/regions?country=ZA
- Location badge is 2-line: top=country+region (dim), bottom=city+suburb
- Tier gating: free→suburb panel, starter→city panel, pro→country panel
- Admin sellerData includes geo_city_id (int) for suburb lookups
- Edit-after-publish: sellers use `PUT /listings/{id}?email=` — email-auth, no API key; NULL seller_email accepts first caller and stamps it
- listing_versions table archives full JSON snapshot before every PUT — version_num increments per listing
- BEA FastAPI route order critical: `GET /listings/mine` MUST be registered before `GET /listings/{listing_id: int}`
- Profile photo: uploaded via `POST /users/{email}/photo` → R2 → stored in users.photo_url; restored on login via GET /users/{email}
- Tuppence balance synced from `GET /tuppence/balance?email=` on buyer app load (server wins if greater than local)
- ⚠️ Dev-only: `POST /dev/credit` endpoint and Dev Tools nav in admin app — **REMOVE BEFORE LAUNCH**
- ⚠️ DEMO DATA SOURCING: `demo_listings.json` is repo-tracked and deployed from local; **`demo_sellers.json` is server-only by deliberate design** — the single source of truth lives ONLY on the box (`/var/www/marketsquare/demo_sellers.json`, served by `GET /demo-sellers`, ~40 sellers). It was de-bloated out of the FEA and a local+server copy kept drifting, so it is intentionally NOT in the repo. Do NOT "fix" its local absence by pulling it down or committing a local copy — that reintroduces the drift. It is purged at launch (may later be promoted to permanent repo-tracked data). Deploy `[3e]` treats its local absence as `[INFO] by design`; the verify step still guards the sole server copy.

## Current development status
- Launch city: Pretoria, South Africa (+ Johannesburg twin under consideration) · 60 staged prospects/city = wave trigger, NOT a 60-seller public threshold (CC-003 corrects old docs; day-one launch carries WHCL + demos + agency onboarding)
- **Live state is authoritative in `STATUS.md` (read first) + `GET /dashboard/summary` — do not hand-maintain version/infra numbers here (F3).** Server: Hetzner CPX32 (4 vCPU · 8 GB) since 25 May 2026; stack FastAPI + SQLite + Redis.
- GitHub backup: github.com/dmcontiki2/marketsquare
- Paystack: test mode (live mode pending CIPC registration)
- 4-level geo hierarchy live: Country → Region → City → Suburb (ZA seeded: 9 provinces, 54 cities, 11,679 suburbs)
- Edit-after-publish with version control live in both apps (Session 20)
- Next milestones: see `STATUS.md` "Next Session" block + `BACKLOG.md` 📌 Deferred items.

## David's document preferences (added 11 Jun 2026)
**Always deliver reports/documents to David as formatted Word (.docx) files, never raw .md/.txt** — he reads them in MS Word and plain markdown opens as an unreadable encoding dialog. Generate the .docx with real styling (headings, tables, colour for CRITICAL/WARN) alongside any machine-readable .md. This applies to audit reports, sweeps, deliberations — anything he will read.

**Always end any change that needs deployment/action from David with the exact, copy-paste-ready PowerShell commands** — never just describe the steps ("redeploy as usual"). One fenced code block, complete and in order.
