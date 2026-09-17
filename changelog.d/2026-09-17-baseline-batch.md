## 2026-09-17 — baseline batch: all nine items built flag-dark, proven in the rendered app (RUL-126)

The whole `BASELINE_BATCH_2026Q4.md` build order is in the tree as ONE change behind
`launch_switches.baseline_q4` (default 0). `/flags` now carries `baseline_q4` and
`effective.baseline_q4`; `POST /admin/flags {baseline_q4:true}` arms it — that is David's act,
not this session's. With the flag dark the existing app is byte-for-byte the same experience.
Preview is honoured only on a local origin (`?baseline=1` / `ts_baseline_preview`); the live
origin never honours the parameter.

Built (each proven at 412×915 in the rendered real app on the smoke rig — `scripts/smoke_harness/rig/`
+ `verify_*.mjs`; visual proofs in `BASELINE_BATCH_PROOFS_2026-09-17.html`):
1. **Zoom** (RG-0221, RUL-076) — `zoom_engine.py` (pure engine, `test_zoom_engine.py` green) +
   `GET /zoom/next` + watches; FEA sheet replaces the filter panel on the six browse doors. Proved:
   3–4 taps to each canonical target, no zero-count option, no facet before its parent, geography
   never first, travel geography starts at country. Local Market has no filter panel today and
   is therefore NOT a Zoom door — stated, not hidden.
2. **DCB-001** (RUL-127, RG-0383) — batch upload, one-tap cover, `POST /listings/photos/order`
   (vision under the ceiling, rules fallback), drag reorder, publish holds the cover.
3. **Credential claims** (RG-0216) — registry seeded from 4,237 FIDE IDs (`migrations/041`),
   `POST /credentials/claim`, `GET /credentials/mine` (404 while dark), Tier A/B, one account per
   credential, badges via a live JOIN, no surface calls a person safe.
4. **Private-seller VEL entries** (RUL-129, RG-0385) — Property and Local Market catalogue rows,
   every one dated and outside-checkable; `GET /trust/catalogue` feeds the Quick draft screens.
5. **Squire** (RG-0224, RUL-077) — Pro-only (403 otherwise), brief → shortlist → approach; a
   ceiling hit never writes an intro; top-up is Tuppence, no second currency.
6. **Quick app at `/quick/`** (RUL-124/125, RG-0386–0391) — `migrations/042` adds the sub-path
   to nginx; `/quick/me` gives the page its key and identity; price basis fixed (QUICK-PRICE-BASIS-1).
7. **One $5 tier** (RUL-128, RG-0392) — `_fold_global_into_starter` runs once on arming, moves
   subscribers at the same price, never touches `wishlist_subscriptions`/Paystack (0 rows today);
   `/pricing/ladder` and the plans screen show one ladder when armed.
8. **AI funds gauge** (RG-0203) — `GET /dashboard/ai-funds` + `data-ai-funds` strip on the +1
   AI Providers card; vendor balances read NOT MEASURED until David enters a dated figure.
9. **Agency letters** (RG-0346) — CityLauncher's three letters tell the agency story and mint the
   console link via `/agencies/wave-prep` (solo link only as a logged fallback).

Live faults found on the way and fixed in the same change: CARD-ONERROR-1 (unterminated onerror
string in `cardHtml`, RG-0384), FOUNDERS-MAP-1 (`founders` dropped in the BEA→FEA map),
QUICK-PRICE-BASIS-1, QUICK-ME-1. Also riding this deploy: R1/R2 repair-lane work (RG-0363/0364).

Ledger: RG-0221/0216/0224/0203/0346 rewritten LOCKED; RG-0383–0392 new. Source halves green;
live halves red until deployed. `rulings_check.py` reflections added for RUL-124–129.
`ms.js` ?v=495, `ms.css` ?v=294. Deploy requested through `scripts/request_deploy.py` (RUL-092).

**Deploy 1 (67ea011, 17:43Z) — DEPLOY OK, health ok; migrations 040 (115 listings stamped) and
041 (4,237 registry rows) recorded. 042 jammed the chain (QUICK-PATH-2):** its proof probed
`http://127.0.0.1/quick/`, measured Certbot's port-80 301, followed it out through Cloudflare and
read a cached 404, then restored the vhost — the exact CSP-SCRIPT-SRC-7 trap 033 documents.
The vhost block was right; the instrument was wrong. Fixed to measure the origin on :443 over
loopback with trustsquare.co SNI, never following a redirect; re-shipped in the same session.
