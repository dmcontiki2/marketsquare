## 2026-09-13 — Why the draft was invisible, and two faults found doing it

David: *"I don't see it, and truthfully i don't know where to look."* Claude's earlier directions
were wrong because they were read out of `ms.js` instead of looked at in the running app — the
screen is not called "Dashboard" anywhere a user can see.

### The cause: the browser was signed in as somebody else

Read from the live page in David's own Chrome: `localStorage.ms_aa_email` =
**`walkthrough.tutor@trustsquare.co`**. The Seller Hub was faithfully showing that account's
listings, which are none. Fetching `/listings/mine` from inside the same page for
`dmcontiki2@gmail.com` returns **1 row — listing 384, Cleaning — Pretoria East, draft**. Nothing was
wrong with the hand-over or the hub; the session belonged to a walkthrough account.

### Where it actually is, in the words on the screen

**My Hub** (top right) — or **My Space** (bottom bar) — opens **My Seller Hub**, which has the tabs
**My Listings · My Requests · My Profile**. There is no "Dashboard" label in the interface.

### Fault 1 — a false offline banner

The page shows *"You're offline — browsing cached content"* while `navigator.onLine` is **true** and
same-origin fetches return 200. The banner is not telling the truth, and it is the first thing a
seller reads when their listings look empty — it will send people to their router instead of their
account.

### Fault 2 — no service worker is controlling the page

`navigator.serviceWorker.controller` is **null** on the live site. That matches the known push gap
(RUL-122 needs web push; RUL-123 puts the install offer at first publish) — neither can fire while
nothing is registered. It also means the "cached content" the banner claims is not coming from a
service worker at all.

Neither fault was actioned — both are live-app behaviour outside the Quick Listing track.
