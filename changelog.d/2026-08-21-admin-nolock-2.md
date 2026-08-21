## 2026-08-21 — ADMIN-NOLOCK-2: the admin door gets its own failure budget

**Fault (David, 21 Aug):** "I am back it being blocked by my own app." The Session
Dashboard answered *Too many attempts* with the site healthy and no wrong password typed.

**Cause:** GATE-NOLOCK-1 (19 Aug) fixed the origin half of admin lockout but routed
`/admin/login` through `_review_rate_ok` — one per-IP bucket shared with the reviewer
lane, counting **every** attempt including successes. The machine lanes on David's own
IP (regression ledger, maintenance agent, a phone at the gate) each mint a review token;
each successful mint spent one of eight slots. The strongest credential in the system was
locked out by its own housekeeping.

**Fix (bea_main.py):**
- `_admin_attempts` — separate bucket. Reviewer traffic can never starve the admin door.
- Failures-only accounting in **both** lanes: `_rate_note_failure` on a wrong credential,
  `_rate_clear` on a correct one. Successful mints now cost nothing anywhere. This is the
  half that kills the starvation class, not just this instance.
- The 429 carries exact seconds + a `Retry-After` header — "Try again in 3m 20s", not
  "a few minutes". The dashboard renders `detail` verbatim, so David sees the number.
- Master password clears the reviewer bucket too — the strongest credential rescues both lanes.

**Brute force unchanged:** 8 wrong reviewer codes, 10 wrong admin credentials, same 10-min window.

**Locked:** RG-0134, with a live-logic half that exercises the limiter (5 assertions).
RG-0073's assertion corrected in the same pass — it demanded the literal `_review_rate_ok`,
which pinned the admin door to the shared bucket. It now asserts the property, not the spelling.
