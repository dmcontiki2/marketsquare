# THE EASY LANE — Quick Listing for ordinary working people
*Spec written 18 Sep 2026 from David's direction. Housecleaners first, then waiters,
petrol jockeys, truck drivers. The shape is his, in his words:*

> **Promise — visual — 4 clicks — email — EULA — list — building their trust score by
> guiding them with AI.**

---

> **DAVID ANSWERED, 18 September 2026 (evening).** D1, D6 and D7 are decided, and a WhatsApp
> answer supersedes half of D2. The eight decisions are now rulings **RUL-142 … RUL-149** in
> `RULINGS.md` and are written into the sections below — this document no longer asks for them.
> **Still open and still his: D3 (what she is called), D4 (do the SA letters point at this door),
> D5 (where she comes from at all).** Those three are in §4, unchanged.

---

## 0. THE ONE THING TO UNDERSTAND FIRST

**Most of this is already built.** The trust ladder is live code with real point values. The
Quick app is live at `/q/homehelp` and answers 200. The home-help letter strip exists and
says "Four taps, and you have an advert". The employer-confirmation link, the one-tap
confirm page, and the 12 points behind it all shipped on 15 September.

So the work is **not** inventing this. It is that the pieces have never been joined into one
walk, nobody has ever been measured walking it, and the part David cares most about — the
visual that shows her score climbing — does not exist anywhere.

That is a much better position than it looks from the outside. It is also exactly how we got
here: a correct instrument nobody reads, beside a wrong one everybody does.

---

## 1. THE LADDER THAT ALREADY EXISTS (live values, read from `_TRUST_SIGNALS`)

Universal signals, **capped at 40 points in total** (raised from 30 by RUL-142, 18 Sep 2026 —
see the cap arithmetic in §7):

| Signal | Points | What she actually does |
|---|---|---|
| Government ID verified | **15** | Uploads her ID. 12 land at once (RUL-113 interim), 3 wait for confirmation. |
| **A previous employer confirmed her** | **12** | Sends her own link to someone she has worked for. They tap Yes. One tap, no account. |
| **A SECOND previous employer confirmed her** | **6** | RUL-142. The one signal this market can stack. Still one tap, still no account. |
| Complete profile | 5 | Bio, suburb, listing, description all set. |
| Photo of her added | 5 | Adds a photo of herself. |
| **Verified client 1st / 3rd / 5th+** | **5 / 6 / 7** | A client who **actually hired her** confirms it. Rising, so the third is worth more than the first (RUL-142). **Never paid for a signup.** |
| Years of experience stated | 3 | Says how long she has been doing this. |

**The employer confirmation is the centre of gravity for this market.** It is the only
third-party evidence an ordinary person can get without buying a certificate, it costs her
nothing, and the people who can give it are the people she already works for.

---

## 2. RUL-115 CHANGES WHAT THE GUIDANCE *IS*

David ruled on 9 September that a housekeeper is **invisible to strangers** until one
employer confirmation or an ID check lands — absent from search, not greyed out, because a
visible-but-locked card still leaks her free days and her suburb to anyone who looks.

This means the trust-score guidance is **not** post-listing polish. It is the gate to being
seen at all. So the visual is not a motivational chart bolted on at the end — it is the
thing that tells her what stands between her advert and a customer. That is a far stronger
reason for her to finish than "grow your score", and it is honest.

It also means the flow David described has one more beat in it than he wrote:

> Promise — visual — 4 clicks — email — EULA — list — **and now: you are listed but not yet
> findable; here is the one tap that changes that** — guided score.

---

## 3. WHAT IS ACTUALLY MISSING

1. **The score visual does not exist.** Nothing anywhere shows 50 → 62 → 67 with the reason
   attached. This is the heart of David's ask and it is the one genuinely new build.
2. **The Quick app is completely dark.** `quick.html` has zero funnel instrumentation — not
   one beacon. It has been linked from live letters since 14 September and we cannot see a
   single visit or drop-off. We would be tuning it blind.
