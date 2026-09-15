## QUICK-DOOR-1 PARKED — the in-app door is withdrawn, quick.html stays live

David, testing it at work the same day it went up: *"the quick listing link in the app does work,
but going into it means you cant get back into the trustsquare app... i want to rather remove
that link from inside trustsquare to the way it was. For now at least."*

**Removed, and he is right.** `quick.html` is a separate page with its own Back and Restart
inside the flow, but nothing that leaves it — so the door was one-way, and a one-way door out of
the app is worse than no door.

**Only the door went.** `quick.html` is still deployed, still writes real drafts through
QUICK-LIVE-1, and still hands back with the address and the link home (QUICK-HANDBACK-1) — the
installable Quick tile and the emailed copy are untouched.

**Putting it back is one line.** The `.quick-door` rules stay in `ms.css`, unused, and the exact
markup sits commented in the hero body where it was. What it needs first is a way out from
*inside* the flow, not a better label.
