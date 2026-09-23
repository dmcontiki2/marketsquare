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
One tap. You read the Terms, accept, and it goes up. There is no account to make first, no card,
and we take no commission on your trips.

**Take it down** — <<WITHDRAW_LINK>>
One tap and it comes down and your photographs are deleted with it. No reply needed, nothing to
explain.

Do nothing and nothing happens: it stays an unpublished draft that nobody can see, and you will
not hear from us again.

The only reason we are asking is that the advert is good, and it was your work rather than ours.

David Conradie
TrustSquare

---

## The two links — CHANGED 23 Sep 20:30Z, and the reason matters

**The publish link must be a SIGN-IN link, not a bare `?magic=1` link.** AUDIT-AUTH-1 landed in
`bea_main.py` the same day (the publish door now acts as the proven session rather than a typed
`?email=`, so a stranger cannot publish anyone's draft by naming them). That is the right change
and it ships with ours — but it means a cold arrival with no session gets `401 Please sign in to
do that`, and Rick has no session and no account. A bare magic link would walk him into a 401.

    PUBLISH   POST /auth/request-link for rickwemple@aol.com, and send the ?signin=<token>
              link it mints. He lands signed in, on his own draft, at the Terms, with a
              publish button — and the session satisfies AUDIT-AUTH-1.
    WITHDRAW  https://trustsquare.co/listings/382/withdraw?email=rickwemple%40aol.com
              (deliberately needs no session: refusing must never be harder than agreeing)

## Checks before this sends — every one of them, or it does not go

1. Fix A is live: publishing without accepting the Terms is refused, and accepting through the
   link is recorded on the server. Until then the first link is an invitation to a hole.
2. Fix C is live and the withdraw link actually deletes the photographs. **If the R2 delete is
   not implemented, change the sentence** — do not send a letter that promises a deletion we do
   not perform.
3. The publish link is walked end to end in a real browser AS A SIGNED-IN ARRIVAL, on a throwaway address with a real
   draft, and the listing is confirmed publicly visible afterwards. A link that 404s on the one
   man who got this far is worse than no letter.
4. Listing 382 reads `country='US'` — done 23 Sep — so a Montana elk hunt does not surface in the
   South African market.
5. `src=recoup-382` is on the publish link, so whatever he does is measurable and we never have
   to guess again whether this worked.
6. One send. No reminder, no sequence, no second thought a week later — RUL-106(e).

## Judgements in this draft, so they can be overruled rather than discovered

- **It admits the broken promise in the first line.** Hiding it would be the cheap version, and
  he can still read the old footer in his inbox.
- **The withdraw option is given equal weight to the publish one**, and is listed second only
  because that is the order of the sentence, not the order of our preference.
- **No deadline, no scarcity, no "last chance".** He is a licensed professional being asked about
  his own property.
- **It is signed by a person, not the platform.**
