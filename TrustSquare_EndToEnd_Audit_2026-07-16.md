# TrustSquare — End-to-End Launch-Readiness Audit
**Date:** 16 Jul 2026 · **State at audit:** BEA v1.3.1 · Session 139 · trustsquare.co · 65 live listings
**Scope:** Front-end app (HMI + code), backend (BEA + modules), live Hetzner server, and the ops dashboard (audited **and** brought back into line).
**Method:** static analysis of `marketsquare.html` / `ms.js` / `ms.css` / `bea_main.py` + modules, plus read-only SSH verification against the live server. Every headline security/contract claim was checked against the running system, not just the source.

---

## Verdict at a glance
The app is in good structural shape for launch. **Repo and server are byte-identical** across all eight core files (no deploy drift). The historical "undefined handler" bug class is fully eradicated. The blockers are concentrated and fixable: a handful of real security gaps (an API key shipped in the browser, an unauthenticated ID-upload that self-grants trust), some dev scaffolding that must be stripped before go-live, and missing HTTP security headers. The dashboard's staleness was real but confined to one hardcoded view — now corrected.

**Launch blockers (must fix): 4.** Everything else is hardening, cleanup, or polish.

---

## LIVE SERVER — verified state (read-only SSH)
- **No drift.** Local repo == deployed server for `main.py`, `auth.py`, `database.py`, `storage.py`, `payments.py`, `ms.js`, `ms.css`, `index.html` (md5 match on all 8).
- **Services all running:** marketsquare (BEA :8000), advertagent (:8002), citylauncher (:8001), nginx, plus isolated snaptax. `/health` → ok v1.3.1.
- **SSL** valid to **24 Sep 2026** (~70 days). **Disk** 41% root / 44% volume. **RAM** 7.7GB, healthy. Uptime 49 days.
- **`/ai/*` is proxied to the AdvertAgent service (:8002)** via nginx — `/ai/functions` returns **200 live**. See H1 correction below.

---

## CRITICAL (launch blockers)

### C1 — Admin API key hardcoded in browser-served JavaScript
`ms.js:32`, `marketsquare_admin.html:1795`, `APP_PREVIEW.html:5311`:
`const API_KEY = 'ms_mk_2026_pretoria_admin';`
This is the exact value `auth.require_api_key` validates via `X-Api-Key`. It ships in browser-readable JS at trustsquare.co, so every endpoint behind `require_api_key` is effectively open to anyone who views source. **The X-Api-Key gate currently provides no real protection.**
**Fix:** treat X-Api-Key as a publishable/public key only; move privileged writes behind the JWT/admin-PIN flow (already separate); rotate the shared static key.

### C2 — `POST /users/{email}/upload-id` has zero auth and self-grants trust
`bea_main.py:3747` → `async def upload_user_id(email: str, file: UploadFile = File(...))` — **no auth dependency, no ownership check.** Anyone can upload an "ID document" for any email; the handler auto-sets `id_verified_at` and bumps `trust_score +15`. This is a direct attack on the trust primitive the whole marketplace rests on.
**Fix:** bind to the authenticated caller's own email; do not auto-verify on upload.

