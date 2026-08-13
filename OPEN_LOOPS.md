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


## 🔴 BLOCKING NOW
*(nothing proceeds until these clear)*

— none —

## 🟠 LIVE LOOPS (open, need to move) — ranked

| # | Loop | Owner | Single next action | Opened | Source |
|---|------|-------|--------------------|--------|--------|
| L5 | **Fix-agent phase-aware + operational path proven** — pre-launch now: only legal+costly gate, design gets IMPLEMENTED not backlogged (David 9 Aug scoping); runs as root (repo owner), shadow-clean on the real queue. Agent still OFF. | [D]+[C] | Deploy -> re-run the shadow dry-run as root with MAINT_PHASE=prelaunch -> read the design changes it proposes on real faults. Then close: state-dir out of repo + confirm the server can pass its own anonymity gate. | 2026-08-09 | this session |
| L6 | **BIT-AIM-1: FEA probes mis-aimed** — BIT board live (13's timer works) but degraded 5/8: B-FEA-SHELL/EXAMPLE/CONTRACT all fail because BIT_BASE=localhost:8000 carries no FEA. Per-probe base needed (nginx+gate-token on box, or edge+named-UA). | [C] | Tomorrow's maintenance loop (or attended): registry per-probe base + runner resolve + verify on the 15-min board. | 2026-08-11 | changelog.d 2026-08-11-b4-6 |
| L2 | **git-on-FUSE stale .lock files** every commit — worked around via `_to_delete/`, needs a real fix. | [C] | Diagnose root cause + permanent fix in an attended session (not urgent). | 2026-07-23 | STATUS.md S150 |
| L3 | **SCOREBOARD-1 shipped-not-live** — agent + guards + nightly wiring in repo (7/7 tests); probes OFF until enabled. | [D] | Next deploy carries it, then run `enable_scoreboard.bat` once. | 2026-08-03 | CHANGELOG SCOREBOARD-1 |
| L7 | **Tooling-through-the-gate** — GATE-ENFORCE-2 (13 Aug) raises the origin token gate; on-box/edge tooling reading data endpoints anonymously (maintenance-loop intake, server smoke data probes) will 401. UA-EDGE-1's sibling. Ledger already fixed (reads via reviewer cookie). | [C] | Next attended loop: point on-box tools at 127.0.0.1:8000 (or cookie them) + re-aim smoke; verify loop intake green. | 2026-08-13 | changelog.d 2026-08-13-gate-enforce-activated |

## ⚪ DECISIONS AWAITING DAVID / COUNSEL — ranked

| # | Decision | Owner | Single next action | Opened | Source |
|---|----------|-------|--------------------|--------|--------|
| D4 | **privacy.html UK/US/AU supplements** — verified 2 Aug: NEW work, never drafted (EULA got §13.6 Country Schedules on 23 Jul; privacy.html has zero UK/US/AU content). | [C] | David confirms scope → Claude drafts. | 2026-07-23 | STATUS.md S149 |

| D7 | **Wave-1 send: how do email recipients get past the pre-launch Unlock gate?** Deep links + all 9 showcase adverts are DONE; a cold click lands on the editor-PIN gate (by design, REMOVE-BEFORE-LAUNCH). Either wave-1 waits for launch, or Claude builds a read-only `?listing=` preview that bypasses the gate for a single advert (data already publicly readable pre-launch). Test send follows this call. | [D] | Rule: wait-for-launch / build preview bypass. | 2026-08-02 | this session |
| D9 | **FLIP-DRILL-1: pick the hour** — runbook ready (`FIRE_DRILL_RUNBOOK.html`). DEFERRED by David 5 Aug 2026 ("needed, just not now") — STANDS OVER till after launch (David, 11 Aug). | [D] | David names a quiet hour when ready; Claude keeps the log. | 2026-08-03 | this session |
| D10 | **Travelpayouts tours programs: review DECLINED 5 Aug** — "website under development / not yet ready, re-submit after setup" blocks GYG · Viator · Welcome Pickups · Booking.com (+22 others). One "Submit for review" button on any program page re-runs it and AUTO-CONNECTS on pass. Do not resubmit unchanged. Aviasales flights Data API unaffected (re-verified 5 Aug, JNB-CPT R2,284). Payouts note: $400 minimum balance on chosen method. | [D] | Scheduled: 1 Sep 09:00 check-in — Claude resubmits with David's go (launch polish = the changed face). Earlier on David's word. | 2026-08-05 | scheduled follow-up |
| D11 | **Maroushka's TS-0022 letter drafted** — the retest letter IS the remediation (9 pre-fix covers need her re-upload; class fix RG-0047 live). | [D] | Say "send" (chat) or POST retest-send. | 2026-08-11 | Records/FAULT_RECONCILE_2026-08-11.md |
| D12 | **Arm the Maintenance Agent** — deploy DONE (David's 09:08 TSL, release 127b6a6): BIT timer posting, first Tier-2 verdict honest NOT READY (patch-apply), MAINT-B4-6 rewrite fallback built+proven, migration 015 re-runs Tier 2 next deploy. | [D] | Next deploy (tonight's nightly or /TSL) → read static/maint/b4_tier2.json; if READY: one paste from MAINT_ARMING_RUNBOOK.md (after a /backup). | 2026-08-11 | changelog.d 2026-08-11-b4-6 |
| D14 | **Designer-role binding** (5 Aug boundary redraw item 2) — guidelines now written (DESIGN_CHANGE_GUIDELINES.md); until bound, you are the gate by default. | [D] | Rule: you / a design agent / both. No urgency before launch. | 2026-08-11 | MAINTENANCE_AGENT.md amendment |

## ✅ CLOSED — last 7 days

- **D8 CLOSED 11 Aug 2026** — Stays/B&B fully live: code rode the 05:06 /TSL, David ran media_push, STAY_IDS already wired (336/337/338), outreach hrefs already flipped (verified idempotent). 
- **D13 CLOSED 11 Aug 2026** — TS-0018 referent named by David = the dashboard Launch Blockers column; removed same day (VIZ-MAPS-4); fault closed.

- **L4 CLOSED 11 Aug 2026** — the tester fault channel is LIVE in fact: flag on, 30 reports filed through it, ACKs + retest letters flowing (register at 21 verified / 4 closed after today's AMBER-SWEEP-1).
*(short tail; drop rows older than 7 days)*

- **D10 CLOSED 5 Aug 2026** — David approved the fault-intake privacy wording; clause landed in privacy.html as §13 "Reporting a problem" (Changes renumbered §14). Contact = support@trustsquare.co (matches §9 rights address). Rides the next deploy; required-before-flag-opens-wide condition is now met on disk.

- **[D] AFFILIATE GATE CLOSED 2 Aug 2026 (evening)** — David's ruling, attended: gate cleared, **full Drive on**. Presented with the on-disk state (SS6.1A disclosure live in EULA v1.11; counsel ratification + accountant tax/VAT treatment outstanding; Drive auto-inject broader than the curated gate) David chose "Gate cleared — full Drive on". All Drive monetization functions enabled on trustsquare.co ("running at full capacity"). Residual items now ORDINARY follow-ups, not blockers: counsel ratifies SS6.1A wording at next revision; accountant classifies TP commission income (foreign-source, HK payer) when it first accrues; per-click-out disclosure line ships with the planner UI. data_flights/tours flags are no longer legally blocked. Ref: changelog.d TP-DRIVE-2.
- **D1 CLOSED 2 Aug 2026** — "publish the latest EULA": already true at origin (lifecycle clauses live as §§4.6–4.9 + §§14.5–14.6 since v1.10, 23 Jul; v1.11 current on terms.html + in-app gate + modal). Found & fixed in closing: the CDN edge was serving stale **v1.3 (17 May)** on /terms — purged same day, class locked as ledger **RG-0024** (edge stamp must equal origin stamp).
- **D5a CLOSED 2 Aug 2026 (night)** — all NINE email-showcase adverts live and deep-linked: property 315–317 (28 Jul), cars 318–320 (28 Jul, healed: real specs replacing cloned Hilux fields, sort prices fixed, super flag + false attestation cleared then correctly re-stamped), adventures 321–323 (born clean via migration 001). All four templates flipped (2 anchors per card). Remaining test send rides the D7 gate ruling.
- **L1 CLOSED 2 Aug 2026 (evening)** — the pending release SHIPPED via the ONE-deploy engine's first live run: v421→v422, health ok, deep-link ms.js + Saturday's work + DEPLOY-CONSOLIDATION-1 + the Stays sweep all live. MSJS-DRIFT / VERSION-KEY flags clear next audit.
- **D5b CLOSED 2 Aug 2026** — David's ruling: standardize on **"Stays"**. Swept buyer/seller-facing surfaces (filter chip + ADV-SYNC-1 state loop + seller picker + onboarding dropdown + 2 home tiles; ms.js/marketsquare.html, node --check green, live-verified on v422). EULA's formal "Adventures Accommodation" untouched by design — renames at the next counsel revision.
- **D6 CLOSED 2 Aug 2026** — David's call: proceed as-is; post-filing disclosure of reverse-intro + Rank accepted as a small risk alongside the new referrals. **Wave 1 is NOT blocked on counsel.** The drafted attorney email stays in Gmail drafts should he still want the answer.
- **D2 / D3 REMOVED 2 Aug 2026** (David: "re-open when the time is right") → parked in BACKLOG.md → Deferred items; counsel register (LEGAL_VERSIONS.md A6) still tracks the fork consolidation as the authority.
