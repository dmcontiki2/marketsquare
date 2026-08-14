# AI ACCOUNTABILITY PRE-DESIGN — MarketSquare

**v2, 14 Aug 2026.** Supersedes `AI_FAILURE_PREDESIGN.md` v1 of the same day, which proposed
human takeover of throughput surfaces. **That was wrong** — see "The correction" below.

Source: *"Companies Put AI In Charge. Now They're Paying For It"* — House of El: AI,
https://www.youtube.com/watch?v=Jbh8QteVM5g

Canon companions: `AI_ACCOUNTABILITY_REGISTER.json` (data),
`scripts/ai_accountability_check.py` (assertion), `AGENTS.md` (role-not-AI staffing),
`AI_AUTO_FAILOVER_P2_DESIGN.md` (breaker), `AI_SWAP_ARCHITECTURE.md` (the +1 lane).

---

## The correction

v1 read the video and reached for the obvious conclusion: *put a human where the AI decides.*
David's response, and it is right:

> "To use a human to perform complaints doesn't make sense; to use a human to
> detect/sort/decline/advise photos is useless — that task is typically a large amount of
> throughput and would throttle the business to a standstill, hence the AI."

Two things follow, and the second is the one v1 missed entirely.

**First, the throughput argument.** A human on a per-item path in a high-volume surface caps
the business at that human's rate. Photo triage, moderation, classification and drafting are
precisely the tasks where machine speed and tirelessness win.

**Second, and worse: the human control *decays*.** A reviewer looking at 500 photos a day is
rubber-stamping by day three. Vigilance decrement under repetitive high-volume inspection is
well documented and it is not a discipline problem — it is how attention works. So the human
seam on a throughput path is not merely slow. It becomes **a control that looks like a
control**, which is more dangerous than no control at all, because it is trusted. AI does not
have that failure mode: lane 500 is judged exactly like lane 1.

**Klarna does not contradict this.** Klarna's error was not "removed humans". It was
**capability mismatch** — they used AI for emotionally-charged, multi-step, judgement-heavy
resolution, which it could not do, and they did it for cost reasons while claiming quality.
MarketSquare's AI surfaces are classification, extraction, comparison and drafting at volume —
the things AI genuinely does better. Matching the tool to the task *is* the lesson, and
MarketSquare already applied it.

**Pizza Hut does not contradict it either.** Dragon Tail's failure was not a missing shift
manager. It was that **nobody modelled how two independently optimising systems would
interact** when the AI changed the information environment. That is a systems-modelling
failure, and it would have happened with or without a human in the loop.

---

## The corrected axis: humans own interfaces, not tasks

Humans are not the fallback for AI work. They own the **boundaries where MarketSquare meets a
party that can compel it** — a party that requires a named, accountable person.

| | Interface role | Owns | Why it must be human |
|---|---|---|---|
| **R1** | Legal & Regulatory | What the AI is *allowed* to say and do: POPIA, consumer law, the financial-advice boundary, EULA and disclosure wording, dispute-of-record, counsel and regulator liaison, tax/VAT treatment of affiliate income | The counterparty is a legal system. It requires standing, a signature, and someone who can answer a regulator. No AI holds that standing. |
| **R2** | Infrastructure / Server Admin | Hetzner host, deploy ref and rollback, backups and restore proofs, SSL, DNS, secret and key custody, breaker Restore after a T3 ban, disk and cost ceilings | Irreversible physical and financial failure modes, plus credentials that must never sit in an agent's hands. The one lane where the maintenance agent cannot be its own safety net. |
| **R3** | Business & Partner | Agency contracts and onboarding, Paystack, Travelpayouts, founding sellers, partner escalation, commercial terms | The counterparty is another human organisation that negotiates and builds trust over time, and will not contract with a bot. |
| **R4** | Accountable Principal (David) | Non-delegable signature: spend above cap, legal sign-off, launch gate, arming autonomy, reversing a ruling | Accountability cannot be delegated to a system that cannot be held accountable. |

Each role owns **exceptions**, never throughput. Each has a hire trigger stated as an
exception condition, not a volume.

---

## What actually catches a wrong AI answer

Ranked by how well it preserves throughput. A human appears **last**, and only for exceptions
whose *class* is legal, financial, partner or infrastructural.

1. **Deterministic guard** — bounds, schema, allow-list, idempotency. Cheapest, most reliable,
   costs nothing in throughput.
2. **Second AI lane, different vendor — disagreement is the exception signal.** See below.
3. **Economic absorber** — refund, reserve, insurance, so a wrong answer costs money rather
   than trust. Money is recoverable; trust is not.
4. **AI-run appeal route** — the appeal is itself handled by AI; only the residue reaches a
   human interface role.
5. **Human interface role** — exceptions only, never per-item.

### PR-8 — the +1 lane is a control, not just a spare

