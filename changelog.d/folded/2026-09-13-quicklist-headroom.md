## 2026-09-13 — A category that asks for more is headroom, not a bad score

David, 13 Sep 2026: *"Could we for cars, being a type limitation, not say that x amount of score
points can be added for model, mileage or transmission?"*

Yes, and the arithmetic did not have to move to do it. `lsOf()` is still a faithful mirror of
`_import_quality_score()`, so the number the seller reads is still the number the server will
compute on hand-over. What changed is what she is told about it.

- The LS tile now carries **"+69 available"** under the number, so the score is read as a position
  on a climb rather than a mark out of ten.
- The checklist is headed **"Each of these adds to your listing score"**, and Cars now reads
  *+8 add the model · +8 add the mileage · +8 add the transmission* instead of three silent gaps.
- Categories that require four or more fields (Cars, Property) carry one line explaining why they
  start lower: *"Cars listings ask for more than most — 5 details rather than one — so they start
  lower and climb further. Every one you add below is worth points; none of them is a penalty for
  what the quick form did not ask."*

Verified rendered: Cars 31 with +69 available and the three fields named; Housekeeping 60 with +40
available and no note (it requires no structured fields, so there is nothing to explain). All eight
categories still hold 5 taps to a draft and 4+3 to five items, zero duplicates, zero page errors.

**The click budget was not touched.** Asking for model, mileage and transmission inside the quick
form would break RUL-117(c). They stay where they belong — added in TrustSquare, where the score
rises as they land.
