## 2026-09-15 — Two numbers for one Trust Score: the hub had its own calculator

**David:** "i tried to update my Trust Score with edit and AI and was unsuccessful. I added it
eventually manual and saved it but the score stayed on 27%. It is not even sitting on 40% which is the
normal starting baseline?" Both halves were right, and the score half had a single cause.

**PROBED, same seller, same minute, before any change:**

| surface | walkthrough.tutor | dmcontiki2 |
|---|---|---|
| `GET /users/{email}/trust` (My Space hub) | **27** | 40 |
| `GET /trust-score/breakdown` (the ladder) | **62** | 50 |

The hub published its OWN six-signal sum as the headline. That sum has no 40-point base, which is why it
sat under it; and it reads nothing from `user_credentials`, which is why a credential he added could
never move it. `_trust_math` is documented in the file as "THE ONLY PLACE THIS FORMULA MAY LIVE" — this
surface was a second place, and that is the whole bug.

**ONE-SCORE-1.** The hub now builds its answer from the canonical breakdown: the headline is the ladder's
score, and the list under it is the ladder's own items with the base as the first visible row. EVIDENCE-TRUE
keeps the headline, so the agreement is proven on every call rather than assumed. Verified in the rendered
app, not just the API: the hub reads **62**, "Good standing", with "✓ Established base — every seller starts
here +40" and "◐ Government-issued ID verified +12 · 3 pending" beneath it, and the browser's cached 27
healed itself on load. RG-0372 LOCKED over all three properties, and it is a CLASS entry — any surface that
publishes a trust number must read the ladder's result.

**A trap found on the way, left in place and documented:** a breakdown item's `awarded_points` carries the
signal's FACE VALUE even when its status is `missing` — dmcontiki2's universal group reads earned=0 while
every item in it claims 15/5/5/3/2. A contribution must be read from the item's STATUS. The first version
of this fix trusted that field and published a list that summed to 100 against a score of 50.

**The AI half — cause found, one fact still missing.** The live log shows `POST /advert-agent/coach` returning
**401 four times** in his session. That endpoint raises exactly one 401, and only when the email on the form
has no row in `users`; the guidance endpoint answers 200 for every category tried, on his own signed-in
session, so the AI itself is healthy. COACH-SAYS-WHICH-1: the refusal now names the address it did not
recognise instead of a bare "Unrecognised account", because the old wording left the person with nothing to
act on. Which address was on that screen is the one thing not on record — the message will say it next time.

**Also:** the session counter had fallen behind the day's fragments (RG-0154 red) — re-derived to session 199.
