## 2026-10-07 — PHOTO-EMPTY-1 + YEAR-EXACT-1: removed photos stay removed; a Quick year range is never filed as a year

Dave jnr via David, 7 Oct: "he edits his photos but cant delete them all, it deletes to one then all of them appear again" and "on quick selecting a year, then porting to trustsquare doesn't transfer correctly".

PHOTO-EMPTY-1. Why it came back: the 19 Aug fix (PHOTO-ORDER-1) stopped the edit screen from re-reading the advert while she worked on her photos, but it used an EMPTY photo list to mean "not read yet". Removing the last photo emptied the list, so the screen read the advert again (the old photo list or the [photos:...] prefix in the description) and every removed photo came back. Reproduced on the live page: 3 photos, three removes -> 3, 2, 1, 3. Now "read once" is its own flag; removing every photo leaves none, Save sends an empty list, and the server clears the cover too. PHOTO-CAP-3: the server kept only 20 photos per edit while the app allows 24 for property, cars and stays; it now keeps 24. Ledger RG-0932.

YEAR-EXACT-1 (AUD-212, found in the 4 Oct audit). Quick's year chips are ranges (2020+, 2015-2019, 2010-2014, Older) and the hand-over turned the range into its first year, so a 2018 car read 2015 in TrustSquare. Reproduced on live /quick/: Sedan > Toyota > 2015-2019 sent vehicle_year 2015. Now only an exact year she typed becomes the car's year; a range stays in her advert's words ("Year: 2015-2019") and TrustSquare's Edit asks for the exact year. Migration 069 clears the year on Quick cars already filed wrongly (dry by default, backup before --apply). Ledger RG-0933.

Cost model impact: none.
