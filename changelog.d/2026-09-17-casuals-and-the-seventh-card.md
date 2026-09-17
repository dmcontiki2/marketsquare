## CASUALS-IS-SERVICES-1 · the seventh card on every step

David: *"I have been thinking on the housekeeper, it is not a new category, it is part of casual
services. Please make it everywhere part of services."* And: *"we do need a written seventh card
for text, or a sentence... a text entry for costs card everywhere for a different input... what
are you hunting can also have a separate card for a text option."*

**Housekeeping is a doorway, not a category.** The card stays where she can find it — a
housekeeper does not go looking for "Services" — but what the app WRITES is now
`category: Services`, `service_class: Casuals`. That is also the key the Trust Score resolves
under (`Services-Casuals`), so an advert made here is scored like every other service.

**The same correction for Local Market,** whose DB category has always been `local_market` while
Quick wrote "Local Market". A door's label and the platform's category are two different things,
and only one of them travels.

**The lookup bug underneath it.** `REQ` and `FIELD_FROM` are keyed by the category KEY but were
looked up by its lowercased NAME. That matched for seven of the eight by luck and missed
`homehelp` entirely — so the work she picked never travelled (the app re-asked for the service
type, which is what David hit), and the listing score was computed against no required fields at
all. Looked up by key now, with a `homehelp` entry.

**The seventh card was already built.** `drawFree()` has been in this file all along — a typed
line that commits exactly like a tap, so the trail, the draft and the hand-over need to know
nothing about it. It was switched on for WHERE and nowhere else, which left six tiles as the whole
world on every other question. It is now on **every step in both directions** — what you do, what
you are hunting, the price, all of them — with a hint written for each. The week is the one
exception: a calendar is not a list of words.

**And it takes a sentence now,** not just a name: 40 characters to 80, counter included. Whatever
is typed is what people see — including in the advert title, which is the existing rule, not a
new one.

Verified headless end to end: the free card on the "what" step, a typed price on the cost step,
and the hand-over carrying `Services` / `Casuals` / the typed service type. 0 JS errors.
Both `quick.html` and `genie/HARNESS.html` changed together — they are one app in two files.
