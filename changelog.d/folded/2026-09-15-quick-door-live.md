## QUICK-DOOR-1 / QUICK-LIVE-1 — Quick is on the first page, and it now writes a real draft

David: *"i think we need the Quick Listing as an option on the First page, it is currently the
path of least resistance to list anything, and if people gets introduced by it and become
familiar with it then they very well prefer to use it?"* Then: *"Please add it there and make
it live."*

**Where it went: the hero's own empty body.** `<div class="hero-body">` had been empty since the
LM-19 stats row came out, so the door drops in above the Categories grid without moving a pixel
of anything below it. Violet `#7C3AED` — the Quick tile's colour under QUICK-TILE-1, and a colour
no category tile uses, so the door cannot be mistaken for a seventh category. It hides in demo
mode with the rest of the seller surface.

**Both directions on the label,** because the spreader finds as well as lists: *List anything in
5 taps / or find what you want, just as fast*.

**"Live" was the bigger half.** `quick.html` has been deployed since QUICK-TILE-1 but every
Publish ended in `DRY RUN — no server is wired to this prototype`, so a front-page door would
have been a dead end. `HANDOVER` now fills itself on the app's own origin: the URL from
`location.origin`, the key from the one ms.js has shipped to every browser since MAINT-B1b (now
mirrored to `localStorage` so there is no second copy of it to forget on a rotation), and the
seller's email from the app's signed-in marker — read, never written, so this door can never
fake a sign-in the app did not do.

**The demo switch is gone on the live origin,** which is what the note above it always said would
happen: *"There is no switch and no sign-in screen; the door simply already knows."* A signed-in
member is not re-asked; a stranger still gets the one ask at the end, and that email now reaches
`seller_email` instead of being dropped — a draft with no seller is an orphan.

**A file:// copy opened from an emailed Downloads folder still runs dry,** exactly as before.
That was the one behaviour this could not lose.

Verified headless before shipping, both paths: member → `POST /listings` → *Draft #… is in
TrustSquare*; stranger → one ask → same, with his own address on it. 0 JS errors.