The designated swap-out provider exists for failover and **sits idle in normal operation**.
On RED surfaces it can run as a second opinion, with **disagreement between lanes — not low
self-reported confidence — as the exception signal.** Model confidence is notoriously
uncalibrated; cross-vendor disagreement is an independent, empirical signal.

This is the neatest fit in the whole design: it preserves throughput, uses AI's strength to
police AI, and converts dormant failover capacity into a live control. Concrete applications:

- **AS-01 KYC** — both lanes read the document; disagreement routes to AI appeal, not a person.
- **AS-02 Anonymisation** — an *adversarial re-read* whose only job is to try to recover
  identity from the anonymised output. If it can, the redaction failed. Continuous machine-speed
  red-teaming, impossible for a human at volume.
- **AS-05 Grading / AS-06 Price** — disagreement **widens the published range** rather than
  escalating. The honest uncertainty gets expressed to the user instead of hidden behind a
  confident single number.

---

## The eight pre-design rules

| | Rule | In one line |
|---|---|---|
| **PR-1** | Parallel run, never a switch-over | Both lanes run and are compared under real load. AI-vs-AI or AI-vs-deterministic — never AI-vs-human, which cannot keep pace and so proves nothing |
| **PR-2** | AI is policed by AI; humans own interfaces | Guards, second lanes and economic absorbers catch wrong answers. Humans own the law, the machine, the partner, the signature |
| **PR-3** | Never remove the fallback and add the new lane in the same change | Yum did both at once and left the franchise with neither |
| **PR-4** | Run the Dragon Tail test on every new information surface | Write down what a purely self-interested actor does with it. Systems modelling, not staffing |
| **PR-5** | No public claim the machinery cannot yet honour | Klarna's most expensive loss was narrative |
| **PR-6** | **A human in a throughput path is a defect, not a control** | It throttles the business and decays into rubber-stamping. The checker fails any design that does it |
| **PR-7** | **The exception rate is the trigger, never the volume** | Rising volume is the design working. It must never be the reason a person gets pulled in |
| **PR-8** | **The +1 lane is a control, not just a spare** | Run it as a second opinion on RED surfaces; disagreement is the exception signal |

---

## What is asserted, and how

`scripts/ai_accountability_check.py` reads `AI_ACCOUNTABILITY_REGISTER.json` and **fails** if:

- any surface is missing a field or carries a blank one;
- **any high- or medium-throughput surface puts a human on every item** (PR-6);
- any RED surface has no machine-speed check — no deterministic guard *and* no AI check;
- any surface that can raise an exception names no owning interface role, or an interface role
  is defined as touching every item;
- **any trigger is phrased in raw volume rather than an exception rate** (PR-7);
- any declared incentive leak has no action, or any of PR-1…PR-8 has gone missing.

Negative-tested on 14 Aug 2026: re-injecting the two v1 mistakes — a human reviewing every
photo, and a ">40 verifications per week" trigger — makes it exit 1 and name both. It bites.

**Current state: 14 surfaces — 5 RED, 7 AMBER, 2 GREEN; 12 high-throughput. 14 of 14 keep
humans off the per-item path. 0 FAIL, 3 WARN.** The three warnings are the build queue:
AS-05 grading, AS-06 price, AS-07 yield.

---

## What survives from the video, unchanged

Both cases still teach, but neither teaches "hire people":

- **Dragon Tail → model the system, not the staffing.** Our own latent version is live: a
  public `GET /tuppence/balance` read, a published trust rubric with an unverified referral
  lane, and a boost that lowers the match threshold 60→45. All three are Dragon Tail-shaped:
  information given to independent economic agents who will use it rationally.
- **Klarna → match the tool to the task, and never claim what the machinery cannot honour.**
  MarketSquare passes the first half by design. The second half is PR-5, and it applies to the
  AI-first story itself.

And PR-6 adds a rule the video does not contain: **the naive fix is also a failure mode.**
Bolting a human onto a high-volume AI surface produces a slow business *and* a decayed control.
Both companies would still have failed with a person in that chair.

---

## Next actions, in order

| # | Action | Owner |
|---|---|---|
| 1 | Authenticate `GET /tuppence/balance` before the edge gate lifts — **launch blocker** (IL-01) | R2 |
| 2 | Decouple boost from relevance: visibility up, match threshold untouched (IL-03) | R4 |
| 3 | Frame grading and price as ranges/estimates with a dispute route; yield gets a disclaimer and an agency hand-off (AS-05/06/07) — clears the three WARNs | R4 / R1 |
| 4 | Gate referrals on evidence before the lane goes live (IL-02) | R4 |
| 5 | **Pilot PR-8 on AS-02**: adversarial re-read of anonymiser output. Highest value, lowest risk, and it protects the business model directly | R3 |
| 6 | Add ledger entries for 1–5, and run `ai_accountability_check.py` alongside the regression ledger each session | R4 |
