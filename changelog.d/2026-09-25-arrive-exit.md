## 2026-09-25 — Quick: a way out of the "Your advert is live" screen (ARRIVE-EXIT-1)

David, with two screenshots: *"There is no go back button from this screen, is it by design or can the user go back?"*

- Not by design: the arrival screen (ARRIVAL-1) offered only "See my advert" and "Send it to myself on WhatsApp",
  so a seller who wanted to stay in Quick was stuck.
- Added a close (×) top right and "List something else" under the buttons. Both go to a FRESH start on the
  Quick front door, never back into the form she just published (that would only invite a duplicate advert).
- New words in roles/quick_i18n.json, all five languages (preview, RUL-160 review).
- Rendered test before shipping (phone size, publish mocked): arrival -> "List something else" -> front door,
  nothing carried over, no page errors. Ledger entry added (OPEN until live).

Cost model impact: none.
- Live 25 Sep 07:25 UTC: checked in Chrome on trustsquare.co/q/ (publish answered in-page, no real advert): arrival screen shows the close and 'List something else'; tapping it returns to the front door with nothing carried over. RG-0476 LOCKED.
