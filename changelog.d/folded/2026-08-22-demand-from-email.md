## 2026-08-22 — a config line systemd had been discarding, and the guard that hid it

Found in passing while repairing the inbound secrets: `systemd-analyze verify` reported
`demand.conf:5: Invalid environment assignment, ignoring: <hello@mail.trustsquare.co>`.

**The fault.** The line was written unquoted:

    Environment=DEMAND_FROM_EMAIL=TrustSquare <hello@mail.trustsquare.co>

systemd splits `Environment=` on whitespace, so it set `DEMAND_FROM_EMAIL` to the single
word **"TrustSquare"** and threw the address away as a malformed second assignment. PROBED
before the fix: the running process carried `DEMAND_FROM_EMAIL='TrustSquare'`. The configured
sender for outbound demand mail had never once been in effect.

**Why nothing broke.** `_safe_from()` (RESEND-FROM-1, added 7 Aug after a real sender
incident) rejects any value that is not a well-formed address on the verified sending domain
and substitutes `_RESEND_SAFE_FROM` — which is defined as *exactly*
`"TrustSquare <hello@mail.trustsquare.co>"`, the string the broken line was trying to set.
So the guard silently produced the intended result and the defect was invisible. Defence in
depth working as designed, and also the reason it survived undetected.

**Fixed:** the assignment is quoted as a whole, the orphaned `<hello@…>` fragment removed.
PROBED after: `DEMAND_FROM_EMAIL='TrustSquare <hello@mail.trustsquare.co>'`, service active,
/health 200, and `systemd-analyze verify` reports **no invalid environment assignment in any
drop-in** — the check was widened to the whole unit, not just this line.

**The lesson, and it is the day's theme again:** a fault that a fallback absorbs is still a
fault. It waits for the day someone changes the fallback or sets a different sender. The same
shape as the Gmail SMTP fallback that had never authenticated, and the BIT mitigator flipping
flags nothing reads.

**Added to the monthly sweep:** `systemd-analyze verify marketsquare.service` must report no
invalid assignments. It costs one command and would have caught this the month it appeared.
