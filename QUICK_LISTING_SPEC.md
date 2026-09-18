# THE EASY LANE — Quick Listing for ordinary working people
*Spec written 18 Sep 2026 from David's direction. Housecleaners first, then waiters,
petrol jockeys, truck drivers. The shape is his, in his words:*

> **Promise — visual — 4 clicks — email — EULA — list — building their trust score by
> guiding them with AI.**

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

Universal signals, **capped at 30 points in total**:

| Signal | Points | What she actually does |
|---|---|---|
| Government ID verified | **15** | Uploads her ID. 12 land at once (RUL-113 interim), 3 wait for confirmation. |
| **A previous employer confirmed her** | **12** | Sends her own link to someone she has worked for. They tap Yes. One tap, no account. |
| Complete profile | 5 | Bio, suburb, listing, description all set. |
| Photo of her added | 5 | Adds a photo of herself. |
| Referral 1 / 3rd / 5th+ | 5 / 3 / 2 | Shares her referral link with clients. |
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

## 4. THE FIVE DECISIONS THAT ARE DAVID'S

Batched, not dripped. Everything else in this document is mine to execute.

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
