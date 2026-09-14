## 2026-09-14 — The comms got an identity, and the spreader got a keyboard

**Buzz, and then eighteen more endpoints, stopped taking the caller's word for who he is.** The app
key that gates them ships inside ms.js, so it was public; every one of them read the acting person
out of the request body. Proved live, read-only, on a non-existent address before anything was
touched: `GET /buzz/pairs` answered 200 with that key and 401 without it. Account closure, banking
details, KYC documents, ID upload, the identity check that awards trust, Tuppence balance and
history were all on the same footing — Buzz was never the worst of them, only the one that got
asked about. All twenty-three are now bound to the signed-in session, or to the env-only admin key
where the endpoint is ours rather than a person's. Enforced by default; `BUZZ_BIND=0` reverses the
whole class without a deploy. 43 checks green against the real patched source, RG-0371 sweeps every
route in the file and was proved to fail on six mutations. **Live and verified on the server.**

**Buzz also needs the terms ticked, not just a sign-in.** `eula_accepted_at` was written in one
place only — the seller flow at first publish — so somebody who clicked a magic link and never
listed would have been admitted by the very clause §3.8 was written to bind. First switching Buzz on
is now the acceptance moment: one tick, no ID, no document. [[RUL-135]].

**The Quick Listing spreader is installable and no longer Gauteng-only.** It serves from
`/quick.html` with its own violet tile — the registered mark, re-hued, so it cannot be confused with
the TrustSquare one. Two fixes since: a phone turned sideways was being handed the DESKTOP simulator
and clipped, which is now a real landscape layout; and the area step's six hardcoded suburbs have
grown an "Another option" tile that takes one typed line — FILTER-DATA-2 applied where I had broken
it, resolved against [[RUL-117]] as a seventh tile rather than a replacement. **Both verified, both
waiting on one deploy.**
