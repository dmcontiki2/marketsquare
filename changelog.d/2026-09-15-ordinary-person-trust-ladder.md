## RUL-136 - a route up the ladder for somebody with no certificates

David, looking at the AI plan the Trust Score coach had just written him: *"Even the request
to add degrees, SACE, PCC, DBS... all of these are some specialists type credentials and not
related to a normal person?"* Then, on the fix: *"Please add that, the more we allow the more
invested a user will become. A previous employer is a good addition."*

He was right about the cause and it was not the AI. Of the universal signals every seller
shares, exactly two could be earned by an ordinary person - an ID (15) and a complete profile
(5). The other three were referrals, which the app has never tracked and computes `missing`
unconditionally, so they could never pay. Everything else on the ladder was a professional
credential. A housekeeper could reach 60 and no further, and the coach, sorting by points,
told her to get a degree.

**Three new universal signals.** A photo of the person (5), years of experience stated (3),
and a previous employer confirming them (12). The universal cap stays 30 - this inflates
nobody; it gives a person with no certificates a second route to the same 30 that an ID plus
referrals fills for someone else.

**The employer confirmation is worth 12 because it is third-party.** It is the only outside
evidence an ordinary person can get without buying a certificate. The seller sends her own
link; the person she worked for opens `/confirm/<token>`, taps Yes, and is done - no account,
no sign-up, nothing to install. The direction is the protection: a stranger cannot declare
himself her employer, because he never receives a link. The confirmer is never named, stored
or published - only that a confirmation happened. It cannot stack: the signal is "somebody
outside vouched for you", which is true once.

**Every new signal ends in a button.** The years-of-experience step asks for the number in
place, inside the plan. The employer step mints the link and hands it over with a WhatsApp
button, because that is how this actually gets sent here. The photo step opens the same file
picker that already backs the Me tab avatar, so the photo lands where the rest of the app
reads it from.

**The coach no longer offers referrals.** Asking somebody to do a thing that will not move
their score is worse than not asking. They keep their seats on the ladder and are simply not
advertised until they can be earned.

**Also fixed:** the photo used to be a hidden precondition of *Complete profile*, so a seller
could keep failing that 5 without ever being told a photo was the missing piece. It is now its
own signal, which says so.

Ledger: RG-0374 (locked). RG-0373's document-step leg broadened rather than left inert.
