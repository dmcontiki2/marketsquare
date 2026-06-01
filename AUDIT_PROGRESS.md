# TrustSquare — Commercial Readiness Audit · Running Change Log

Companion to `TrustSquare_Commercial_Readiness_Audit.docx`. One line per change.
Severity-tagged findings (S=security, C=cost, P=perf, O=ops, D=data) match the report.

## Session 31 May 2026 — Audit + Phase 1 start

**Audit produced:** full-stack findings report (13 findings ranked CRIT/HIGH/MED) + 4-metric cost model. 128 BEA endpoints reviewed; no hardcoded secrets, all SQL parameterised, WAL already on.

**Fixes applied this session:**
- [S2 · CRIT · DONE] Pulled server-only modules `auth.py`, `database.py`, `storage.py` into the repo (payments.py already present). Verified byte-identical to server via sha256. Your auth/payment/storage IP is now versioned + backed up, not server-only.
- [S1 · CRIT · DONE] `auth.py`: removed guessable default API key (`ms_admin_changeme`). BEA now refuses to start if `MS_API_KEY` is unset (fail-closed). Confirmed `MS_API_KEY` is set on the server, so deploy is safe.
- [P1 · partial] Confirmed SQLite WAL + synchronous=NORMAL already enabled in database.py — corrected in report. Postgres migration remains a Phase-3 item.

**Next (Phase 1 cont.):** C1 token ceiling (per-user + platform daily budget, refuse-when-exceeded) · C2 real token-count costing · C3 add spend logging to AI3/AI4 · dashboard cost panels.

**Cost snapshot (modelled, see report for detail):** every paid AI op 93–99% margin; 100 users ≈ $11.61/mo total; 100k users ≈ $2,474/mo total, net positive. Real-token actuals replace these once C2/C3 land.

## Session continuity design (decided 31 May 2026)
Zero-manual-git session handoff, server as source of truth. See SESSION_BOOTSTRAP.md.
- Session end: Claude scp's STATUS/CHANGELOG/AUDIT_PROGRESS to server (no git, no manual push).
- Session start: paste "New TrustSquare session — baseline from the server and continue."
  Claude fetches /dashboard/summary and briefs back. Plus a scheduled morning brief (hands-off).
- Honest limit: a chat must be opened by a human, so the minimum input is one pasted line.
- Phase-1 build items: enrich /dashboard/summary (audit + 4 cost metrics + tasks);
  scheduled morning-brief task; deterministic session-end scp helper.

## Session 97 — 31 May 2026 · Phase 1 cost guardrails landed

- [C2 · DONE] Real-token costing. `_MODEL_PRICE` (per-1M-token list prices) + `_token_cost()` + `_usage_tokens()`. `ai_spend_log` += input_tokens/output_tokens/cost_is_real. `_log_ai_spend()` takes optional token counts → exact cost when present, flat estimate otherwise. Wired into all 7 paid AI ops. Live: real_token_pct 0→7.7% on first real call.
- [C3 · DONE] AI3 (price-check) + AI4 (yield) now log spend with real tokens (were unlogged).
- [C1 · DONE] `_check_cost_ceiling()` hard daily ceiling — REFUSES (429), not just alerts. Per-user ($0.50 default) + platform ($100 default) caps in ai_spend_config. Superusers exempt from user rail; fail-open on error; 0=off. Live-verified refusal: platform cap < today's spend → 429 + no spend logged.
- [C4 · DONE] `GET /dashboard/cost` (no-auth) + "💰 AI COST & MARGIN" dashboard panel: cost/user, cost/call, margin, real-token %, modelled @100/@100k, ceiling bar, per-endpoint ●real/○est. `/admin/ai-spend` enriched; config PUT accepts ceilings.
- Deployed main.py + dashboard.html, BEA restarted clean, Cloudflare purged, smoke 30/30. Server backups: main.py.s96bak, dashboard.html.s96bak.

**Next (Phase 1 close → Phase 2):** O2 guarded sync of auth/database/storage/payments into auto-deploy. Then Phase 2 audit items.

## Session 98 — 31 May 2026 · Operator-reported UX/data fixes (not audit findings)

