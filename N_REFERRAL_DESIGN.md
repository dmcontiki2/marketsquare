# N#-REFERRAL-1 — build spec: catalogue-referred valuation without holding catalogue data

**Ruling it implements:** David, 22 Aug 2026 (FEED_LICENCES.md). One catalogue search per
LISTING, never per view; store the N# identifier (permitted without time limit) and nothing
else from Numista; every later view is a LINK OUT to Numista where the user reads the price
themselves. The 1T fair-price guidance stands on OUR OWN data.

**Why this shape:** Numista's licence forbids storing or caching catalogue data (metadata max
7 days). Any design that pins a Numista price to a listing is either a breach (stored) or a
per-view cost (re-fetched). Referral removes both — and the abuse vector with them, because
requests then scale with listings created, which sellers cannot inflate for free, rather than
with page views, which anyone can.

## Data model

New columns on `listings` (migration `029_numista_ref.py`):

| column | type | why |
|---|---|---|
| `numista_id` | INTEGER NULL | the N# — the ONE thing the licence lets us keep forever |
| `numista_title` | TEXT NULL | the catalogue title the seller confirmed; shown as the link label |
| `numista_matched_at` | TEXT NULL | when the seller confirmed the match |
| `numista_matched_by` | TEXT NULL | `seller` or `admin` — a match is a human act, never a guess |

Deliberately absent: any price, estimate, mintage, or metadata field. **If a future column
would hold a Numista figure, this design has been broken.** RG-0150 asserts the absence.

## Flow

1. **At listing creation (coins category only, to start).** Seller types the coin; ONE call to
   `GET /api/v3/types?q=…` returns matches; the seller **picks the right one**. We store the
   four columns above. One request per listing, ever.
2. **A seller may skip.** No match = no link, and the listing still works. Nothing about the
   catalogue may block a listing going live.
3. **At view time.** If `numista_id` is set, render a link to
   `https://en.numista.com/catalogue/pieces{N#}.html` labelled with the catalogue title, plus
   the required source credit. Zero API calls, zero stored catalogue data.
4. **The 1T fair-price guidance is a SEPARATE lane** and never touches Numista. It reasons over
   our own local comps and previous actuals, and says so in its wording. It may never imply
   the number is catalogue-verified.

## Licence obligations, discharged by design

- *Display the N# identifier* — it IS the link, visible and labelled.
- *Credit Numista as the source* — required copy beside every link.
- *Do not store catalogue data* — we store an identifier and a title the seller confirmed;
  no prices, and nothing cached from a response body.
- *Keep credentials confidential* — the key stays server-side; the browser never sees it.

## Quota

Search is called only on listing creation, so the free plan's 2,000 requests/month equals
2,000 new coin listings a month. A counter with a hard monthly cap still guards it: on cap,
matching degrades to "skip" (listing proceeds, no link) — never an error, never an overspend.

## What this replaces

The earlier plan to buy Numista's paid plan (EUR100 activation + EUR100/month minimum) for
the fair-price feature. That plan is no longer needed at all. It returns only if the bulk
**set evaluation** becomes a paid product — a discrete business case with its own numbers.

## Build order

1. `029_numista_ref.py` — the four columns (additive, nullable, safe).
2. `numista_match.py` — one function: search, return candidates, no storage, hard cap.
3. `POST /listings/{id}/numista-match` — seller confirms a candidate; writes the four columns.
4. `ms.js` — the picker at listing time, and the link + credit at view time.
5. RG-0150 — asserts no Numista figure is ever persisted, and the link/credit render.