3. **The return mail does not fire for the main lane.** The 18 Sep fix is gated on
   `source == 'quick'`. Listing 382 — Montana, the only advert anyone has ever built — came
   from the main app's sell-flow, which sends no source. The hole that swallowed him is
   still open on the lane that produced him.
4. **The walk has never been proven for a Quick-origin draft.** The 18 Sep proof used seeded
   test rows, not a draft that started in `/q/`.
5. **No promise screen.** `/q/homehelp` opens straight into the first question. There is no
   one-line promise and no picture of the destination before the work starts.

---

## 4. THE DECISIONS THAT WERE DAVID'S

Batched, not dripped. Everything else in this document is mine to execute.

**D1 — ANSWERED 18 Sep: yes, a second employer confirmation counts, at 6 points, and the universal
cap rises to 40. RUL-142.** The original argument is kept below because the cap arithmetic it
works through is what forced the cap to move.

**D2 — ANSWERED IN PART, 18 Sep, and better than the question asked.** The return path is
WhatsApp via `wa.me/?text=` with no number held anywhere (RUL-146, §8). Whether the ACCOUNT KEY
also moves off email is still open and still a bigger build.

**D6 — ANSWERED 18 Sep: 5 / 6 / 7, for verified CLIENTS, never signups. RUL-142.**

**D7 — ANSWERED 18 Sep: the unit is the taxi drop. RUL-147, §9.**

**D1 — Does a SECOND employer confirmation count?**
David said "+x for a second employer". The shipped code says no: `UNIQUE(email, signal_id)`,
with the comment *"the signal is 'somebody outside vouched for you', which is true once."*
Two confirmations is materially more evidence than one, and for a housecleaner it is the most
attainable signal she has. But the universal cap is 30, so adding it either displaces
something else or the cap moves. **Changing this is changing a ruling, so it is his.**
*My recommendation: yes, a second confirmation at 6 points, and raise the universal cap to 36.
Rationale: it is the one signal this market can actually stack, and RUL-136's own test is
"the more of a person's own life the ladder pays for, the more invested she becomes."*

**D2 — Is email really the key for this market?**
The flow says "4 clicks — email — EULA". A domestic worker in Johannesburg is far more likely
to have WhatsApp she reads every day than an email address she checks. If email is both the
account key and the way back to her draft, we will lose her at exactly the point we lost
Montana. **This is the single biggest risk to the whole idea.**
*My recommendation: phone number as the identifier, WhatsApp as the return path, email
optional. That is a bigger build and it touches the account model, so it needs his call
before anything is designed around an email field.*

**D3 — What is she called?**
"Housecleaner", "domestic worker", "home help", "cleaner" carry very different weight in
South Africa. The Quick door is currently labelled `homehelp` and files under Services /
Casuals. The word she sees is positioning, which is his.

**D4 — Do the SA letters get re-aimed at the Quick door as the primary call to action?**
Today the home-help strip is a secondary block under a "list your business" letter written
for companies. For this market the Quick door should probably *be* the letter.

**D5 — Where does she come from at all?**
We have no list of housecleaners, and there is no member directory to harvest. Domestic
workers are reached through employers, community groups, churches, taxi ranks and WhatsApp
groups — not cold email. **This is the honest gap in the plan**: the product idea is strong
and the acquisition channel for it does not exist yet. Worth thinking about on the drive to
chess, because it decides whether this is a four-week or a four-month move.

---

## 5. BUILD ORDER (mine, once D1–D3 are answered)

1. **Instrument `quick.html`** — the same beacons ms.js already posts. Without this every
   later change is guesswork. Half a day, zero risk, and it makes everything after it real.
2. **Close the return-mail hole** — widen the gate from `source == 'quick'` to the self-serve
   lanes, so anyone who finishes an advert gets the way back to it. Two lines.
3. **The promise screen** — one line, one picture of a finished advert with a score on it,
   then straight into the four taps.
4. **The score visual** — the new build. A ladder she can see, with her own number on it,
   what each rung is worth, and which single rung makes her findable. Never the word "safe"
   (RG-0238); never a claim that a verified email is identity (RUL-135).
5. **Prove one walk end to end from `/q/homehelp`** in a real browser at phone width, as a
   stranger, and only then point a letter at it.

