# Private property seller → agency/agent contact, and the comms after it
**Status: RULED 14 Sep 2026 as RUL-131 (who pays, and one holder at a time). The build shape below
is still design, not canon.**

David: *"This same message mechanism may be required for property sellers who want to sell their own
properties, but with a slight change. We need to give them a mechanism to contact our local listed
agencies or agents, then to have a similar mechanism for comms between them, obviously considering
their unique requirements?"*

---

## A. The mechanism splits at the PAIR, and the split is already canon

Buzz needs a `buzz_pairs` row before anything can be sent. Everything David is describing lives on
one side or the other of that row:

- **After the pair exists** — the comms between a seller and the agent who took the job — **Buzz
  transfers whole, with no change at all.** One line, the sender's name on it, each side's own
  switch, push then email. Nothing about a property makes that different from a housekeeper telling
  an employer she is running late.
- **Before the pair exists** — a private seller reaching agencies he has never met — **is not a
  buzz, it is an INTRODUCTION**, and the line was drawn in QUICKLIST_DESIGN_NOTES section B:
  *connections the worker brings are free; connections the PLATFORM makes cost a Tuppence.* The
  housekeeper's employer is free because she brought him. An agent the seller has never met is the
  platform's introduction, and the till applies at the normal moment.

So the honest answer to "same mechanism with a slight change" is: **the comms half is not a change
at all, and the contact half is not Buzz — it is the introduction lane the app already has.** That
is a better outcome than a variant, because a variant would mean two consent models to reason about.

## B. What actually is unique here — four things, none of them about messaging

1. **It is one-to-many, not one-to-one.** A seller does not want *an* agent; he wants the local
   agencies to come to him and then picks. Buzz is deliberately a pair. The front of this is a
   REQUEST that lands with several agencies at once — the shape of the demand loop already ratified
   6 Jul 2026 (search-miss → prospect-pool match → anonymity-safe coded invite → priority window),
   pointed the other way round.
2. **Anonymity matters more than anywhere else in the app.** For a housekeeper the thing exchanged
   is a name and a phone number. For a private seller it is *an address*, which is the asset itself
   — an address handed to ten agencies before he has chosen one is the whole value given away for
   nothing, and it is also a safety question about who knows what is in that house. The seller's
   identity and the exact address must stay behind the intro, not in front of it.
3. **The volume asymmetry runs the other way.** A housekeeper buzzes one employer; an agency would
   contact every seller in a suburb. That makes the per-pair switch and the hourly limit load-bearing
   rather than belt-and-braces — they are what stops "Buzz" becoming agency marketing.
4. **Mandates are the seller's business, not ours.** Sole vs open mandate, commission, the mandate
   form itself — an agent and a seller settle that between them. TrustSquare introduces and gets out
   of the way; RG-0238 (no listing surface ever calls a person safe) is the same discipline applied
   to the same temptation.

## C. The one decision that is David's — WHO PAYS

Canon today (CC-001): **payer = the service consumer, the party requesting the introduction.** Read
literally, a private seller asking local agencies for help pays the Tuppence.

The commercial reality points the other way: a seller with a property to sell is a *lead*, and a
lead is worth far more to an agency than a Tuppence is to anyone. A seller charged to ask for help
mostly does not ask, and the supply side of the loop dies before it starts.

**RULED by David, 14 Sep 2026: THE AGENCY PAYS.** A seller with a property to sell is a lead, and
the side that gains the mandate is the side that consumes the service. The seller never pays to ask
for help.

Consequences to carry into the build, none of them settled here:
- It **inverts CC-001's default payer for this lane**, so CC-001's wording needs a carve-out rather
  than a quiet exception — a rule with an unwritten exception is how canon rots.
- The hold model still applies in its own direction: an agency commits on requesting the seller's
  details, burns on delivery, and is released if the seller declines. The seller declining must cost
  the agency nothing, or agencies stop bidding.
- It makes the anonymity requirement (B2) load-bearing rather than nice: what the agency is buying
  is precisely the address and the name, so those cannot be visible before the charge.
- Free for the seller means the abuse direction flips too — a fake listing costs its author nothing
  and costs agencies real Tuppence. Whatever gate answers that is part of this build, not a later
  patch.

## D. One flag worth raising before it gets built, not after

`CHANGE_REGISTER` CC-001 carries the parenthetical *"claims C10–C13 (reverse-auction = lead)"*.
AD-14 queried it in June because no reverse-auction concept existed anywhere in the tree, and David
**closed it as "not important — placed on hold for future design/possible use"**. What he has just
described *is* that shape arriving: a seller broadcasting a want, suppliers responding, the lead
being the thing of value. It is worth knowing that before building, because the launch freeze exists
precisely so that nothing is published before the patent position is settled (see
`project_launch_freeze`). Not a blocker — a "check this while it is still cheap".

## E. What this would cost to build, given what now exists

Small, and mostly not new:
- Buzz: **nothing**. It already takes any two paired people.
- The pair: created the moment an introduction is delivered, instead of from a referral link — one
  extra call at the existing intro-delivery point.
- The one-to-many front: the real work, and the demand loop is the pattern to copy rather than
  invent.


---

## F. RULED 14 Sep 2026 — RUL-131, and what it touches

David: *"I agree, your reasoning is good. Please make it the design decision."*

**The ruling in one line:** the agency pays, one agency holds the seller's lead at a time, the
window ends on the seller's word or on silence, and the queue is ordered by the three scores.

