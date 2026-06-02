# ROADMAP 3 — FEA Streamline & Modularization Plan
**Drafted Session 100 · 2 June 2026 · PLANNING ONLY — no code changed in this pass**

This is the front-end sibling of `MODULARIZATION_PLAN.md` (the BEA M-series). It targets **size and modularity**, not bugs — a prior ESLint sweep found `ms.js` structurally clean (0 errors). The goal: turn one 12k-line monolith into a small set of concern-scoped files loaded in order, **incrementally and atomically**, never a big-bang rewrite.

## The artefact today (measured, this session)
| File | Lines | Bytes | Role | Served from |
|---|---|---|---|---|
| `ms.js` | **11,996** | 703,274 | All FEA behaviour | `/static/ms.js?v=131` |
| `marketsquare.html` | 3,974 | 369,455 | Shell + `#ms-data` globals + admin gate | `index.html` |
| `ms.css` | 1,187 | 115,801 | All FEA styling | `/static/ms.css?v=115` |

`ms.js` carries **308 top-level `function` declarations** and **115 module-scope `const/let/var`** bindings. It is the single biggest FEA quality/truncation risk and the blocker to safe concurrent front-end agent work (two agents cannot edit one 12k-line file without collision).

---

## How ms.js is structured today (the constraints that shape everything below)

**1. Bare top-level globals — NO outer IIFE wrapper.** Every `function name(){…}` declared at column 0 becomes `window.name`, which is exactly how the HTML reaches it: `onclick="goTo(...)"`, `oninput="..."`, etc. The HTML handler surface is large — e.g. `toggleOpt` appears in **158** inline `onclick`s, `goTo` in **49**, `sbGoStep` in **25**. **Any module split must keep these names global** (window-scoped). This is the central load-order/coupling rule.

**2. Self-running inline IIFEs do order-sensitive init.** Four `(function(){…})()` blocks run on parse:
   - L6625 — injects an `sb-*` onboarding `<style>` block into the head
   - L7652 — `_preloadWonders()` fetch on DOMContentLoaded
   - L8645 — AA section close
   - L10261 / L10264 — `window.addEventListener('load', …)` boots the wishlist (`wlBootToken → wlLoadFeed → wlStartPolling`)
   Plus the main boot: `_msInit()` behind a `document.readyState` guard (L788–795) which calls `renderFeatured/renderGrid/renderDash/renderRecruit/renderHomeStats/renderCatCounts/loadHomeWonders/catHomeInit` and `_resolveActiveCity().then(loadLiveListings)`.

**3. CSS-in-JS leakage.** **11** dynamic `<style>` injections live inside `ms.js` (e.g. the `sb-gate-btn` block at L6625). These are styling that escaped `ms.css` — a consolidation candidate (§2).

**4. Only 12 explicit `window.X =` assignments.** Almost all globalness is implicit (bare `function`). The 12 explicit ones (`window.goTo`, `window.openDetail`, `window.filterBrowse`, `window.setFilter`, `window.poiTabClick`, and dev/transient state like `window._sbMarketNoteTimer`) are defensive re-exports — worth auditing but not load-bearing for the split.

---

## 1 · Function / concern inventory & proposed module boundaries

`ms.js` already uses **prefix-based pseudo-namespacing** — the functions cluster cleanly by prefix, which makes the module boundaries almost self-evident. Top-level function counts by prefix:

| Prefix | Count | Concern |
|---|---|---|
| `sb*` | 36 | "Smart Build" seller onboarding wizard (photo→fields→signals→preview) |
| `go*` | 23 | "Guided Onboarding" 3-step photo-first flow |
| `aa*` | 23 | Advert Agent (AI listing assistant + flow sheet) |
| `ms*` | 17 | Core init / tabs / trust / stats / wishlist render / history |
| `sob*` | 10 | Seller onboarding (magic-link / tier / EULA gate) |
| `pa*` | 7 | Publish-after wizard steps |
| `el*` | 6 | Edit-listing screen + doc hub |
| `wp*` | 5 | Wonders/POI link-picker |
| `wl*` | 5 | Local-market wishlist feed/polling |
| `hiw*` | 4 | "How Introductions Work" explainer |
| `wf*` | 3 | Wonders feed taps/scroll |
| `tx*` | 2 | Transaction-history filters |
| `lm*` | 2 | Local-market modal |
| (un-prefixed) | ~165 | geo, grid/cards, wallet, filters, map, detail, modals, formatters |

