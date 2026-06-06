# TrustSquare — Status

## Live State
BEA v1.3.1 · FastAPI + SQLite · Hetzner CPX32 (8GB RAM) + 100GB volume · trustsquare.co · 65 live listings · World Heritage layer 332 sites · AI email triage LIVE · AI Price Check feed-driven + deliver-then-charge · AI cost guardrails LIVE (real-token + hard daily ceiling + dashboard panel) · Card photos: vision auto-orient on collectibles + 9 live cards fixed upright · Backend modules (auth/database/storage/payments) now in guarded auto-deploy (O2) · CORS locked to trustsquare.co origins (S4) · KYC verification path crash-fixed (SCAN-1 SONNET_MODEL + SCAN-2/3/4/6 missing imports re/hashlib/urllib/base64 + _json name + SCAN-5 doc-upload MEDIA_DIR→_LOCAL_MEDIA_DIR + SCAN-7 vision-draft background_tasks param — block SCAN-1→7 closed) · FEA wallet UX overhaul: How-introductions compact picker + transaction filters + AI-services list refresh (added Yield Estimate & Batch Card Lister) + refund mechanism removed (ms.js v130 / ms.css v115) · S3 DONE: BEA API key now X-Api-Key-header-only on the 3 KYC seller-document endpoints (`?api_key=` query fallback removed + dead `require_api_key_header_or_query` retired; CDN header-stripping assumption disproven) · JS-1 DONE: buyer-app post-payment Tuppence balance refresh crash-fixed (undefined `updateTuppenceDisplay()`→`updateTuppenceUI()`; ms.js v131) · Maroushka property photos cleaned (David-requested, data-only): 39 units de-duplicated (perceptual-hash) + location-revealing exterior/entrance/signage shots removed for anonymity + capped ≤10/unit (510→254 kept; DB [photos:] block only) · TVS steps 3-5 live: free/owned price+yield tiers + flag store + FEA chip selector (paid OFF, B7 intact) · JS-2 DONE: buyer-app location-badge refresh crash-fixed (undefined `updateLocBadge()`→`updateBadgeLabel()`; ms.js v133) · Wave 1+2 launch cities selectable + maps auto-aligned (geo seed US/GB/AU + 3 ZA; ms.js v141) · ZA dupe-city merge: Nelspruit→Mbombela + Port Elizabeth→Gqeberha (ms.js v142) · SCAN-8 DONE: trust-score dup-key removed (Cars_private `category.cars.service_history` deduped — fuller "Service history on file" entry kept; points 4 unchanged)  · Demo home counts now city-filtered: empty city (e.g. NY) reads 0, not Pretoria's totals (ms.js v143)  · World Heritage filter now resets on demo→live (was stuck on the demo country's sites) (ms.js v144)  · Pretoria 'coming soon' placeholder cards no longer leak into other cities' category counts (ms.js v145)  · For You/wishlist feed now hidden in demo mode (was bleeding real Pretoria listings into demo prospect cities; live geo-scope open as W12-FORYOU) (ms.js v146)  · Category tiles now always show (empty cities read '0 listings' instead of being hidden) (ms.js v147) · SCAN-9 DONE: dead PUT /wonders stub cleaned (removed unused import json/asyncio + body/body_bytes locals; handler behaviour unchanged)  · Demo-mode sweep fixes: titles + Adventure currency + US heritage parks + heritage type-filter reset (data + ms.js v149, incl. David QA-pass fixes: adv-grid broken-image fallback + 'us US' flag dedup) · Demo P2 fixes (Detect-engine run): Wave-1 adventures normalized to Stays/Experiences + 9 new verified-image stays (NY/Lon/Syd) + card↔detail photo-source parity poka-yoke (fixes 4 dead card images) (ms.js v150) · LIVE empty-city demo-bleed fixed: Sydney/etc no longer show demo totals — purge demo on switch-to-live + complete the !DEMO_MODE guard + selectCity re-renders Featured/HomeStats (ms.js v152) · Orchestration v2 Phase 2 (Triage) built+deployed: deterministic triage.py + visual board + cockpit (first live run — S123 sweep: 12 findings → 3 green to Fix, 3 resolved, 6 dismissed, 0 red) behind /orchestrator/v2 auth · server smoke_test.py deploy-drift synced (stale cat:Adventures assertion; demo data was fine) · Orchestration v2 Phase 3 (Fix) built + first green-lane batch shipped: DEMO-6 renderAdvGrid honours l.per + DEMO-7 renderCatCounts paused-guard (ms.js v153, smoke-green, live-verified) · DEMO-5 routed to DEMO-4 (R2 self-host, not re-hotlinked) · Orchestration v2 Phase 4 (Prevent) built: 3 regression guards (DEMO-6/7 + photo poka-yoke) + gentle demo-image monitor; a guard FAIL re-enters Triage→Fix so the loop closes on itself; first run 3/3 guards pass + monitor caught 3/30 dead (0 false positives, 498 watched) · Orchestration v2 Phase 5 (Automate) built: deterministic zero-token nightly conductor orchestrator_v2.py runs Detect→Triage→Fix→Prevent on the box (cron 03:50 SAST, SHADOW — deploys nothing, old loop untouched); cockpit 'since last night' panel live; 5-stage arc complete end-to-end; controlled cutover staged (CUTOVER-1, gated on parity) · SCAN-10 DONE: removed 2 redundant module-level `from datetime import timedelta` re-imports in bea_main.py (F811; line 25 canonical) — behaviour-neutral, auto-shipped · Session 128 complete