---

## 6. THE RULES THIS LANE MUST NOT BREAK

- **Never call a person safe** (RG-0238). The score is evidence gathered, not a safety claim.
- **A verified email is not KYC** and must never be described as it (RUL-135).
- **The confirmer is never named or stored** (RUL-136/137) — only that a confirmation happened.
- **Never advertise the absence of an account** (RUL-137). The employer who confirms is a
  prospect; the free account is offered after the decision, never as a price for it.
- **Where she works, never where she lives** (RUL-115).
- **Representation parity in every image** (SO-2). This market is exactly where getting the
  pictures wrong would do real harm: clean, well-kept workwear for everyone, prefer anonymous
  framing, and compare the set rather than the photo.
- **She publishes by her own hand.** Nobody taps it for her.
- **The confirmer's reachability is held, never shown** (RUL-144). They verify a phone or an
  email, with no account. We store it, we never publish it, never share it, never attach it to
  her listing — and we say exactly that in the sentence that asks for it. Their NAME is still
  never stored.
- **Never share private details — that is not the same as never store them** (RUL-148). Collect
  only what a stated purpose needs, say what we hold when we ask, never show it to anyone.
- **The English EULA binds, and we say so in her language** (RUL-143). A translation that
  quietly prevailed was drafted once and corrected before shipping; it does not come back.
- **Four languages minimum, isiXhosa fifth for Cape Town, twelve official languages not eleven**
  (RUL-149).

---

## 7. TWO LATE ADDITIONS FROM DAVID (18 Sep, evening)

### D6 — Referrals at 5 / 6 / 7 instead of 5 / 3 / 2

**First, the freeing fact: the referral signals are a V1 placeholder.** `COACH-EARNABLE-1`
records it plainly — `_compute_universal_track_status` writes them "missing" unconditionally
and *nothing in the app can ever write them "earned"*. The coach deliberately stays silent
about them, because asking someone to do a thing that cannot move their score is worse than
not asking. So changing 5/3/2 to 5/6/7 today changes nothing at all. Nothing to migrate, and
we can define this properly the first time.

**The inversion is the good idea.** A ladder that pays *more* for the third than the first
turns the score into a reason to keep going, instead of a reason to stop after one. That is
exactly right for this market.

**The one hard constraint: pay for verified CLIENTS, never for signups.** The invariant in
the code is explicit — the Trust Score measures the seller: verified identity, credentials,
system-calculated track record. If points come from people she recruits for us, the score
starts measuring how good she is at marketing TrustSquare, and a trust score that measures
that is not a trust score. A neighbour reading "78" must be reading evidence about her work,
not her recruiting.

The honest version keeps everything David wants: pay for a **client who actually hired her
and confirmed it**. That is real third-party evidence, it genuinely is more evidence the more
there are, it justifies rising weights — and it still delivers the growth, because a verified
client is a real user who arrived through her.

**Cap arithmetic, which forces a choice:** 5 + 6 + 7 = 18 from referrals, plus 12 for the
employer confirmation, is 30 — the entire universal cap. Her photo, her ID and her years of
experience would then be worth literally nothing. So rising referral weights require the
universal cap to move (~40 is the natural number) or the rest of the ladder to be rebalanced.
*My recommendation: 5 / 6 / 7 for verified clients, universal cap to 40, employer confirmation
stays 12 and a second employer adds 6 (D1). An ordinary housecleaner can then reach 50 + 30
without owning a single certificate, which is the whole point of RUL-136.*

### D7 — A local map of where she works

**The instinct is the most commercially valuable thing in this market.** "She already works
two doors down, on Tuesdays" is the single fact most likely to convert a neighbour, and no
competitor can show it. Worth building.

**But it must never publish addresses or streets.** Three reasons, and the first is the one
that ends the argument:

1. **They are her employers' addresses, not hers.** Those households never agreed to anything
   and are not our users. We would be publishing third-party home addresses.
