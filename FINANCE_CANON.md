# FINANCE CANON — TrustSquare (Pty) Ltd / MarketSquare
**Created 11 Jul 2026 (David's two concerns: payment rails + "all of the finances I don't even know of")**
**Canon-of-record for payment RAIL decisions stays BACKLOG F4 + GATE1-PAY-ZA/INTL. This file maps the finance FUNCTION.**
**Disclaimer: orientation, not legal/tax advice. §4 questions go to the accountant before acting.**

## §1 Payment rails — decided state (re-verified 11 Jul 2026)
**ZA (launch):** Paystack. CIPC done (2026/340128/07), FNB business account open, KYC resubmitted
2 Jul — WAITING ON PAYSTACK. On approval: GATE1-PAY-ZA checklist (live keys env-only, webhook
signature verify + idempotent credit re-test, one real-card E2E, settlement seen in FNB).
**International (US/UK/AU):** Merchant of Record, per David's F4 ruling 5 Jun 2026 — NO foreign
entity, NO US company, no travel. Re-verified 11 Jul:
- Stripe still does NOT onboard SA-registered businesses (SA is served via Paystack, a separate
  platform). The "complex Stripe route" = foreign entity — correctly parked as Phase-2.
- MoR fees current: Paddle 5% + $0.50, no monthly fee, mature tax coverage (US state sales tax,
  EU/UK VAT, AU GST, B2B reverse charge). Lemon Squeezy same base +1.5% intl +1% non-US payout,
  post-Stripe-acquisition reliability complaints (May 2026 mass-cancel incident, payout freezes).
  **Lean: Paddle.**
- Phase-2 (only if MoR fee delta > admin): remote UK Ltd -> full Stripe (~3%), but UK VAT from
  FIRST digital B2C sale, UK filings, agent fees. Break-even roughly: 2% fee saving must exceed
  ~£1.5-2.5k/yr admin -> intl card volume > ~$100-150k/yr before it pays.
- **OUTSTANDING PRE-CHECK (F4 FIRST ACTION, still open):** confirm with Paddle that Tuppence
  qualifies — position it as a prepaid fee for a defined introduction/AI service (HOLD
  charge-on-delivery, never cash-out, no wallet withdrawal). Ask sales directly before building.

## §2 The books — four sources of truth + one rule
1. **BEA Tuppence ledger** (LIVE) — every credit/HOLD/settle/release. Already models unearned
   revenue correctly: Tuppence sold = liability; earned only on settle/burn.
2. **Paystack settlement reports** (pending activation) — gross, fees, net per batch.
3. **FNB business statements** (LIVE — PDFs already in paystack/).
4. **MoR payout reports** (future — Paddle pays net of its 5%, tax already remitted).
**The reconciliation rule (the whole "bank statements verified" concern in one line):** every FNB
line traces to a PSP settlement batch; every batch traces to ledger entries; every ledger credit
traces to a payment. BEA <-> PSP <-> bank, monthly, no orphans in any direction.

## §3 Obligations calendar — TrustSquare (Pty) Ltd
**SA — live now:**
- CIPC annual return + beneficial-ownership filing: annually from incorporation anniversary (2027).
- SARS Corporate Income Tax: ITR14 annually; IRP6 provisional tax x2 (month 6 + month 12 of the
  financial year) — estimates required even at small revenue.
- **VAT: NOT registered; not required yet.** Compulsory threshold rose R1m -> R2.3m taxable
  supplies /12mo (effective 1 Apr 2026); voluntary from R120k. ⚠ Zero-rated exports still COUNT
  toward the threshold. **On-plan Year 1 (~$235k ≈ R4.3m) crosses R2.3m mid-Year-1 -> VAT
  registration becomes compulsory during Year 1 if the ramp holds.** Plan for it, don't be
  surprised by it. (2026 budget also shifts digital-platform VAT to platform operators — an
  accountant question, §4.)
- PAYE/UIF/SDL: only when salaries start (incl. David's own, if taken as salary).
**Global — the MoR is the answer:** with Paddle as seller-of-record, foreign VAT/GST/US sales tax
is Paddle's problem (that is what the 5% buys). Without MoR (Phase-2 Stripe): UK VAT from first
sale, AU GST at A$75k, US state-nexus tracking — per GATE1-PAY-INTL.

## §4 Accountant — engage at FIRST REVENUE, not Year 2 (recommendation)
The model budgets R2,000/mo from Year 2; a Year-1 structuring consult is cheap vs one wrong VAT
call. Hand them exactly these six questions:
1. VAT: when does compulsory registration trigger on our ramp, do zero-rated exports to a
   non-resident MoR (Paddle) count as taxable supplies, and does the 2026 platform-operator
   change touch us?
2. Is revenue via MoR a zero-rated export of services (Paddle = non-resident B2B customer)?
   What documentation (90-day rule) must we keep?
3. Tuppence: confirm deferred-revenue treatment (liability on sale, income on settle) — BEA
   ledger already records it this way; books should mirror the ledger.
4. Small Business Corporation (SBC) rate eligibility for TrustSquare?
5. Director remuneration: salary vs dividends, PAYE timing.
6. Provisional tax estimates for a ramping Year 1 (avoid underestimation penalties).

## §5 Monthly close — 30 minutes, day 1-3 of each month
1. Export FNB statement CSV + Paystack settlement report + BEA month summary (spend/revenue
   endpoints exist; extend per FIN-2).
2. Run the §2 reconciliation (manual eyeball until FIN-1 exists).
3. File to finance/YYYY-MM/ (statements, settlements, ledger export, one-page summary).
4. Flag any orphan line immediately — an unexplained bank line is a P1, not a note.
Uses installed finance skills (reconciliation, financial-statements, close-management) when run
with Claude. Cross-check candidate for the second-vendor roving auditor
(AI_VENDOR_STRATEGY_DECISION_2026-07-11.md).

## §6 Build backlog (filed here, not started — post-Paystack-activation)
- **FIN-1** recon script: Paystack settlement export <-> BEA credit ledger <-> FNB CSV; outputs
  matched/orphans. Zero-token, deterministic.
- **FIN-2** BEA "CFO pack" endpoint: month revenue by SKU, Tuppence liability outstanding,
  AI COGS vs ceilings, settlement totals -> one JSON/PDF.
- **FIN-3** Tuppence unearned-revenue report (liability at month-end; feeds accountant Q3).
- **FIN-4** MoR payout ingestion (when Paddle live).

## Verified vs unverified (11 Jul 2026)
- VERIFIED (web, sources in session): Stripe-SA unavailability; Paddle/LS fees + LS incidents;
  VAT R2.3m/R120k thresholds eff. 1 Apr 2026; CIPC AR + IRP6 basics.
- UNVERIFIED (needs direct contact): Paddle acceptance of Tuppence model; SBC eligibility;
  exact zero-rating treatment with MoR counterparty; platform-operator VAT impact.
