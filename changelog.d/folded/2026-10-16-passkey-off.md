## 2026-10-16 -- PASSKEY-OFF-1: Face ID / fingerprint sign-in removed

- **PASSKEY-OFF-1** (ms.js, bea_main.py, route_policy.json, scripts/regression_ledger.py) -- David, 16 Oct 2026: on Android the
  browser passkey sent him through Google Password Manager set-up screens and ended nowhere; "Then we stick with what we have."
  Removed: the "Sign in with Face ID or fingerprint" button, the "Next time, sign in with Face ID" offer, and the five
  `/auth/passkey/*` routes with their policy rows. Kept: the `passkeys` table (unread, no data destroyed). Unchanged: email
  sign-in once per phone, then the 180-day sliding session (SESSION-SLIDE-1) and SESSION-ADOPT-1 keep her in until she signs
  out, which ends every device (SESSION-END-1). RG-0799 / RG-0807 / RG-0931 now check that Face ID stays removed.
