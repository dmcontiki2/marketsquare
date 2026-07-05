# Launch Sequence v2 — agreed guidance 2 Jul 2026
(Replaces David's draft 8-step order after checking it against BACKLOG.md F4/GATE1-PAY-INTL/LAUNCH-GATES-1/LEGAL-COUNTRY-1/PITCH-AGENCY-1 and verifying Stripe availability.)

## Key corrections to the draft plan
1. **Steps 2–3 "Stripe registration + integration" → replaced by MoR (Paddle/Lemon Squeezy).**
   Stripe still does not onboard South African entities (verified 2 Jul 2026); a TrustSquare
   (Pty) Ltd can only reach Stripe via a foreign entity — the exact path BACKLOG F4
   (5 Jun, David proceeding) already rejected in favour of Merchant of Record:
   ~5% + $0.50/txn, accepts US/UK/AU cards, handles UK VAT / AU GST / US nexus,
   pays out to SA. Note Paystack IS Stripe's African arm — Paystack = our "Stripe" for ZA.
   FIRST ACTION (per GATE1-PAY-INTL): MoR compliance pre-check that Tuppence qualifies
   (prepaid fee for a defined introduction service, never cash-out, HOLD charge-on-delivery).
2. **Cleanup (draft step 6) moves BEFORE the first agency emails (draft step 5).**
   Scalpel emails are our highest-value first impressions; the app must be at launch
   quality when the first agency clicks. Cleanup = Gate 4 (app baseline joint sign-off)
   and is internal work → do it NOW during the Paystack wait.
3. **Two omitted gates sit before ANY agency email fires:**
   - LEGAL-COUNTRY-1 — counsel pass per country BEFORE its emails (AU Spam Act consent,
     UK PECR/GDPR, US CAN-SPAM, NY brokerage rules). 4 cities at once = 4 jurisdictions at once.
   - PITCH-AGENCY-1 — agency-facing material circulates ONLY after the provisional patent
     is filed (absolute novelty). A7/AD-01 patent-pack desync must be resolved first.
4. **AGENCY-IMPORT-1 (or a manual concierge equivalent) must exist before agency replies land**,
   otherwise a responding agency has no same-week onboarding path.
5. **Per-city release, not big-bang:** a city's emails fire only when THAT city is
   payments-currency-true + legally cleared. Pretoria may lead the 3 international
   cities by weeks; that is acceptable and expected.

## Corrected sequence (3 parallel tracks, then serial)
- **Track A · Payments:** Paystack acceptance → GATE1-PAY-ZA checklist (live keys,
  webhook signature + idempotent credit re-test, ONE real-card E2E). In parallel:
  MoR pre-check → MoR registration → MoR integration for NY/LON/SYD.
- **Track B · Product (start now):** launch-quality cleanup sweep → improved Launch-wave
  setup (draft step 4) → AGENCY-IMPORT-1 → wave-2 gating signals defined (manual gate
  on the Launch Control board; 60 staged prospects/city stays the trigger; do NOT
  build gating automation yet).
- **Track C · Legal (start now, long-lead):** provisional patent filed → per-country
  counsel sessions (ZA trivial; AU/UK/US before their emails).
- **Then:** scalpel agency emails per green city (small volume also warms the Resend
  domain) → watch onboarding signals → broad auto email waves → wave 2 cities on
  adequate wave-1 signals (manual decision, David).

## Decisions that are David's
- D1: Confirm MoR replaces Stripe as the international rail (or explicitly choose
  the UK-entity+Stripe path knowing UK VAT from first sale + entity admin).
- D2: Pick the MoR vendor after the Tuppence compliance pre-check (Paddle vs Lemon Squeezy).
- D3: Accept per-city staggering (Pretoria first) vs holding all 4 for simultaneity.
- D4: Define the 3–5 wave-2 "adequate onboarding" signals (e.g. agency listings live
  per city, organic signups, first paid intros) — numbers are his call.

## Decision log
- 2 Jul 2026 · **D1 DECIDED** — David confirms the MoR route replaces Stripe for steps 2–3 (MoR guidance session planned same evening). D2 stays open, gated on the Tuppence compliance pre-check.
- 2 Jul 2026 · **Ordering confirmed** — cleanup (draft step 6) before scalpel emails (draft step 5).
- 2 Jul 2026 · **Legal posture** — David acknowledges the LEGAL-COUNTRY-1 counsel disclaimer and proceeds on best-advice basis, consequences accepted; per-country counsel remains the recommended gate.
- Styled copy: "TrustSquare Launch Sequence v2 — nice.docx" (same folder).