2. **Her open days plus her streets tells a stranger exactly where she is and when.** That is
   a safety problem for her and a pattern-of-life map of her employers' empty houses. RUL-115
   exists because David saw this: *"A listing that puts a woman's open days and her suburb in
   front of anybody at all, with no accountability on the other side, is not a service to
   her."* Streets are far more precise than the suburb he was already uneasy about.
3. SO-1 bars presenting any exemplar map as a real surveyed location.

**The version that keeps all the value and none of the risk** — and I think it is actually
*more* persuasive than pins:

- A soft shape, not points: the suburbs she works in, shaded, with no marker anywhere.
- The useful fact stated in words: *"Works in Lynnwood and Menlo Park · open Tuesdays and
  Thursdays."*
- Proximity computed **for the viewer, about the viewer**: *"Already works about 400 m from
  you"* — true, compelling, and it draws nothing. The precision lives in the sentence, where
  it is safe, instead of on the map, where it is not.
- Exact detail is exchanged only after an introduction is accepted, which is already how the
  platform works.

*My recommendation: build the shaded-area map and the proximity sentence. Never a pin, never
a street name, never an employer's address — not even blurred, because a blurred pin is still
a pin.*


---

## 8. WHATSAPP WITHOUT HOLDING A NUMBER (RUL-146 — David approved this text verbatim)

*David, 18 Sep 2026: "i dont want us to regress". This is carried in full, not paraphrased down.*

> The WhatsApp answer is better than you'd hope, because the mechanism you want already exists and
> costs nothing.
>
> `https://wa.me/?text=<message>` opens WhatsApp on her phone with a message pre-filled and no
> recipient. She picks who it goes to from her own contacts. We never learn who she chose, never see
> a number, never store one, never transmit one. The link does not contain a number because it does
> not need one.
>
> That gives you three things immediately:
>
> **Her employer referral.** She taps "Send this to someone I work for", picks them in her own
> contacts, and the one-tap confirm link travels over the channel she actually uses. This is exactly
> RUL-115(b) already — she sends her link — just expressed in WhatsApp instead of email. The
> confirmer stays unnamed and unstored, as you said.
>
> **Her way back to her own draft.** This is the Montana problem solved for a market with no email:
> a "Send this to myself on WhatsApp" button. She picks her own chat, and the link to her
> half-finished advert now lives in the app she opens fifty times a day. No API, no cost, no number,
> nothing for us to lose.
>
> **Buyer to seller — you already built it.** Buzz connects two parties without either seeing the
> other's details. That is the answer for introductions; nothing about WhatsApp changes it.
>
> The one thing that genuinely costs money is us messaging her unprompted — that needs the WhatsApp
> Business API and per-message fees, so it stays yours to decide. The two patterns above need none
> of it.

**Build rule, asserted by the ledger (WA-NONUMBER-1 / RG-0407, LOCKED):** every WhatsApp share link
the app emits is `https://wa.me/?text=...` with **no phone number in the path**, and no code path
stores, logs or transmits a recipient number obtained from one. Scope: every Easy Lane button
(employer referral, send-to-myself) and any future WhatsApp share anywhere in the product.

---

## 9. THE AREA UNIT IS THE TAXI DROP (RUL-147 — answers D7)

Publish **the route and the drop, plus the suburb**. Never an address, never a street, never a
block. A block plus her open days can identify a household — hers to be found at, and her
employers' to be found empty. Those households are not our users and agreed to nothing.

Proximity is computed **for the viewer, about the viewer** — *"within walking distance of you"* —
and published nowhere. The precision lives in the sentence, where it is safe, not on the map, where
it is not. Never a pin; a blurred pin is still a pin.

The taxi drop is also simply the better unit for this market: it is what she would tell a friend,
and it is how the person reading her advert already navigates.

---

## 10. THE POST-CONFIRM GLIMPSE (RUL-145 — decision 4)

The moment an employer taps **Yes** is the only moment we will ever have their full attention, and
today it ends in a receipt. Instead, on that same page, with **no wall and no account**:

1. **Her card, with the score moving in front of them** — 50 → 62, animated, the reason attached
   ("a previous employer confirmed her"). This is the visual §3 calls the heart of David's ask; the
   confirm page is where it earns the most, because the person watching it just caused it.
