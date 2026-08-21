## 2026-08-21 — ONETAP-DOC-1: Google OAuth was live; the doc said dark, and I repeated the doc

David, on reading the new third-party register: *"I am sure we have done this already."* He was
right and the register was wrong.

`GET /auth/providers` on the live server returns `{"google":true,"apple":false}` and
`/auth/oauth/google/start` returns 302 to Google. Google federated sign-in — RUL-028's "primary
door" — has been live and serving. **RG-0111 already knew**: it is LOCKED and its own info line
reads "live providers configured: google".

What was stale was `ONETAP_SETUP.md`, which still opened with "Status: **code shipped, lane
dark**" and, worse, annotated the example `{"google":false,"apple":false}` with "(this is
today)" — a line that was true when written and silently became a lie. I built the register's
Google row from that file instead of from a probe, and handed David a ten-minute task he had
already done.

Corrected: the setup doc now states the verified live state and dates the old one; the register
row reads LIVE with RG-0111 cited; the David-only action is removed. The only residue worth a
mention is confirming the Google consent screen is *Published* rather than left in Testing —
which cannot be established from the API and needs a human eye in the Cloud Console.

**The rule this earns**, now written into the daily sweep's own prompt as the first thing it
reads: *verify live, never report a state read from a file; if a file and a probe disagree, the
probe wins and you fix the file in the same run.* The probes existed. I used the document
because it was easier, which is exactly the failure the probes were built to prevent — the same
shape as trusting a green "READY" that only proves presence.

Cost model impact: none.
