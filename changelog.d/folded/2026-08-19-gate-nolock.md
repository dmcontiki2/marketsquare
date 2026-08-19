## 19 Aug 2026 — GATE-NOLOCK-1: the gate can no longer lock out the people it is meant to let in

**The fault (David, with screenshots).** He could not get into his own app or dashboard on his
laptop. Three independent layers each did their job and produced a total lockout of the one
person who cannot be locked out:

1. **The magic link only unlocks the device that opens it.** He requested the link on his
   laptop; the mail opened on his phone. The phone got the `ts_review` cookie. The laptop — the
   machine he actually works on — stayed locked, with no way to finish the entry.
2. **The admin password could not rescue him.** `GATE-ENFORCE-2` arms the nginx catch-all and
   `/admin/login` was never exempt, so the origin refused the request with an HTML 401 *before
   the app saw the password*.
3. **The screen then lied about it.** The `GATE-TRUTH-1` branch rendered that origin 401 as
   *"Incorrect reviewer code"* — a correct super-admin password reading back as a wrong one —
   and `dashboard.server.html` told him to go enter the reviewer code at trustsquare.co first,
   i.e. to perform the exact step that was impossible.

Urgency: Maroushka is about to hand this link to agencies. A gate that locks out the super
admin will lock out testers, and each one is a lost first impression.

**The fix — two new doors, no new privilege.**

- **Cross-device 6-digit code.** `/review/request-link` now mints a 6-digit code and puts it in
  the same email as the link. It is redeemed at the new `POST /review/claim-code` **on the
  locked device**: read the code wherever the mail landed, type it where you are stuck. Same
  allowlist, same 30-minute life, single use, 6-guess budget, same per-IP limit, same
  review-scope cookie. The link path stays — the code is a second door, never a replacement.
- **The admin credential opens the gate.** A correct master password or team PIN now grants the
  `ts_review` cookie alongside the admin token. An admin token already outranks a reviewer
  cookie, so this adds nothing — it just stops the strongest credential in the system being the
  one that cannot open the door. `/admin/login` is now behind the shared 8-per-10-min per-IP
  limiter, since it is anonymously reachable through the gate.
- **`migrations/025_gate_nolock.py`** exempts `/review/claim-code`, `/admin/login`,
  `/admin/change-pin` and `/admin/verify` at the origin. None of them serve content; they accept
  a credential and answer 200/401. The catch-all stays armed and the migration refuses to write
  if its own edit would disarm it.
- **Truthful messages.** The gate screen now names what was actually rejected; the dashboard no
  longer instructs the admin to perform an impossible step. `/review/request-link` returns its
  real `delivery` status, so the screen never says "check your email" when the mail failed.

**Ledger.** RG-0107 (device-independent entry) and RG-0108 (the super admin is never locked out)
added, both OPEN until migration 025 rides a deploy. RG-0066's assertion was **corrected, not
weakened**: it pinned the literal sentence *"Incorrect reviewer code. Please check it and try
again."*, and that exact sentence turned out to be the next lie in the same class — so the
ledger was defending the wording instead of the property. It now asserts the property and trips
if the discredited sentence returns.
