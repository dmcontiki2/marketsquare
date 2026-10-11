# AUTO-RENEW — build brief (AUTO-RENEW-1, RUL-224)
**David, 11 Oct 2026 23:28 SAST:** *"I did request you change the subscriptions to be auto-renew. It should be shown as auto-renew standard with an manual change of a tick box to change it to monthly."* Recorded as RUL-224 (amends RUL-201(a)); PRICING_CANON.md §1 updated. Build scheduled Mon 12 Oct 2026 01:30 SAST, unattended (David 9 Aug 2026: overnight build/deploy desired). **Flag-dark:** `launch_switches.auto_renew` ships OFF; arming is David's act (RUL-076).

## 1 · The change in one paragraph
Starter (R90), Pro (R360) and the Agency Pro seat (R90) renew automatically every 30 days on the card used at checkout. The checkout shows one tick box, ticked by default: **"Renew automatically each month — cancel any time with one tap."** Unticked → today's one-off 30-day payment, untouched. Where the plan is shown (Plans / subscription screen / Wallet) a **Cancel renewal** button disables the Paystack subscription; the paid period runs to its end date and then lapses exactly as RUL-201 lapses it (adverts above the limit rest, nothing deleted, KEEP-CHOICE-1). A failed renewal is retried by Paystack; after its last retry the plan lapses the same way, with one Buzz + email saying so.

## 2 · Mechanism (Paystack, ZA)
- One **plan** per tier in Paystack (`POST /plan`: name, amount in kobo/cents, interval monthly), created once by a maintenance script and stored in `feature_flags.json` or a small `paystack_plans` table — never created per checkout.
- Checkout with the tick box ON: `initialize_payment(..., plan=<plan_code>)` — Paystack creates the subscription on the first successful card payment. Tick box OFF: today's call unchanged.
- Webhook `/payment/webhook` (signature already verified) gains: `subscription.create` (store `subscription_code` + `email_token` on users), `charge.success` with `data.plan` (a renewal: extend `billing_period_end` by 30 days from the previous end, keep tier, grant the monthly Tuppence as today's path does), `invoice.payment_failed` (log; Buzz "Your renewal did not go through — Paystack will retry"), `subscription.disable` / `subscription.not_renew` (mark auto_renew=0; nothing else — the lapse pass does the rest at the end date).
- **Cancel renewal:** `POST /payment/seller-subscription/cancel` → Paystack `POST /subscription/disable` with code + token; answer the app with the end date. Declared in `route_policy.json` (user-level, bound to the session email; SEC-GATE-1).
- Non-card channels (EFT etc.) give no reusable authorization: the tick box is shown disabled with "Automatic renewal needs a card payment" and the one-off flow runs.
- Idempotency: a renewal `charge.success` already recorded by reference is ignored (the existing reference guard).
- **Never** auto-charge from our side (no `charge_authorization` calls) — Paystack's subscription does the charging; we only read events and disable.

## 3 · Schema
`users.auto_renew INTEGER DEFAULT 1`, `users.paystack_subscription_code TEXT`, `users.paystack_email_token TEXT`, `users.renewal_failed_at TEXT`. Migration in init (ALTER TABLE, like `listings.reach`).

## 4 · App (ms.js — both plan surfaces + Wallet)
- Tick box on the plan checkout step, default ON; the acceptance line reads: "Renews automatically every month until you cancel. Cancelling takes one tap and your paid days still run to the end." (CPA s14 / ECTA s43 disclosure for a month-to-month plan — no new EULA version.)
- Plan card for a subscriber: "Renews on <date>" + **Cancel renewal**; after cancelling: "Runs to <date>, then Free" + **Renew again**.
- Agency Pro seat: same tick box and button.
- DEMO_MODE guard on every new call.

## 5 · Dashboard + canon
`dashboard.server.html`: renewals this month, failed renewals, cancellations, auto-renew share. `RULINGS.md` RUL-224 (recorded), `PRICING_CANON.md` §1 (recorded), `scripts/rulings_check.py` RUL-224, regression ledger entry asserting: tick box present and default ON only when the switch is on; OFF = one-off flow byte-identical; cancel route declared; webhook handles the four events.

## 6 · Definition of done (David's standard: verified in the RENDERED app)
1. With the switch OFF: the plan checkout and `/payment/seller-subscription/initialize` behave exactly as today (ledger asserts the one-off path unchanged).
2. With the switch ON, Paystack **test keys**, headless Chromium (IDENTITY-GUARD-1 — never David's Chrome): a QA account buys Starter with the tick box on → Paystack subscription exists for the test customer; the plan card shows "Renews on <date>" and Cancel renewal; cancel → Paystack subscription disabled, card shows the end date; screenshots saved.
3. Webhook replay: a synthetic `charge.success` with `plan` extends `billing_period_end` by 30 days and grants the monthly Tuppence once; a replayed reference is ignored; `invoice.payment_failed` sends one Buzz; `subscription.disable` sets auto_renew=0.
4. Tick box off → one-off purchase, no subscription created.
5. Regression ledger green, `stranger_test` passes, `check_pricing_canon.py` ALL IN LINE; deploy through the normal gate with the switch OFF.
6. Report to David (SO-3): built · verified (screenshots) · the one item he arms (`auto_renew`) · anything he may veto. Nothing parked.

## 7 · House rules that apply
Big files by Python string-replace + verify; `.bak-autorenew-<ts>` before edits; `quick.html` untouched (Quick does not sell plans); no AI model named as a label; no secrets printed (the Paystack secret stays in the systemd unit — read nothing that echoes it); wait for silence before the one commit; push + deploy via `scripts/request_deploy.py`; close every loop in `OPEN_LOOPS.md`.
