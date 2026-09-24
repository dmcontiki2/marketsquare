# RECOUP-1 — the one letter to Rick Wemple (DRAFT, NOT SENT)

To: rickwemple@aol.com · Wemples Wildlife Outfitter LLC, Victor, Montana · source `register:moga`
Permission: `.secrets/recontact_permission.json` (David, 23 Sep 2026, RUL-106(b), this address only)
Blocked on: the flow fixes in `PENDING_FIXES_RUN17.md` landing first — David's order.

**What he already did:** letter 11 Sep 22:12 UTC → opened 23:45 → clicked 12 Sep 15:19 → finished
advert 15:37. Eighteen minutes from click to a complete listing with four of his own photographs.

---

## Subject

    Your Montana advert is still here — do you want it up, or gone?

## Body

Rick,

When we wrote to you on the 11th we said we would not email you again. This is us breaking that
once, to ask you a question about your own work, and then not writing again either way.

The day after that letter you built an advert with us — Guided Fair Chase Hunts, your four
photographs, your words, your price. You never put it live. It has been sitting here as a draft
since the 12th.

We would rather ask you than quietly delete it or quietly leave it. So, two links, and either one
is a complete answer:

**Put it live** — <<PUBLISH_LINK>>
One tap. You read the Terms, accept, and it goes up. There is no card, and we take no commission
on your trips. That link works for a week; after that, go to trustsquare.co and sign in with this
same address — the advert will be sitting there waiting either way.

**Take it down** — <<WITHDRAW_LINK>>
One tap and it comes down and your photographs are deleted with it. No reply needed, nothing to
explain.

Do nothing and nothing happens: it stays an unpublished draft that nobody can see, and you will
not hear from us again.

The only reason we are asking is that the advert is good, and it was your work rather than ours.

David Conradie
TrustSquare

---

## The two links — CORRECTED 24 Sep 03:20Z (run 18). Read this before minting anything.

**The publish link must be a SIGN-IN link, not a bare `?magic=1` link.** AUDIT-AUTH-1 landed in
`bea_main.py` on 23 Sep (the publish door now acts as the proven session rather than a typed
`?email=`), so a cold arrival with no session gets `401 Please sign in to do that`. PROBED 24 Sep
03:10Z on a throwaway draft: `PUT /listings/397/publish?email=…` answers **401**, and so does the
same call with `&accepted_terms=1`. A bare magic link walks him into that 401.

**AND THE TOKEN MUST NOT COME FROM `/auth/request-link`.** The 23 Sep recipe said to call that
endpoint and send the link it mints. That endpoint mints a **20-minute** token (`auth_request_link`,
matching `_SIGNIN_CODE_MIN = 20`) — right for a code somebody just asked for, wrong for a letter.
Rick opens his post when he opens it. The 23 Sep letter would have reached him carrying a button
that was dead before he ever saw it, and the app would have told him his link had expired — which
is the precise failure this project already paid for once: `QUICK-RETURN-TTL-1` (18 Sep 2026) was
written after the first draft-return letter went to *this same man* at ~01:15 his local time with a
20-minute link in it. The lesson was learned, written down, and the recoup recipe reached for the
short lane anyway.

**Mint it the way `_quick_draft_return()` does** (`bea_main.py`, the QUICK-RETURN-TTL-1 block) —
same claims, same 7-day life, same `&draft=` param:

    PUBLISH   https://trustsquare.co/?signin=<jwt>&draft=382&src=recoup-382
              jwt = {"email": "rickwemple@aol.com", "purpose": "signin",
                     "exp": now + 7 days, "iat": now}  signed with MS_JWT_SECRET
              Minted on the server (the secret lives only there). Guard first: if
              MS_JWT_SECRET is empty the token is signed with an empty key and is dead
              on arrival — QUICK-RETURN-GUARD-1 says fail closed and send nothing.
    WITHDRAW  https://trustsquare.co/listings/382/withdraw?email=rickwemple%40aol.com
              (deliberately needs no session: refusing must never be harder than agreeing)

