## 2026-09-13 — The hand-over is proven on the live server

David, 13 Sep 2026: *"I authorize one draft listing on trustsquare.co under Dave Junior's tester
account."* Done, once, exactly as authorised.

The payload was composed by the harness itself — `handoverPayload()` run in the page against a real
five-tap Housekeeping journey (Cleaning → Pretoria East → Mon → R250), not hand-written — and posted
to the live `POST /listings`.

**Result: `{"id":383,"message":"Listing saved as draft — seller must complete onboarding to go live"}`,
HTTP 200.**

Verified afterwards by reading it back:

- `GET /listings/383` → title *Cleaning — Pretoria East*, category Housekeeping, suburb Pretoria East,
  price R250, `listing_status: "draft"`, `published_at: null`, `seller_email: davidconradie1234@gmail.com`.
- The server did its own half correctly — `geo_city_id` resolved to **47** (Pretoria) from the city
  name, and `safety_score` was computed at 25. Neither was sent; both are the server's.
- `GET /listings/mine?email=…` for Dave Junior returns exactly one row, id 383.

**This closes the last unproven link in the chain.** Taps → advert card → real listing → the seller
finishes onboarding and the EULA in TrustSquare to go live. One server, one rulebook (RUL-125(b)),
and the draft gate means nothing the Quick app creates can reach the public shelf on its own.

### Where it is visible

Signed in as Dave Junior: **Dashboard → Listings tab**, shown with a draft badge (`loadLiveDash()`
maps `listing_status==='draft'` to a draft status, so drafts do appear there). It is NOT on the
public shelf and cannot be — draft listings are excluded until published.

### One thing left open for David

Listing 383 is a test row sitting in the production database. It is invisible to the public and
harmless, but it is real. **Leave it as the reference specimen, or delete it — David's call.**

### Second draft, under David's own account

David could not sign in as Dave Junior — TrustSquare sign-in is passwordless (`/auth/request-link`,
`/auth/verify-code`), so the code goes to that account's own inbox. `seller_email` is not a field on
`ListingUpdate`, so listing 383 could not be re-pointed; a second draft was authorised and created
instead.

**Listing 384** — same payload, `seller_email: dmcontiki2@gmail.com`, status draft.
`GET /listings/mine` for that account returns exactly one row, id 384.

Two test rows now exist in production: **383** (Dave Junior) and **384** (David). Both are drafts,
both invisible to the public. Keeping or deleting them is David's call; `DELETE /listings/{id}`
exists for it.
