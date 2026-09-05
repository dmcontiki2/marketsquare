## 2026-09-05 — AUDIENCE-LANE-1: David was right, the model was wrong, and it was wrong in its strongest engine

David, after reading v1.6: *"you mentioned how we will be able to get a wider audience going the
teachers, clubs etc. route; but the simulation do not show this to be true?"* And the example
that pins it: *"teachers that want to make some part time money tutoring... will spread the app
to their current pupils, accelerating the spread faster and onboard much more pupil users and
their parents as well."*

**Probed before agreeing, and the probe agreed with him.**

The model already had the mechanism — `custPer` (22 contacts an ordinary seller can bring) ×
`custJoin` (9% of them join). It is the strongest engine in the whole simulation: switch it off
and week-52 sellers collapse from **131,558 to 35,910**. Roughly two thirds of the entire curve
is sellers bringing their own people.

But the association lanes added that morning deposited their sellers into the same
undifferentiated `E` pool as everyone else, so the audience term read the **pool average**. A
teacher who came in through a union was bringing **2.0 people** — the same as somebody selling a
second-hand bicycle. Nothing was missing from the code. There was a number there; it was just
the wrong one, and that is precisely why nobody had noticed.

### The fix

`assocAud` and `assocJoin`, and a per-city pool (`AE`) that the club, federation and union lanes
feed. At activation the week's first-listers are split by origin, and association-origin sellers
draw their audience with their own parameters.

- **`assocAud` — 90 (20–350).** A part-time tutor teaches 15–60 pupils and **every pupil comes
  with a parent who is the one who actually pays**, so the register is roughly double the class.
  A club is the same shape at organisation scale.
- **`assocJoin` — 0.25 (0.04–0.60).** Three things are true here and nowhere else: the ask comes
  from someone you already know and pay and will see next week; it is transactional rather than
  promotional (if the tutor takes bookings through the app, joining is how you get your lesson);
  and the person joining is a **buyer**, which carries none of the model's seller-side friction.

Clubs are deliberately under-counted: a club adds `clubSeats` listings to the seller pool but
only **one** audience-bearing unit, because a club has one membership, not one per listing.
Under-claiming is the safe direction for a guessed number.

### What it changes, same seed, measured

| | week 8 (the goal week) | week 52 ever-listed | week 52 buyers |
|---|---|---|---|
| no association lanes | 43 self-published | 137,407 | 679,043 |
| clubs + federations + union | **87** | **199,530** | **1,134,559** |

At the human-verified click rate — the pessimistic reading — the goal week goes from **1** to
**7**. Off only **108** association sellers. And those buyers then feed the buyer-to-seller
crossover already in the model, which is the second round nobody plans for.

### The honest limit, asserted rather than buried

Both new parameters are **guesses**. Swing them across their stated range and one year's sellers
move between **160,232 and 264,363** — a hundred thousand sellers on two untested numbers. So
`RG-0292` is OPEN: measure what an association seller actually brings. Two ordinary things block
it — there is no referred-by column in the schema, and no association seller exists yet because
no club letter has been sent. Neither is a decision for David.

### Two more honesty changes to the screen itself

- **WHAT-IS-WORKING-1.** The diagnostic strip only ever showed the three most SEVERE items, so a
  mechanism that was *working* could never appear on it — which is how the biggest thing the
  association lane does stayed invisible on a screen built to explain the model. The constraint
  list is unchanged; a working item now shows beside it, and mechanism items win that slot ahead
  of level reports.
- **SHAPE-NOT-FORECAST-1.** Past 20,000 sellers the strip now says so out loud: 64 of the model's
  90 parameters are stated guesses, the compounding terms multiply, and by that point the output
  is the product of a dozen assumptions. The model is for COMPARING lanes at the same settings.
  The first year, where numbers can still be checked against something real, is where it earns
  its keep.

Model **v1.7**; dashboard pin moved with it and the +1 page card now carries the correction and
the 22-versus-2 line. Ledger: **RG-0291 LOCKED** (association lanes can never silently fall back
to the average audience again), **RG-0292 OPEN**. The dup guard did its job on the way in — a
concurrent session had taken RG-0289/0290, so these moved rather than colliding.

The number is still **0**.