### Proposed file boundaries (loaded in this order)

The split groups by concern and by load dependency. Earlier files define helpers and state that later files use; the shell loads them sequentially so all names land on `window` before `_msInit` runs.

| # | Proposed file | Concern | Seed functions / state | Est. lines |
|---|---|---|---|---|
| **F0** | `ms-core.js` | Config, env, formatters, tiny utils, **shared mutable state** | `BEA_URL`, `BEA_ENABLED`, `API_KEY`, `DEMO_MODE`, `r2Fallback`, `normCat`, `formatZAR`, `formatDesc*`, `formatIntroTime`, `isOffline`, `isSuperuser`, `esc`, `showToast`, offline banners | ~600 |
| **F1** | `ms-geo.js` | Location hierarchy + map | `activeCountry/Region/City/Suburb`, `_haversineKm`, `_distLabel`, `_detectLocation`, `handleCityBadgeClick`, `selectDemo*`, `setViewMode`, `renderMap`, `_resolveActiveCity` | ~700 |
| **F2** | `ms-wallet.js` | Tuppence / subscription / top-up | `tuppence`, `trustTier`, `tbadge`, `updateTuppenceUI`, `topUp`, `addTx`, `_renderSubscriptionScreen`, `openPlans`, `setPlan`, `_SUB_TIERS`, `_TIER_ORDER` | ~550 |
| **F3** | `ms-listings.js` | Grid, cards, featured, detail, filters, saved | `LISTINGS`-consuming code: `renderGrid`, `cardHtml`, `renderFeatured`, `openDetail`, `findListing`, `catCfg`, `filterBrowse`, `setFilter`, `applyFilters`, `filterState`, `toggleWish`, `renderSaved`, advent grid (`adv*`, `renderAdvGrid`) | ~2,000 |
| **F4** | `ms-seller-profile.js` | Anonymous seller CV / credentials | `openSellerCV`, `openBEASellerProfile`, `cvAvatarHtml`, `maskContactInfo`, `credPhotoHtml`, edit-CV (`openCVEdit`, `renderCVEditForm`, `saveCVEdit`, tags) | ~700 |
| **F5** | `ms-onboard-sb.js` | Smart-Build wizard | all `sb*` + `hk*` + `_sb*` + `SB_FIELDS`/`SB_PHOTO_SLOTS`/`SB_SIGNALS` | ~1,900 |
| **F6** | `ms-onboard-go.js` | Guided-onboarding flow | all `go*` + `GO_CAT_*` + `goState` | ~1,200 |
| **F7** | `ms-onboard-misc.js` | Magic-link / tier / publish-after / dash | `sob*`, `pa*`, `obSelect*`, `submitOnboard`, `renderDash`, `dashState`, `renderRecruit` | ~1,400 |
| **F8** | `ms-edit-listing.js` | Edit-after-publish + doc hub | all `el*` + `EL_DOC_*` | ~900 |
| **F9** | `ms-ai-advert.js` | Advert Agent | all `aa*` + `AA_CATEGORIES`/`aaDB`/`AA_FLOWS` | ~1,500 |
| **F10** | `ms-wonders.js` | Wonders / POI / link-picker | `wp*`, `wf*`, `wonders*`, lightbox (`openLightbox*`, `_lb*`) | ~900 |
| **F11** | `ms-local-market.js` | Local-market wishlist + modal | `wl*`, `lm*`, `_wl*`, `_lm*`, `WL_*` keys | ~900 |
| **F12** | `ms-me.js` | "Me" tab: trust hub, tx history, intros, HIW | `msTab`, `msRenderTrust`, `msRenderIntroList`, `tx*`, `hiw*`, `_tx*`, history (`msTrackView`, `msTimeAgo`) | ~1,100 |
| **F13** | `ms-boot.js` | **Loads LAST.** `_msInit`, readyState guard, the `window.load` wishlist boot, the 30s refresh interval | (no new logic — just the orchestration moved out) | ~200 |

