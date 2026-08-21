## 2026-08-21 — ID-NPR-5: the front end, so this stops being armed-but-unreachable

David: *"Now please Claude, lets not leave it only to be forgotten again."* Fair. The backend
had been live and correct since ID-NPR-3 while no seller could reach it, which is the exact
shape of a thing that quietly never ships.

Three pieces in `ms.js`, all deliberately non-blocking:

**The seller's buy-a-check card.** Renders under the trust-signals list, creating its own host
node rather than editing the 418KB page. Asks for full name and 13-digit ID, calls
`POST /users/{email}/verify-identity-npr`, and states plainly that the charge only happens if
the register answers. It checks `GET /id-verify/status` first: if the lane is down it says so
and offers nothing to click, rather than taking a Tuppence for a call that cannot complete.
`402` is handled explicitly, so a seller short on Tuppence gets a sentence, not a raw error.

**The green tick.** Keyed strictly on `green_tick`, which only an NPR pass sets. A guard
asserts it never reads the AI document-check flag — that check proves a document is legible,
not that a person is who they claim, and it must never reach a buyer as "verified".

**The buyer warning.** Fires before the introduction POST when the seller has no NPR pass, and
names the deposit risk for stays specifically. It is advisory in the strongest sense: it
defaults to letting the buyer through, and its `catch` returns `true`, so an error in the
warning can never cost a buyer their introduction. Declining is the buyer stepping back, never
us refusing them. The acknowledgement rides along as `unverified_ack` and is recorded.

Styles added to `ms.css` (both already on the deploy manifest — checked, after
`id_verify_provider.py` was found missing from it two commits ago).

Guards: `scripts/idnpr_ui_selftest.js`, 13 assertions covering the permissive default, the
fail-open catch, the tick's source flag, the deposit wording, the lane-availability check and
the 402 path — plus four new ledger assertions in RG-0136 so a future edit that makes the
warning fail closed, or points the tick at the AI flag, trips red.

RG-0136's scope corrected: it still claimed the front end was unbuilt. **What remains
genuinely unproven is that no real NPR query has ever run** — the free-tier question and the
outcome mapping against a live registry response are both untested until a seller completes
one.

Cost model impact: none. The UI spends nothing; the 1T charge is the backend's, unchanged.