2. **Two or three other already-public workers in their area** — the product discovered as a
   BUYER, from the one page where we can prove it works.
3. **The free account offered after the decision, never as its price** (RUL-137(d)).


---
---

# PART II — THE BETA ROLL-OUT (David, 19 September 2026)

*David's direction, verbatim in substance: add all of these roles under **Service — Casuals** and
**Service — Technical**; add the employer side ("this is a huge change"); and **"the aim is to use
these service types to 'enroll' their current employees or previous employees as referrals."***

---

## 11. THE ONE THING TO UNDERSTAND ABOUT PART II

That last sentence is the whole strategy, and it answers **D5 — the honest gap this document has
carried since 18 September: we have no way to reach these people.**

Cold letters to individuals convert at **8 human clicks per 2,499 letters**. One HR department at
one mine has three thousand employees and is **one conversation**. The employer is not primarily a
demand side. **The employer is the supply channel** — and it arrives carrying the single most
valuable thing on the trust ladder already attached.

Because when a mine, a hotel group, a transport company or a municipality confirms someone, that
is worth *more* than a household's confirmation, not less:

- It is an **institution, not a neighbour** — verifiable, accountable, and it has a name anyone can
  check.
- It is **issued at source**, not a scanned letter of unknown provenance (`category.services_cas.ref_1`
  today pays 8 points for a letter with "verifiable contact" — this is that signal without the scan,
  the doubt, or the phone call).
- It **scales**: one employer action enrolls hundreds of people, each of whom then does the one act
  that counts — publishing their own advert, by their own hand.

**So the order is inverted from how it looks.** We are not adding roles so that miners can sell
things. We are adding roles so that **employers can vouch for their people at scale**, and those
people then sell whatever they can actually sell — weekend cleaning, driving, welding, childcare —
with institutional proof already on their profile.

---

## 12. MOST OF THE EMPLOYER SIDE IS ALREADY BUILT. IT IS CALLED "AGENCIES".

This is the good news and it changes the size of the job. The agency lane already does, today, in
shipped code, almost exactly what the employer lane needs:

| Built already | Where | What it does |
|---|---|---|
| `create_agency` | bea_main.py | Registers the organisation |
| `set_agency_verified` | bea_main.py | Marks it verified — and verification drives member tier |
| `invite_agent` | bea_main.py | **Creates the person's own account, sets a listing cap, mints a magic sign-in link and emails it** |
| `_sync_agency_member_tiers` | bea_main.py | One writer; invite-then-verify and verify-then-invite end in the same place (AGENCY-REACH-1) |
| `_agency_agent_rollup` | bea_main.py | The organisation sees its own people |
| Agency import + anonymisation | AGENCY_IMPORT_ANONYMISATION_SPEC.md | Bulk intake that already anonymises |

**And it already respects the line that matters most.** `invite_agent` creates a user, a membership
and a sign-in link. **It creates no listing.** The regression ledger records this as a property
worth protecting in its own right (RG-0395/RG-0404: *"the agency import lane sends no source and
still mails nobody"*).

**So the employer lane is a generalisation, not a new build:** an estate agency is one kind of
organisation; a mine, a hotel group, a fast-food franchise, a transport operator, a farm, a factory
and a municipality are others. The work is renaming the concept, widening the verification evidence
(a CIPC number and a letterhead rather than an EAAB licence), and giving the organisation a reason
to care.

### 12a. THE HARD LINE, AND IT IS NOT NEGOTIABLE

**The employer enrolls the person. The employer NEVER creates the listing.**

`ONBOARDING_GOAL.md` §3 bars it in terms — *"You may not create the listing for them. Nor may
David. They do it themselves."* — and it is also the only thing that makes the trust score mean
anything. A thousand listings generated from an HR export is a database, not a marketplace, and
every one of them would be a lie on the number.

The enrollment flow is therefore:

    employer verifies  ->  employer invites (name + a way to reach them)
      ->  the worker gets HER OWN sign-in link
      ->  she builds her own advert, in her own language, in four taps
      ->  she publishes it BY HER OWN HAND
      ->  the employer confirmation is already on it

A bulk CSV that ends in listings is the one shape this must never take. Build the importer so that
it *cannot* — the ledger entry should assert it, not the code review.

### 12b. WHY AN EMPLOYER WOULD ACTUALLY DO IT

Worth being honest that this needs a reason, and "help us with supply" is not one. The three that
hold up:

1. **It is a staff benefit that costs nothing.** Their people earn on their off days, with the
   employer's name behind them.
2. **Retrenchment and seasonal lay-off.** A mine or a farm that lets people go can hand them
   something real on the way out. This is the strongest version of the pitch and the one most
   likely to open a door, because it solves a problem the employer already has.
3. **Former employees cost them nothing to vouch for** — David's word was *"previous employees"*,
   and that is deliberate: it is a much easier ask than anything involving current staff, payroll,
   or a union conversation.

---

## 13. THE ROLE REGISTRY — DATA, NOT CODE

**Every role is a row, never a door.** The Quick app's `CATS` array is already data (8 categories,
JSON), and the `homehelp` door's first question is **already a role picker** — *"What work do you
do?"* → Cleaning / Laundry & ironing / Cooking / Childminding / Office cleaning / Garden help.