**Rationale for the boundaries:** the four onboarding/AI clusters (`sb`, `go`, `aa`, plus edit-listing) are ~5,500 lines combined and are the bulk of the weight — they are also the most self-contained (their own state objects, their own field configs). Splitting those four out alone would drop `ms-core` + the always-loaded path well under 4,000 lines, which is the single highest-value move. The boot orchestration must be the **last** file so every name it references already exists on `window`.

---

## 2 · Candidate dead-weight / consolidation (conservative — FLAG, do not assume)

These are *flagged for a human/architect decision*, not pre-approved deletions. None should be removed inside a modularization step — consolidation is a separate, later track.

1. **`PROP_PHOTOS` — 0 references in ms.js.** Defined in the HTML `#ms-data` block, never read by `ms.js`. **Flag:** likely dead, but confirm it isn't read by the second inline script or admin before removing.
2. **`PROSPECTS` — 1 reference.** Near-dead. Verify the single use is live before touching.
3. **11 CSS-in-JS `<style>` injections in ms.js** (e.g. `sb-gate-btn` at L6625). **Flag:** these belong in `ms.css`. Moving them is a clean win but is a *CSS* change with its own visual-regression risk — schedule as a separate "CSS-in-JS reclaim" step **after** the JS split, one block at a time.
4. **`DEMO_MODE` / `DEMO_DISPLAY_MODE` / `setDemoDisplay` / dev toggles** — already tagged `// TODO: REMOVE BEFORE LAUNCH` in source. These are demo scaffolding, not dead, but are a known pre-launch reduction. Out of scope for *this* roadmap (launch checklist owns it) — listed so the modularizer doesn't accidentally bake them into a "permanent" module.
5. **`formatDescLegacy` vs `formatDescJSON` vs `formatDesc`** (L445/490/505) — three description formatters. **Flag:** check whether `formatDescLegacy` still has live callers; if `formatDesc` fully supersedes it, it's a consolidation candidate. Do **not** assume — grep callers first.
6. **12 explicit `window.X =` re-exports** — once a clean module layout exists, decide whether these stay (belt-and-braces) or are redundant. Low priority; harmless if kept.

**Net:** there is little hard dead code (the ESLint-clean finding holds). The real "weight" is structural, not garbage — so the win comes from *splitting*, not *deleting*. Keep deletions minimal and separately gated.

---

## 3 · Global-coupling / load-order risk — and how to preserve it

This is the load-bearing risk. Three coupling layers:

### (a) HTML `#ms-data` → ms.js data globals
The inline `<script id="ms-data">` (HTML L41–140) defines globals that `ms.js` depends on. Confirmed reference counts in `ms.js`:

| Global | Defined in | ms.js refs | Kind |
|---|---|---|---|
| `SELLERS` | `#ms-data` | **45** | `let` (reassigned by boot) |
| `LISTINGS` | `#ms-data` | **44** | `let` (reassigned by boot) |
| `SELLER_PHOTOS` | `#ms-data` | 14 | `const` |
| `CATS` | `#ms-data` | 13 | `const` |
| `acceptedIntros` | `#ms-data` | 6 | `const` |
| `PROSPECTS` | `#ms-data` | 1 | `const` |
| `PROP_PHOTOS` | `#ms-data` | 0 | `const` |

**Critical subtlety:** `_msInit` *reassigns* `LISTINGS` and `SELLERS` when demo data is fetched (`LISTINGS = dlData.listings`). Because they are `let` on the shared global scope, this mutation is visible everywhere. **Any module that holds a private reference would break this.** → Rule: keep `LISTINGS`/`SELLERS` as mutable globals on `window` (or a single shared `window.MS_DATA` namespace); never `import`-copy them into a module closure.

### (b) ms.js bare functions → HTML inline handlers
The HTML has hundreds of `onclick="fnName(...)"` attributes resolving against `window`. Top callers: `toggleOpt` ×158, `goTo` ×49, `sbGoStep` ×25, `toggleOptMulti` ×12, `selectAdvCountry` ×10. **Rule:** every split-out function must remain a global `function` (or be explicitly re-assigned to `window`). **Do NOT introduce ES modules (`type="module"`)** — module scope is not global, so every inline handler would 404. If a true module system is ever wanted, every inline handler must first be migrated to `addEventListener` — that is a large, separate project, explicitly *out of scope* here.