- Dashboard: AI Cost panel moved above Email Triage.
- Session-end checklist rewritten (CLAUDE.md) — baseline write-back (scp 4 docs) is now a mandatory step; dashboard is live-data-driven, no DATA hand-edit.
- MtG cards: 9 sideways live cards rotated upright (234 left alone — genuinely landscape). Forward fix: `_vision_orient_image()` on landscape Collectors uploads (text-based, EXIF-independent). Admin sends category=Collectors.
- Horizontal card rows: arrows moved inside edge + shown all viewports; strips flex-wrap:nowrap + touch scroll. ms.css v114.
- O2 (auth/db/storage/payments deploy-sync) STILL deferred — next session priority.

## Session 99 — 31 May 2026 · O2 DONE (auto-deploy module sync)

- [O2 · DONE] `deploy_marketsquare.bat` now syncs `auth.py`/`database.py`/`storage.py`/`payments.py` to the server (pre-flight existence checks + new Step 3d scp before BEA restart + post-deploy verify line). These were repo-only and never auto-deployed.
- Live-deployed the four modules this run (server `auth.py` was still the pre-S1 `ms_admin_changeme` version — now the hardened fail-closed one). MS_API_KEY confirmed set in systemd env + running process first; server auth.py backed up to `auth.py.bak-20260531`. AST 4/4 OK, BEA active, /health v1.3.1, bad-key→401, CF purged, smoke 30/30.
- **Phase 1 + O2 now all CLOSED.** Next open items are Phase 2 audit findings from the readiness report.


## Session 100 — 1 June 2026 · Phase 2 starts — S4 CORS lock-down

> ⚠️ **RUNNER PRIORITY OVERRIDE (set 1 June 2026, David-approved).** The next items to pick are the **KYC crash-bugs SCAN-1 → SCAN-7** in the "Static-analysis discovery scan" block below — these are guaranteed runtime NameError crashes in the live SA-ID/KYC verification path and outrank S3, S5, and L3a. Work them **in numeric order (SCAN-1 first)**, one per run, before resuming S3/S5/L3a. SCAN-2/3/4/6 (missing module-level imports `re`, `hashlib`, `urllib`, `base64`, and `_json`→`json`) can optionally be batched into ONE run since they are all "add a top-level import / fix a name" edits in the same file — but still verify AST + smoke 30/30 before deploy. After SCAN-7, resume the normal order: S3 → S5 → L3a → SCAN-8…12.

- [S4 · HIGH · DONE] BEA CORS restricted from `allow_origins=["*"]` + `allow_origin_regex=".*"` to an explicit allowlist (`https://trustsquare.co`, `https://www.trustsquare.co`); regex removed; `allow_credentials` stays False. Same-origin apps + header/email auth → no legitimate caller affected. Deployed main.py (backup `main.py.bak-20260601`), AST OK local+server-venv, BEA active, /health v1.3.1, CF purged, smoke 39/39. Live: allowed origin echoed in ACAO, evil origin blocked (no ACAO).
- Continuity fix: also completed the **Session-99 baseline write-back** the previous runner had skipped (dashboard was stuck on Session 98 though O2 was done/committed). Docs now scp'd; /dashboard/summary current.
- **Phase 2 remaining:** S3 (HIGH — move API key from `?api_key=` query param to X-Api-Key header only; verify/remove the CDN header-stripping assumption first), S5 (MED — gate test/auto-approve payment endpoints behind a production env flag, fail-closed). Then S-sweep input validation, D1 fabrication sweep (Phase 4).

- [OPS · L3a · OPEN] **support@trustsquare.co not a real mailbox** (verified Session 100). Triage pipeline works but sends replies from `dmcontiki2@gmail.com` (Gmail SMTP, display name "TrustSquare Support"); MX = Cloudflare Email Routing (forward-only), domain SPF/DKIM/DMARC point at Brevo. So that earlier triage "sent" reply went from the personal Gmail, not support@. Launch blocker stays OPEN. Full fix plan + ready-to-ship BEA code change documented in `SUPPORT_MAILBOX_SETUP.md`. Owner: ops for Cloudflare/Brevo/env (dashboard access needed); Claude for the one surgical `_smtp_send_reply()` env-driven edit next session.

## Static-analysis discovery scan — 1 June 2026 (ruff F/E9/B + vulture + pylint cyclic-import on bea_main/auth/database/storage/payments)

