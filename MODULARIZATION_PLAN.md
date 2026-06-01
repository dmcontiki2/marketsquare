# bea_main.py Modularization Plan
**Drafted Session 99 · 1 June 2026 · the keystone quality investment**

`bea_main.py` is **10,705 lines / 129 routes / 191 defs**. It is the single biggest quality risk (large-file truncation has bitten us repeatedly) and the blocker to safe concurrent agent work (two agents cannot edit one 10k-line file). This plan splits it into FastAPI `APIRouter` modules **incrementally, atomically, and gated** — never a big-bang rewrite.

## Hard rules (non-negotiable)
1. **One extraction at a time.** Each step is fully done + verified + deployed before the next begins. Never leave `bea_main.py` half-split.
2. **Atomic or not started.** Do not begin an extraction unless it can finish within the session, clear of the build runner's window (fires 19/01/07/13 local). Check time-to-next-run first.
3. **Safe-edit method only.** Python `open/read/str.replace()/write` driver, asserting each old-string matches once. Never the Edit/Write tool on `bea_main.py`. `ast.parse` after every change.
4. **Full gate per step:** `ast.parse` (local) → `node --check` if JS touched → `python3 smoke_test.py` 30/30 → scp to server → AST in the BEA venv → restart → `/health` ok + bad-key→401 → 2-3 live endpoint GETs for the moved routes. If any gate fails: revert, document, stop.
5. **Server is source of truth.** Back up `main.py` on the server before each deploy (`main.py.modN.bak`).

## Extraction order (lowest-risk first — earn confidence)
The cost helpers are the safest seed (self-contained, recently written, well understood). Routes come after a shared `core` exists for them to import.

| Step | Extract | To file | Risk | Notes |
|---|---|---|---|---|
| M1 | `_token_cost`, `_usage_tokens`, `_log_ai_spend`, `_check_cost_ceiling`, `_maybe_fire_spend_alert`, `_AI_COST`, `_MODEL_PRICE` | `core_spend.py` | Low | Deps: `database`, `_log`, `_fire_webhook`, `N8N_WEBHOOK_AI_ALERT`. Pass `_fire_webhook` + env in, or move them too. Import back into bea_main. |
| M2 | `_s3_upload`, photo compression consts/helpers | `core_media.py` | Low | Self-contained image/R2 helpers. |
| M3 | wonder/POI/geo helpers (`_haversine_km`, `_overpass_query_pois`, `_geocode_address`, `_load_wonders`, …) | `core_geo.py` | Med | Several callers; grep all refs first. |
| M4 | `/admin/*` routes (12) | `routes_admin.py` (APIRouter) | Med | First ROUTER extraction — proves the pattern: `router=APIRouter()`, `app.include_router(router)`. |
| M5 | `/wishlist/*` (20) | `routes_wishlist.py` | Med | Largest clean cluster. |
| M6 | `/listings/*` (24) + photo/version | `routes_listings.py` | High | Biggest + most interlinked; do late, once pattern proven. |
| M7 | `/users/*` (17), `/local-market/*` (10), `/trust-score/*` (5) | respective routers | Med | |
| M8 | AI ops (AI1–AI5, email triage, orient) | `routes_ai.py` | High | Touch money + ceiling — extract carefully, keep spend logging intact. |
| M9 | payment, geo, intros, tuppence, subscription | routers | Med | |

After each router extraction, `bea_main.py` shrinks; final `bea_main.py` = app init + migrations + `include_router(...)` calls + startup. Target: no file over ~1,500 lines.

## Concurrency unlock
Once M4+ land, two build agents can work on *different* router files in separate git worktrees with no collision — this is the prerequisite for the concurrent-agent model in the Way-of-Working plan.

## Coordination with the build runner
While modularization is in progress, the build runner MUST NOT do its own structural edits to `bea_main.py`. A guard note is added to its prompt: "MODULARIZATION IN PROGRESS — do not restructure bea_main.py; only surgical in-place fixes to existing functions. Module extraction is owned by the watched modularization track."

## Status
- [ ] M1 core_spend.py — **next action** (watched session, clear of build-runner window)
- [ ] M2–M9 — sequenced after M1 proves the gate.