### (c) Order-sensitive boot
`_msInit` and the `window.load` wishlist boot assume all render/fetch helpers already exist. **Rule:** the boot file (`ms-boot.js`, F13) loads **last**; all other files load before it in dependency order (F0 core first).

### How to preserve all three
- Split files are **plain classic scripts** (`<script src=...>`), not modules — globals stay global automatically.
- Load order in the HTML is explicit and fixed: `ms-core.js` → … → `ms-boot.js` (F0…F13), each with its own `?v=` cache-bust.
- The `#ms-data` block and its 7 globals **stay exactly where they are** in the HTML, loaded before any `ms-*.js`. The split changes *where ms.js code lives*, not *how the data globals are provided*.
- Optional hardening (later, not required for the split): wrap the 7 data globals in one `window.MS_DATA = {…}` object to make the contract explicit — but only if every reference is updated in the same atomic step. For the first pass, **leave the globals untouched**.

---

## 4 · Safe-edit method (mirrors the CLAUDE.md HTML/JS write rule)

Per CLAUDE.md and the "large-file-edits truncate" memory: **never use the Edit or Write tool on `ms.js` or `marketsquare.html`.** They are large and will be silently truncated. All edits go through a Python string-replace driver, gated by `node --check`.

**Per-extraction procedure (atomic):**
1. **Back up first.** Copy the current `ms.js` to `ms.js.feaN.bak` (local) before any change. Server `static/ms.js` is also a recoverable source of truth (mirror the BEA rule).
2. **Carve, don't retype.** A Python driver reads `ms.js`, slices the exact line range for the target cluster into the new `ms-<concern>.js`, then `str.replace()`s that block out of `ms.js` with a one-line load-order comment. Assert each `old_string` matches **exactly once** before writing (raise/abort otherwise). Never hand-retype function bodies.
3. **Syntax-gate both files:** `node --check ms.js` AND `node --check ms-<concern>.js`. Both must pass. (The BEA uses `ast.parse`; the JS equivalent is `node --check`.)
4. **Tail-integrity check.** After every write, verify the file did not truncate. `ms.js` currently ends with the comment line `// ── END Category Home Mode ─…` plus a trailing `\n` — note it is a `.js`, so the check is **not** `endswith('</html>')`. Use a known-final-marker assertion:
   ```python
   c = open('ms.js', encoding='utf-8').read()
   assert c.rstrip().endswith('END Category Home Mode'), 'ms.js TRUNCATED: ' + repr(c[-60:])
   ```
   (After F13 retires the old tail, re-anchor on whatever the new final marker is.) For `marketsquare.html`, keep the existing rule: assert it still ends with `</html>`.
5. **Wire the new file into the HTML** via the Python driver too (insert `<script src="/static/ms-<concern>.js?v=1"></script>` in the correct order **before** `ms-boot.js`). Never Edit-tool the HTML.
6. **Local smoke + manual render check**, then deploy, then **verify in a real browser** before reporting done (per "verify-before-reporting" memory): load the demo URL, confirm grid renders across all 4 cities, open a listing, open the wallet, run one onboarding step. Check the console for `ReferenceError: <fn> is not defined` — that is the canonical symptom of a load-order break.
7. **If any gate fails: revert from `ms.js.feaN.bak`, document, stop.** Never leave `ms.js` half-split.

**Deploy note (from CLAUDE.md):** `ms.js`/`ms.css` are served from `/static/` — `scp ms.js root@…:/var/www/marketsquare/static/ms.js` (NOT root). Bump `?v=` and purge Cloudflare after deploy. Ask David to run git from PowerShell — never commit from the sandbox.

---

## 5 · Incremental sequence (the F-series — smallest/safest first)

Mirrors the BEA M-series philosophy: **one extraction at a time, atomic, fully gated, independently shippable, each smoke-tested before the next begins.** Earn confidence on the safest cluster first.

The order is chosen so that (a) the first step proves the "carve a cluster into a new classic-script file + wire load order + boot still works" pattern on the **most self-contained** cluster, and (b) the highest-traffic, most-interlinked code (`ms-listings`, core) moves **last**, once the pattern is proven.

