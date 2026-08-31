## 2026-08-30 — RUL-078: Pro includes Global reach; Squire's build shape and acceptance criteria approved

David resolved the question RUL-077 had reserved to him, and closed two sections of the Squire spec.

**(a) Bundling.** The **$20 Pro subscription carries the $5 Global buyer reach automatically.**
Reason accepted: reach is a query filter, not a cost, and Squire watches across the reach its
subscriber holds — an unbundled Pro would confine the agent to one city and kill its two best cases
(a collector hunting nationally, a parent comparing tutors across a metro).

*Naming corrected against canon in passing:* David's message said "the local $5 reach". On the buyer
axis **Free is the local tier; Global ($5) is national + global.** The ruling reads: Pro includes
Global reach. Nothing on disk needed changing.

**(b) This is a CODE fact, not a pricing sentence.** `_buyer_tier()` reads `wishlist_subscriptions`
alone and returns `free` | `global`. It must **also** return `global` when the account holds a live
**Pro** seller subscription. Until that lands, a Pro subscriber is silently treated as local — the
product would under-serve the people paying most, invisibly, with nothing on screen to reveal it.
Recorded as PRICING_CANON §2c and as acceptance criterion 9 on RG-0224.

**(c) Approved and closed to re-litigation.** SQUIRE_SPEC.md §6 (build shape — server-side and
scheduled per RUL-070; cheap model for nightly matching with the Sonnet-class call reserved for brief
drafting and Q&A, which is exactly what the cap counts; flag-dark on arrival; **Zoom first, Squire
second**) and §7 (now nine acceptance criteria). A build session implements these; it does not reopen
them.

**(d) Pricing-page hazard logged — David's call, not a blocker.** There are now **two distinct $5
products**: *Starter* ($5, 10 seller slots) and *Global* ($5, buyer reach) — and **Starter does not
include Global reach.** Someone paying "$5" could reasonably assume they get both. The two axes must
read as visually separate on the pricing page. The $5 tier keeps the name *Global*; Pro simply
includes it, the ordinary way a higher plan includes a lower one.

Files: PRICING_CANON.md §2c · SQUIRE_SPEC.md §5/§6/§7 · RULINGS.md RUL-078 · regression ledger
RG-0224 (scope + criterion 9) · scripts/rulings_check.py RUL-078. Rulings check: 78 checked, 0 FAIL.