## Last Completed (Session 128 — 2026-06-06)
- **SCAN-10 DONE (LOW · redundant `datetime` re-imports · auto-shipped).** `bea_main.py` re-imported `from datetime import timedelta` twice at **module level** — line 4046 (the LocalKeywordMatcher block, beside `import re as _re_match`) and line 8490 (the admin-auth import block, between `import jwt as _pyjwt` and `from pydantic import BaseModel as _BaseModel`) — both F811-redundant with the canonical module-top import at line 25 (`from datetime import datetime, timezone, timedelta`). Removed both; `timedelta` stays bound module-wide via line 25, so behaviour is identical. Two surgical Python `str.replace` edits (each old-string anchored on its unique neighbour import and asserted to match exactly once), never Edit/Write; −62 bytes (539310→539248); the aliased `from datetime import datetime as _dt` at line 8108 left untouched.
- **Gate:** import-only cleanup — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / KYC-SA-ID code, no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2); auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv (`py_compile` on the served copy); whole-file diff vs a freshly-pulled server copy = exactly the 2 removed lines (local byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post. Server backup `main.py.bak-20260606-scan10`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`).
- **Cost model impact:** none — dead-import removal; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (129)
- **CUTOVER-1 (attended/gated — NOT a fixer item):** after a shadow parity night, execute the documented orchestration-v2 cutover (automate.html) — v2 Fixer on (Sonnet checkpoint), retire the 3 old Claude tasks, conductor `--live`. Carried forward from the Session-128 plan; the background fixer cannot self-authorise this.
- **Maintenance auto-ship queue (top → back):** SCAN-11 (dead locals `skip_fields`/`sig_suburb_id`/`cutoff` + vulture `family`/`hint` + unused `_sqlite3` import; rename unused loop vars `hi2`/`idx` → `_`, bea_main.py) → SCAN-12 (`import os` unused, database.py:2) → DASH-VER-1 (stale `bea_version` 1.3.0→1.3.1 in /dashboard/summary — reconfirmed live-drifted this run; the `app = FastAPI(…, version="1.3.0")` title string @line 27 is the source vs `/health` 1.3.1) → HTML-1 → HTML-2 → SCAN-PANEL-1+2.
- **Standing:** ORCH-POLICY-1 (§5 reconcile); DEMO-4 R2 self-host (carries DEMO-5, monitored nightly by M-IMG); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1 (moot once the old loop retires).
- **Awaiting your approval:** none.

## Last Completed (Session 127 — 2026-06-05)
- **Orchestration v2 Phase 5 (Automate) — the loop runs itself (shadow); the 5-stage arc is complete.** New deterministic, zero-token `orchestration_v2/orchestrator_v2.py` conductor: nightly it runs sensor.py (sense) + prevent.py (guards+monitor) → assembles findings → triage.py → writes a "since last night" report. The surgical Fix stays a Sonnet checkpoint (surfaced as a green work order); the conductor never edits/ships code.
- **Shadow + scheduled:** server cron 03:50 SAST (after the 03:30 sensor, before the old Claude loop). Writes only /orchestrator/v2/, deploys nothing, old loop §9 files untouched. First pass: smoke 39/39, guards 3/3, monitor 2 dead/15 (0 FP), triage → 1 green (filed)/1 amber/0 red, $0/0 tokens. Cockpit: live "since last night" panel, Phase 5 → built, automate.html + cutover plan. Behind auth (644, sha-parity, 401).
- **Cutover staged (CUTOVER-1, gated on parity):** turn on a v2 Fixer (Sonnet checkpoint) → retire the 3 old Claude tasks (orch-sensor/fixer/orchestrator) → flip conductor to --live. Fully reversible; nothing fires without David's go.
- **Cost model impact:** standing maintenance token cost trends to ~zero at cutover (deterministic loop replaces the per-night model loop).

## Next Session (128)
- **CUTOVER-1 (the finale's last switch):** after a shadow parity night, execute the documented cutover (automate.html) — v2 Fixer on, old loop off, conductor `--live`.
- Standing: ORCH-POLICY-1 (§5 reconcile); DEMO-4 R2 self-host (carries DEMO-5, now monitored nightly by M-IMG); PREVENT-HOMESTATS; W12-FORYOU (live); PAYMENTS (F4); LOOP-1 (moot once the old loop retires).

## Last Completed (Session 126 — 2026-06-05)
- **Orchestration v2 Phase 4 (Prevent) — guards + monitor; the loop closes.** New deterministic `orchestration_v2/prevent.py`: regression guards (G-DEMO6 renderAdvGrid l.per; G-DEMO7 renderCatCounts paused-guard both paths; G-PHOTO card/detail photo poka-yoke) + a gentle demo-image link-health monitor (M-IMG). It watches, never edits; a guard FAIL / monitor alert is written as a Detect-schema finding (`findings_prevent.json`) so it re-enters Triage → Fix.
- **First run:** 3/3 guards PASS (the Phase 2–3 fixes are now permanent); M-IMG sampled 30 of 498 gallery URLs → 3 dead, 0 false positives (the link-rot DEMO-5 was routed to DEMO-4 for, now monitored). Cockpit: Phase 4 → built, Prevent card live; deployed prevent.py/prevent_checks.json/cockpit to /orchestrator/v2/ behind auth (644, sha-parity, 401).
- **Cost model impact:** none.

## Next Session (127)
- **Orchestration Phase 5 (Automate) — the last brick:** wire the Orchestrator + Scheduler to run Detect → Triage → Fix → Prevent nightly on the box (server cron, like sensor.py), surfacing only amber/red + a one-line "since last night" to the cockpit, and retire the old patched overnight loop (controlled cutover, shadow first).
- Candidate Detect finding: renderHomeStats has the same paused pattern as DEMO-7 (left out of scope); process poka-yoke: add smoke_test.py to the standard deploy set (the S125 drift).
- Standing: ORCH-POLICY-1 (§5 reconcile), DEMO-4 (R2 self-host, carries DEMO-5), LOOP-1, W12-FORYOU, PAYMENTS (F4).

## Last Completed (Session 125 — 2026-06-05)
- **Orchestration v2 Phase 3 (Fix) — built + first green-lane batch shipped.** New deterministic `orchestration_v2/fix.py` harness (queue-manager + gate-recorder + board-regenerator): consumes the green lane of `triaged.json` one item at a time; `--ship/--route/--fail` update status + append `fix_results.json` + regenerate the board; green ships (pre-authorised), amber stages, red never touched. The surgical edit stays the Sonnet checkpoint (bash-python str-replace + node/ast + smoke).
- **First Fix run = the S123 green queue (3 items): 2 shipped, 1 routed.** DEMO-6 (renderAdvGrid now honours l.per — the mislabeled /person/night stay) + DEMO-7 (renderCatCounts excludes l.paused at both count paths) shipped in ms.js v153 (diff = exactly the 3 regions; node-check; backup; smoke-green; live-verified; FEA baseline refreshed). DEMO-5 (27 dead gallery URLs) routed to DEMO-4's R2 self-host rather than re-hotlinking rot-prone URLs (S122 lesson; "never make it worse").
- **Cockpit:** Phase 3 → built, Fix card live with Copy-run-command, fix.html playbook button. Deployed fix.py/fix_results.json/triaged.json/board/cockpit to /orchestrator/v2/ behind auth (644, sha-parity, 401).
- **Cost model impact:** none.

## Next Session (126)
- **Orchestration Phase 4 (Prevent):** a poka-yoke per fixed defect class (so DEMO-6/7-style bugs can't recur) + scheduled monitors for the weak points we don't control (e.g. the demo image link-health check); then Phase 5 (Automate) — the Orchestrator + Scheduler cutover running Detect→Triage→Fix→Prevent nightly.
- **DEMO-4** (R2 self-host of demo images) now carries DEMO-5; **renderHomeStats paused-guard** is a candidate Detect finding (same class as DEMO-7, left out of scope this run).
- Standing: ORCH-POLICY-1 (§5 reconcile), LOOP-1, W12-FORYOU, PAYMENTS (F4).

## Last Completed (Session 124 — 2026-06-05)
- **Orchestration v2 Phase 2 (Triage) — built, deployed, first live run.** Design-first (data model + dedupe key + lane rules confirmed against the approved Phase 0). New deterministic, zero-token `orchestration_v2/triage.py`: dedupes each Detect finding on `file :: root-token` (line-numbers excluded) against ignore-list / BACKLOG / CHANGELOG; classifies a lane (red checked first by path/term, fail-safe to red, green only for confirmed-safe classes, else amber; a red proposal is never downgraded); prioritizes P1–P3. Emits `triaged.json` (the queue Fix consumes) + `triage_board.html`.
- **First live triage = the S123 Detect sweep (12 findings):** DEMO-5/6/7 → green Fix queue; 3 resolved (taxonomy/photo-parity/LIVE-bleed); 6 dismissed (false positives seeded into `ignore.json`, never re-raised); 0 amber/red/new. Cockpit: Phase 2 → built, Triage card live with Copy-run-command, playbook + board buttons. Deployed to `/orchestrator/v2/` behind Basic-Auth (644, sha-parity, 401 unauthed).
- **Smoke gate caught deploy drift:** server `smoke_test.py` was pre-S123 (stale bare-`Adventures` assertion → false fail); synced the committed local test (test-only, zero app risk). Smoke now all-green; demo data was correct (302 listings).
- **Filed (BACKLOG):** Detect findings-JSON poka-yoke (TRIAGE-IN-1); ORCHESTRATION_POLICY §5 ↔ v2 red-security reconciliation incl. re-laning the ADMIN_KEY backstop off the green nightly lane (ORCH-POLICY-1); Triage→BACKLOG safe-append discipline (TRIAGE-WB-1; LOOP-1 hazard — Edit tool truncated triage.py/ignore.json, rebuilt via bash-python).
- **Cost model impact:** none.

## Next Session (125)
- **Orchestration Phase 3 (Fix):** consume the green Triage queue (DEMO-5/6/7 as the first batch) — apply + verify, stage amber/red. The Detect→Triage→Fix tissue is now in place.
- **Reconcile ORCHESTRATION_POLICY §5** with the v2 red lane (security/secrets = red); re-lane the ADMIN_KEY backstop accordingly (ORCH-POLICY-1).
- Standing: LOOP-1 doc-writeback hardening; W12-FORYOU live geo-scope; PAYMENTS Merchant-of-Record (BACKLOG F4).

## Last Completed (Session 123 — 2026-06-05)
- **Orchestration cockpit live + Detect-engine run + 2 P2 demo fixes.** Added the Control Room (cockpit) launch button to the ops dashboard and aligned its Basic-Auth realm to the dashboard's ("TrustSquare Internal"→"TrustSquare Orchestrator") so the saved login auto-fills both (David login fix); fixed the cockpit 403 (deployed files were mode 700 → chmod 644). Ran the Phase-1 Detect engine end-to-end over demo mode (4 cities): deterministic audit → 3 parallel code-verified subagent sweeps → adversarial re-verify → gentle low-concurrency image-health (234 URLs). 7 of 9 initial flags ruled out as false positives.
- **P2 #1 (taxonomy):** Wave-1 (NY/London/Sydney) adventures were tagged bare `cat:Adventures`, so the Adventures Stays/Experiences sub-tabs were dead ("No Adventures yet"). Re-tagged all 30 → `adventures_experiences` (+ proper `experience_type`) and added 9 genuine `adventures_accommodation` stays (3/city) with HEAD-verified-live images. Each Wave-1 city now = 10 experiences + 3 stays (293→302 demo listings).
- **P2 #2 (photo parity):** card/featured/my-requests/local-market rendered `l.photo` while detail rendered `photos[0]||photo`; 23 Wave-1 listings diverged, 4 showed a dead card image. Added the `(l.photos&&l.photos[0])||l.photo` poka-yoke at all 4 card sites — card now matches detail and the 4 dead cards resolve. `ms.js` v149→v150 + demo_listings.json (BEA restarted; FEA baseline refreshed to v150; smoke updated for the new taxonomy). node --check + smoke all-green; live-verified.
- **LIVE-mode demo bleed (follow-up · reported by David):** on LIVE, an empty city (Sydney) showed the full demo totals (Property 40 / Adventures 59) + a 4-city Featured strip. Root cause: switching to live didn't purge demo listings from LISTINGS (asymmetric with switch-to-demo), the per-city scoping in renderHomeStats/renderFeatured + the renderCatCounts fallback only excluded demo when DEMO_MODE=true, and selectCity never re-rendered Featured/HomeStats. Fixed: purge demo/ph_ on switch-to-live + complete the `!DEMO_MODE && demo_` guard at the 3 sites that lacked it + selectCity/selectDemoCity now re-render Featured+HomeStats. ms.js v150→v152; predicate-simulation verified (live Sydney → 0; demo scoping intact); smoke green; FEA baseline v152.
- **Filed (BACKLOG):** DEMO-5 (27 dead gallery URLs / 34 listings), DEMO-6 (renderAdvGrid hardcoded per-suffix), DEMO-7 (renderCatCounts paused-guard latent).
- **Cost model impact:** none.

## Next Session (124)
- **Orchestration:** Phase 2 (Triage) when ready — the Detect run above is the model for it.
- **DEMO-5/6/7** demo polish; **DEMO-1** LM-tile dual-writer.
- **LOOP-1** harden loop doc-writeback; **W12-FORYOU (live)** geo-scope For You feed; **PAYMENTS** Merchant-of-Record (BACKLOG F4).

## Last Completed (Session 122 — 2026-06-05)
- **Demo-mode "one-pass" sweep + fixes (first parallel-subagent audit).** 4 subagents audited every home section × city, cross-checked; found 3 HIGH user-visible bugs (only 1 previously seen) + MED/LOW.
- **Fixed:** 60 missing titles (NY/Lon/Syd Collectors+Cars → "undefined") via real derived titles in `demo_listings.json` + code title-fallback; Adventure currency (grid "R89" vs detail "$89") via new `_priceLabel` helper through `ADV_COUNTRY_CURRENCY`; US World Heritage parks vanishing (USA alias, 13→16); heritage type-filter stuck (resets on city/mode switch); blank heritage strip on first load (loading placeholder); Adventure priceNum/per null. `ms.js` v147→v148 + demo_listings.json (BEA restarted). node --check + smoke green; API-verified.
- **Filed (BACKLOG):** DEMO-1 LM-tile suburb inconsistency (latent), DEMO-2 heritage coverage gaps, DEMO-3 demo cosmetics.
- **Cost model impact:** none.

## Next Session (123)
- **DEMO-1:** LM-tile dual-writer + suburb-filter inconsistency.
- **LOOP-1:** harden the loop doc-writeback (still truncating BACKLOG).
- **W12-FORYOU (live):** geo-scope the For You feed (BEA). **PAYMENTS:** Merchant-of-Record setup (BACKLOG F4).
- Maintenance queue: SCAN-10…12, DASH-VER-1, HTML-1/2.

## Last Completed (Session 121 — 2026-06-05)
- **SCAN-9 DONE (MED · dead code in `update_listing_wonders` · auto-shipped).** The `PUT /listings/{listing_id}/wonders` handler in `bea_main.py` was a dead stub: it computed `body = asyncio.run(request.json())…`, set `body_bytes = b""`, and did a local `import json as _j` — then ignored all three and `return _update_listing_wonders_sync(...)`, which only raises HTTP 500 "Use POST form". The live, working endpoint is `POST /listings/{id}/wonders` (`set_listing_wonders`), which parses the body itself via `await request.json()`. So `import json` (F401) and `body`/`body_bytes` (F841) were genuinely unused, and removing `body` also orphaned the local `import asyncio` (its only consumer).
- **Fix:** removed the whole 6-line dead block, leaving the docstring + the real `return _update_listing_wonders_sync(listing_id, request)` — behaviour-neutral (the PUT stub still 500s callers to POST, exactly as before) and complete (no newly-orphaned `import asyncio` for next week's scan to re-flag). One surgical Python str.replace (old-string asserted to match exactly once; −186 bytes), never Edit/Write.
- **Gate:** World-Heritage wonders-link handler — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / SA-ID-KYC code, no pricing/refund path → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2). Auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; whole-file diff vs a freshly-pulled server copy = exactly the 6 removed lines (local was byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post (incl. the BEA `/wonders` check, 304 sites). Server backup `main.py.bak-20260605-scan9`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`).
- **Cost model impact:** none — dead-code removal; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (122)
- **Maintenance auto-ship queue (top → back):** SCAN-10 (redundant `from datetime import timedelta` re-imports, `bea_main.py` ~4001/~8446), then SCAN-11 (dead locals `skip_fields`/`sig_suburb_id`/`cutoff` + vulture `family`/`hint` + unused `_sqlite3` import; rename unused loop vars `hi2`/`idx` → `_`), SCAN-12 (`import os` unused in `database.py`:2), DASH-VER-1 (`/dashboard/summary` `bea_version` 1.3.0→1.3.1 — confirmed live-drifted again this run vs `/health` 1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **Awaiting your approval:** none.
- **Standing:** PAYMENTS Merchant-of-Record path (BACKLOG F4); LOOP-1 harden the orchestrator doc-writeback; W12-FORYOU live geo-scope of the For You/wishlist feed; self-hosted Overpass re-import (BLOCKER); Paystack live mode; EULA v1.6 attorney review; support@ mailbox (L3a); A11Y-1/2/3 + ADMIN_KEY filed to the design/ops track.

## Last Completed (Session 120 — 2026-06-04)
- **Category tiles always show, even at 0 (David feedback).** Empty demo/prospect cities (Chicago, Cape Town) were showing no category tiles because demo mode hid 0-count tiles. Now the six category tiles + Local Market always render with their count ("0 listings" when empty) so the structure is always visible.
- **Fix (`ms.js` v146→v147):** removed the demo-only hide-empty-tiles behaviour (a pre-launch TODO) in `renderCatCounts`. Populated cities unchanged; empty cities show all categories at 0. node --check + smoke green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (121)
- **PAYMENTS (David proceeding):** stand up the Merchant-of-Record path (Paddle / Lemon Squeezy) for US/UK/AU launch — no US entity or travel; sidesteps the Stripe-direct + Paystack blockers. See BACKLOG F4. (Optional first step: Claude's fee-math one-pager.)
- **LOOP-1 (open):** harden the orchestrator loop's doc-writeback (it truncated BACKLOG repeatedly this run).
- **W12-FORYOU (live):** geo-scope the For You / wishlist feed on the BEA (affects live mode).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 119 — 2026-06-04)
- **"For You" feed hidden in demo mode (David-reported follow-up).** After the placeholder fix, demo prospect cities (Phoenix) still showed real Pretoria collectibles in the For You strip — that's the personalised wishlist feed (`wlLoadFeed` → BEA `/wishlist/feed`), which has no demo data, so in demo it could only show real listings.
- **Fix (`ms.js` v145→v146):** `wlLoadFeed` hides the whole For You section in demo mode (restores in live); `devSetMode` re-evaluates it on toggle. Demo cities now have a clean home; live unchanged. node --check + smoke green; deployed; CF purged.
- **Still open (BACKLOG W12-FORYOU):** LIVE geo-scoping of the feed (BEA-side) — a live Houston/Phoenix buyer should see local recommendations, not Pretoria.
- **Cost model impact:** none.

## Next Session (120)
- **LOOP-1 (open action):** harden the orchestrator loop's doc-writeback (safe-write+verify) — it truncated BACKLOG.md repeatedly this run. See BACKLOG.
- **W12-FORYOU (live):** geo-scope the For You / wishlist feed on the BEA (affects live mode).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 118 — 2026-06-04)
- **Placeholder cards leaked into every city's category counts (David-reported).** Demo empty city (Houston) showed Property/Tutors/Services = "1 listing" (the paused Pretoria `ph_*` "coming soon" cards) while other categories were hidden. They aren't `demo_`/`isLive`, so they bypassed the Session 116 city filter via the `renderCatCounts` fallback + `renderGrid`.
- **Fix (`ms.js` v144→v145):** excluded `ph_` from the count fallback and city-scoped them in `renderGrid` — empty cities now read 0 (tiles hidden, like New York), Pretoria unchanged. Simulated against live demo data (Houston→{}, Pretoria→full) + node --check + smoke green; deployed; CF purged.
- **Filed (BACKLOG W12-FORYOU):** the "For You"/wishlist feed isn't geo-scoped — showed Pretoria collectibles in Houston and would do the same in live mode; needs a server-side city/country scope on the BEA `/wishlist/showcase` + `/feed` endpoints.
- **Cost model impact:** none.