| Step | Extract | To file | Risk | Why this order |
|---|---|---|---|---|
| **F1** | Advert Agent (all `aa*` + `AA_*`/`aaDB`) | `ms-ai-advert.js` | **Low** | Largest *self-contained* cluster (23 fns, own state, own consts). Few cross-refs into core render path. Best proof-of-pattern seed. |
| **F2** | Edit-listing (all `el*` + `EL_DOC_*`) | `ms-edit-listing.js` | Low | Self-contained screen, clear boundary, own state. |
| **F3** | "How Introductions Work" + Wonders/POI + lightbox (`hiw*`, `wp*`, `wf*`, lightbox) | `ms-wonders.js` | Low–Med | Mostly leaf UI; `_preloadWonders` IIFE moves with it (keep its DOMContentLoaded guard). |
| **F4** | Local-market wishlist + modal (`wl*`, `lm*`, `WL_*`) | `ms-local-market.js` | Med | Moves the `window.load` wishlist boot — must stay registered; verify polling still starts. |
| **F5** | Smart-Build wizard (`sb*`, `hk*`, `SB_*`) | `ms-onboard-sb.js` | Med | 1,900 lines, biggest single win. Moves the `sb-gate-btn` `<style>` IIFE (keep it). |
| **F6** | Guided-onboarding (`go*`, `GO_CAT_*`) | `ms-onboard-go.js` | Med | Sibling of F5; same pattern. |
| **F7** | Magic-link / tier / publish-after / dash (`sob*`, `pa*`, `obSelect*`, `renderDash`, `renderRecruit`) | `ms-onboard-misc.js` | Med | The remaining onboarding tail. |
| **F8** | Seller CV / credentials (`openSellerCV`, `cvAvatarHtml`, `maskContactInfo`, CV edit) | `ms-seller-profile.js` | Med | Anonymity-sensitive — verify masking unchanged (A2 rule). |
| **F9** | Wallet / Tuppence / subscription (`tuppence`, `topUp`, `addTx`, `_SUB_TIERS`) | `ms-wallet.js` | Med–High | Money-touching UI; verify balance display + top-up + ledger render. Coordinate with no-refunds rule. |
| **F10** | Geo + map (`active*`, `_detectLocation`, `renderMap`, `_resolveActiveCity`) | `ms-geo.js` | High | Boot depends on `_resolveActiveCity`; map uses Leaflet (already a CDN dep). |
| **F11** | Listings/grid/cards/detail/filters (`renderGrid`, `cardHtml`, `openDetail`, `filterState`, adv grid) | `ms-listings.js` | **High** | Biggest + most interlinked + most inline handlers (`toggleOpt` ×158). Do late, once pattern is bullet-proof. |
| **F12** | Core config/formatters/utils + shared state | `ms-core.js` | High | What's *left* after F1–F11 — the always-loaded base. Loads **first**. |
| **F13** | `_msInit`, readyState guard, `window.load` boot, 30s interval | `ms-boot.js` | Med | Pure orchestration move. Loads **last**. Final step — the file `ms.js` is now just (or near-empty and retired). |

**Per-step gate (every F-step):** back up → Python carve (assert unique match) → `node --check` both files → tail-integrity check → wire `<script>` in correct order via Python → local smoke + browser render check across 4 cities → deploy to `/static/` + bump `?v=` + Cloudflare purge → re-verify live → if any gate fails, revert and stop.

**Concurrency unlock (same as BEA):** once F1–F3 land, two front-end agents can work on *different* `ms-*.js` files in separate git worktrees with no collision — the prerequisite for concurrent FEA agent work. While this F-series is in progress, the build runner must **not** do its own structural edits to `ms.js` — only surgical in-place fixes to existing functions; module extraction is owned by this watched track (mirror the guard note already in `MODULARIZATION_PLAN.md`).

**Definition of done per step:** code works in a live browser (verified, not assumed) AND a one-paragraph CHANGELOG entry appended. Target end-state: no FEA file over ~2,000 lines; `ms-core` + always-loaded path well under 4,000; the four onboarding/AI clusters fully isolated.

## Status
- [ ] F1 `ms-ai-advert.js` — **next action** (lowest-risk seed; proves the classic-script carve + load-order + boot pattern)
- [ ] F2–F13 — sequenced after F1 proves the gate, smallest/safest first, each independently shippable.

---
*Planning deliverable only. No edits were made to `ms.js`, `marketsquare.html`, or `ms.css`; no deploy; no git. All structural facts above were measured against the live files this session.*
