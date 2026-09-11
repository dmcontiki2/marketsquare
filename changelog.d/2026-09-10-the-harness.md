## 2026-09-10 — The Harness: voice is out, the front door is one tap-only frame for every category

David tested the Home Help conversational prototype and ruled against the whole interaction model:
*"the chat sounds very bad — about a 2 against Siri... the response is also bad — it does not accept
and goes into a loop from which i could not recover... there was no way to go back or restart...
we don't want any talking."* And the framing that matters: *"Our success live and die with this
first screen, for all categories and products or services."*

**Built: `genie/HARNESS.html`** — one engine, driven by per-category data, serving all eight
categories in both directions. Design only; nothing wired, nothing deployed.

**The click budget is the spec (RUL-117), and it is met exactly:**
- **5 taps** from the door to a **draft advert** — a prototype the seller then finishes.
- **4 taps** to a shelf of adverts, then **3 narrowing taps**: 18 → 12 → 8 → **5**.

**What changed on the door:** kept the green wash, the round photo, the rounded buttons. Removed the
tap instruction and the bottom explanation — no instructional text at all. The category is chosen by
**swiping** left and right. Two rounded buttons, worded per category (*Find help / Get work*,
*Find a car / Sell a car*).

**Back and Restart on every screen, always.** The unrecoverable loop was the defect that caused the
ruling, so it is now structurally impossible: Back steps one pick backwards, Restart returns to the
door, and both are visible on every screen after the door.

**The photos are the feedback.** Every step is photo tiles drawn from `assets/super/`; the picture
set changes with each tap and the chosen tiles stack as a trail of thumbnails across the top. That
trail is how the user keeps track of where they are — no breadcrumbs, no text.

**Narrowing ranks, it never lies.** A price answer re-ranks by price, anything else by rating, and
the count line says "best match". A shelf never shows R400 under a heading that says under R300.

**Voice is gone** — zero speech APIs in the file, asserted in the test. The conversational BOTs
(Collector, Sell It, Home Help) are superseded as an interaction model and survive as the record of
the employer-link and vouching-gate design (RUL-115), which David endorsed and which still stands.

Verified in a rendered mobile browser: 5 taps to draft, 4+3 to five, all eight categories swipe,
Back and Restart both return correctly, console clean.
