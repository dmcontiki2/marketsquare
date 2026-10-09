### Her own photo, straight from the draft card (Goal run 33b)

David, 9 Oct 2026: "Why can't a new lister add her photo here by clicking on the photo … It will look good and be an
incentive to go on?"

- **QUICK-OWN-PHOTO-1** — on Quick's "Here is your listing", the example picture carries "📷 Tap to add your own photo".
  The phone's camera or gallery opens; her photo takes the example's place at once, the strength ring counts it, and
  after Save it is attached to her draft (or to the listing, when she published in one tap). The server hands the draft's
  photo token only to the phone that made the draft — never for an address that belongs to somebody else's account.
- **HUB-ADD-PHOTO-1** — a Seller Hub card with no photo shows "📷 Add photo" (into Edit) instead of the category icon.
- **LANG-ONE-HOME-1** — Home shows one language button, the header globe; it opens the same menu under the header.

### The regression ledger is clean again

Eleven checks were failing on `origin/main`. Nine were checks that had fallen behind deliberate changes (FIND-CLOSE-1,
GENERIC-EX-1, PHOTO-EMPTY-1, TEXT-ANON-1, a longer arrival screen, a respaced language list) and were brought up to date
after confirming the behaviour they guard still holds, live. Two were real:

- **RG-0501** — CARWASH-1's seven car-wash phrases had only Afrikaans; they now read in isiZulu, isiXhosa, Sepedi and
  Sesotho (and the other ten Quick languages).
- **RG-0504** — the profile checklist said "At least one advert" / "Create my advert"; it says listing now (the server
  sends the part as `listing`, and still as `advert` for a page cached before today).

The audit proofs (RG-0840, RG-0871) now run under the app's own Python, where they pass. RG-0194: the relay checkout's
Windows scripts had LF endings on disk; restored to CRLF.

RG-0947.