## Next Session (119)
- **LOOP-1 (open action):** harden the orchestrator loop's doc-writeback (safe-write+verify) — it truncated BACKLOG.md twice this run (Sessions 117 & 118); caught + restored each time. See BACKLOG.
- W12-FORYOU: geo-scope the For You / wishlist feed (BEA-side; affects live).
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 117 — 2026-06-04)
- **World Heritage strip stuck on demo country after returning to live (David-reported).** Demo US city → toggle live ZA left the heritage strip showing US sites (unscrollable to ZA) while the selector read "All". Root cause: `selectDemoCity` set `_wfCountry` to the city's country without syncing the dropdown, and `devSetMode`→live never reset `_wfCountry` or re-rendered the strip.
- **Fix (`ms.js` v143→v144):** selectDemoCity syncs the `wf-country-select` dropdown; devSetMode→live resets `_wfCountry='all'` + dropdown; devSetMode re-renders the strip. Live ZA now shows "All" heritage (Africa/ZA first), matching the selector. node --check + smoke green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (118)
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 116 — 2026-06-04)
- **Demo home-page counts now respect the selected city (David-reported).** In demo mode an empty prospect city (e.g. New York) showed Pretoria's category counts + home stats even though the grid correctly showed nothing. Root cause: `renderHomeStats()` and the `renderCatCounts()` count-all fallback ignored `activeCity` (unlike `renderGrid`).
- **Fix (`ms.js` v142→v143):** applied the grid's demo/live active-city filter to both count paths, so an empty city reads 0 (empty tiles hidden) and home matches the grid. Node unit-test of the predicate (NY→0, Pretoria→its listings) + node --check + smoke all-green; deployed; CF purged.
- **Cost model impact:** none.

## Next Session (117)
- Maintenance auto-ship queue: SCAN-9…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing follow-ups: admin onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU seed; in-app visual click-test when Chrome reconnects.

## Last Completed (Session 115 — 2026-06-04)
- **SCAN-8 DONE (MED · trust-score dup-key · auto-shipped).** `_CATEGORY_SIGNALS["Cars_private"]` in `bea_main.py` defined `category.cars.service_history` **twice**: the fuller line 6060 (`"Service history on file"`, richer how-to-earn) was silently overridden by the terser line 6064 (`"Service history"` / `"Upload service book."`), so the weaker copy was what rendered. Both entries carried **points: 4**, so trust-score math was already correct — only the displayed name + how-to-earn text was affected.
- **Fix:** removed the terser duplicate (6064), leaving the fuller 6060 entry as the sole definition; the better "Service history on file" / "Upload scan of service book or dealer service records…" copy now renders. One surgical Python `str.replace` (old-string asserted to match exactly once; key occurrences 2→1; −124 bytes), never Edit/Write.
- **Gate:** trust-score config only — touches no `payments.py` / Tuppence-ledger / EULA-Terms-Privacy / SA-ID-KYC code, and the points value is unchanged → clears Gate 1 + Gate 2 with positive confidence (ORCHESTRATION_POLICY §5 / §6.2). Auto-shipped.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; diff vs a freshly-pulled server copy = exactly the one removed line (local was byte-identical to server beforehand); `smoke_test.py` all-green pre **and** post. Server backup `main.py.bak-20260604-scan8`; scp `bea_main.py` → `main.py` (server sha256 == local); BEA restarted **active**, `/health` ok v1.3.1 (localhost + public); Cloudflare purged (`{"purged":true}`); served `main.py` now carries the key once.
- **Cost model impact:** none — config dedup; no AI calls, pricing, concurrency, or city-launch change.