### C3 — Dev DEMO/LIVE toggle ships visible to every user
`marketsquare.html:448` `<div id="dev-mode-toggle" style="display:flex;...">` (buttons → `devSetMode()`), hard-coded visible and **never hidden by JS** (unlike the `?demo=1`-gated `demo-toggle-panel`). Tagged "TODO: REMOVE BEFORE LAUNCH". A dev control exposed to every buyer/seller.
**Fix:** remove the block (part of C4's demo-scaffolding sweep).

### C4 — Missing HTTP security headers on the live site (verified)
Live `curl -I https://trustsquare.co/` returns **none** of: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Strict-Transport-Security. (Matches the dashboard's own risk r2, still open.) Clickjacking / MIME-sniff / no HSTS at launch.
**Fix:** add the header block to the nginx `marketsquare` server (one-time; low risk).

---

## HIGH

### H1 — AI console routes: NOT broken (false alarm, corrected by live check)
Static analysis flagged `/ai/functions`, `/ai/run`, `/ai/jobs/{id}` as missing from `bea_main.py`. **They are not in BEA by design** — they live in the AdvertAgent service on :8002, nginx-proxied at `/ai/`. Live: `/ai/functions` → **200**; `/ai/run` and `/ai/jobs/test` return 404 only because the probes used an empty body / unknown job id (expected). The live `advert_agent.py` defines all three routes and was restarted after its last edit. **No action needed** beyond confirming the AdvertAgent launch gate is intentional.

### H2 — `GET /users/{email}` returns the full user row, no auth
`bea_main.py:3520` → `SELECT * FROM users WHERE email=? → dict(row)` for any email. Leaks whatever the users table holds (subscription, trust, IDs, contact).
**Fix:** add auth + a field allow-list.

### H3 — `_require_admin` does not verify the JWT `sub` (ADMIN-SUBCHECK-1, already filed)
Any `_JWT_SECRET`-signed token is accepted as admin regardless of subject. Combined with C1, admin-surface hardening should be treated as a launch item, not a post-launch defer.

### H4 — Three screens defined but unreachable
- `screen-saved` → `renderSaved()` (`ms.js:3252`) has no caller and no `goTo('saved')` — fully orphaned (superseded by `screen-wishlist`).
- `screen-recruit` → `renderRecruit()` runs every refresh (`ms.js:879`) but **no `goTo('recruit')` exists** — wasted render work, screen unreachable.
- `screen-aa-coach` → reachable only via `aaGoTo()` (`ms.js:10231`), which is never called.
**Fix:** delete or wire up; at minimum stop calling `renderRecruit()` on every refresh.

---

## MEDIUM

- **M1 — Demo/dev scaffolding (12 "REMOVE BEFORE LAUNCH" TODOs)** threaded through `ms.js` (`DEMO_MODE`, `DEMO_DISPLAY_MODE`, `devSetMode`, demo country/city injection) and `marketsquare.html`. Confirm the intended launch default of `DEMO_MODE`/`DEMO_DISPLAY_MODE` and strip the dev toggles (ties to C3).
- **M2 — Payment endpoints rely only on the public C1 key:** `POST /payment/initialize` (`:4007`), `POST /payment/seller-subscription/initialize` (`:4192`) accept arbitrary email/amount. `/payment/verify` is lower risk (verifies against Paystack, idempotent). `/payment/webhook` **does** verify a signature (good).
- **M3 — Account mutation by email, no ownership check:** `POST /users/{email}/photo` (`:3692`), `POST /users/{email}/seller-tier/downgrade-free` (`:9559`).
- **M4 — Ops-endpoint PII via obscurity:** `/dashboard/email-triage` (`:14306`) returns from-addr/subject/draft-reply with no auth; `/dashboard/scan`, `/dashboard/bit` same posture. Put behind the nginx Basic-Auth realm already used for `/orchestrator/*`. (`/dashboard/summary` + `/dashboard/cost` expose only aggregates — sanctioned.)
- **M5 — Stale local `main.py` (590KB, 17 routes behind `bea_main.py`).** It's an older snapshot of the same service, not a separate microservice — a deploy/edit-the-wrong-file trap. Delete or gitignore.
- **M6 — Dead code, self-described:** `ms.js:8004` "Legacy stubs" block (`goPhase`, `handleImg`, `clearImg`, `selCatBig`, `goPhaseB2OrC`, `selAdvSubcat`, `doPublish`, `submitClaim`, `skipClaim` — all verified single-reference; keep `showPhase`). Plus ~9 more dead functions (M-list in FEA audit) and **65 unused CSS classes** (clusters from removed adventure/local-market card variants). Low-risk cleanup, do after the toggle removal.
- **M7 — `alert()` at a payment step** (`ms.js:11705`, subscription flow) — inconsistent with the app's `showToast` pattern.
- **M8 — `?v=` cache-buster is the only version source of truth** for ms.js (v293) / ms.css (v213). ms.css mtime (Jun 30) trails ms.js (Jul 16); confirm v213 matches current CSS content so a stale-CSS cache miss can't happen at launch.

---

## LOW / INFO
- No hardcoded secrets in the `.py` files — all load from env and fail-closed if unset (good). The only exposed key is the front-end one (C1).
- Bare `except: pass` at `bea_main.py:14860/14903` only swallow rollback/cleanup then re-raise 500 — benign.
- No DEBUG flags, 0 TODO/FIXME in backend, ~10 `print()` (not hot paths). Front-end: 0 `console.log`, 20 `console.warn` + 4 `console.error` (legit error paths), 1 `alert` (M7).
- Accessibility: 27/51 JS-generated `<img>` lack `alt`; only ~22/331 `<button>` have accessible names (icon/emoji-only buttons unlabelled). 1 empty `<button>`. WCAG cleanup for post-launch.
- Route inventory: **161 BEA routes**, no duplicate (path,method); 1 retired 410 stub (`/advert-agent/buy-pack`) — safe to remove.

---

## DASHBOARD — audited AND brought into line
**Finding:** the default Dashboard and Ops views are fully live (driven by `/dashboard/summary`, `/dashboard/cost`, `/dashboard/bit`, `/dashboard/scan`, `/health/resources`). **All staleness lived in one place** — the hardcoded D3 "Graph/Galaxy" view, frozen ~94 sessions back (Session 45, fabricated "BEA v1.3.4", CityLauncher "paused", AdvertAgent "pre-kickoff", Codex v4.5, haiku model, 23/60 sellers, 0 live listings, Paystack "test/CIPC").

**Action taken (local file `dashboard.html`, backed up first, guarded str.replace, validated):** 24 stale literals corrected to Session-139 truth —
- BEA v1.3.4 → **v1.3.1** (everywhere)
- CityLauncher paused → **Engine LIVE (S130), 1,416 prospect pool**
- AdvertAgent pre-kickoff → **LIVE dev-gated (S132), integrated in-app (S133)**
- Session 45 → **Session 139** (now reads `DATA.currentSession` live)
- Codex v4.5 → **v4.8**; haiku → **Sonnet (claude-sonnet-4-8)**
- 0 live listings → **65**; retired "AI Coach/pack" framing → current per-use AI + Tuppence ledger
- Two stale risk/priority tiles repurposed to surface the **embedded-API-key risk** and the **sell-flow-redo** priority
- Paystack "test mode/CIPC" risk → **payments-posture monitor** (Stripe-global shelved 16 Jul)

Validation: all stale markers now grep to **0**; backticks balanced; 5/5 `<script>` tags intact; backup at `dashboard.html.bak-<ts>-auditsync`.

**Not yet done (your call — these are deploys/edits to canon-controlled files):**
1. **Deploy the refreshed dashboard** (`refresh_dashboard.bat` pushes docs; the HTML itself deploys via the normal path). I did **not** deploy — that's a live change for you to trigger.
2. **Server-side stale direction cards** in `bea_main.py:9688–9704` (`dir_cl` "Wave 1 Pretoria" n8n) and `:9727–9746` (`dir_aa` "AI Coach — Tier Gating", `advert-agent/coach`) still frame retired workflows and render on the live main dashboard. Editing `bea_main.py` is a deploy-gated backend change — flagged, not touched.

---

## Recommended fix order
1. **C1, C2** — kill the browser-embedded API key + auth-bind `upload-id`. Non-negotiable before launch.
2. **C4** — add nginx security headers (one-time, low risk).
3. **C3 / M1** — strip dev toggles + demo scaffolding; confirm launch defaults.
4. **H2, H3, M2–M4** — close the by-email PII/mutation reads, enforce admin `sub`, gate ops endpoints.
5. **Deploy refreshed dashboard + fix the 2 server-side direction cards.**
6. **H4, M5–M8, a11y** — dead-code/CSS cleanup, remove stale `main.py`, `alert→toast`, alt/aria labels. Post-blocker.

*Nothing in this audit was deployed. The only file changed is the local `dashboard.html` (backed up).*
