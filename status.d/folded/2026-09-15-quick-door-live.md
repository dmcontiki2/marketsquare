## 2026-09-15 — The Quick door is on the front page and no longer a dry run

David: *"i think we need the Quick Listing as an option on the First page, it is currently the
path of least resistance to list anything."* He is describing acquisition, not convenience —
somebody who meets the app through four taps has already succeeded at it once.

**The slot was free and had been for weeks.** The hero body has sat empty since LM-19 took the
stats row out, so the door needed no layout argument with anything.

**The part that was actually missing was the other end.** `quick.html` went live with QUICK-TILE-1
on 14 Sep but its hand-over was still a prototype stub printing the JSON it *would* have posted.
A door on the home page pointing at that would have been the worst kind of live — visible,
tried, and ending in nothing. It now posts to the same `/listings` every other listing goes
through: one server, one rulebook, RUL-125(b) intact.

**Deferred on purpose:** the identity note at the door still wants `GET /quick/me` off the
`ts_user` cookie (RUL-125(a)). That endpoint does not exist, so the door reads the app's own
signed-in marker on the same origin instead. Same answer, no new surface; when `/quick/me`
is built it replaces four lines.

Rendered-verified at 400px before the deploy, and both publish paths walked headless.
This release also carries the LANDSCAPE-1 and referral-lane work that was waiting on a deploy.