## Next Session (116)
- **Maintenance auto-ship queue (top → back):** SCAN-9 (dead local `import json` + unused `body`/`body_bytes` in `update_listing_wonders`, `bea_main.py` ~8268 — confirm the body is parsed elsewhere first), then SCAN-10 (redundant `from datetime import timedelta` re-imports), SCAN-11 (dead locals / unused loop vars → `_`), SCAN-12 (`import os` unused in `database.py`), DASH-VER-1 (`/dashboard/summary` `bea_version` 1.3.0→1.3.1 — confirmed live-drifted again this run vs `/health` 1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **Awaiting your approval:** none — S5 is verified DONE + fail-closed since 2 Jun; do NOT re-stage.
- **Standing:** self-hosted Overpass re-import (BLOCKER), Paystack live mode (`PAYSTACK_WEBHOOK_SECRET` + `sk_live` keys), EULA v1.6 attorney review, support@ mailbox (L3a); A11Y-1/2/3 + ADMIN_KEY filed to the design/ops track.

## Last Completed (Session 114 — 2026-06-04)
- **ZA duplicate-city fix (David-spotted).** Nelspruit & Mbombela showed as two cities on one spot — Nelspruit was officially renamed Mbombela (2009, upheld 2014). The Session 113 Wave 2 seed had added "Nelspruit" though the official "Mbombela" was already in the GeoNames seed; a near-dupe sweep found the **same bug for Port Elizabeth → Gqeberha** (renamed 2021).
- **Fix (`dedupe_za.py`, data-only, DB backed up):** deleted the two 0-suburb/0-listing duplicates and renamed the canonical entries to `Mbombela (Nelspruit)` (id50, 331 suburbs) and `Gqeberha (Port Elizabeth)` (id70, 51 suburbs) so the former names stay discoverable via the `q=` typeahead. ZA cities 57→55; verified live.
- **FEA `ms.js` v141→v142:** demo-list entries updated to the canonical names+coords; node --check clean; deployed; CF purged; **smoke all-green**. `seed_wave12_cities.py` hardened so it cannot re-add the dupes.
- **Cost model impact:** none.

## Next Session (115)
- Standing follow-ups (carried from S113): admin seller-onboarding country selector for non-ZA prospects; international suburb seeding; Wave 3 AU city seed; in-app visual click-test when the Chrome extension reconnects.
- Maintenance auto-ship queue (unchanged): SCAN-8…12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.

## Last Completed (Session 113 — 2026-06-04)
- **Wave 1 + Wave 2 cities now selectable + maps auto-aligned (David-directed pre-launch prep).** Seeded the geo hierarchy for US/GB/AU (3 countries, 10 regions, 23 international cities) plus the 3 missing ZA Wave-2 cities (Port Elizabeth, East London, Nelspruit), all with accurate centre lat/lng; verified through the public `/geo` API. Idempotent `seed_wave12_cities.py`; live DB backed up; data-only (no BEA change/restart — `/geo` endpoints were already country-agnostic).
- **Map auto-alignment (`ms.js` v140->v141).** `selectCity` now captures the city lat/lng the `/geo` API already returns and `renderMap` centres on it — replacing the hardcoded 4-city `CITY_CENTERS` dict that had been mis-centring every non-Pretoria city (incl. Cape Town/Joburg) on Pretoria. `DEMO_COUNTRY_CITIES` extended with all Wave 1/2 cities + coords; map re-renders on city switch in map view. 5 surgical str-replace edits; `node --check` clean; deployed; CF purged; **smoke all-green**.
- **Verification:** picker click-path (country->region->city) resolves with correct coords across a ZA/US/UK/AU sample; served `ms.js` carries all edits. In-app visual walkthrough pending Chrome reconnection (extension offline this session).
- **Gaps filed (BACKLOG):** Wave 3 AU seeding; international suburb hierarchy; admin seller-onboarding country selector for non-ZA prospects.
- **Cost model impact:** none — geo data + display-centring only; launch cadence unchanged (still gated on patent + whitepaper).

## Next Session (114)
- **Wave 1/2 readiness follow-ups:** admin seller-onboarding country selector (region/city currently hardcoded `country=ZA`) so international prospects get a `geo_city_id`; international suburb seeding if suburb-level gating is wanted for intl cities; Wave 3 AU city seed when Wave 3 approaches.
- **In-app visual click-test** of the city picker + map alignment once the Chrome extension is back online.
- **Maintenance auto-ship queue (unchanged):** SCAN-8...12, DASH-VER-1, HTML-1/2, SCAN-PANEL-1/2.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 111 — 2026-06-03)
- **JS-2 DONE (HIGH · buyer-app crash-fix · auto-shipped).** `ms.js:86` called `updateLocBadge()` — a function defined nowhere (the second and last genuinely-undefined call in `ms.js` per the 1 Jun ESLint sweep, after JS-1). It sat in the "Re-render everything" block (alongside `renderGrid()`/`renderCatCounts()`/`initLMHomeTile()`) that runs after a demo↔live listings mutation, so the location-badge refresh threw a ReferenceError on every demo/live toggle.
- **Fix:** renamed the single call to `updateBadgeLabel()` — the real zero-arg 2-line location-badge repaint fn (`ms.js:112`; rewrites `home-city-badge` with country+region / city and calls `_refreshCityLabels()`). Verified the target's signature/behaviour match the call shape before renaming (zero-arg; identical to the 5 existing `updateBadgeLabel()` call sites). One surgical Python binary str.replace (old-string unique; `updateLocBadge` 1→0; `updateBadgeLabel` 6→7; ms.js +2 bytes 714993→714995), never Edit/Write.
- **Gate:** frontend-only (`ms.js` + index cache-bust) — clears Gate 1 and Gate 2; the JS-1-class auto-ship boundary example (ORCHESTRATION_POLICY §5). Auto-shipped.
- **Verify/deploy:** `node --check` clean (local + server); diff vs freshly-pulled server copy = exactly the one renamed line (local byte-identical to server beforehand) + the `ms.js?v=132→133` cache-bust in index.html. No BEA change → no restart. Server backups `*.bak-20260603-js2`; scp `static/ms.js` + `index.html` (server bytes == local, sha-matched); Cloudflare purged (POST). Live through CF: index serves `ms.js?v=133`, served `ms.js` has 0 `updateLocBadge` + 7 `updateBadgeLabel`, line 86 = `updateBadgeLabel();`; `/health` ok v1.3.1; **smoke all-green** pre + post; FEA baseline refreshed (ms.js v133/714995). **ms.js is now free of undefined-call crashes — JS-1 + JS-2 both closed.**
- **Cost model impact:** none — display-repaint rename only; no AI calls, pricing, concurrency, or city-launch change.
- **S5 — VERIFIED ALREADY DONE + LIVE (held in error this morning, corrected same day).** The run first held queue-top S5 on a bare `approved:true` the audit trail contradicted (`orchestrator/log.md`: "S5 left unapproved"). A same-day check (David-prompted) then confirmed S5 was **already built, committed (`1f40b58`, "Session 110c"), and deployed on 2 Jun**: `_payment_grants_allowed()` is live on the BEA (definition @3089 + 4 guard sites @3129/3201/3359/5021 across all grant paths) plus `/payment/verify` idempotency. Live env (`sk_test`, `ALLOW_TEST_PAYMENTS` unset) → gate returns False → test-card grants fail-closed (correct pre-launch posture). The "hold" was **tracking drift** — S5 was never marked DONE in the audit queue, so it kept resurfacing — not a real pending item. Corrected: removed from `staged.json` + the queue; nothing awaits approval. When live `sk_live_` keys land, grants auto-resume with no code change.

