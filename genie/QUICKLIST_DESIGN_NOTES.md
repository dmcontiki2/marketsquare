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

### The one thing that must NOT be uniform: how much proof is required

A dog walker and a child carer are not the same trust problem, and treating them alike is either
insulting to one or dangerous to the other. **The evidence should scale with who is exposed:**

| Exposure | Examples | Proposed floor |
|---|---|---|
| Low | dog walker, porter, waiter, griller | one employer confirmation |
| Medium | housekeeper, chef, driver, chauffeur | employer confirmation + ID |
| High — a vulnerable person, alone | child carer, old-age carer, bodyguard | ID + employer confirmation + the platform states plainly what it has NOT checked |

**The honest bit we must not dodge:** TrustSquare does not run criminal record checks. For a child
carer or an elder carer that absence has to be said out loud on the listing, not buried. Whether to
require a police clearance for those two categories is **David's call** — it raises the bar and
lowers supply, and it is a real trade-off, not a technicality.

---

## B. Number 6 — the communication link. This is the one that decides whether it works.

It also collides head-on with the business model, so it needs care: **MarketSquare introduces, it
does not intermediate.** If a hirer and a worker can talk freely before an introduction, nobody ever
pays a Tuppence. If they cannot talk at all, nobody books.

### The resolution, and it falls straight out of what is already ruled (RUL-121 tiers)

- **Before the introduction — an anonymous question relay.** The hirer asks a short question
  ("free on Wednesday?"), the worker answers. Neither sees the other's number. Cheap, useful,
  no bypass.
- **The introduction IS the moment identities are exchanged.** One Tuppence, exactly as ruled.
- **After the introduction — direct contact.** Phone, WhatsApp, whatever they like. The platform
  steps out. That is the model working, not a gap in it.

### The buzzes and alarms are load-bearing, not decoration

If a hirer asks "Wednesday?" and the worker sees it two days later, the booking is gone. So:

- **WhatsApp is the real channel in South Africa, not email.** Most of this workforce has WhatsApp
  and many have no working email at all. It costs money per conversation through the Business API —
  **a vendor and spend decision, David's.**
- **Push through the installed app is free** — but the app registers no service worker today, which
  the BOTs work already flagged. Until that is fixed there is no push at all.
- **SMS as last resort**, costs money, but arrives on any phone.
- It must **degrade**: the worker may have no data for a day. A missed push cannot mean a lost job.
- The worker's reply must be **one tap** — *Yes / No / Ask me later* — not a form. Typing on a cheap
  phone with bad data is where these loops die.

---

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
2. Do child care and elder care require a police clearance, or a plain statement of what is not checked?
3. WhatsApp notifications — worth the per-conversation cost, or push-and-SMS only to start?
4. Does the anonymous question relay open before the introduction, or is even that reserved?
5. Number 4 — the Advert Card before TrustSquare: is the Quick List app a **separate app** that hands
   over, or the same app with a lighter front door? That decides how much is duplicated.
