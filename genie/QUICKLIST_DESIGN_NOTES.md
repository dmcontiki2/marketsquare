# Quick Listing app — notes for the design discussion
**Status: NOTHING RULED. These are notes to argue with on 12 Sep evening, not decisions.**
David: *"i do have a few requirements lined up in my mind but want to discuss them with you before we commit them."*

## David's six, as given

1. Minimalistic
2. Photo rich
3. Fast lure to get referrals for the real app (housekeeper gets house owner to load link)
4. A first Advert Card view before the listing goes to TrustSquare for the EULA and the real listing
5. The user sees what their location allows, plus adventures and the things we want them to see — otherwise local and auto-viewed
6. **A very simple communication link to the hirer** — to be contacted, booked, asked simple questions, with phone buzzes and alarms

---

## A. The category is much wider than housekeeping

David, 12 Sep: *"we have only pursued the one type of service, there are Porters, hoteliers, waiters,
grillers, chauffeurs, body guards, drivers (informal), chefs, child carer's, old age carer's, dog
walkers, etc."*

**What unites them — and it is not "services".** These are people whose *labour is the product*.
Not a company with a trade certificate; a person with a day free. They share four things:

- paid by the **day, shift or hour**, very often cash
- hired into a **private or trusted space** — your home, your car, your children, your parents, your event
- found today almost entirely by **word of mouth**: *"who do you use?"*
- almost none has a CV, a website or any online presence

**So the thing being listed is TIME, not an item.** That is why the housekeeping flow generalises
without change: what · where · **when** · rate. The weekly-openings grid is the product for the whole
class, not a housekeeping feature.

**Naming — David's call.** "Services" is wrong (that is trades and companies). Candidates: *People*,
*Hands*, *Hire a person*, *Day work*. It wants to sound like a person, not a category.

### Proof requirement — SETTLED by David, 12 Sep. One mechanism, no special cases.

Claude proposed a risk tier that would require a **police clearance** for child and elder care.
**David ruled against it, and was right on canon Claude should have checked first:**

*"we use the Quick Listing app to get listers, it does not clear them from still adhering to our
three scores, that is where the other type of workers will be judged correctly for the viewers to
determine if they want to trust them with an Intro request."*

Why his answer is the better one:

- **RG-0238 already forbids Claude's version.** *No listing surface ever calls a PERSON safe — we
  publish dated, sourced FACTS about a credential, never a conclusion about someone.* Mandating a
  clearance makes the platform the vetter, which is that line crossed and liability imported.
- **It would kill the category before it started.** Clearances cost money and take weeks in SA.
- **One mechanism stays meaningful.** A special gate per category is what makes a score mushy.

The three scores do the work. A carer with an ID check and two confirmed employers carries a high
TS; one without carries a low TS; **the viewer decides** whether to send an Intro request.

**Claude's one refinement inside the ruling, not against it:** the same number carries different
consequence for a dog walker and a child carer. Not a gate — a *fact*. At the moment someone asks
for an introduction in a high-exposure category, state plainly what has and has not been checked:
*"Confirmed by two employers since 2023. No criminal record check — TrustSquare does not run them."*
A fact, never a conclusion; gates nothing; costs nothing.

### And this settles question 5 without it being asked

*"we use the Quick Listing app to get listers, it does not clear them from still adhering to our
three scores"* — **Quick List is a lighter FRONT DOOR into the same standards, not a parallel
system.** No duplicate scoring, no second rulebook, no separate trust model. Just a faster way in.

---

## B. Number 6 — the communication link. SMALLER than Claude first wrote it.

**Claude's first framing was wrong and David corrected it.** The note said an open channel would let
people dodge the Tuppence. David, 12 Sep: *"the users already know the hirers they are onboarding,
there we don't expect any tuppence, we are actually using their already known connection to become a
real app user. therefore we lose nothing."*

Correct. **There is no introduction to sell here.** Charging to introduce a housekeeper to her own
employer would be absurd, and that relationship never earned us anything anyway. Converting both
into app users is pure gain.