## Next Session (112)
- **Filter v1 LIVE (FEA · David-directed, 3 Jun):** global **Trust ≥** selector now in the browse filter bar (Any/60/70/80/90), client-side over loaded listings, surfaced as a "★ Trust ≥ N" tag (`ms.js` v134; smoke 39/39; served-through-CF verified). First increment of the Filter design — UI-first; Step 1 backend parked. **Next:** Save-as-Wishlist, then scope + currency (ride on Step 1). Design: `FILTER_APP_MOCKUP.html` · `GLOBAL_MARKETPLACE_DESIGN.html` · `STEP1_BUILD_SPEC.html`. (Browser click-test pending — Chrome extension was offline.)
- **Maintenance auto-ship queue:** SCAN-8 (duplicate dict key `category.cars.service_history`, bea_main.py ~6017), then SCAN-9, SCAN-10, SCAN-11, SCAN-12, DASH-VER-1 (stale `bea_version` 1.3.0→1.3.1), HTML-1, HTML-2, then SCAN-PANEL-1/2.
- **S5 — DONE, no action (do NOT re-stage).** Already deployed + fail-closed since 2 Jun (see the Session 111 correction above); it is not awaiting approval. The real money-path go-live items (separate from S5, triggered when Paystack approves live mode): set `PAYSTACK_WEBHOOK_SECRET` (currently unset → reliable webhook credit path off) and swap `sk_test` → `sk_live` keys — both server-env only, grants auto-resume, no code change.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 110 — 2026-06-03)
- **Tiered Value Selector steps 3-5 — BUILT, VERIFIED, SHIPPED (free tiers only; paid OFF; B7 intact).** Steps 1-2 (tier config + `GET /listings/{id}/value-tiers` + tier-aware price/yield) were committed in S108 but never deployed; shipped here together with 3-5.
- **STEP 3 — FREE/owned resolvers** (`tier_resolvers.py` + versioned/dated `value_benchmarks.py`): UK property = HM Land Registry Price Paid (keyless SPARQL, OGL); US/UK rent = HUD FMR / ONS-VOA area benchmarks; internal comps (median of comparable listings, min-8 gate) for property+vehicles; ZA PayProp/TPN aggregate area guide (0T); collectible feeds (BrickLink/Numista/JustTCG) wired but credential-gated -> dark until a key is set. Flat `NET_COST_PCT=3.0` replaced by a versioned, dated, per-region net-cost band (ZA 3.0% unchanged). Country-aware yield benchmarks (H7b). The NUMBER always comes from a feed/arithmetic; the model only narrates. `_resolver_ready()` reflects built + credential-aware readiness so the FEA hides any chip we cannot deliver.
- **STEP 5 — flag store** (`feature_flags.py` + `feature_flags.json`): replaced the hardcoded `PAID_TIERS_ENABLED` + per-provider booleans with a server-readable, mtime-cached store. Default paid OFF / all paid providers OFF / free ON; a malformed file fails safe (never enables paid). Enabling a provider later is a config edit, no redeploy.
- **STEP 4 — FEA chip selector** (`ms.js` v132): the listing detail calls value-tiers and renders colour chips (green 0T / blue 1T / gold 2T) for ready:true only, hiding the service entirely when none. Tap calls price/yield with the chosen tier; 2T cost disclosed before the call; full workings shown (gross formula, annual rent, used/implied price, net-cost band, benchmark, AI context, provenance + date) with the mandatory "Indicative only - not financial advice or a formal valuation" label (H7a/H7b). DEMO_MODE guard, both branches. Added as new `tvs*` functions; legacy buyerPriceCheck/buyerYieldCalc left untouched.
- **Verify/deploy.** New modules sha-matched server + py_compile in BEA venv; pyflakes clean (0 undefined-name, 0 new warnings); module unit tests 9/9. FEA: node --check clean (local+server), diff = exactly the 2 button blocks -> chip containers + new fns, all smoke invariants intact. Deployed main.py + 4 modules + feature_flags.json + ms.js v132 + index.html; BEA restarted active v1.3.1; Cloudflare purged. Live: value-tiers returns the ZA 0T area-guide chip ready:true (fair_price + yield); 0T price-check returns a real benchmark range with charged:False. **smoke all-green** (server --local); fea_integrity OK (version-bump notes only); fea_baseline refreshed (ms.js v132/714993, ms.css v120/116322).
- **Cost model impact:** only FREE tiers enabled; no consumption/paid API called; PAID_TIERS_ENABLED stays False -> live AI unit economics unchanged. (0T price-check is a templated zero-model response; 0T area-yield reuses one cheap existing-budget Haiku narration.)
- **FILED (BACKLOG):** comics/watches fair-price + US/AU fair-price 0T have no free specific feed yet (config-only, hidden); collectible 1T feeds stay config-only until David sets BrickLink/Numista/JustTCG keys.

## Next Session (111)
- **Optional TVS follow-ups:** set BrickLink OAuth / Numista / JustTCG keys in env to light the LEGO/coins/TCG 1T chips; drop a `value_benchmarks.json` on the server to refresh area benchmarks without a redeploy; consider skipping the model on 0T area-yield to make it strictly zero-cost.
- **Maintenance auto-ship queue (unchanged):** JS-2 (`updateLocBadge`->`updateBadgeLabel`), then SCAN-8..12, HTML-1/HTML-2.
- Standing: self-hosted Overpass re-import (BLOCKER), Paystack live mode, EULA v1.6 attorney review, support@ mailbox (L3a).

## Last Completed (Session 109 — 2026-06-02)
- **Maroushka property-photo cleanup (David-requested · data-only, no code change).** Maroushka's 39 furnished-apartment listings (ids 192–230, one building) carried **510 published photos** (0–35/unit) — bloated with re-uploaded duplicates and with exterior/entrance/street/signage shots that exposed the location (193 Albert Street, 308 Florence Ribeiro Road, security-boom gate, "Entrance for 301,302…", "To Let" board), breaking seller anonymity (A2). David could not get Maroushka to trim them.
- **Method.** Downloaded all 510 from R2; content-hashed (md5 + 256-bit pHash/dHash) → **276 distinct images** (216 byte-identical re-uploads); union-find clustered near-identical (validated: zero clusters with intra-max pHash >14, no over-merge). Visually reviewed all 276 via labelled contact sheets + a 150-tile high-res confirmation pass to classify every cluster (interior / amenity / exterior-or-signage) — essential because location shots included UUID-named files (no address in the filename) and bare-numbered files that were exterior in some units, interior in others.
- **Rules applied per unit:** drop exact + near-identical duplicates (keep best) → remove location-revealing exterior/entrance/street/signage/perimeter shots (kept generic amenity per David: pool, garden, private balcony/patio) → cap at ≤10, prioritising unit-specific interiors, reserving up to 2 amenity slots. Shared interior "lobby/main-entrance" staircase shots were also removed (no unit value + address embedded in their R2 filename).
- **Result: 510 → 254 photos.** Removed 81 duplicates + 153 location-revealing + 22 over-cap. All 39 units now ≤10; 0 duplicate URLs; 0 location-leaking URLs except the pool amenity (see flag). Units 109 (198) & 308 (211) were already photoless; **Unit 314 (216)** is now photoless — its only 3 photos were an exterior entrance + 2 copies of the shared lobby (it never had a photo of the actual unit) → **needs real interior photos**.
- **Backup/verify/deploy.** Live `marketsquare.db` backed up (`marketsquare.db.bak-20260602-photocleanup`); every original description archived (`maroushka_photos_backup_2026-06-02.json` on server + local). Transactional UPDATE of the `[photos:]` prefix only (preserves description text; `photo_urls` left NULL — FEA reads `[photos:]` first, ms.js:248); dry-run diff confirmed (5 already-clean units reproduced byte-identically → no corruption). BEA restarted, Cloudflare purged. Live re-query: 254 photos, all ≤10, no dupes/leaks; spot-checks 192→9, 200→8, 205→10 (pool present), 216→0. **smoke 39/39**.
- **Flag (URL filename leak, not actioned):** the kept pool shots' R2 filenames still read `Pool_308_Florence_Ribeiro…` — the *image* shows only a pool, but a user opening the URL sees the address. Fully closing anonymity would mean re-uploading kept amenity images under sanitised keys (touches R2 storage). Offered to David as a follow-up.
- **Cost model impact:** none — no AI calls (local hashing only), no pricing/infra/concurrency/email/city-launch change.

## Next Session (110)
- **RM-4 Phase 1 LIVE (shadow):** deterministic zero-token `sensor.py` on server cron @ 01:30 UTC (=03:30 SAST) writing `findings.cron.json` for parity vs the Claude Sensor; model-tiering policy adopted as ORCHESTRATION_POLICY §11; `smoke_test.py` gained `--local`. First parity run: smoke 38/38, health/spend/anomaly all match; only gap = open_items 16 vs 17 = **AUDIT_PROGRESS.md marker staleness** → flip SCAN-2…6 to DONE + add `[· OPEN]` markers for A11Y-1/2/3, ADMIN_KEY, L3a, S5. After ~7d parity → `sensor.py --live` + pause `trustsquare-orch-sensor` task. Monday scan still on the Claude pass until ruff/vulture/pylint venv is on the box. (Plan: `LAUNCH_READINESS_PLAN.html`, Wave A.)
- **H2/H3 introduction notification loop — DONE (verified 2 Jun).** Was fully built in a prior session but had never run; switched on + tested end-to-end this session — 3 branded, anonymity-safe emails (new-intro->seller, accept/decline->buyer) confirmed delivered to Primary inbox. No code change (BEA already fired the webhooks; n8n workflows already active). Flag: the accept email references an in-app "anonymous messaging system" — confirm that channel exists / define the post-acceptance connection path.
- **Unit 314 (listing 216)** — get real interior photos from Maroushka (now photoless); same for already-empty Units 109/308.
- **Optional anonymity follow-up:** sanitise kept amenity image filenames on R2 (re-upload pool/garden shots under hashed keys, rewrite URLs) to remove the address from the photo URL.
- **Still pending from CHANGELOG Session 108 (built, NOT deployed):** Tiered Value Selector steps 3–5 + David's `git add/commit` of the BEA framework + `ai_service_tiers.py`.
- **Maintenance auto-ship queue (unchanged):** JS-2 (`updateLocBadge`→`updateBadgeLabel`), then SCAN-8…12, HTML-1/HTML-2.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 107 — 2026-06-02)
- **JS-1 DONE (HIGH · buyer-app crash-fix).** The Paystack payment-return handler in `ms.js` credited the local balance (`tuppence += credited`) then called `updateTuppenceDisplay()` to repaint it — a function defined nowhere (the only genuinely-undefined call in `ms.js` per the 1 Jun ESLint sweep). It threw a ReferenceError, aborting the rest of the top-up success path (success toast + navigation to the wallet) on every real payment return.
- **Fix:** renamed the single call to `updateTuppenceUI()` (the real repaint fn, `ms.js:823` — zero-arg, writes `tuppence` into the nav badge, balance display, home balance, and dash counter). Verified the target's signature/behavior match the call shape before renaming; the `tuppence += credited` credit line was left untouched (pure display repaint, not ledger — authoritative balance is server-side). One surgical Python str.replace (old-string unique; `updateTuppenceDisplay` 1→0; `ms.js` −5 bytes), never Edit/Write.
- **Gate:** frontend-only (`ms.js` + index cache-bust) — clears Gate 1 and Gate 2; JS-1 is the exact auto-ship boundary example in ORCHESTRATION_POLICY §5. Auto-shipped.
- **Verify/deploy:** `node --check` clean; diff vs freshly-pulled server = exactly the one renamed line + the `ms.js?v=130→131` cache-bust in index.html (local byte-identical to server beforehand). No BEA change → no restart. Server backups `*.bak-20260602-js1`; scp `static/ms.js` + `index.html` (bytes == local); Cloudflare purged. Live through CF: index serves `ms.js?v=131`, served `ms.js` has 0 `updateTuppenceDisplay`, fix site reads `tuppence += credited;`→`updateTuppenceUI();`; `/health` ok v1.3.1; **smoke 39/39** pre + post.
- **Cost model impact:** none — display-repaint rename only.

