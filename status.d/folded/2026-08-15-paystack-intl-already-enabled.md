## 2026-08-15 — Paystack international payments: ALREADY ENABLED (verified)
Checked live dashboard (account 1777715, Live/Approved): 'Accept international payments' ticked.
Phase 0 of GLOBAL_PAYMENT_RAILS sequence complete without action. Open David-only items spotted:
set up 2FA on Paystack (banner active); decide on enabling Apple Pay checkbox (helps intl buyers).
UPDATE same day: David ENABLED Apple Pay in the dashboard (terms accepted, confirmation modal seen).
No further setup needed — payments.py uses transaction/initialize (redirect/hosted checkout), which
gets Apple Pay automatically; domain registration/.well-known only applies to inline integrations.
Unverified until tried: a real checkout from an iPhone/Safari on the live site. Apple Pay has
per-currency minimum transaction amounts — low-value Tuppence packs may not show the button.
