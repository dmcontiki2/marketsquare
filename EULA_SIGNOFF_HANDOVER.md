# EULA-SIGNOFF-1 — handover for the lane holding the bea_main.py / quick.html lock

**David, 23 Sep 2026 (evening):** *"I dont see it as optional, all new lister/subscribers has to mandatory sign off on the EULA before we can accept them on the app."*

Found by: session claude-da (waiter-route test). Written here because `bea_main.py`, `quick.html`,
`genie/HARNESS.html` and `RULINGS.md` are under WORK-LOCK-1 by `lang-quick-2026-09-23` (RUL-140).

## The fault
ONE-TAP-PUBLISH-1 (RUL-163 b) treats the Publish tap as acceptance: the client hard-codes
`accept_terms:true`, and `/listings/quick-publish` stamps `users.eula_accepted_at` for any new email.
So a first-time lister goes live without ever seeing, scrolling or signing the EULA.

## Ruling to add — RUL-166 (amends RUL-163 b, design phase)
David, 23 Sep 2026, restating the original design: the Quick app makes a viewable, publish-ready
DRAFT for the prospect; publishing happens only in the TrustSquare app, where he sees the EULA; nothing
goes live without BOTH his email and his EULA acceptance. RUL-163(b)'s "save and publish in one tap"
is withdrawn for anyone without a signed EULA; the former end-of-flow draft hand-over returns.

## Build
1. **bea_main.py `quick_publish`** — keep the endpoint, but: if `users.eula_accepted_at` for `em` is NULL,
   save the advert as a DRAFT (no `publish_listing` call), never stamp `eula_accepted_at`, send the
   draft-waiting mail with the app link, return `{"id":..,"live":false,"need":"eula"}`.
   Only a member whose EULA is already signed publishes in the one tap. Remove the COALESCE stamp entirely.
2. **quick.html + genie/HARNESS.html** — button says "Save my advert" for anyone without a signed EULA
   (`/quick/me` `eula_accepted`); no terms-acceptance wording; arrival screen shows the draft card and
   "Open in TrustSquare to publish". Signed members keep "Publish".
3. **Main app** — publishing that draft goes through the existing sob EULA scroll-to-end gate
   (marketsquare.html phase 3) and `publish_listing`'s 403 gate (bea_main.py ~4159), both already in place.
4. **Guard** — ledger check: quick-publish for a fresh email → listing_status 'draft', eula_accepted_at NULL.
5. **Accounts stamped by the one-tap path since c9e5181** (log `ONE-TAP-PUBLISH-1 ... session=False`):
   clear `eula_accepted_at`, return their adverts to draft, mail them the app link to sign and publish.
6. Verify in the RENDERED /quick/ signed-out (incognito): advert saves as draft, nothing goes live; then
   publish from the app shows the EULA gate.

## Overlap note (20:25 UTC)
Lane `onboarding-run17` holds bea_main.py for EULA-PUBLISH-1 (publish_listing gate, PENDING_FIXES_RUN17.md A).
That fix does NOT close this one: `quick_publish` stamps eula_accepted_at itself before calling
publish_listing, so the gate passes. Build this on top of their commit; keep their accepted_terms param.