## Next Session (108)
- **JS-2 (HIGH)** — next auto-ship item in the maintenance queue: `ms.js:86` calls `updateLocBadge()` (defined nowhere) inside a "re-render everything" block after a listings mutation → ReferenceError on the location-badge refresh. Rename to `updateBadgeLabel()` (defined `ms.js:112`) after confirming its signature/behavior match the intended 2-line location-badge update. `node --check` + smoke before deploy.
- **Then the rest of the auto-ship queue:** SCAN-8 (duplicate dict key `category.cars.service_history`), SCAN-9 (dead `json` import + `body`/`body_bytes` locals), SCAN-10 (redundant `from datetime import timedelta` re-imports), SCAN-11 (dead locals / unused loop vars → `_`), SCAN-12 (`import os` in database.py), HTML-1 (dead `currentView`), HTML-2 (unused admin module-level locals).
- **Attended / staged track (deliberately NOT in the auto-ship queue):** S5 (MED · Gate 2 — gate the test/auto-approve payment endpoints behind a prod env flag, fail-closed; **stages** for David's approval), L3a (support@trustsquare.co real mailbox), SCAN-PANEL-1/2 (weekly-scan dashboard panel), the ADMIN_KEY FOUND_NEW, and A11Y-1/2/3.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 106 — 2026-06-02)
- **S3 DONE (Phase 2 · HIGH).** Moved the BEA API key off the `?api_key=` query param to the `X-Api-Key` header only, across the three seller-document (KYC) endpoints that shared the dual-mode dependency `auth.require_api_key_header_or_query`: `POST` / `GET` / `DELETE /users/{email}/documents[/{doc_id}]`. A key in the query string lands in nginx + Cloudflare logs and browser history; every other protected endpoint was already header-only.
- **Disproved the CDN assumption first (the gate).** The query fallback rested on a docstring claim that "Cloudflare strips custom headers." False, proven twice: (a) the admin app already calls these same three endpoints header-only in production through Cloudflare; (b) a live request through trustsquare.co with only `X-Api-Key` → 200, no-auth → 401, wrong key → 401. Cloudflare passes the header through untouched.
- **Edits (surgical, 3 files + cache-bust).** `bea_main.py`: 3 endpoint deps `require_api_key_header_or_query` → `require_api_key` (whole-file diff = exactly those 3 lines). `auth.py`: deleted the now-dead `require_api_key_header_or_query` fn + its orphaned `Query` import — the query-auth path is gone, not just unused. `ms.js`: retired all 3 `?api_key=` sites — the POST upload already sent the header (URL trimmed); the two `apiGet` list calls relied only on the query string (the shared `apiGet` sends no headers), so added an `apiGetAuth(path)` helper that sends `X-Api-Key` and pointed both at it. Bumped `ms.js?v=129 → v=130`. All via the Python str.replace driver, never Edit/Write.
- **Verify/deploy.** AST clean local + BEA venv; node --check clean; per-file diff vs the freshly-pulled server copy = only the intended changes (local was byte-identical to server on all four files); `main.py` imports under the live systemd unit env before restart. Server backups `*.bak-20260602-s3`; scp main.py/auth.py/static/ms.js/index.html (server bytes == local on all 4); BEA **active**, `/health` ok v1.3.1 (localhost + public). **Live auth test through CF:** GET header→200, GET `?api_key=`→401, GET no-auth→401; DELETE header→404 (auth passed, doc absent), DELETE `?api_key=`→401. Cloudflare purged; live app serves `ms.js?v=130`; **smoke all-green** pre + post.
- **Cost model impact:** none — auth-mechanism change only; no new AI calls, pricing, concurrency, email-volume, or city-launch change.

## Next Session (107)
- **Phase 2 cont. — S5 (MED):** gate the test / auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode is pending). AST + smoke before deploy.
- **Then L3a:** support@trustsquare.co real mailbox — one surgical env-driven `_smtp_send_reply()` edit + ops Cloudflare/Brevo config (see SUPPORT_MAILBOX_SETUP.md). Replies currently send from dmcontiki2@gmail.com.
- **Then:** SCAN-8…12 cleanup + SCAN-PANEL-1/2 (weekly-scan dashboard panel) + JS-1/JS-2 (ms.js latent ReferenceErrors) + HTML-1/HTML-2 dead-var cleanup + the ADMIN_KEY FOUND_NEW (`/admin/purge-cache` + `/admin/refresh-pois` unauthenticated when `ADMIN_KEY` unset) + A11Y-1/2/3 (focus ring, aria-live, admin alt-text/labels).
- **Deferred (David default):** EULA "Refunds" → "No Refunds" heading rename — leave for the v1.6 attorney-review pass (not an audit item).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 105 — 2026-06-01)
- **SCAN-7 DONE (HIGH · final KYC/vision crash-bug — block SCAN-1→7 now CLOSED).** `bea_main.py` `vision_draft` (`POST /listings/vision-draft`) called `background_tasks.add_task(_log_ai_spend, …)` (line 9365) but `background_tasks` was never in the endpoint signature — a guaranteed `NameError` → HTTP 500 at request time, *after* the Claude Vision call had already run (so the draft was computed then discarded and its spend never logged). Latent because every existing param had a `File(...)`/`Form(...)` default, so the route imported cleanly.
- **Fix:** added `background_tasks: BackgroundTasks` as the **first** parameter of `vision_draft` (a no-default param must precede defaulted ones — valid Python; matches `create_listing`/`create_intro`). `BackgroundTasks` already imported (line 1); FastAPI injects it by annotation regardless of position, so the unguarded call site is now always non-None. One surgical Python str.replace (old-string unique); +39 bytes (501792→501831), LF-only, diff = exactly one inserted line.
- **Verify/deploy:** `ast.parse` clean local + BEA venv; AST introspection confirms the deployed `main.py` `vision_draft` now lists `background_tasks` first. main.py deployed (server backup `main.py.bak-20260601-scan7`, server bytes == local); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅** pre- and post-deploy.
- **Minor finding (flagged, not actioned — one item/run):** `ADMIN_KEY` is unset on the server, so `/admin/purge-cache` + `/admin/refresh-pois` accept unauthenticated calls. Low risk (cache purge / POI refresh only); logged in AUDIT_PROGRESS.md for triage.
- **Cost model impact:** none — adds a framework-injected parameter so the already-billed vision-draft spend actually logs (it was dropped on the crash); no new AI calls, no pricing/concurrency change.

## Next Session (106)
- **Phase 2 resumes (KYC/vision crash-bug block closed) — S3 (HIGH):** move the BEA API key off the `?api_key=` query param (it lands in nginx/Cloudflare logs + browser history) to `X-Api-Key` header only across the 3 endpoints + ms.js; first verify/remove the CDN header-stripping assumption that justified the query fallback. AST + smoke before deploy.
- **Then S5 (MED):** gate the test/auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode pending).
- **Then L3a:** support@trustsquare.co real mailbox — one surgical env-driven `_smtp_send_reply()` edit + ops Cloudflare/Brevo config (SUPPORT_MAILBOX_SETUP.md).
- **Then:** SCAN-8…12 cleanup + SCAN-PANEL-1/2 (weekly-scan dashboard panel) + JS-1/JS-2 (ms.js latent ReferenceErrors) + HTML-1/HTML-2 dead-var cleanup.
- **New minor finding (this run):** `ADMIN_KEY` unset → `/admin/purge-cache` + `/admin/refresh-pois` unauthenticated; set the env or fail-closed (rank below S3/S5/L3a).
- **Deferred (David default):** EULA "Refunds" → "No Refunds" heading rename — leave for the v1.6 attorney-review pass (not an audit item).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 104 — 2026-06-01)
- **Tuppence Wallet UX overhaul (FEA, David-requested).** Buyer-app `marketsquare.html` / `ms.js` / `ms.css`:
  1. **"How introductions work"** — replaced the 4×8 model-table with a compact explainer: 7-category dropdown + scrollable one-feature-at-a-time top bar (chevrons + dots) + colour-coded answer card with a plain-language line.
  2. **Transaction history** — added type + date-range filters, a fixed-height (~340px) scroll, and a working "Load more"; client-side filter over loaded items.
  3. **AI Services** — moved below transactions and refreshed: added the previously-missing **AI Yield Estimate** + **AI Batch Card Lister** (both live + in active use) with accurate entry-point hints; clarified "Why No Intros?" lives in the listing Edit screen.
  4. **Refund removed as a mechanism** — dropped the Refunds filter option + the `refund` `_TX_ICON` ledger type. Kept all `non-refundable` policy/legal/EULA text and the BEA "never promise refunds" guardrail.
- **Verify:** node --check clean; CSS braces balanced; HTML intact; HIW data unit-tested (21/21 cells vs old table) + filter logic; full jsdom DOM test green. Bumped ms.js v128→129, ms.css v114→115.
- **Deploy:** scp'd index.html + static/ms.js + static/ms.css (remote bytes == local), Cloudflare purged, smoke **all-green**, FEA baseline refreshed (`--update-baseline`); live markers confirmed (hiw-cat present, refund/model-table absent, v129/v115). No BEA change → no restart.
- **Cost model impact:** none — display/UX only; added AI services already existed and were already billed.

