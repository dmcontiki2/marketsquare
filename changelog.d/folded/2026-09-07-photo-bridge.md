## 7 Sep 2026 — PHOTO-BRIDGE-1: the way back from a photoless listing (RG-0338 LOCKED)

David: *"Yes, let them list without a photo first, there should be no resistance at all, mistakes can
be fixed afterwards and so can photos be added. But we need to be sure that they can modify, because
Maroushka could not and we fixed that a few times. She still haven't tried again due to frustration.
Please design it and make it live, we don't want the new prospects to fail again."*

**REUSE-BEFORE-RECREATE CAUGHT THE FIRST HALF: the photo gate was ALREADY OPEN.** INVITE-GATE-1 shipped
earlier the same day (commits c4d7da4 / 1ebcfff) and is LIVE — PROBED on `/static/ms.js`: `INVITE-GATE-1`
present, "No photo handy? Continue and add one later" present, the old disabled-button gate gone. Then
WALKED it in a browser with `src=probe-ledger`: the invited path reaches **Step 2 of 6 · Tutoring
Details with zero photos**, suburb pre-filled from the invite. Building it again would have been the
exact waste CLAUDE.md warns about.

**WHAT WAS ACTUALLY MISSING — the return journey.** The success screen congratulated the seller
("X is now live on TrustSquare") and stopped. No mention that photos may be added, no Listing Rating,
no route to the edit screen. A door you may walk through and never come back to is half a fix, and it
is precisely how Maroushka was lost: the edit machinery worked (RG-0120 LOCKED, 20 Aug, her exact
fault) but she gave up looking for it.

**BUILT — PHOTO-BRIDGE-1:**
- `marketsquare.html` `#sob-photo-nudge` — a green card on the success screen: *"Add a photo when you
  have one. Your listing is live without one — that is fine. Listings with photos get roughly 3x more
  buyer contact, and you can add, change or remove them any time."* with **Add photos now →** and a
  **Later** dismiss. Hidden by default.
- `ms.js` `sobGoLive()` — reveals it ONLY when the listing genuinely has no photos, and wires the
  button straight to `openEditListing(id)` so the seller never hunts. Emits `published_without_photo`
  and `photo_bridge_open` so the funnel can measure how often this path is used.
- **Fails closed on purpose:** the whole block is in a try/catch (a nudge may never break a successful
  publish) and a seller who DID upload is never nagged.

**LEDGER: RG-0338 LOCKED**, asserting the class — *any gate we remove from the front of a flow must
leave a route back, or we have swapped a wall the seller can see for one they cannot.* Six legs
checked; run in isolation: green.

**A REAL MISTAKE MADE AND CAUGHT IN THE SAME RUN:** the first write to `marketsquare.html` converted
all **4,485 CRLF line endings to LF** — a whole-file diff masquerading as a 14-line change, and the
file SHRANK by 2,723 bytes while gaining content. Caught by comparing sizes against the backup before
any deploy. Restored from the `.bak` and redone with `newline=''` on BOTH read and write. Final
`git diff --stat`: **46 insertions, 0 deletions.** Note for future sessions: `marketsquare.html` is
CRLF, `ms.js` is LF — a Python rewrite must preserve each file's own endings.

**Honest limit:** the browser walk used `src=probe-ledger`, which RG-0293(b) EXCLUDES from the funnel's
default view by design. So this does **not** satisfy RG-0326, which correctly still waits for a real
invited person to reach a step beyond photos. The instrument is watching; nobody has to remember to look.