So adding fifty roles is adding rows to that list plus one field, **not fifty forks of the same
page**. This matters more than it sounds: this project has now been bitten twice in eight days by
forked copies of the same file (`quick.html` vs `genie/q_index.html`; the fourth EULA copy in
RG-0400). A role-per-door design would be that mistake fifty times over.

**One row per role carries:**

| Field | Why |
|---|---|
| `key` | stable id, never translated |
| `service_class` | **`Casuals` or `Technical`** — already in the model (`bea_main.py:2307`) |
| `label[lang]` | what she is called, in each language |
| `questions[]` | the four taps, defaulted from the class and overridden only where a role needs it |
| `signals[]` | which category trust signals apply (both ladders already exist — see §14) |
| `draft_title` / `draft_body` | templates per language |
| `employer_kinds[]` | which organisations vouch for this role — the enrollment join |

**Naming (D3, answered by default since it was not overridden):** **the role name only, never a
collective noun.** She is a *Cleaner*, a *Chef*, a *Welder*. Not "domestic worker", not "help", not
"service provider". It is what she would call herself, it sidesteps every loaded word, and it
translates cleanly. Veto this if you want a different line.

---

## 14. BOTH TRUST LADDERS ALREADY EXIST — THIS IS WHY THE TWO CLASSES ARE THE RIGHT HOME

David's instruction to file everything under the two service classes lands on machinery that is
already built and already correct for these people:

**Services-Casuals** (live values, `_CATEGORY_SIGNALS`):
police clearance **10** · any NQF qualification or short course **8** · 2–4 years in service **6** ·
5+ years **8** · reference letter **8** · second reference letter **5** · strong profile **5**

**Services-Technical** (live values):
trade licence (PIRB / DoEL) **12** · professional body registration (ECSA, PIRB) **12** · formal
trade certificate **8** · CIDB grading **6** · public liability insurance **5** · primary industry
licence / CoC **5** · registered company (CIPC) **5**

Two observations that should shape the build:

1. **The Casuals ladder is already designed for someone with no certificates** — clearance,
   experience and references, not qualifications. That is exactly RUL-136's test, and it means a
   petrol jockey or a till worker is not a second-class citizen of this ladder.
2. **An employer confirmation is a better `ref_1` than a scanned letter.** Rather than inventing a
   new signal, the enrollment should *satisfy the reference signals at source* — digital, verified,
   no scan, no phone call. That is a smaller change than it looks and it makes the enrollment
   immediately worth points to the worker, which is what makes her finish.

---

## 15. THE ROLE SLATE — DAVID'S LIST, MAPPED, PLUS THE ONES HE DID NOT LIST

*A seed slate for discussion, not a closed list. Every one of these is a row.*

### 15a. SERVICES — CASUALS

**David's:** Home cleaner · Hotel cleaner / room attendant · Petrol / forecourt attendant ·
Quick-food kitchen hand · Till / counter assistant · Factory worker (general) · Municipal worker
(general) · Chef · Farm worker

