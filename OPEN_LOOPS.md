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
| L2 | **git-on-FUSE stale .lock files** every commit — worked around via `_to_delete/`, needs a real fix. | [C] | Diagnose root cause + permanent fix in an attended session (not urgent). | 2026-07-23 | STATUS.md S150 |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D4 | **privacy.html UK/US/AU supplements** — verified 2 Aug: NEW work, never drafted (EULA got §13.6 Country Schedules on 23 Jul; privacy.html has zero UK/US/AU content). | [C] | David confirms scope → Claude drafts. | 2026-07-23 | STATUS.md S149 |
| D7 | **Wave-1 send: how do email recipients get past the pre-launch Unlock gate?** Deep links + all 9 showcase adverts are DONE; a cold click lands on the editor-PIN gate (by design, REMOVE-BEFORE-LAUNCH). Either wave-1 waits for launch, or Claude builds a read-only `?listing=` preview that bypasses the gate for a single advert (data already publicly readable pre-launch). Test send follows this call. | [D] | Rule: wait-for-launch / build preview bypass. | 2026-08-02 | this session |
| D8 | **Stays/B&B showcase trio missing** (David, 2 Aug: "we totally overlooked them"). Verified: adventures_accommodation_outreach.html has ZERO showcase cards (all other tracks have 3) and no ZA B&B/guesthouse showcase adverts exist (only lodge super 271 + tour stays). Needed: 3 Stays adverts (safari lodge B&B / boutique guesthouse / bush camp — clone-271 pattern, born clean per hardened script), AI photo set (Higgsfield, David-assisted), phone-card composites, template section + deep links. | [D]+[C] | Next working session: David generates photos → Claude wires end-to-end (advert script rows → migration → cards → template → links). | 2026-08-02 | this session |

## ✅ CLOSED — last 7 days
*(short tail; drop rows older than 7 days)*

- **D1 CLOSED 2 Aug 2026** — "publish the latest EULA": already true at origin (lifecycle clauses live as §§4.6–4.9 + §§14.5–14.6 since v1.10, 23 Jul; v1.11 current on terms.html + in-app gate + modal). Found & fixed in closing: the CDN edge was serving stale **v1.3 (17 May)** on /terms — purged same day, class locked as ledger **RG-0024** (edge stamp must equal origin stamp).
- **D5a CLOSED 2 Aug 2026 (night)** — all NINE email-showcase adverts live and deep-linked: property 315–317 (28 Jul), cars 318–320 (28 Jul, healed: real specs replacing cloned Hilux fields, sort prices fixed, super flag + false attestation cleared then correctly re-stamped), adventures 321–323 (born clean via migration 001). All four templates flipped (2 anchors per card). Remaining test send rides the D7 gate ruling.
- **L1 CLOSED 2 Aug 2026 (evening)** — the pending release SHIPPED via the ONE-deploy engine's first live run: v421→v422, health ok, deep-link ms.js + Saturday's work + DEPLOY-CONSOLIDATION-1 + the Stays sweep all live. MSJS-DRIFT / VERSION-KEY flags clear next audit.
- **D5b CLOSED 2 Aug 2026** — David's ruling: standardize on **"Stays"**. Swept buyer/seller-facing surfaces (filter chip + ADV-SYNC-1 state loop + seller picker + onboarding dropdown + 2 home tiles; ms.js/marketsquare.html, node --check green, live-verified on v422). EULA's formal "Adventures Accommodation" untouched by design — renames at the next counsel revision.
- **D6 CLOSED 2 Aug 2026** — David's call: proceed as-is; post-filing disclosure of reverse-intro + Rank accepted as a small risk alongside the new referrals. **Wave 1 is NOT blocked on counsel.** The drafted attorney email stays in Gmail drafts should he still want the answer.
- **D2 / D3 REMOVED 2 Aug 2026** (David: "re-open when the time is right") → parked in BACKLOG.md → Deferred items; counsel register (LEGAL_VERSIONS.md A6) still tracks the fork consolidation as the authority.