Read-only scan run from a Cowork session at David's request. NO code changed, NO deploy. **PRIORITY (updated 1 June 2026): the CRIT KYC crash-bugs SCAN-1 → SCAN-7 now run FIRST, ahead of S3/S5/L3a — see the RUNNER PRIORITY OVERRIDE note under the Session 100 header.** The remaining MED/LOW items (SCAN-8…12) stay at the back of the queue after S3/S5/L3a. Each item is scoped to one surgical fix. Verify with `python3 -c "import ast; ast.parse(...)"` + smoke 30/30 before deploy, per the runner's normal rules.

**CRIT — latent runtime crashes (NameError) in the KYC / SA-ID verification path. These endpoints will 500 the moment they execute; appear never exercised in prod yet. Highest priority of this block.**
- [SCAN-1 · CRIT · DONE] `bea_main.py` `SONNET_MODEL` is undefined (F821 at 7541, 7568, 7572) — referenced in the KYC ID-verification call but never assigned anywhere in the module. The codebase standard is `VISION_MODEL = "claude-sonnet-4-6"` (line 8952). Fix: define a module-level `SONNET_MODEL = "claude-sonnet-4-6"` near the other *_MODEL constants (≈ line 897), OR replace the three `SONNET_MODEL` refs with `VISION_MODEL`. One choice, applied consistently.
- [SCAN-2 · CRIT · OPEN] `bea_main.py` bare `re` used with no binding (module imports it only as `_re_match`, line 4000) in `_sa_id_validate` (7425), `_hash_id_number`, `_normalise_name` (7452/7458), and the KYC fetch block (7555, 7611, 7754). Fix: add `import re` at module top (line ~18 block). Verify no later code depends on `re` being absent (it doesn't — `_re_match` alias is separate and can stay).
- [SCAN-3 · CRIT · OPEN] `bea_main.py` bare `hashlib` undefined at 7453 (`_hash_id_number`) — F821. Fix: add `import hashlib` at module top.
- [SCAN-4 · CRIT · OPEN] `bea_main.py` bare `urllib` undefined at 7500/7501 and `base64` at 7503 (KYC doc fetch). Fix: add `import urllib.request` and `import base64` at module top.
- [SCAN-5 · CRIT · OPEN] `bea_main.py` `MEDIA_DIR` undefined at 7104 (F821, `upload_seller_document`) — module defines `_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"` (line 935) instead. Fix: replace `MEDIA_DIR` with `_LOCAL_MEDIA_DIR` at 7104 (confirm that is the intended dir first).
- [SCAN-6 · CRIT · OPEN] `bea_main.py` `_json` undefined at 6823/6827 (F821) — module imports `json` at top and `json as _json_mod` at 8191. Fix: replace `_json` with `json` at both 6823/6827.
- [SCAN-7 · HIGH · OPEN] `bea_main.py` `background_tasks` undefined at 9358 (F821) inside `vision_draft` — the spend-logging `background_tasks.add_task(...)` will crash the vision-draft endpoint if reached. Fix: add `background_tasks: BackgroundTasks` to the endpoint signature (BackgroundTasks already imported, line 1) and ensure FastAPI injects it; confirm the call site is inside the request handler.

**MED — correctness / dead code (no crash, but real):**
- [SCAN-8 · MED · OPEN] `bea_main.py:6017` duplicate dict key literal `"category.cars.service_history"` (F601) — the second definition silently overrides the first in the trust-score points map. Confirm intended entry (likely one should be a different key) and remove/rename the duplicate.
- [SCAN-9 · MED · OPEN] `bea_main.py` `import json` unused at 8233 (F401, local re-import) + `body`/`body_bytes` assigned-never-used at 8231/8234 (F841). Dead code in one handler. Fix: delete the three unused lines (verify the handler still parses its body elsewhere).
- [SCAN-10 · LOW · OPEN] `bea_main.py` redundant `from datetime import timedelta` re-imports at 4001 and 8446 (F811 — already imported at line 18). Remove both local re-imports.
- [SCAN-11 · LOW · OPEN] `bea_main.py` unused locals: `skip_fields` (3878), `sig_suburb_id` (4179), `cutoff` (6225), and unused loop vars `hi2` (5910), `idx` (10239) (F841/B007). Vulture also flags unused vars `family` (1495,1596), `hint` (2254) and unused import `_sqlite3` (1685). Remove dead assignments; rename unused loop vars to `_`.
- [SCAN-12 · LOW · OPEN] `database.py:2` `import os` unused (F401). Remove.

**Clean (no action — scan confirmed these are NOT problems):**
- No circular imports. Dependency graph is one-directional: bea_main → {database, auth, storage, payments}; the four leaf modules import none of each other. (pylint cyclic-import: 0 findings.)
- No hardcoded secrets surfaced by this pass (consistent with the 31 May audit).
- AST parses clean; module is not broken at import time — all SCAN-1..7 crashes are latent (only fire when those specific endpoints run).

**Scope note:** scan covered the production Python modules only (bea_main/auth/database/storage/payments + smoke_test). The large HTML/JS bundles (marketsquare.html, ms.js, dashboard.html) and utility dirs (scripts/, archive/, pptx_tools/) were NOT linted this pass — a JS/ESLint sweep of ms.js is a candidate follow-up if desired.

## ESLint sweep — ms.js — 1 June 2026 (no-undef, no-unused-vars, no-dupe-keys/args, no-unreachable, no-redeclare, no-const-assign, etc.)

Read-only ESLint 9 sweep of `ms.js` (11,891 lines, browser-script, browser+Leaflet globals) at David's request. NO code changed, NO deploy. ms.js is in good structural shape: **0 errors** — no duplicate object keys, no duplicate args, no unreachable code, no redeclarations, no const reassignment anywhere. Two genuine latent-crash bugs found (below). These are FEA bugs; the phase-runner deploys ms.js to `/var/www/marketsquare/static/ms.js` (nginx serves from /static/ not root — see CLAUDE.md). ⚠️ ms.js is a large file — per CLAUDE.md HTML/JS write rule, apply edits via a Python open/read/str.replace()/write driver (assert each old-string matches exactly once) + `node --check` before deploy, NOT the Edit/Write tool. These rank BELOW the Python KYC crash-bugs (SCAN-1..7) but are worth doing before the LOW-severity SCAN-8..12.

**HIGH — latent ReferenceError crashes (call to a function that exists under a different name; both on live, reachable paths):**
- [JS-1 · HIGH · OPEN] `ms.js:617` calls `updateTuppenceDisplay()` which is defined NOWHERE (no-undef). Fires right after a Tuppence credit (`tuppence += credited`), so the post-purchase/AI-session balance refresh throws and the success path aborts. The intended function is almost certainly `updateTuppenceUI` (defined line 810). Fix: change `updateTuppenceDisplay()` → `updateTuppenceUI()` at 617 — BUT first confirm `updateTuppenceUI` takes no args / same call shape and actually repaints the balance the caller expects. If signatures differ, adapt the call rather than blind-rename.
- [JS-2 · HIGH · OPEN] `ms.js:86` calls `updateLocBadge()` which is defined NOWHERE (no-undef). Sits in a "re-render everything" block (alongside `renderGrid()`/`renderCatCounts()`) after a listings mutation, so the location-badge refresh throws. Intended function is almost certainly `updateBadgeLabel` (defined line 112). Fix: change `updateLocBadge()` → `updateBadgeLabel()` at 86 — same caveat: verify the target's signature/behavior matches the intended 2-line location badge update before renaming.

**Clean / NOT bugs (scan confirmed — do NOT action these):**
- `loadDashboard` (ms.js:4370) is undefined but guarded by `if (typeof loadDashboard === 'function')` — an intentional optional hook, safe. Leave as-is.
- 115 `no-undef` warnings are dominated by legit cross-file globals defined in `marketsquare.html` (`SELLERS` 44×, `LISTINGS` 34×, `SELLER_PHOTOS`, `CATS`, `PROSPECTS`, `acceptedIntros`) and the Leaflet library global `L` (5×). Not bugs — ESLint just can't see the HTML inline scripts / CDN libs. JS-1/JS-2 are the only two with no definition in ANY file.
- ~317 `no-unused-vars` warnings are overwhelmingly top-level FEA functions invoked from inline `onclick=`/`oninput=` handlers in the HTML (e.g. `topUp`, `signInSeller`, `setPlan`, `setFilter` — all verified present in marketsquare.html). These are NOT dead code; do NOT delete them. (Genuinely-unused *local* variables exist but are low value and high false-positive risk in a file with this many HTML-facing globals — deliberately NOT logged as action items to avoid the runner deleting a live handler.)

**Scope note:** this sweep covered `ms.js` only. `marketsquare.html`, `marketsquare_admin.html`, and `dashboard.html` inline scripts were NOT linted (they hold the globals above); a separate HTML-embedded-JS sweep is a possible future item but lower priority given ms.js came back this clean.

## ESLint sweep — marketsquare.html + marketsquare_admin.html inline JS — 1 June 2026

Read-only ESLint 9 sweep of the inline `<script>` blocks in both HTML apps (extracted with line numbers preserved; linted with browser + Leaflet + all 412 ms.js top-level names declared as known globals so cross-file refs aren't false-flagged). NO code changed, NO deploy. **Result: both files are clean of crash-class bugs.** Zero undefined references (no typo'd function calls like the ms.js JS-1/JS-2), zero duplicate object keys, zero unreachable code, zero genuine redeclarations, zero const reassignment. marketsquare.html's inline JS is just a thin ~174-line bootstrap (real FEA logic lives in ms.js); admin.html holds ~3,500 lines of inline JS and still came back crash-clean.

Only minor, non-urgent items found — all LOW. ⚠️ Per CLAUDE.md, NEVER use Edit/Write on marketsquare.html or marketsquare_admin.html (they truncate) — apply any of these via a Python open/read/str.replace()/write driver + verify the file still ends with `</html>`, per the HTML WRITE RULE. These rank at the very BACK of the queue, after SCAN-8…12.

**LOW — dead code (admin.html inline JS; safe to remove — confirmed unreferenced anywhere in HTML + ms.js):**
- [HTML-1 · LOW · OPEN] `marketsquare_admin.html:2785` `let currentView = 'onboard'` is assigned at declaration and reassigned at 2794 (`currentView = name`) but NEVER read anywhere. Dead state variable. Fix: remove both the declaration and the assignment at 2794 (confirm 2794 isn't doing other work on the same line first).
- [HTML-2 · LOW · OPEN] `marketsquare_admin.html` unused module-level locals flagged by no-unused-vars and confirmed unreferenced: `editingIdx` (1834), `photoFile` (4503), `tier` (5216), `ur` (5218), `status` (5290). Each is assigned but never read. Fix: remove the dead assignments (verify each line isn't a destructuring that also binds a used sibling before deleting).

**Reviewed — NOT bugs (do NOT action; documented so a future pass doesn't re-flag them):**
- `marketsquare_admin.html:5369` `tshLoad = async function(email){…}` (no-func-assign) is an INTENTIONAL monkey-patch: it saves `const _origTshLoad = tshLoad` (5368) then wraps it to also call `docHubLoad` after the original. Valid, deliberate. Leave as-is.
- `DOC_TYPE_LABELS_SERVICES_CAS` (admin 4820) is "unused" but INTENTIONAL: the dispatcher `_docTypeLabelsForCategory` (4861) has an explicit comment "casuals handled by sub-type" and deliberately routes `services` → `DOC_TYPE_LABELS_SERVICES_TECH`. The CAS map is reserved for future sub-type wiring, not dead-by-mistake. Do NOT delete without product sign-off — it's a placeholder for planned behavior, not a bug.
- The bulk of admin's ~105 and fea's ~5 no-unused-vars warnings are top-level functions called from inline `onclick=`/`oninput=` handlers in the same HTML — NOT dead code. Not logged.
- All `no-undef` for `SELLERS`/`LISTINGS`/`CATS`/`SELLER_PHOTOS`/`PROSPECTS`/`acceptedIntros` (defined in marketsquare.html's `#ms-data` block) and `BEA_URL`/`API_KEY`/`sellerData`/`showToast`/`formatZAR`/`isSuperuser` (defined in admin's own script) and `L` (Leaflet) are legit cross-file/library globals — NOT bugs.

**Net of the full FEA/HTML lint pass (ms.js + both HTML apps):** the only genuine FEA crash bugs are JS-1 and JS-2 in ms.js (already queued above). The HTML apps themselves are crash-clean; only trivial dead-variable cleanup remains (HTML-1, HTML-2). Front-end static-analysis coverage is now complete — no further JS/HTML lint sweep needed unless new code lands.

## Weekly discovery-scan dashboard panel — build item (queued 1 June 2026, David-requested)

David wants a SEPARATE dashboard report for weekly scan findings (found-vs-fixed over time), distinct from the audit reporting, placed RIGHT AFTER the "💰 AI COST & MARGIN" panel. A weekly scheduled scan (`weekly-discovery-scan`, Mondays 5 AM) now writes `SCAN_REPORT.json` to the project root (schema: totals{found_this_week,fixed_this_week,still_open}, severity_breakdown, open_issues[], fixed_issues[], history[{week_of,found,fixed,open}]). A baseline `SCAN_REPORT.json` already exists in the repo root. "Fixed" = re-scan delta (issue present last week, gone this week — which naturally captures items THIS runner fixed, since they disappear from the scan).

Build this as a normal runner item (surgical, verify smoke 30/30, deploy per CLAUDE.md). Two parts, can be one run:

- [SCAN-PANEL-1 · OPS · OPEN] BEA: add a no-auth `GET /dashboard/scan` endpoint mirroring the existing `/dashboard/cost` pattern (≈ bea_main.py line 10627). It reads `SCAN_REPORT.json` from the app dir via the existing `_read_file()` helper (used by /dashboard/summary), `json.loads` it, and returns it (or `{"available": false}` if the file is missing, so the panel degrades gracefully). Do NOT parse it into the STATUS/CHANGELOG summary — keep it a separate endpoint so scan reporting stays distinct from audit reporting, per David. Add `SCAN_REPORT.json` to the deploy list (deploy_marketsquare.bat) and scp it to /var/www/marketsquare/ alongside the .md docs so the server copy exists.
- [SCAN-PANEL-2 · OPS · OPEN] dashboard.html: add a new panel immediately AFTER the AI Cost & Margin panel (anchor: the `💰 AI COST & MARGIN` health-title block, ≈ dashboard.html line 1316; insert the new panel div after that panel's closing div, BEFORE Email Triage). Panel title e.g. "🔍 WEEKLY CODE SCAN — found vs fixed". On load, fetch `/dashboard/scan`; render: this week's found / fixed / still-open as metric tiles; a severity breakdown; the open_issues list (id · sev · file · summary); and a small found-vs-fixed-over-time line/bar from `history[]` (Chart.js is already loaded in the dashboard — reuse it). If `available:false`, show "No scan report yet — first weekly scan runs Monday." Keep styling consistent with the AI Cost panel (same .health-title/.health-grid classes). ⚠️ dashboard.html is large — edit via the Python str.replace driver + node --check, never Edit/Write; respect the DASHBOARD VERSION GUARD (check server currentSession first).

Note: this is OPS/reporting infra, lower priority than the KYC crash-bugs (SCAN-1..7) and JS-1/JS-2 — schedule it after those but it's independent, so it c

## Session 101 — 1 June 2026 · SCAN-1 DONE (KYC crash-bug)

- [SCAN-1 · CRIT · DONE] Defined module-level `SONNET_MODEL = "claude-sonnet-4-6"` (bea_main.py:900, beside `AA_MODEL`) — the name was referenced at 7544/7571/7575 in the SA-ID/KYC verification path but never bound (latent NameError → 500). AST OK local + BEA venv; deployed main.py (backup `main.py.bak-20260601`); BEA active, /health v1.3.1, CF purged, smoke 30/30 ✅. Cost model impact: none. **Next: SCAN-2→7 (may batch the import/name fixes SCAN-2/3/4/6), in numeric order, before resuming S3/S5/L3a.**


## Session 102 — 1 June 2026 · SCAN-2/3/4/6 DONE (batched KYC crash-bugs)

- [SCAN-2 · CRIT · DONE] Added module-level `import re` — bare `re.*` in the SA-ID/KYC path (7428/7455/7461/7558/7614/7757) was unbound (module only had `re as _re_match`). Alias left intact.
- [SCAN-3 · CRIT · DONE] Added module-level `import hashlib` — `hashlib.sha256` in `_hash_id_number` (7456) was unbound.
- [SCAN-4 · CRIT · DONE] Added module-level `import urllib.request` + `import base64` — KYC doc-fetch block (7503/7504/7506) referenced both unbound. In-function locals at 543/655/5070 left intact (harmless shadow).
- [SCAN-6 · CRIT · DONE] Replaced two bare `_json.loads` → `json.loads` in the score-guidance fallback (~6826/6830); `_json` was unbound there (every other `_json` use has an in-function `import json as _json`).
- Single Python str.replace driver, each old-string asserted to match exactly once; AST clean local + BEA venv; module loads under systemd env with re/hashlib/urllib/base64 all bound. Deployed main.py (backup `main.py.bak-20260601-scan2346`); BEA active, /health v1.3.1; CF purged; **smoke 39/39 ✅**. Cost model impact: none.
- **Next: SCAN-5** (`MEDIA_DIR`→`_LOCAL_MEDIA_DIR` at 7104, confirm dir first) then **SCAN-7** (`background_tasks: BackgroundTasks` param on `vision_draft`, ~9358), in numeric order. After SCAN-7 resume Phase 2: S3 → S5 → L3a → SCAN-8…12.

## Weekly discovery-scan — 2026-06-01 09:14Z (auto)

Read-only re-scan (ruff F/E9/B/C90 + vulture + pylint cyclic-import on bea_main/auth/database/storage/payments/smoke_test; eslint 9 on ms.js + extracted inline JS of marketsquare.html/marketsquare_admin.html). NO code changed, NO deploy. **No new findings this week** — 0 FOUND_NEW. Nothing appended to the action queue.

Re-scan delta vs the 1 June baseline (informational only — DONE marking is the runner's job, not recorded here): **5 issues disappeared from the scan** (fixed by the audit-runner) — SCAN-1 (`SONNET_MODEL` now defined bea_main.py:904), SCAN-2 (`import re` at :11), SCAN-3 (`import hashlib` at :12), SCAN-4 (`import urllib.request`/`import base64` at :13-14), SCAN-6 (`_json` refs now resolve, no longer F821). **11 baseline issues still detected and remain in the queue above** (no re-append): SCAN-5, SCAN-7, SCAN-8, SCAN-9, SCAN-10, SCAN-11, SCAN-12, JS-1, JS-2, HTML-1, HTML-2 — current line numbers refreshed in SCAN_REPORT.json (baseline lines shifted ~+3–7 in bea_main.py after the SCAN-1/import fixes landed). SCAN-5 (`MEDIA_DIR` F821 @7111) and SCAN-7 (`background_tasks` F821 @9365) remain the only latent-crash F821s left in the Python KYC/vision paths. Details + full open/fixed lists in SCAN_REPORT.json.

## Session 103 — 1 June 2026 · SCAN-5 DONE (KYC doc-upload crash-bug)

- [SCAN-5 · CRIT · DONE] `bea_main.py` `upload_seller_document` (`POST /users/{email}/documents`) used undefined `MEDIA_DIR` at line 7111 in the R2-unconfigured local-fallback branch (latent F821 → NameError/500 on any document upload when `_S3_CONFIGURED` is false). Replaced with the module's `_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"` (line 942) — confirmed the intended dir (it is what `_s3_upload` mirrors to, nginx serves it at `/media/`, and the fallback's `url = /media/{safe}` resolves there). One surgical str.replace (old-string unique); definition (942) + existing use (972) untouched; `os` (line 9) + `_LOCAL_MEDIA_DIR` both module-level bound. AST clean local + BEA venv; deployed main.py (backup `main.py.bak-20260601-scan5`); BEA active, /health v1.3.1; CF purged; smoke all-green ✅. Cost model impact: none.
- Continuity: synced the 09:14Z weekly-discovery-scan block to the server (was local-only) and purged the stale Cloudflare-cached /dashboard/summary (it had been pinned to a 31 May Session-98 snapshot; now reflects the live session).
- **Next: SCAN-7 (HIGH)** — last of the KYC crash-bug block: `background_tasks` undefined at ~9365 in `vision_draft` → add `background_tasks: BackgroundTasks` to the endpoint signature (BackgroundTasks already imported), confirm the call site is inside the handler. After SCAN-7, resume Phase 2 normal order: S3 → S5 → L3a → SCAN-8…12 + SCAN-PANEL-1/2 + JS-1/JS-2 + HTML-1/HTML-2.