**Not listed, and they belong:**

- **Home & care:** Nanny / childminder · Elder carer · Home nurse aide · Cook (domestic) ·
  Laundry & ironing · Gardener · Pool cleaner · Window cleaner · Housekeeper (live-in / live-out)
- **Food & hospitality:** Waiter / waitress · Barista · Bartender · Dishwasher / kitchen porter ·
  Baker · Butcher's assistant · Banqueting / function staff
- **Retail & forecourt:** Shelf packer · Stock assistant · Spaza / shop assistant · Car guard ·
  Parking attendant
- **Logistics & yard:** Warehouse picker / packer · Loader · Removals / moving help · Delivery
  rider (e-hailing / food) · Courier on foot
- **Site & general labour:** General labourer · Painter's assistant · Builder's assistant ·
  Cleaner (office / industrial) · Grounds & landscaping help
- **Trades-adjacent & informal:** Seamstress / tailor · Hair braider · Salon assistant ·
  Cobbler · Car washer · Event staff · Crèche assistant
- **Security:** Security guard (PSIRA-graded — see the note below)

### 15b. SERVICES — TECHNICAL

**David's:** Miner · Transport / business driver · Industry worker (skilled)

**Not listed, and they belong:**

- **Mining & heavy industry:** Rock drill operator · Blaster · Winch driver · TMM / machine
  operator · Rigger · Boilermaker · Millwright · Fitter & turner · Welder · Crane operator ·
  Forklift operator
- **Motor & transport:** Code 10 / 14 driver · Long-haul driver · Taxi / shuttle driver ·
  Diesel mechanic · Motor mechanic · Auto electrician · Panel beater · Spray painter · Tyre fitter
- **Building trades:** Electrician · Plumber · Bricklayer · Plasterer · Tiler · Carpenter · Roofer ·
  Glazier · Ceiling & partition installer · Painter (qualified) · Paving · Waterproofing
- **Systems & installation:** Refrigeration / HVAC technician · Solar PV installer · Borehole &
  pump technician · CCTV / alarm installer · Gate & garage-door technician · Locksmith ·
  Appliance repair · IT / networking technician · Small-engine repair

### 15c. THREE ROLES THAT NEED A DECISION BEFORE THEY SHIP

Flagged now rather than discovered later:

- **Security guard** — PSIRA registration is a legal requirement to work, not a trust bonus.
  Listing an unregistered guard could expose both him and us. Either verify PSIRA or leave the role
  out; do not ship it as an ordinary Casuals row.
- **Driver (passenger-carrying)** — a professional driving permit (PrDP) is likewise a legal
  requirement. Same treatment.
- **Home nurse aide / elder carer** — the closer a role sits to health care, the more a trust score
  reads as a competence claim we are not making. Keep the language to what the ladder actually
  evidences and never near a clinical claim (RG-0238: never the word "safe").

---

## 16. LANGUAGE — THE MULTIPLIER, AND IT IS THREE DIFFERENT THINGS

David, 19 Sep: *"The multiplier addition will be the language option... but we are also going to
add this for the other countries — New York may have Mexican, Mandarin, Indian etc. This language
option is a great tool."*

**He is right that it is a great tool, and the reason is worth naming precisely: language is not an
accessibility feature here, it is a MATCHING feature and a trust signal.** A Johannesburg household
that speaks Sesotho at home and a Sandton family that wants a nanny who speaks Mandarin are both
doing the same thing — looking for someone their household can actually talk to. That is a reason
to hire, and no competitor in this market shows it.

**These must never collapse into one field:**

| # | Field | What it is | Frozen? |
|---|---|---|---|
| 1 | `speaks[]` | **The languages she can work in.** Seller-declared, shown on her card, filterable by the buyer. **This is the multiplier.** | No — build it |
| 2 | `composed_in` | The language she wrote her advert in. Drives display and RUL-086 runtime translation. | No |
| 3 | `ui_locale` | The app's own chrome. 5,171 strings inventoried. | RUL-075 lane |
| 4 | EULA language | RUL-143 — English binds, said plainly in her language. | RG-0412, waits on RG-0400 |