Rejected in the same breath, on David's own instinct: **one free referral then the seller pays.** He
called it an exception-type requirement and he was right — it would put two payers in one lane and
bill the side we most need at the moment they are most engaged. The one-at-a-time rule is not an
exception, because it limits the LEAD rather than the seller: he may ask again whenever he likes,
and only the exclusivity queues.

### What it touches in TRUSTSQUARE (the live app)

| Piece | State |
|---|---|
| Buzz, once an agency is engaged | **Nothing to build.** It already takes any two paired people. |
| The pair | One call at the existing intro-delivery point: delivered intro → `buzz_pairs` row. |
| The seller's request | New — one-to-many in appearance, one-at-a-time in fact. |
| The queue | Existing ranking, RS → TS → LS. Nothing new to compute. |
| The hold | Existing hold model, pointed at the agency; full release on decline or lapse. |
| The window | New — a clock, a seller-side release, and a non-contact trigger. |
| Anonymity | Address and name stay behind the charge; the existing coded-invite pattern is the one to copy. |
| CC-001 | Owes an explicit carve-out for the inverted payer. |

### What it touches in QUICK LISTING

The honest answer is that it touches it **more than it looks**, and in one specific place.

Quick Listing today has exactly one outcome: five taps produce a DRAFT LISTING handed to
`POST /listings` — "one server, one rulebook" as RUL-125(b) puts it. A private seller who wants an
agent is not publishing a listing at all; he is asking for an introduction. So Quick Listing would
gain a **second hand-over target**, and that is an amendment to RUL-125(b) rather than a feature —
it should be ruled as one, not slipped in.

Everything else is free:

- The tap engine already varies its steps per category, so a property seller's four taps (what ·
  where · what kind · price band) need no new machinery — the open-days week simply does not appear
  for property, exactly as it does not today.
- The Buzz panel in the harness already posts the real `/buzz` contract and only needs a pair, which
  the delivered introduction creates. No change.
- The category fits the app's actual shape unusually well: someone with one big thing to sell, no
  website, no idea how, and every reason to want a person rather than a form.

### Still open, and named rather than parked

The window's length, the non-contact trigger's duration, and the abuse gate implied by
free-for-the-seller — though burn-on-delivery already answers most of the last one, since a fake
seller who never accepts costs the agency nothing.


---

## G. AMENDED 14 Sep 2026 — RUL-132, and what it releases

David: *"Let the users benefit at our 'common and simple' expense?"*

Section A above argued that the mechanism splits cleanly at the pair and that this was a *better*
outcome than a variant, because a variant would mean two consent models. **Half of that was right and
half was Claude's tidiness.** The consent point stands and is now an invariant. The rest — insisting
that one flow serve every category — was the user paying for our convenience.

**What is now free to vary, per category:**
- A traveller wanting three B&B quotes gets three; one-holder-at-a-time was a property rule about a
  lead with resale value, and it does not generalise.
- Guides, tour agents and B&Bs can each have the flow their trade actually needs.
- Quick Listing may hand over to more than one target without that breaching "one server, one
  rulebook" — that phrase was always about one rulebook and one database, never one destination.

**What may never vary, in any category:** connected parties only, each side's own switch, consent
never transitive, the sender's name on every buzz and every answer, a decline costing the decliner
nothing, and no per-message-cost channel. And the user sees **one** thing called Buzz — free or
Tuppence is a billing fact behind it, never a second tool to learn.

**The bill, stated plainly:** every extra flow is maintenance on one founder. Worth paying when the
user is genuinely doing something different; not worth paying because a category exists.


---

## H. David's takeaway, 14 Sep 2026 — and what is sharper in it than it first reads

David: *"this surfaces our initial goal of getting the sellers and users to have an easy
interaction, route to contact whilst we still keep the anonymity but now increase the possible
amount of new tuppence introductions."*

**The sharper version of his own point: this is not more volume, it is a second DIRECTION of
origination.** Until now every Tuppence began with somebody SEARCHING — demand side, one shape. A
private seller pulling agencies to him begins with somebody ASKING TO BE FOUND. A private seller was
previously a dead end unless a buyer happened to stumble on him; he is now an origin. Every category
variation RUL-132 releases — guides, tour agents, B&Bs — adds another origin, not another copy.

**Anonymity here is structural, not a promise.** In this lane the seller's identity and address are
literally the thing being purchased, so they cannot leak before the charge without the product
ceasing to exist. That is a stronger guarantee than a policy, and it should be described that way:
not "we keep it anonymous" but "revealing it IS the transaction".

**The honest caveat, because the free lane grows at the same time.** Every user-brought connection is
deliberately free ([[RUL-131]] lineage, QUICKLIST_DESIGN_NOTES B). So more pairs does not
automatically mean more Tuppence — it means more of BOTH, and the net is positive only while paid
origins grow at least as fast as free ones. That is measurable rather than arguable, and David's own
rule applies: to measure is to know.

**A second caveat worth carrying: pairs are a leak as well as an asset.** Once two people can Buzz
each other they have less reason to come back through a paid introduction for their NEXT thing —
which is correct and intended, since their own connection was never ours to sell. The consequence is
that the paid lane must be fed by NEW strangers, so the growth engine is pair CREATION, never
messaging volume. Any dashboard that celebrates buzz counts will be measuring the wrong thing.

**What is already in place to measure it, by accident of the build.** `buzz_pairs` carries `source`
and `created_at` (and `created_by`), so pairs-per-period-split-by-origin — free lane versus platform
introduction — is a query, not a build. That is the number that says whether the flywheel is turning.
