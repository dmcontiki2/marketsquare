## 2026-09-15 — David walked the Quick hand-over end to end; four findings, one removal

**The door came off, and he was right about why.** *"going into it means you cant get back into
the trustsquare app."* `quick.html` has Back and Restart inside its own flow but nothing that
leaves it, so the in-app link was one-way. Parked, not deleted: the markup sits commented in the
hero body and the styles stay in `ms.css`. It goes back when the flow has a way out of itself,
not when it has a better label.

**The hand-over itself held up.** Publish → "Handed over" → the draft is in the app, editable,
and after adding a UNESCO link it published. So the seam works; everything below is about what
travels across it.

### Why it re-asked for the service type
He chose **Childminding**, which lives under Quick's **Housekeeping** category. Two things stack:
`FIELD_FROM` in `quick.html` has entries for `property`, `cars`, `tutors` and `services` only, and
it is looked up by the category's lowercased NAME — so `housekeeping` misses, `from` comes back
empty, and **none** of the category fields (`service_type` among them) are sent at all. Underneath
that, "Housekeeping" does not exist anywhere in `ms.js` or `bea_main.py` — seven of Quick's eight
categories match the app exactly; that one has no counterpart, which is also why the app files the
listing under Services.

### Why the numbers disagree
**60 is not a trust score.** Quick's draft screen shows a LISTING score — how complete the advert
is — and says so on the same line: *"trust not opened yet"*. Comparing it to 80 compares two
different things.

**80 vs 57 vs 75 is the real one.** Both screens use `_trust_math`, the canonical formula, but it
is CATEGORY-SCOPED: the dashboard panel calls `/trust-score/breakdown?email=&category=<whatever
the dashboard is scoped to>`, while the public seller CV calls `/sellers/credentials/<listing_id>`
and scores against THAT listing's category. Different category in, different number out. And the
CV endpoint does not just display its answer — it writes it back to `users.trust_score` and to
every one of that seller's listings (the JNR-FIX-2 self-heal). So with an unresolvable category
the two views disagree, and whichever screen was opened last wins the stored value.

**The refresh before it appeared** is consistent with the same write-back landing after the page
had already rendered; not yet proven, and not chased today.

### Reserved for David
Housekeeping/Casuals is his lane and his naming: either it becomes a real category in the app, or
Quick maps it to Services on the way out. Nothing is patched until he says which — a mapping
invented here would be a third vocabulary, not a fix.

Buzz untested — he ran out of time at work, not a result.
