# Patent / Whitepaper / Legal — Alignment Analysis & Launch Sequence
**Date:** 29 Jun 2026 · **Purpose:** get the filing pack in line with the app's *current* status and the planned launch (self-filing the SA provisional; not a counsel hand-off). · **Author:** Claude (working session)

## Verdict
The pack is **fileable as a provisional now.** The three documents already describe only what is **live in production** and correctly scope out what is staged. The convergence loop (23 Jun) drove all machine-fixable defects to Δ=0; what remained were **7 counsel items**, and — importantly — **those are complete-specification / prosecution concerns, not blockers to getting the provisional on file.** A SA provisional only has to *fairly describe* the invention (claims are optional at this stage); the annexed whitepaper does that richly. Two small alignment defects existed and are now **fixed** (below).

## 1. Are the documents in line with the app + planned launch?
| Document (canonical) | In line? | Finding |
|---|---|---|
| **Provisional Spec — FILING** (`patent-loop/…_FILING.docx`) | Yes, after 1 fix | Summary/description claim only live mechanisms (unified model, hold-settled Tuppence ledger, anonymous intro, signal-points trust score, 402 slot-gate, existence-gated/ceiling AI). Staged items (≥36-mo dormancy, founders qualifier) correctly excluded as "not in force at priority date." **Defect:** Detailed-Description annex pointed at whitepaper **v3.8** while the published whitepaper is **v3.11**. → fixed. |
| **Whitepaper — PUBLICATION** (`patent-loop/…_PUBLICATION.docx`) | Yes, after 2 fixes | Accurately mirrors the live platform (BEA v1.3.x, AI triage live, photo-first $0-first, world-heritage layer, 10 AI fns). **Defect A (important):** §9 said "file with CIPC on **Day 0 (launch day)**" — contradicts its own footer ("not for distribution until after filing") and the novelty rule. → fixed to *file first*. **Defect B:** §8 payments said "Paddle/**Stripe**"; current posture (STATUS) is Paddle/**Lemon Squeezy** for intl (Stripe-direct blocked) + Paystack for SA. → fixed. |
| **IP Brief v6 (DRAFT)** (`Patents/…_IP_Brief_v6_DRAFT.docx`) | Aligned; **no Claude edit** | Counsel-gated; **v5 remains controlling** until landed. Already reflects live status (C10–C13 recite the live hold ledger: `ai_hold/ai_burn/ai_hold_released/ai_release`, idempotent settle, BEGIN IMMEDIATE). The only open item is a **David decision (AD-14)**, not a text fix — see §3. Claim-text is a counsel/David call; not machine-edited by design. |

## 2. Edits applied (reversible; backed up; re-opened & verified clean)
| # | File | Change |
|---|---|---|
| A1 | Provisional Spec FILING | annex pointer `whitepaper v3.8` → `v3.11` (matches the doc actually annexed/published) |
| B1 | Whitepaper PUBLICATION | §9 "file on Day 0 (launch day)" → **"file FIRST — before publication or launch; publishing before filing forfeits novelty"** |
| B2 | Whitepaper PUBLICATION | §8 "Merchant of Record (Paddle/**Stripe**)…" → "(Paddle / **Lemon Squeezy**)…" + SA via Paystack (current posture) |

Backups: `*.docx.bak-align-<ts>` beside each file (restore = `cp backup file`).

## 3. Your calls before filing (genuinely David's — not Claude's to guess)
1. **AD-14** — the IP Brief flags an ambiguous CHANGE_REGISTER note "(reverse-auction = lead)" next to C10–C13. Decide whether a reverse-auction/lead-marketplace distinction was intended as the C10 framing. *Not a provisional blocker* — C10–C13 are drafts; the provisional is valid without final claim wording.
2. **CIPC fee** — doc cites **R590**; a third-party source suggested the provisional official fee may be lower (≈R60) with R590 for *complete* applications. Not authoritatively resolved here. **Confirm the live fee on iponline.cipc.co.za at filing** (the portal shows the exact amount before you pay).
3. **Inventor→company licence** — patent is filed in your personal name (portable IP); the operating licence to Trustsquare (Pty) Ltd is "to be executed separately." Execute that assignment/licence at your convenience (not a filing blocker).

## 4. The 7 counsel items — deferred to the COMPLETE spec (≤12 months), not provisional blockers
From the convergence audit trail (23 Jun). These are legal calls for the complete-spec / PCT stage and for launch ops; none stops the provisional going on file:
1. CPA s63/s63(3) — reconcile "non-refundable / no restitution" vs the consumer's property right in the **un-burned** float; move EULA dormancy to ≥36 months (also an EULA v1.7 launch item).
2. Applicant identity — natural-person patent vs corporate whitepaper authorship; document the assignment/licence chain (= §3.3 above).
3. C3 / Pingsby — still CONDITIONAL; clear, narrow, or drop.
4. Banks Act / SARB closed-loop exemption — confirm Tuppence's non-financial-product classification (do **not** add crypto/MiCA scaffolding).
5. POPIA s71 — confirm the trust score never becomes a solely-automated consequential decision without a human/explanation path.
6. Professional novelty search — independently confirm all cited refs; **US 8,095,377** is the closest and must be distinguished in the complete spec.
7. §101 / COMVIK framing — at complete-spec/PCT, frame claims as a specific technical improvement (hold state machine, existence gate, ceiling pre-flight).

## 5. The one hard rule (the novelty gate)
**The provisional must be ON FILE before the whitepaper is published.** The whitepaper is a deliberate prior-art / defensive publication; releasing it before the filing date would destroy the novelty the provisional exists to protect. Your stated order (patent → whitepaper → …) is exactly right; edit B1 hard-wires it into the document.

## 6. Planned sequence of events
**P0 — File the provisional (next 2 days).** Assemble pack (Form P1 + P6 + provisional spec with whitepaper annexed as the Detailed Description) → confirm fee on iponline → file at iponline.cipc.co.za → record the application/patent-pending number + filing date. *(Optional, parallel: file TRUSTSQUARE trade mark, Nice classes 35/36/42, + TUPPENCE word mark.)*
**P1 — Publish the whitepaper.** Only after the application number is issued. Re-stamp from "CONFIDENTIAL — not for distribution" to a public defensive-publication version carrying the application number + date; then publish.
**P2 — Paystack: register + integrate + go-live.** Integration scaffolding already exists in-app (test mode: ms.js return handler, top-up, plan wiring). Going live needs: merchant registration/verification for Trustsquare (Pty) Ltd → `sk_live` keys + `PAYSTACK_WEBHOOK_SECRET` → finish plan wiring → flip the S5 production gate (fail-closed) → deploy via `deploy_bea_safe.bat`. **Merchant approval is the likely long-pole — start it first.**
**P3 — Test in app.** Real small top-up via Paystack live → webhook confirmation → hold→burn on a delivered introduction and a successful AI run → hold→release on decline/failure → S5 gate verified fail-closed → ledger integrity check.
**P4 — Plan launch cadence.** CityLauncher waves (Pretoria pilot → Wave 1: New York / London / Sydney), Founders cohort issuance + `LAUNCH_SPECIAL_DEADLINE`, comms/video pack. **EULA v1.7 + dormancy ≥36-mo** (counsel) runs in parallel — it's a launch blocker but not a patent/whitepaper blocker.
**P5 — Launch.** Flip launch flags; first wave live.

**Critical path:** P0 → P1 is a hard gate (novelty). P2 (Paystack merchant approval) is the variable-latency long-pole and can start the moment the provisional is filed. P4 planning runs in parallel with P2/P3. P3 gates P5.