### The rule, in one line

> **Connections the WORKER brings are free. Connections the PLATFORM makes cost a Tuppence.**

It is hard to abuse because of the **direction**. She sends the link; a stranger cannot declare
himself her employer to get free contact. The free lane only ever opens the way the worker opens it.
The shelf — a hirer finding someone they have never met — is untouched and still a Tuppence.

The hirer joining costs nothing, ever. They pay only when they later use the app for something that
genuinely costs Tuppence: an introduction to someone they do not know.

### So what number 6 actually needs — and it is much less

No anonymous relay in the Quick List app. These two already have each other's numbers. What is
needed is only:

- **notifications that actually arrive** — WhatsApp is the real channel in South Africa, not email;
  push through the installed app is free but **no service worker is registered today**, so there is
  no push at all yet; SMS as last resort
- **one-tap replies** — *Yes / No / Ask me later*. Not a form. Typing on a cheap phone with bad data
  is where these loops die
- **graceful degrading** — a worker with no data for a day must not lose the job

The anonymous relay still matters, but LATER and ELSEWHERE: in the real app, for stranger
introductions. It is not a Quick List problem.

### The colleague question — SETTLED by David, 12 Sep (mechanism still to confirm)

David: *"That is not designed to be free, we wont regulate it to death though, but the referral only
works from worker to hirer and not from worker to other worker. We could maybe prevent a second
referral of the same task to a hirer to prevent this?"*

**Settled: worker to hirer only. Never worker to worker.** Beyond anti-gaming, this protects the
Trust Score itself: the employer link is worth something *because the vouching comes from outside the
worker's own side of the market*. A worker confirming a worker is not evidence, it is a reference
circle, and allowing it would hollow out the trust half quietly.

**Claude's amendment to the mechanism — "same task" leaves a hole.** Thandi could not refer Grace
the housekeeper to Mrs van Wyk, but could refer Joseph the gardener, who is equally a stranger to
Mrs van Wyk. In this workforce the cross-trade referral is the *most* common one there is
("my husband does gardens", "my cousin drives"). Proposed instead, one rule rather than two:

> **The free lane is the PAIR, not the person.** One worker, one hirer, created by the worker's own
> link. Anyone else arriving at that hirer — any trade — is an introduction.

**And it needs no policing, which is what David asked for.** Do not PREVENT the second referral —
simply do not EXEMPT it. Thandi can still tell Mrs van Wyk about Joseph; it just is not free. It
lands as an ordinary introduction and the till applies at the normal moment, when the hirer wants
the contact details. Nothing blocked, nobody accused, no second rule to enforce. The default is
already a Tuppence; the free lane is the exception, and the exception is defined once.

**SETTLED, David 12 Sep: NO referral rewards.** *"No rewards for these type of referrals. Simply for
design complexity and customer complaints."* Reward schemes breed disputes — *"I referred him, where
is my money?"* — and every one of those is a support ticket and a rule to adjudicate. The free lane
is already the reward: her own hirer, onboarded at no cost.

## C. Number 3 gets much stronger with the wider list — and this is the flywheel

Every one of these workers has an employer who can vouch. Widen the list and look at **who those
employers are**: a porter's is a hotel. A chauffeur's is a company. A child carer's is a family. A
griller's is whoever ran the event.

**So every worker who registers drags in a hirer — and every hirer needs other categories.**
The hotel that confirms a porter also hires waiters, cleaners and drivers. That is not a referral
trickle, it compounds, and it is the only one of the six requirements that does.

**Implication for the referral link:** it should not say "confirm Thandi". It should confirm her
*and* show the confirmer, in one line, that the same place can find them the other four people they
already hire. That is the single highest-leverage screen in the whole product.

---

## D. Questions I want answered tonight, not assumed

1. What is this category called?
3. WhatsApp notifications — worth the per-conversation cost, or push-and-SMS only to start?
(Question 5 — separate app or front door — ANSWERED above: a front door into the same standards.)
