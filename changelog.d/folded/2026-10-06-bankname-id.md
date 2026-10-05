# 6 Oct 2026 -- BANKNAME-ID-1: the bank name check no longer dead-ends on "Verify your ID first"
- David tried "Confirm the name on your bank account" and was told to verify his ID with nothing to press. His ID was
  confirmed (27 May) by upload, a route that never recorded the name on the document; the only route that does (Home
  Affairs, AUD-008) is dark. Every seller confirmed by upload was locked out of the check.
- David's ruling (6 Oct 2026): the verified ID name is read off the confirmed ID document already on file, never typed
  by the seller. Read once, the first time a name check needs it; stored in users.id_name; never returned.
- New GET /users/{email}/verify-bank-name/ready: the sheet asks first, so nobody types an account number into a check
  that cannot run. No confirmed ID -> plain explanation + "Go to the Trust tab". Unreadable document -> Help & Support,
  and /admin/identity/confirm now takes an optional id_name to record it by hand.
- KYC vision calls now take the image type from the bytes (/private-docs/ URLs carry no extension).
- Cost model impact: one metered vision read per seller, once, only when that seller uses a name check.
