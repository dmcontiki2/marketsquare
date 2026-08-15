## 2026-08-15 — Money-path status corrected + webhook arm tool built
David confirmed REAL purchases settled to FNB -> sk_live is live (S111 sk_test note is STALE).
Verified in Paystack dashboard: Live Webhook URL already https://trustsquare.co/payment/webhook.
Only unknown: PAYSTACK_WEBHOOK_SECRET on server (no probe exists; endpoint 400s identically
either way). Built add_paystack_webhook_key.bat (resend-key pattern: presence check first, then
ssh paste + restart; Claude never sees the key). A10 narrowed accordingly. E2E proof pending:
smallest-pack buy with tab closed before return must still credit. 2FA on Paystack still Disabled.
