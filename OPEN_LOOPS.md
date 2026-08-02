# OPEN LOOPS — the one place that answers "what is open, what is next"

**This file is the single source of truth for open threads on TrustSquare.**
It exists so *Claude* is the integrator, not David. Everything else (STATUS.md prose,
audit reports, chat threads) FEEDS this file; David reads only this.

## The rule (structural, not a reminder)
1. **Every session reads this file FIRST** (it is in the /start boot-up).
2. **Every session that opens or closes a loop EDITS this file LAST** — before ending.
   A loop that lives only in a chat transcript does not exist. Put it here or it's lost.
3. **Ranked top-down. David reads until he stops caring and stops.** He never sorts.
4. **One line per loop.** Detail lives in the linked file, never here. If this file grows
   past one screen, that's the signal to CLOSE loops — never to start a second list.
5. Owner tag: **[C]** = Claude can just do it (reversible → done, then reported).
   **[D]** = genuinely David's call (deploy / spend / legal / irreversible).

Durable "do it later" (not active) stays in **BACKLOG.md → Deferred items**. Not duplicated here.

---

- **[D] AFFILIATE-INCOME COMPLIANCE GATE (opened 1 Aug, TP-FLIGHTS-1):** before `data_flights`/tours ever flip live: (a) DONE 1 Aug: SS6.1A disclosure clause LIVE in EULA v1.11 — counsel to RATIFY wording; still to ship with planner UI: a "we may earn a commission at no extra cost to you" line ships next to travel click-outs; (b) accountant confirms tax/VAT treatment of Travelpayouts commission (foreign-source, HK payer, likely USD — new income class in the tax module, exported-services zero-rating to confirm). Zero exposure while flags stay dark; the flag flip is BLOCKED on both. Detail: CHANGELOG 1 Aug (TP-FLIGHTS-1) + CLAUDE.md travel section.

## 🔴 BLOCKING NOW
*(nothing proceeds until these clear)*

— none —

## 🟠 LIVE LOOPS (open, need to move) — ranked

| # | Loop | Owner | Single next action | Opened | Source |
|---|------|-------|--------------------|--------|--------|
| L1 | **Deploy staged & pending** — repo ms.js v372+deep-link, live v370; audit flags MSJS-DRIFT + VERSION-KEY. 28 Jul added `?listing=<id>` deep link (email showcase cards → exact advert; node --check green; ms.js.bak-20260728-deeplink). | [C] | Say "ship" — /TSL (or deploy_marketsquare.bat) now publishes the deploy ref; the server engine deploys with monotonic buster + auto-rollback (DEPLOY-CONSOLIDATION-1, 2 Aug). | 2026-07-24 | AUDIT_GLOBAL_QA/LATEST.md |
| L2 | **git-on-FUSE stale .lock files** every commit — worked around via `_to_delete/`, needs a real fix. | [C] | Diagnose root cause + permanent fix in an attended session (not urgent). | 2026-07-23 | STATUS.md S150 |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D4 | **privacy.html UK/US/AU supplements** — verified 2 Aug: NEW work, never drafted (EULA got §13.6 Country Schedules on 23 Jul; privacy.html has zero UK/US/AU content). | [C] | David confirms scope → Claude drafts. | 2026-07-23 | STATUS.md S149 |
| D5a | **Email-showcase adverts** — property trio DONE (315–317 live 28 Jul, agency template deep-linked). SIX remain (3 Cars + 3 Adventures), fully staged 2 Aug: migration 001 creates them at next release (ids print in deploy log) → `CityLauncher/emailer/flip_showcase_hrefs.py <card>=<id>…` flips cars_dealer/tour_guide/travel_agency → test send. | [D] | Say "ship" (release runs migration) → Claude flips hrefs + test send. | 2026-07-28 | CityLauncher za-agency-readiness |
| D5b | **Stays vs Accommodation** — the real decision found 2 Aug: buyers browse "Stays", sellers list under "Accommodation", the live EULA formally names "Adventures Accommodation". Rename is mechanically trivial but touches published EULA vocabulary. Recommend: "Stays" everywhere buyer-facing now; EULA formal name follows at next counsel revision. | [D] | One-word ruling ("Stays" / "Accommodation" / discuss with Jnr) → Claude sweeps. | 2026-07-22 | STATUS.md:38 |
| D6 | **Counsel: post-filing disclosure of reverse-intro + Rank** — explained 2 Aug: both mechanisms are NEW post-filing inventions (payer+moment inverted vs claims C10–C13; published 50/50 rank formula), publicly visible since 18 Jul. Ready-to-send draft asks counsel (a) still protectable? (b) risk to filing 2026/06760? (c) pause marketing? Settle BEFORE Wave 1. | [D] | Send the draft (in your Gmail drafts) to the attorney. | (earlier) | Patents/DRAFT_Counsel_Email_NewMatter_2026-07-21 |

## ✅ CLOSED — last 7 days
*(short tail; drop rows older than 7 days)*

- **D1 CLOSED 2 Aug 2026** — "publish the latest EULA": already true at origin (lifecycle clauses live as §§4.6–4.9 + §§14.5–14.6 since v1.10, 23 Jul; v1.11 current on terms.html + in-app gate + modal). Found & fixed in closing: the CDN edge was serving stale **v1.3 (17 May)** on /terms — purged same day, class locked as ledger **RG-0024** (edge stamp must equal origin stamp).
- **D2 / D3 REMOVED 2 Aug 2026** (David: "re-open when the time is right") → parked in BACKLOG.md → Deferred items; counsel register (LEGAL_VERSIONS.md A6) still tracks the fork consolidation as the authority.
