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
