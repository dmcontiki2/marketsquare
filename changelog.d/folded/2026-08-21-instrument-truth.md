## 2026-08-21 — INSTRUMENT-TRUTH-1: the +1 page's remaining panels audited, two lies and one missed panel

Follow-on from AIPROV-VERIFY-1, answering David's question — *how many of these six are impossible
to verify by AI, how many would not have survived an AI verification?*

**Impossible to verify: zero.** All six were checkable from source against canon — no live access,
no admin token, no human eyes. They were unlooked-at, not unverifiable.

**Would not have survived: two, plus a third the audit list itself missed.**

1. **SERVER SPECS** hardcoded `CPX32 €17.99 + Volume €6.58 = €24.57/mo` against
   `canon.yml server_eur_month: 15.49` — contradicting **RUL-025**'s grandfathered price and
   overstating the box by €2.50/mo. Corrected to €15.49 / €22.07, labelled with its source and
   the €35.49 rescale warning.
2. **BIT SELF-TEST** painted its dot **green as the pre-data default** — healthy while loading,
   and still healthy if the fetch died. Now grey until `/dashboard/bit` answers.
3. **The SERVICES panel** — six hand-written "✅ Active" verdicts, never probed, which would read
   Active straight through a total outage. **It was missed by the first sweep because it has no
   `id` attribute and the sweep enumerated by id.** That miss is the same shortcut that produces
   these faults: counting what is easy to enumerate and calling it the set. Now labelled
   **STATIC REFERENCE — NOT MEASURED**, green stripped, reader pointed at the Infrastructure card
   which probes `/admin/services-status` per row.

Clean: hp-grid, directions-grid, prompt-panel, travel-lane-card — all display server data or
static copy and paint no health verdict.

**Ledger RG-0133 promoted OPEN → LOCKED**, now asserting three properties mechanically: every
panel is measured / display-only / labelled; the static cost line must equal `canon.yml`; and no
dot may default to a health colour. The cost assertion was negative-tested (it bites).
