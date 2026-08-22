## 2026-08-22 — the Ops Dashboard made to tell the truth about the rotation

David asked for the day's changes to be reflected on the Ops Dashboard, and checking it
first found the panel was wrong or blind in five places. All fixed in the repo; **none of it
is live until the next deploy.**

**1. A false red on Cloudflare (VERIFY-IN-SCOPE-1).** `_infra_cloudflare` judged the token
with `GET /user/tokens/verify` (user-level) and a zone ruleset read (needs Zone Read). The new
purge token is scoped to **Cache Purge on one zone and nothing else** — least privilege, on
purpose — so the panel reported `FAIL — token INVALID … roll token in CF dash` about a token
that had performed a real purge successfully minutes earlier. The advice would have restarted
the exact loop that cost an hour this morning. Now: broad endpoints first (they still say more
when a token IS broad), falling back to a real purge of a non-existent URL. Asserted by RG-0151.

**2. A green that could not fail on object storage.** `_infra_hetzner_s3` did a bare `GET` on
the endpoint and called any HTTP response "ok" — proving a host is reachable, not that our
credentials work. Revoked keys would have shown green. Now a signed `ListObjectsV2`.

**3. A row naming the wrong vendor AND the wrong purpose.** It read *"Hetzner S3 · object
storage · backups"*. The endpoint is **Cloudflare R2** and the bucket holds **listing photos**;
backups are a different lane entirely. That mislabel sent this very session to the Hetzner
console, where credentials were generated and installed into an R2 lane — a real photo-storage
outage. Now: *"Object storage (R2) · listing photos · bucket marketsquare-media"*.

**4. Two live feeds that were invisible.** **Numista** was serving coin data with no row at all
— the precise "a partner you cannot see fails silently" fault the panel's own comment says it
exists to prevent. Added, presence-only by design (a live search would spend free-tier quota,
same rule as the billable DHA row) and showing the monthly counter. **Encrypted backups** had no
instrument anywhere: the rclone → R2 lane ran nightly on trust and was verified by hand for the
first time today. Added, reading the last run's own log — ok under 36h, warn to 96h, then fail.

**5. Two hand-written verdicts wearing health colours (RG-0133's rule).** The Paystack card
carried a hardcoded `test mode` chip fed by nothing — false since the live key went in, on the
one card where a wrong answer costs money. It now starts "not wired" and is filled from the
probe. And JustTCG's row read as a plain fault when it is **OFF BY DECISION** (free tier
licensed non-commercial); it now says so, because "not set" invites someone to helpfully set it
back into a licence breach.

**Also confirmed, not a defect:** the red `service checks offline` chip and the admin lockout
were the JWT and admin-password rotations working as intended. Sign-in with the new password
restores both.
