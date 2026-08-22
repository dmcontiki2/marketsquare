# FEED_LICENCES.md — may we use this data feed COMMERCIALLY, and on what terms?

Born 22 Aug 2026 (RG-0148), found while rotating API keys: JustTCG's free tier is
explicitly **personal and non-commercial**, and it was serving card prices into a
commercial marketplace seven days before launch. A licence breach found after launch is
a takedown, not a bug — so every feed gets a row, a dated decision, and its obligations
written where the next session will read them.

**Rule:** no external data feed reaches a customer until it has a row here with a DATED
position. RG-0148 fails while any feed listed is missing or undated.

| Feed | Commercial use on the free tier? | Position + date | Obligations we must honour |
|---|---|---|---|
| JustTCG | **NO** — "The free tier stays personal and non-commercial"; commercial use needs a paid plan (Starter $19/mo, 10k calls; free 1,000/mo, 100/day) | **LANE DARK from 2026-08-22.** `JUSTTCG_API_KEY` removed from the server so `justtcg_price()` returns None and the TCG price tier simply does not light. Free tier stays inside its licence (dev/testing only), nothing is spent, and the collectibles shelf still works. **Switch on the day David subscribes — the key is rotated and valid, it is only unset.** Spend decision is David's (RUL-037) | Paid tier permits storefront use, caching with no retention limit, blending with other sources. May never resell the raw feed |
| Numista | **Yes, within "development, testing and small applications"** — 2,000 requests/calendar month, no explicit commercial bar. Paid plan is **€100 activation + €100/month minimum** (~R2,000/mo), so the free plan is the working position for a long time | **IN USE, free plan, 2026-08-22.** Key rotated and PROBED the same day (HTTP 200, 58 matches) | **Three hard obligations, not yet verified in our UI:** (1) display the **N# identifier** for catalogue search results; (2) clearly identify **Numista as the source**; (3) **do not store or cache catalogue data** — permitted metadata may be cached max **7 days**, other catalogue data not at all. Also: keep credentials confidential; never sublicense or redistribute as a database/API/bulk download |
| Travelpayouts / Aviasales | **Yes** — affiliate programme, no contract, no billing exposure (marker 758984). Flight Data API returns cached fares by design | **IN USE, 2026-08-22.** Token is UNROTATABLE-ACCEPTED (see SECRETS_REGISTER.md) | Affiliate disclosure already live in EULA §6.1A. **No Travelpayouts script on app pages** (RG-0025, post-breach) — any partner imagery must be server-side or link-out |
| eBay Browse | not configured | **DARK, 2026-08-22** — `EBAY_APP_ID`/`EBAY_CERT_ID` unset, so the lane never lights | Honest "asking, not sold" wording already enforced at the consumer if it is ever switched on |
| BrickLink | not configured | **DARK, 2026-08-22** — no token set | — |

## HOW THE VALUATION FEATURES ARE BUILT — David's design, 22 Aug 2026 (N#-REFERRAL-1)

The storage rule, not the price, is what shapes this. Numista forbids storing catalogue
data but **permits storing N# identifiers without a time limit**. That single permission
is the whole architecture.

**One search per LISTING, never per view.**
1. A seller lists a coin → ONE catalogue search → the seller picks the right match →
   we store the **N#** (permitted forever) and nothing else from Numista.
2. Every later view links OUT to that coin's Numista page. The user reads the catalogue
   price on Numista, as a free Numista user, under Numista's terms. No data passes
   through us: nothing to cache, nothing to breach, no per-view cost.
3. Requests therefore scale with **listings created**, not page views — so the 2,000/month
   free plan equals 2,000 new coin listings a month, and a visitor cannot burn quota.

**The 1T fair-price guidance stands on OUR data** — local comps and previous actuals,
which we own and may store freely. It is honest about what it is: our estimate from what
things actually sold for here, NOT a catalogue-verified figure. Copy may never imply
Numista verified our number.

**Consequences worth stating:**
- The €100/month paid plan is no longer needed for the fair-price feature at all. It
  returns only if the bulk **set evaluation** becomes a paid product — a discrete
  business case with its own numbers, not a licence problem hanging over the feature.
- The abuse vector is gone: a visitor cannot cause a billable request.
- This is the introductory model applied to DATA rather than trade — we inform, then hand
  the user to the specialist, exactly as the travel lane hands a trip brief to an agency.

**Feed-choice rule taken from this:** choose data feeds by their RETENTION RIGHTS, not
their headline price. JustTCG's paid tier explicitly permits server-side caching "with no
retention limit"; Numista will not sell storage at any price. That makes JustTCG paid
architecturally cheaper than Numista free for anything that must persist.

## The unfinished item this file exposes

Numista's **no-store rule versus how we serve prices** has not been checked against the
code. `ai_service_tiers.py` credits "Catalogue price from Numista", which answers
obligation (2), but nothing yet proves we display N# identifiers or that we are not
persisting catalogue data in listings beyond their 7-day metadata window. That is
tracked as RG-0149, not as a promise to remember. **N#-REFERRAL-1 shrinks that item
rather than closing it:** under the referral design we stop holding catalogue data at all,
so the retention question narrows to "is any Numista figure persisted anywhere", and the
N# display obligation becomes natural — the identifier IS the link the user clicks.