## Next Session (105)
- **EULA wording decision (David):** ToS still has a clause titled "Refunds" (body: non-refundable) in the inline + rendered EULA. If the word should go from the heading too, rename "Refunds" → "No Refunds" across all EULA copies in one pass (default: leave for the v1.6 attorney-review pass).
- **Resume KYC crash-bug block — SCAN-7 (HIGH):** `background_tasks` undefined at ~9365 in `vision_draft` (F821) → add `background_tasks: BackgroundTasks` to the endpoint signature; verify AST + smoke before deploy.
- **After SCAN-7: Phase 2 normal order** — S3 (API key off `?api_key=` → X-Api-Key header), S5 (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), L3a (support@trustsquare.co mailbox), then SCAN-8…12 + JS-1/JS-2 + HTML-1/HTML-2 cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 103 — 2026-06-01)
- **SCAN-5 DONE (CRIT · KYC doc-upload crash-bug).** `upload_seller_document` (`POST /users/{email}/documents`, bea_main.py:7111) used undefined `MEDIA_DIR` in its R2-unconfigured local-fallback branch — a latent `NameError` → HTTP 500 on any document upload when `_S3_CONFIGURED` is false. Replaced with the module's `_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"` (line 942) after confirming it is the intended dir: it is the same dir `_s3_upload` mirrors to, nginx serves it at `/media/`, and the fallback's returned `url = /media/{safe}` resolves there.
- Latent in prod (R2 is configured, so the fallback never runs) → fix is behavior-neutral on the live path. One surgical Python str.replace (old-string unique); the `_LOCAL_MEDIA_DIR` definition (942) and its existing correct use (972) untouched; `os` (line 9) and `_LOCAL_MEDIA_DIR` both module-level bound so the line resolves at runtime.
- `ast.parse` clean local + BEA venv; deployed main.py (server backup `main.py.bak-20260601-scan5`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke all-green ✅**.
- **Continuity:** synced the 09:14Z weekly-discovery-scan block into the server's AUDIT_PROGRESS.md (was local-only) and purged the stale Cloudflare-cached `/dashboard/summary` (it had been pinned to a 31 May Session-98 snapshot; now reflects the live session).
- **Cost model impact:** none — undefined name → correct module constant; no new AI calls, no pricing/concurrency change.

## Next Session (104)
- **SCAN-7 (HIGH) — the last KYC crash-bug, then Phase 2 resumes.** `bea_main.py` `background_tasks` undefined at ~9365 inside `vision_draft` (F821) — the spend-logging `background_tasks.add_task(...)` will crash the vision-draft endpoint if reached. Fix: add `background_tasks: BackgroundTasks` to the endpoint signature (`BackgroundTasks` already imported) and confirm FastAPI injects it / the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (move API key off the `?api_key=` query param → X-Api-Key header only; verify/remove the CDN header-stripping assumption first), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2) + the ms.js latent-crash fixes JS-1/JS-2 + HTML-1/HTML-2 dead-var cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 102 — 2026-06-01)
- **SCAN-2/3/4/6 DONE (CRIT · KYC crash-bugs, batched).** Four latent `NameError` → HTTP 500 bugs on the SA-ID / KYC verification path in `bea_main.py`, all fixed in one run as the runner override permits (every edit is a top-level import or a name fix in the same file).
- **SCAN-2** bare `re.*` (7428/7455/7461/7558/7614/7757) was unbound — module had only `re as _re_match`. **SCAN-3** `hashlib.sha256` (7456) unbound. **SCAN-4** `urllib.request` (7503/7504) + `base64` (7506) unbound in the KYC doc-fetch block. **SCAN-6** two bare `_json.loads` (~6826/6830) where `_json` was never bound.
- **Fix:** added four module-level imports after `import json` — `import re`, `import hashlib`, `import urllib.request`, `import base64`; and changed the two `_json.loads` → `json.loads`. Pre-existing aliases/in-function imports left untouched (harmless shadows). Single Python str.replace driver, each old-string asserted unique.
- `ast.parse` clean local + BEA venv; module loads under systemd env with re/hashlib/urllib/base64 all bound. Deployed main.py (server backup `main.py.bak-20260601-scan2346`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**.
- **Cost model impact:** none — stdlib imports + a name fix; no new AI calls, no pricing/concurrency change.

## Next Session (103)
- **SCAN-5 (CRIT) then SCAN-7 (HIGH) — finish the KYC crash-bug block, numeric order.** SCAN-5: `MEDIA_DIR` undefined at 7104 in `upload_seller_document` → replace with `_LOCAL_MEDIA_DIR` (`/var/www/marketsquare/media`, line 935) after confirming that's the intended dir. SCAN-7: `background_tasks` undefined at ~9358 in `vision_draft` → add `background_tasks: BackgroundTasks` to the endpoint signature (BackgroundTasks already imported) and confirm the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — see SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 101 — 2026-06-01)
- **SCAN-1 DONE (CRIT · KYC crash-bug, first of SCAN-1→7 per the runner priority override).** `bea_main.py` referenced `SONNET_MODEL` at three sites in the SA-ID / KYC ID-verification path (model arg + two response payloads, ~7544/7571/7575) but the name was **never defined anywhere** in the module — a guaranteed `NameError` (HTTP 500) the moment that endpoint executed. Latent because the KYC path isn't exercised in prod yet.
- **Fix:** added a module-level constant `SONNET_MODEL = "claude-sonnet-4-6"` next to the other `*_MODEL` constants (line 900, right after `AA_MODEL`), matching the existing `VISION_MODEL` standard. One surgical Python string-replace; `ast.parse` passed locally and in the BEA venv on the server (SONNET_MODEL now resolves: 1 definition + 3 usages).
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 30/30 ✅**.
- **Cost model impact:** none — defines a constant already implied by the existing call; no new AI calls, no pricing/concurrency change.

## Next Session (102)
- **SCAN-2→7 (CRIT/HIGH · KYC crash-bugs) — continue in numeric order.** SCAN-2/3/4/6 are all "add a missing module-level import / fix a name" edits in `bea_main.py` (`re`, `hashlib`, `urllib.request`+`base64`, `_json`→`json`) and **may be batched into one run** per the override; SCAN-5 (`MEDIA_DIR`→`_LOCAL_MEDIA_DIR` at 7104) and SCAN-7 (`background_tasks` param on `vision_draft`, 9358) are separate. Verify AST + smoke 30/30 before deploy.
- After SCAN-7: resume Phase 2 normal order — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), then SCAN-8…12 cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 100 — 2026-06-01)
- **S4 DONE (Phase 2 · HIGH).** BEA CORS locked down. Was `allow_origins=["*"]` + `allow_origin_regex=".*"` (any site could call the BEA from a visitor's browser); now an explicit allowlist `https://trustsquare.co` + `https://www.trustsquare.co`, regex removed, `allow_credentials` still False.
- Same-origin apps (buyer/admin/dashboard all on trustsquare.co) + header/email auth mean no legitimate caller is affected. One surgical Python string-replace; `ast.parse` passed local and in the BEA venv on the server.
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**. Live CORS check: allowed origin → ACAO echoed; `https://evil.example` → no ACAO (blocked).
- **Continuity fix:** also completed the Session-99 baseline write-back the previous runner had left unsynced — the dashboard was still reporting Session 98 even though O2 was done + committed. STATUS/CHANGELOG/AUDIT_PROGRESS now scp'd; /dashboard/summary reflects the true latest session.
- **Cost model impact:** none — security/config change only.

## Next Session (101)
- **Phase 2 cont.** — **S3 (HIGH)**: move API key off the `?api_key=` query param (lands in nginx/Cloudflare logs + browser history) to X-Api-Key header only across the 3 endpoints + ms.js; first verify and then remove the CDN header-stripping assumption that justified the query fallback. **S5 (MED)**: gate the test/auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode pending).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 99 — 2026-05-31)
- **O2 DONE (deferred since 96/97/98).** Guarded sync of the four backend modules `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Previously these were imported by `main.py` but never auto-deployed (server-only).
- **deploy_marketsquare.bat**: added (a) pre-flight existence checks for all four modules (abort if any missing), (b) a new **Step 3d** that scp's the four modules to the server *before* the BEA restart so the new code is picked up atomically, each with the standard fail-on-error guard, and (c) a verify line confirming all four are present on the server post-deploy.
- **Live deploy this session**: server `auth.py` was still the old (pre-S1) version with the guessable `ms_admin_changeme` default; deployed the hardened fail-closed version (the other three were already byte-identical). Confirmed `MS_API_KEY` is set in the systemd unit env and the running process before deploying — fail-closed auth is therefore live-safe.
- Backed up server `auth.py` → `auth.py.bak-20260531`. scp'd all four modules; AST-checked each in the BEA venv (4/4 OK); shas now match local exactly. BEA restarted **active**, `/health` ok v1.3.1, bad-key write → 401 (auth still enforced), Cloudflare purged. smoke 30/30 ✅.
- **Cost model impact**: none — deploy-tooling change only, no AI-path or pricing change.

## Next Session (100)
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1 + O2 are now all closed.
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 98 — 2026-05-31)
- **Dashboard**: AI Cost & Margin panel moved above Email Triage (Ops tab).
- **Session-end write-back now mandatory** (CLAUDE.md checklist rewritten to 5 steps): scp STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server every session — dashboard is live-data-driven (no DATA hand-edit). Corrected the stale step-4. This guarantees the latest is always viewable.
- **MtG card orientation**: root cause = EXIF correction can't fix tag-less rotated scans (not a regression). (a) Rotated the 9 genuinely-sideways live cards upright (231,232,233,235,236,237,238,239,240); 234 left alone (genuinely landscape). Verified visually (first pass was 180° off — caught before finalising). (b) Forward fix `_vision_orient_image()`: landscape Collectors uploads get a cheap Haiku text-orientation check → rotate before baking. EXIF-independent, scales, fails open. Admin sends `category=Collectors`.
- **Horizontal card rows**: arrows were positioned outside the strip and clipped; moved inside (4px), shown on all viewports, strips set `flex-wrap:nowrap` + touch scroll. Fixes all 6 carousels. ms.css v114.
- Deployed main.py + dashboard.html + ms.css + admin.html + index.html; BEA restarted clean; Cloudflare purged; smoke 30/30 ✅.
- **Cost model impact**: vision-orient fires only on landscape Collectors uploads (~1 Haiku call, logged + ceiling-bound). Negligible.

## Next Session (99)
- **O2 (deferred since 96/97/98) — do first**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Live-safe (MS_API_KEY set).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths (currently batch-card path covered); set `monthly_income_usd` once paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), GET /listings pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 97 — 2026-05-31)
- **Phase-1 cost guardrails (audit C1–C3 + dashboard).** All BEA edits via Python string-replacement after a mid-session truncation was caught and the file restored byte-clean from the server.
- **C2 real-token costing**: `_MODEL_PRICE` per-1M-token table + `_token_cost()`/`_usage_tokens()`; `ai_spend_log` += input_tokens/output_tokens/cost_is_real; `_log_ai_spend()` computes exact cost from real tokens (flag `cost_is_real`), flat estimate when absent. Wired into all 7 paid AI ops. Live: real_token_pct 0→7.7% on first real call.
- **C3**: AI3 (price-check) + AI4 (yield) now log spend with real tokens (were unlogged).
- **C1 hard ceiling**: `_check_cost_ceiling()` REFUSES paid AI calls (HTTP 429) when daily per-user ($0.50 default) or platform ($100 default) USD cap is hit. Superusers exempt from user rail; fail-open; 0=off. Live-verified refusal + no-spend-on-refusal. Tunable via `PUT /admin/ai-spend/config`.
- **Dashboard**: no-auth `GET /dashboard/cost` + "💰 AI COST & MARGIN" Ops panel (cost/user, cost/call, margin, real-token %, modelled @100/@100k, ceiling bar, per-endpoint ●real/○est). `/admin/ai-spend` enriched.
- Deployed main.py + dashboard.html, BEA restarted clean, Cloudflare purged, smoke 30/30 ✅. Server backups: `main.py.s96bak`, `dashboard.html.s96bak`.
- **Cost model impact**: per-call economics unchanged; costing now exact (real tokens). C1 is a true spend cap — at the $100/day platform default, max AI exposure ≈ $3,000/mo regardless of load.

## Next Session (98)
- **O2 (deferred from 96/97)**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat` auto-deploy. The auth.py fail-closed change is live-safe (`MS_API_KEY` set), but wiring needs a coordinated deploy — do it as the first task.
- **Set AI spend config** once first paid subs arrive: `PUT /admin/ai-spend/config` with `monthly_income_usd` (unlocks the margin % on the dashboard) — ceilings already default-on.
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination (M0), Paystack plan wiring, EULA v1.6 attorney review.
- Continuity: session-end scp of STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to server is the handoff — `/dashboard/summary` parses currentSession from STATUS.

