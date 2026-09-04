## 2026-09-04 — The onboarding PLAN, with the arithmetic that decides it

David asked whether there is a follow-up plan. There is now, and it is built on measured
numbers rather than intent: `MarketSquare/ONBOARDING_PLAN.md`, with a Professional Navy
Word version for David and a colour-coded board in Visuals.

**The decisive finding is an arithmetic one.** 461 emailed, 155 opened (34%), 48 clicked
(10%), 0 published — and the 0 is uninformative, because every one of those 48 clicks met
a locked door. Click→publish has never been observed. Working backwards from 20
publishers at the observed 10% click rate: a 20% publish rate needs ~1,000 emails, 10%
needs ~2,000, 5% needs ~3,800, and 2% needs ~9,600. We hold 2,860 unemailed prospects
(~2,737 organisations). **So we have roughly ONE PASS through the list, and 20 is
reachable only if click→publish lands at about 5% or better.** Sending capacity is not
the constraint (~4,000 sends available before the deadline); supply and conversion are.

Hence the shape of the plan: **measure before spending.** Phase 1 (to 11 Sep) treats the
130 apology recipients as the experiment and adds no volume — the webhook resolves opens
and clicks by recipient, so their behaviour is captured even though that lane writes no
'sent' row (denominator is 130, from sent_log.json). Phase 2 (to 18 Sep) fixes whatever
drop-off Phase 1 exposes, as a class. Phase 3 (to 24 Oct) spends the list only if the
measured rate justifies it. A reserve week converts whoever is mid-flow.

**A decision gate is written in, at the END of Phase 1 rather than the end of October:**
under 2,000 implied emails, proceed; 2,000–3,800, proceed but line up more supply now;
over 3,800, stop and say plainly that 20 is not reachable with this list. Bad news in
mid-September is useful; bad news on 31 October is not.

**One correction to yesterday's reading, on the record.** The 4 Sep wave's "no sendable
prospects" on nine lanes was reported here as a supply drought. It was not: the AGENCY
category was dry in those cities while the list still holds 1,509 teachers/trainers and
159 tutors untouched. Rotate the category before concluding the list is empty. The plan
carries that correction so the next session does not act on the wrong constraint.
