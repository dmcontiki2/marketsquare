## 19 Aug 2026 — Account binding ON: charges bind to proven identity (RG-0119)

David flipped ACCOUNT-BIND-1 to enforcing at ~19:50 SAST. The flip was *informed, not hopeful*,
exactly as the 5 Aug design intended: 7 days of shadow log showed **0 mismatches** and 1
no-session — and the 1 was this morning's relay E2E test itself.

Verified live from outside within minutes, all four quadrants: key-only intro **accept → 401**
(closing the hole the relay test walked through this morning); no-session intro create → 401;
signed-in buyer acting as self → 200 (positive path: fresh 6-digit sign-in, throwaway listing
#374, deleted after); signed-in buyer acting as someone else → 403.

Google one-tap is what made this flip cheap: the sign-in a refused caller is bounced to is now
one tap, not an email round trip. With the relay on (this morning) and binding on (now), both
Trust & Privacy rails are live. RG-0119 LOCKED — its probe uses a sessionless request only, so a
ledger run can never create a real intro.