## Last Completed (Session 96 — 2026-05-31)
- **Full commercial-readiness audit** (deliverable: `TrustSquare_Commercial_Readiness_Audit.docx`; running log: `AUDIT_PROGRESS.md`). Reviewed all 128 BEA endpoints, FEA, server modules, deploy, security, cost. Findings: no hardcoded secrets, all SQL parameterised, SQLite WAL already on, every paid AI op modelled at 93–99% margin.
- **S2 (CRIT) DONE**: pulled server-only IP modules `auth.py`, `database.py`, `storage.py` into the repo (payments.py was already local); verified byte-identical to server via sha256. Previously unversioned/unbacked-up.
- **S1 (CRIT) DONE**: removed guessable default API key (`ms_admin_changeme`) from `auth.py` — BEA now fails closed if `MS_API_KEY` unset. Confirmed set on server, safe to deploy.
- **P1**: confirmed WAL + synchronous=NORMAL already enabled (no change needed).
- **Deferred (O2)**: auth/database/storage/payments NOT yet wired into auto-deploy — server copies are source of truth; auth.py change needs a coordinated guarded sync.
- **Cost model impact**: none this session (no AI-path changes). 100 users ≈ $11.61/mo, 100k users ≈ $2,474/mo, both net positive.

## Next Session (97)
- **Phase 1 cont. (the audit's next items):**
  1. **C1** — hard token/cost ceiling per-user + platform-wide: refuse when exceeded, not just alert.
  2. **C2** — derive cost from real API token counts, not flat constants.
  3. **C3** — add missing spend-logging to AI3 (price check) and AI4 (yield).
  4. Cost + margin + server-cost panels on `dashboard.html`.
- **O2**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into auto-deploy (coordinated; auth.py fail-closed change is live-safe since MS_API_KEY is set).
- **Continuity**: session-end now scp's STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server (done this session — `/dashboard/summary` was stale at Session 94). Add a deterministic session-end scp helper + scheduled morning brief per SESSION_BOOTSTRAP.md.
- Architecture decision (recorded): server scaling/KPI logic lives INSIDE the BEA as read-only observe-and-alert feeding the dashboard — never auto-scale, no new service, no machine that can spend money on its own.

## Last Completed (Session 95 — 2026-05-30, incl. 95b/95c/95d)
- **AI Price Check integrity (95)**: re-architected AI3 on "the model writes the sentence, the system produces the number." New helpers `live_usd_zar()`, `resolve_scryfall_id()`, `scryfall_price_by_id()`, `price_caution()`. Verified Scryfall prices for collectibles; no-feed categories return an honest qualitative guide or cannot_assess.
- **95b deliver-then-charge**: Tuppence deducted only after a verified service is delivered. AI3 no-feed → `cannot_verify`, free. AI4 yield rebuilt — gross computed in Python from purchase price + rent, missing input prompts the user, free until a real number is produced.
- **95c**: softened low-price warning to a neutral price-position note (no fraud/counterfeit language); `fraud_flag()` → `price_caution()`, verdict `below_verified_market`.
- **95d**: `deploy_marketsquare.bat` now auto-bumps `ms.js`/`ms.css` `?v=` and deploys static assets + Cloudflare purge — one-script deploy.

## Last Completed (Session 94 — 2026-05-30)
- **AI email triage — end to end.** `POST /email/inbound` (secret-auth) classifies inbound mail with Claude Haiku → `{category, urgency, draft_reply, auto_safe}`, stores in new `email_triage` table, AI spend logged. Categories: support/billing/legal/compliance/spam/other.
- **Conservative auto-send gate**: draft-only by default. Auto-reply only when `EMAIL_AUTO_SEND=1` + `GMAIL_APP_PASSWORD` set + model `auto_safe` + category ∈ {support,billing}. Legal/compliance/ambiguous always held. Spam → skipped.
- `GET /admin/email-triage` (API-key) for ops review. `_smtp_send_reply()` Gmail SMTP sender (587 STARTTLS), threads replies.
- **Cloudflare Email Worker** built (`cloudflare_email_worker/`): postal-mime parse → POST to BEA + safety-net forward to inbox, never bounces mail. wrangler.toml + README + package.json.
- `EMAIL_INBOUND_SECRET` generated, added to `/etc/environment`, BEA restarted. Verified live: support→drafted, spam→skipped, legal→drafted/high, bad secret→401. Smoke 30/30 ✅.
- **ROLLOUT COMPLETE (done this session)**: Cloudflare worker deployed (dashboard, postal-mime parser), `EMAIL_INBOUND_SECRET` set as Wrangler secret, `support@trustsquare.co` routed to worker. `GMAIL_APP_PASSWORD` + `GMAIL_ADDRESS` + `EMAIL_AUTO_SEND=1` added to `/etc/environment`. Live-verified: real support email auto-replied via Gmail SMTP (status=sent), legal email held (status=drafted). Replies currently send FROM dmcontiki2@gmail.com.
- **Ops dashboard panel**: `GET /dashboard/email-triage` (no-auth, obscure-URL) + "📧 EMAIL TRIAGE" panel on Ops tab — category/status counts + recent emails with drafts inline.
- ⚠️ **Repaired two truncations this session** (large-file Edit hazard): local `bea_main.py` (rebuilt from server, now 9972 lines) and `dashboard.html` (rebuilt tail via Python after a broken copy briefly deployed; now intact, smoke 30/30).
- **For David**: (1) Commit from PowerShell: `bea_main.py`, `dashboard.html`, `cloudflare_email_worker/`, `STATUS.md`, `CHANGELOG.md`. (2) Optional: route `legal@`/`billing@`/`compliance@`/catch-all to the same worker. (3) Optional: switch reply From-address to support@trustsquare.co via a transactional sender (e.g. Resend, already used in CityLauncher).

## Last Completed (Session 93 — 2026-05-29)
- **World Heritage / Wonders layer expanded 120 → 332 sites** (+212; clears ≥320 target). UNESCO-led: 142 UNESCO, 97 National Park, 47 National Museum, 46 Archaeological. South Africa 5 → **30 sites**; 91 countries total.
- **Photos all royalty-free (Wikimedia Commons)** with photographer attribution: 228/231 new scenic photos credit a named author; all 332 photo URLs verified HTTP-200 before deploy. `photo_author`/`photo_licence`/`photo_source` populated from Commons extmetadata.
- **Path fix**: canonical `wonders.json` moved to project root (matches loader + server layout); `assets/` synced; deploy script updated.
- **Auto-link cap 3 → 5** (`auto_link_wonders` default in bea_main.py) — reversible, flagged for David. FEA renders 5 cleanly.
- **All 55 live listings re-linked** via `relink_wonders.py` (selle