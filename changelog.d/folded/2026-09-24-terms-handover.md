# TERMS-HANDOVER-1 — the seller sent to the Terms now lands on the Terms (onboarding run 19)

**24 Sep 2026 · ms.js · RG-0449 · found by walking the live journey, not by reading it.**

The cold-seller journey was walked end to end on the live site in headless Chromium at phone
size, as a seller with no acceptance on record arriving on a seven-day `?signin=&draft=` link —
the journey the onboarding number counts, and the one the recoup letter to Rick Wemple sends a
man down. It completes: the terms render (v1.18, 106k characters), the scroll gate opens, both
boxes tick, the publish answers 200, and a logged-out reader sees the advert live. That is the
sixth and last pre-send check on `RECOUP_RICK_LETTER.md`, and it now passes on live evidence.

One defect was found on the way, two requests apart:

* `PUT /listings/{id}/publish` answered **403** (EULA not accepted) — RG-0443 working as built.
* The very next request, `GET /users/<him>`, answered **401**.

That endpoint carries `Depends(auth.require_api_key)`. The one call in `sobInit()` that makes it
sent no `X-Api-Key`, while every neighbouring call in the same file sends it. So `if (uRes.ok)`
was false for **every** seller ever handed over: `_eulaSigned` was never read, the note that
explains why he is on that screen stayed hidden, and `sobGoPhase(3)` never fired. `dashPublish`
said *"One step first — please read and accept the Terms"* and then dropped him on phase 1, a
listing preview whose only button reads "Looks good". Nothing there mentions terms; they are two
taps further on, unexplained.

**Fixed, two legs.** The lookup sends the key the endpoint asks for. And a gate that cannot read
the truth now fails *towards* asking rather than past it: when the server has just refused the
publish for want of an acceptance, a failed lookup still lands him on the Terms. Strictly
tightening — no arrival that reaches the terms today stops reaching them.

**Also recorded, not changed:** the terms box is 39,829 px in a 338 px window — about 118
screenfuls to swipe on a phone before the confirm row appears. The scroll-to-the-end gate is
deliberate (conspicuous *and* acknowledged), and the text is David's, so this is reported rather
than adjusted.

Harness: `scripts/smoke_harness/verify_terms_handover.mjs` (repeatable; archive the probe after).
Probe listing 399 was live for about four minutes and is archived; it never appeared in a feed.
