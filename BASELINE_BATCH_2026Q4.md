# BASELINE BATCH 2026-Q4 — the plan of record for ONE baseline change

**Ruled by [[RUL-126]] (14 Sep 2026).** Every open post-launch design item ships as ONE baseline
change, built flag-dark in the real app, seen by David before the field, armed by David.
A partial revert is the drip this plan exists to prevent.

**Not governed by this plan:** live faults. A false banner or a dead lane is repaired the day it
is found. RUL-126 governs DESIGN, not repair.

---

## 0 — REPAIR LANE (outside the batch, fix now)

| # | Item | Why it cannot wait |
|---|------|--------------------|
| R1 | False "You're offline — browsing cached content" banner | It is the first thing a seller reads when listings look empty, and it is untrue (`navigator.onLine` true, same-origin fetches 200). It sends people to their router instead of their account. |
| R2 | No service worker controlling the live page (`navigator.serviceWorker.controller` null) | Web push ([[RUL-122]]) and the add-to-home-screen offer ([[RUL-123]]) are both built and neither can fire. The Quick app at `/quick/` shares this worker. |

**BOTH REPAIRED 14 Sep 2026** — `OFFLINE-TRUTH-1` and `SW-REGISTER-1` in `ms.js`, proven in a
rendered headless browser, ledger entries **RG-0363** and **RG-0364** green. Not yet deployed:
another session's work is in the tree today and a deploy would carry it.

R2 was also a dependency: item 6 below could not have been proven without it.

---

## 1 — BUILD ORDER

Ordered by dependency, not by size. Each item is built flag-dark; nothing is armed until §3.

| # | Item | Ledger / ruling | Depends on | Note |
|---|------|-----------------|------------|------|
| 1 | **ZOOM — the narrowing funnel** | RG-0221 · [[RUL-076]] | R2 not required | Replaces the filter panel on every category door. Facets carry a dependency graph; zero-count options removed; geography never opens the funnel. Spec: `ZOOM_HMI_SPEC.md`. |
| 2 | **DCB-001 — batch upload, then order** | [[RUL-127]] | — | Sell-flow photo step in `ms.js` + a BEA order-suggestion call. No schema change. Independent of Zoom; built in parallel. |
| 3 | **Credential claims (FIDE-CLAIM-1)** | RG-0216 | — | `/credentials/mine` 404s today. Claim endpoint, `CREDENTIAL_CLAIMS` flag, seeded registry from CityLauncher `fide_trainers` (4 237 rows). Spec: `CREDENTIAL_CLAIMS_DESIGN.md`. |
| 4 | **Private-seller VEL entries** | [[RUL-129]] | 3 | Same lane as 3. Property and Local Market gain evidence a private seller can hold; every entry must be a dated, sourced fact, outside-checkable, added once. |
| 5 | **SQUIRE — the Pro subscriber's agent** | RG-0224 · [[RUL-077]] | 1 | Builds AFTER Zoom by ruling: a brief is a Zoom path plus prose, so Squire first writes the matching engine twice. Spec: `SQUIRE_SPEC.md`. |
| 6 | **Quick Listing app at `/quick/`** | [[RUL-124]] / [[RUL-125]] | R2, 1 | Same origin, sub-path, own manifest, own tile. Harness is built and the hand-over is proven live; what is missing is the ship and the baseline-readiness ledger entries. |
| 7 | **One $5 tier — fold Global into Starter** | [[RUL-128]] · [[RUL-080]] | — | Live Paystack table. Existing Global subscribers migrate at the same price, never cancelled and re-sold. The pricing page is rewritten in the same change, never before it. |
| 8 | **AI funds gauge on the +1 card** | RG-0203 | — | `dashboard.server.html` carries no `data-ai-funds` strip, so "can this AI function stop?" is unanswerable. Cheap, independent. |
| 9 | **Agency letters** | RG-0346 | — | The three letters the sending lane draws still tell the solo-seller story and never mint the agency console link. Copy and flow, not mechanics. |

---

## 2 — WHAT EACH ITEM MUST PROVE BEFORE IT COUNTS AS BUILT

Verified in the RENDERED app at phone width, not at the API or DB layer.

- **Zoom** — 3–4 taps to each of the five canonical targets; no zero-count option ever offered; no facet asked before its parent; geography never first; travel geography starts at country.
- **DCB-001** — a photo set uploads in any order, one tap sets the cover, AI order arranges the rest, drag adjusts, publish holds the cover. Time-to-publish measured before and after; David Jnr retests.
- **Credential claims** — `/credentials/mine` answers; a badge comes from a live JOIN; one account per credential; no surface calls a person safe (RG-0238).
- **Private-seller entries** — the Property and Local Market draft screens carry the block, every entry dated and sourced, points read from the catalogue and not from a screen.
- **Squire** — Pro-only, never GRANTS an introduction, seller identity never enters its context, top-up is Tuppence and no second currency exists.
- **Quick app** — the five-tap journey completes on a real phone, the hand-over lands as a real listing with the expected score, the vouching gate holds, the personal link brings a hirer in free, the buzz arrives, the coloured tile installs.
- **$5 fold** — every existing Global subscriber still has what they paid for, at the same price, with no Paystack cancellation; the pricing page shows one ladder.
- **Funds gauge** — each AI function's lane shows funds and auto-top-up state on the rendered dashboard.
- **Agency letters** — a rendered letter tells the agency story and carries a working console link.

---

## 3 — THE ARMING SEQUENCE (David's, not the CTO's)

1. The whole batch is built flag-dark; the existing app is untouched for every user.
2. David sees it on the **actual app, locally first** — [[RUL-076]]'s binding constraint.
3. Then in the gated sandbox that [[RUL-075]] already schedules for **30 Oct**. Zoom shares it; no second preview mechanism is built.
4. David arms the flag. It changes the front door of every category, so it is his act.
5. One baseline moves. Nothing in it is hotfixed out alone.

---

## 4 — STILL RESERVED TO DAVID (does not block the build)

- **Travel funnel endpoint** — the funnel's conclusion for tours, stays and guides is a PLAN (the Expedition Dossier handed to a partnered agency, which IS the introduction). Commercial shape. Needed before the travel lane is armed, not before Zoom is built.
- **Designer-role binding (OPEN_LOOPS D14)** — you, a design agent, or both. You are the gate by default until you say.
- **Agency Pro seat (RUL-048)** — the third $5 price point. [[RUL-128]] folded two products, not three; the seat stays its own price until you say otherwise.

---

## 5 — CLOSED ON 14 SEP 2026 BY THIS SESSION

- Listings **383** and **384** — the two hand-over proof drafts — DELETED from production and re-probed: both `GET /listings/{id}` return **404**.
- DCB-001's GATE line — filled after eleven weeks empty ([[RUL-127]]).
- RUL-080's reserved mechanism — chosen ([[RUL-128]]).
- The Property / Local Market credential gap — ruled ([[RUL-129]]).