**(1) is the one to build first and it is cheap.** It is a seller attribute and a filter. It needs
no translated app at all: a Pretoria buyer reading English can still see *"speaks isiZulu, Sesotho,
English"* and that is already the whole commercial value.

### 16a. LANGUAGE SETS ARE PER-COUNTRY DATA — SAME SHAPE AS THE GEO HIERARCHY

The app already carries Country → Region → City → Suburb. Languages hang off **country**, as a
seeded table, never hardcoded:

- **South Africa** — English, isiZulu, isiXhosa, Sesotho, Afrikaans, Setswana, Sepedi, Xitsonga,
  siSwati, Tshivenda, isiNdebele, **SASL**. *(Twelve. SASL was added in 2023 — any screen of ours
  saying eleven is a defect, RUL-149.)*
- **United States** — English, Spanish, Mandarin, Cantonese, Tagalog, Vietnamese, Korean, Hindi,
  Gujarati, Punjabi, Haitian Creole, Arabic, Russian, Portuguese, Polish, ASL.
- **United Kingdom** — English, Polish, Urdu, Punjabi, Bengali, Gujarati, Romanian, Arabic,
  Portuguese, Somali, BSL.
- **Australia** — English, Mandarin, Arabic, Vietnamese, Cantonese, Punjabi, Greek, Italian,
  Tagalog, Hindi, Auslan.

The seller picks from her country's set; the buyer filters on the same set. Adding a country is a
data seed, exactly like adding a city.

### 16b. ONE REAL CAUTION, AS A CAUTION AND NOT A GATE

**Seller-declared and displayed is safe everywhere. A buyer-side hard filter is not, in every
market.** In the United States, an *employer* screening workers by language moves close to
national-origin discrimination under Title VII, and the same logic reaches housing contexts. In
South Africa it is unremarkable and genuinely useful.

The design that keeps the value and the safety in every market: **she declares it, we display it,
and the buyer sorts by it rather than being able to exclude on it.** "Speaks Mandarin" appears
prominently and ranks her up for a Mandarin-speaking viewer; there is no "hide everyone who
doesn't" switch in the employment-facing lanes. That is a one-line design rule now and an expensive
retrofit later.

---

## 17. WHAT THIS DOES TO THE 31 OCTOBER NUMBER — HONESTLY

The current trajectory is stated plainly in GOAL_STATE: on how the cold letter performs today,
**20 published listings by 31 October is not reachable through that channel.**

**This changes that, and it is the first thing that has.** One verified employer enrolling two
hundred former employees, of whom a few per cent finish, is the whole goal in one conversation —
and every one of them is a real person from our outreach, publishing by their own hand, with no
rule in §3 bent.

**But it is honest to say what it now depends on**, because it moves the bottleneck rather than
removing it: it depends on **David or someone opening one employer door**, which is a conversation
with a human being, not a thing the agent can do from a sandbox. That is the one genuine hand-off
in this plan, and it is worth more than every remaining letter on the list.

**Build order, highest effect on the number first:**

1. **`speaks[]` on the seller** — smallest change, immediate commercial value, no dependencies.
2. **The role registry** — the two classes, the slate above, as data. Unblocks everything else.
3. **The organisation lane** — generalise `agencies`, widen verification, and assert in the ledger
   that enrollment can never create a listing.
4. **Enrollment satisfies the reference signals at source** — makes the invitation worth points on
   arrival, which is what makes her finish.
5. **Language on the composing surfaces**, with the parity harness built alongside rather than
   ahead of it.
6. **The employer-side demand product** — businesses hiring through TrustSquare. Real, and second.

---

## 18. WHAT IS STILL DAVID'S

- **Which employers to approach first** — and the retrenchment / former-employee angle is the one
  most likely to open a door.
- **Whether the organisation lane is priced** — it is free supply today; charging changes it into a
  commercial product and that is money, which is reserved.
- **The three flagged roles in §15c** (security, passenger-carrying drivers, care) — each carries a
  legal registration question, not a design one.
- **The beta slate and its order** — the list above is a seed for discussion, as he asked.