**Seven days, not thirty, and the letter carries the fallback in writing.** Seven is the reasoned
in-house figure and it keeps a month-long key out of an inbox. Because this is one send with no
follow-up, the letter must ALSO tell him the unexpiring way back — sign in at trustsquare.co with
this address and the advert is there — so a link that lapses costs him nothing. The body above
carries that sentence.

## Checks before this sends — every one of them, or it does not go

1. **PASS (24 Sep 03:08Z, probed live).** Publishing without a proven session is refused: `401
   Please sign in to do that`, with and without `accepted_terms=1`. The 23 Sep hole — a fresh
   address publishing with no account and nothing accepted, 200 and publicly visible — is closed.
2. **PASS (24 Sep 03:06Z, walked in a real browser).** The withdraw link does exactly what the
   letter says. A throwaway draft (397) with a real uploaded photograph: the photo answered 200 at
   its public URL before, the withdraw page rendered "Done - your advert is down. Your photographs
   have been deleted.", the row went `archived / withdrawn_by_seller` with the photo columns
   cleared, and the object answered **404** afterwards. The promise is kept, not merely displayed.
3. **PASS (24 Sep 2026 04:06Z, walked end to end in a real browser) — and it found a defect on
   the way, which is why it existed.** Headless Chromium at phone size, on the LIVE site, as a
   throwaway seller with no acceptance on record arriving on a seven-day `?signin=&draft=` link
   exactly like the one above (draft 399). The mile completes: he is signed in, the hub puts his
   advert in front of him with Publish in reach, the server refuses the publish with 403 (EULA),
   the terms render in the box — **v1.18, 106,368 characters**, the same version the site
   publishes — the scroll gate opens at the end, both boxes tick, `PUT /listings/399/publish`
   answers **200**, the screen says "YOU'RE LIVE", and a **logged-out** reader sees
   `listing_status: "live"` with `published_at` stamped. The probe was archived immediately and
   never appeared in a public feed.
   **WHAT IT CAUGHT (TERMS-HANDOVER-1, RG-0449, fixed and shipped the same session):** two
   requests after the 403, `GET /users/<him>` answered **401** — that endpoint requires the app
   key and this one call sent none. So the returning-seller gate never ran for anybody:
   `sobGoPhase(3)` never fired, the note explaining why he is on that screen stayed hidden, and
   the handover dropped him on phase 1, a listing preview whose only button reads "Looks good".
   He could still reach the terms in two more taps, unprompted and unexplained — at the one
   moment we have his attention. Now: the lookup sends the key, and a lookup that fails still
   lands a refused publish on the Terms.
   **THE ONE CONDITION ON THIS PASS:** the fix must be LIVE before the letter goes, because the
   letter sends him down exactly this road. Confirm the served `static/ms.js` carries
   `TERMS-HANDOVER-1` and that the walk reports `handover landed on sob-p3`, then send.
   Re-runnable: `node scripts/smoke_harness/verify_terms_handover.mjs "<url>" <id>`.
   **Also measured, not a blocker:** the terms box is 39,829 px tall in a 338 px window — about
   118 screenfuls on a phone before the confirm row appears. The gate is deliberate and the text
   is David's; it is reported, not adjusted.

4. **PASS.** Listing 382 reads `country='US'` (verified 24 Sep 02:58Z on the live DB), so a Montana
   elk hunt does not surface in the South African market. The create path now carries country too:
   a fresh Montana draft (397) was born `US`, where before it would have been `ZA`.
5. **PASS by construction.** `src=recoup-382` is on the publish link above, and `draft=382` lands
   him on the advert itself rather than the hub's front page.
6. One send. No reminder, no sequence, no second thought a week later — RUL-106(e).

## Judgements in this draft, so they can be overruled rather than discovered

- **It admits the broken promise in the first line.** Hiding it would be the cheap version, and
  he can still read the old footer in his inbox.
- **The withdraw option is given equal weight to the publish one**, and is listed second only
  because that is the order of the sentence, not the order of our preference.
- **No deadline, no scarcity, no "last chance".** He is a licensed professional being asked about
  his own property.
- **It is signed by a person, not the platform.**
