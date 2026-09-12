## 2026-09-12 — RUL-121: a lister sees all three of their own scores, with coaching

David, correcting an over-strict line Claude wrote into RUL-120: *"a lister should be able to see all
three of their own scores and even be told how to use it to improve their viewable listings, the purpose
is not to keep it a secret but not to 1. clutter a viewing, 2. to prevent obvious tuning for the purpose
of views rather than quality."*

**Claude had it wrong.** RUL-120 said the composite RS is never displayed to anyone, including in a
seller's own dashboard. That treated the score as a secret. It is not a secret — it is kept off the
public card for two plain reasons, and neither is concealment:

1. **It would clutter a viewing.** The shelf is a glance, not a report card.
2. **It would invite tuning for position** rather than for the two things that actually matter.

**So: on their own listing a seller sees RS, TS and LS — all three — and is told how to raise them.**
RS may be named and explained openly, in help and in onboarding, because a seller who understands that
ranking is half trust and half listing quality is being pushed toward exactly what we want raised. What
is withheld from a public card is a number on a tile, not the method.

**The coaching already exists.** `_import_quality_score()` already returns what is missing, sorted
biggest-win-first — the same list the Sell It BOT read out. It needs surfacing on the seller's own
listing, not building.

RUL-120's anti-gaming intent stands for the public surface, and its ruling that the non-monotonic star
column is correct and must not be 'fixed' stands in full.
