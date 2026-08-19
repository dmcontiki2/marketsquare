## 19 Aug 2026 — SIGNIN-CODE-1: zero-retry sign-in for real users (launch path, not the gate)

**David's ruling, on the launch gate:** *"I need access for users with no effort... zero retries.
How do I email 10000 people to help them after they tried a few times."* He is right, and he was
right to reject the workaround: handing one tester a password proves the defect, not the fix.

**The defect is the device, not the email.** A magic link signs in whichever device *opens the
mail*. Mail overwhelmingly opens on a phone; the person is usually on a laptop. Every user that
happens to is stranded mid-task with no self-service way out — and at launch scale there is no
support channel that can rescue them one at a time.

**Fix — the code leads, the link follows.** The sign-in email now carries a 6-digit code above the
button. `POST /auth/verify-code` redeems it in the tab the person already has open: no device hop,
no lost tab, no app switch, and nothing a mail scanner can spend. The link stays for people
already reading mail on the device they want to use. 20 minutes, single use, 6-guess budget,
per-IP rate limited.

- `_establish_user_session` is now the **one** place a user session is created — both the link
  (`/auth/verify`) and the code (`/auth/verify-code`) route through it, so the two doors cannot
  silently drift apart.
- `ms.js` reveals the code box inside the same panel as soon as the email is sent, wired so that
  **every** caller of `requestSignInLink` inherits it — no sign-in surface is left link-only.
- Migration 025 also exempts `/auth/verify-code`, so pre-launch testers get the same door.

**What was already right, and worth stating plainly:** browsing needs no sign-in at all. Only
**6 of 160 endpoints** require a user session, and all six are *actions* (making an intro, the
seller AI tools). The zero-effort path already exists for everyone who is looking rather than
acting; this fixes the single moment where identity is actually needed.

**Correction on record.** An earlier note this session said the account magic link carried the
same single-use prefetch fault as the gate link (RG-0109). It does not — `/auth/verify` has no
`jti` and no single-use, so a scanner fetch is harmless there. The user-path defect is the device
dependency, which is a different and larger problem.

**Ledger.** RG-0110 added (OPEN until deployed), asserting the class: any future sign-in surface
must offer the typed code, not a link alone.
