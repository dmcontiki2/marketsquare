## 2026-09-15 — The trust score stops moving between screens

David watched his own score read 80, then 57, then 75 across three screens in one sitting. It was
not three bugs; it was one surface answering a question it had not been asked.

**What was actually wrong.** The buyer-facing evidence panel built its own picture of a seller —
its own SQL for identity and track record, narrower than the scorer's — and then wrote that
picture back over the stored score and over every listing that seller owns. Two honest guards were
already watching this exact area and neither could see it, because the panel's list summed to the
panel's own headline and its arithmetic used the shared formula. The thing that differed was the
evidence itself.

**The cure is structural, not another checker.** There is now one evidence builder. A surface that
wants a trust number asks for it there or it does not get one, and a third guard fails the deploy
if that ever stops being true.

**What he should expect to see.** The same seller under the same category now reads the same number
everywhere. A number that still differs between two screens means the two screens are scoped to
different categories — which is real, because category credentials differ per advert — and the
panel now returns its `category_key` so that is answerable rather than mysterious.

**Still his to decide:** whether the seller CV should say out loud which category it is scoring,
and whether Housekeeping becomes a real category or Quick maps it to Services on the way out.
