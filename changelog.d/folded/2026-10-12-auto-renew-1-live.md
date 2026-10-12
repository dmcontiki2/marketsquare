## 2026-10-12 — AUTO-RENEW-1 (RUL-224) is LIVE, flag-dark: released, probed, and the live check LOCKED

- **Released** as af39a00 at 07:11 SAST through the one deploy lane (relay -> origin main + deploy -> server timer). Deploy log: stranger test PASS, QA Bot gate pass, `DEPLOY OK · now live at af39a00f · health ok`, post-deploy hook ok, no rollback. The switch `launch_switches.auto_renew` is **0** on the live database.
- **PROBED live after the release landed (12 Oct 2026, ~07:15 SAST):**
  - `/flags` -> `auto_renew: false`, `auto_renew_tiers: []`, `effective.auto_renew: false`.
  - The served ms.js carries `function _arOn()` and the tick box (ms.js?v=1028).
  - `POST /payment/seller-subscription/cancel`, `/resume` and `/admin/auto-renew/plans` each answer **401** to a stranger (also 401 at the front door for cancel).
  - Live database, read-only: `users.auto_renew`, `paystack_subscription_code`, `paystack_email_token`, `renewal_failed_at` exist; `auto_renew = 1` on all 206 users (the default; it means nothing until a subscription exists); `paystack_plans` 0 rows; 0 users with a subscription.
  - 0 error lines in the service journal since the restart.
- **EXECUTED on the server's own Python against the deployed source:** `scripts/prove_auto_renew.py` -> ALL AUTO-RENEW-1 CHECKS PASS (88). On David's PC this proof is NOT EVALUATED from either vantage (the Linux sandbox lacks starlette, the host Python lacks boto3) -- the same instrument limit as RG-0840 / RG-0871, not a verdict.
- **Ledger:** RG-0966 printed READY TO LOCK and is now **LOCKED** (re-run after the change: HOLDING). Board on the working tree before the commit: sandbox chunked run 767 entries, 1 regression (RG-0908, caused and fixed in this session -- see the WATCH-COVER-1 fragment), then 0; host run on David's Python: no regressions, some entries NOT EVALUATED for host instrument limits (boto3, Windows realpath fixtures, the Linux-only minifier).
- **Rulings check:** RUL-224 reflected. 2 FAIL that pre-date this build and are not touched by it: RUL-169 (confirm.html wording) and RUL-211 (a ms.js marker; RG-0915 holds on the behaviour).
- **Still not proven:** Paystack itself. No Paystack test key is in reach (the server holds the live key only), so no real plan or subscription has been created. The first real checkout after David arms the switch is the one step still to be seen.
