# AI FAILURE PRE-DESIGN — MarketSquare

**Created 14 Aug 2026.** Source: *"Companies Put AI In Charge. Now They're Paying For It"* —
House of El: AI, 18:43, https://www.youtube.com/watch?v=Jbh8QteVM5g

Canon companions: `HUMAN_SEAM_REGISTER.json` (the data), `scripts/human_seam_check.py`
(the assertion), `AGENTS.md` (role-not-AI staffing doctrine), `AI_AUTO_FAILOVER_P2_DESIGN.md`
(the breaker), `ORCHESTRATION_POLICY.md` §12 (escalation).

---

## Why this document exists

Two companies in the video lost enormous amounts of money. In **neither case did the AI
malfunction**. That is the whole lesson.

**Pizza Hut / Dragon Tail.** Yum mandated an AI "super manager" across its franchises. At
Chalk Pizza — 111 stores, delivery-only, entirely dependent on DoorDash — on-time delivery
fell from 90% to ~50%, rack time went from under 5 minutes to 20. The algorithm computed
correctly throughout. What it did was **change the information environment**: it showed gig
drivers when pizzas would leave the oven, what the tips were, and which orders were cash.
Independent economic agents then optimised for themselves — waiting to batch deliveries,
cherry-picking on tip, deprioritising cash. The system was designed to prevent food waiting
on the bench and its first act was to create exactly that. Yum compounded it by centralising
the DoorDash contract **in the same change**, so the franchise lost the AI's replacement and
its own manual tools simultaneously. $100m lawsuit.

**Klarna.** Replaced ~700 customer service staff with an OpenAI chatbot, built a corporate
identity and an IPO narrative on it, listed July 2025. The AI handled volume; it could not
handle complexity, emotion, multi-step resolution or edge cases. By May 2025 the CEO admitted
"we focused too much on efficiency and cost… the result was lower quality." By September 2025
they were rehiring. Ten weeks from IPO thesis to reversal.

The supporting data: Forrester's 2026 report found **55% of employers regret laying off
workers for AI**. Gartner found only 20% of customer service leaders actually cut staff, and
predicts **50% of those who did will rehire by 2027**. The companies seeing returns —
Unity, Hiscox, logistics carriers — used AI to make existing teams faster and cut nobody.

---

## Why our position is different — and where it is *worse*

David's framing is correct and worth stating plainly: **these were human-first companies that
replaced people prematurely. MarketSquare is AI-first by design, and intends to add humans
where they will genuinely be required.** That inverts the failure mode. We are not making the
Klarna mistake, because we are not making the Klarna *claim*.

But the inversion carries one asymmetry that is easy to miss and expensive to discover late:

> **Klarna could rehire the 700 people it fired. They existed, they knew the product, and the
> roles were still defined. MarketSquare has no bench. When a surface finally needs a human,
> there is no one to call back — there is a hiring process, a training curve, and a live
> problem running the whole time.**

Everything below follows from that single asymmetry. The design job is not to avoid AI
failure — it is to **cut the seam a human will one day stand in, while it is still empty.**

---

## The four failure modes, mapped onto us

### 1. The information-environment failure (Dragon Tail)
Dragon Tail leaked internal state to independent economic agents and was surprised when they
used it rationally. **We have the same shape of exposure**, and it is already latent:

- `GET /tuppence/balance?email=` is a **public read**, masked only by the pre-launch edge gate
  — *which lifts at launch*. **Launch blocker.**
- The Trust Score rubric is fully published, with tiers and thresholds (Gold 90+ earns
  featured priority). Publishing the rubric is *right*. Publishing an **unverified** signal
  is not — the referral lane (specced, `evidence_required` varies, "placeholder for V1") is
  the exact Dragon Tail vector.
- **Boost lowers the match threshold 60 → 45** and sorts boosted-first. A seller optimising
  purely for reach boosts weak listings; buyers learn boosted results are worse and stop
  trusting the feed. Boost should raise *visibility*, never lower *relevance*. Decouple them.
- Intro pricing (1T, 2T if boosted) makes sellers **pay to be reachable**. Watch for the
  emergent case: any incentive that makes a seller less reachable works against the only
  thing the till charges for.
- The anonymiser is the only thing between a partnered agency and a free bypass of the intro
  fee. That agency is an independent economic agent **exactly like a DoorDash driver**. Treat
  anonymiser bypass as an adversarial-testing target, not a QA case.

**Rule PR-4 — run the Dragon Tail test on every new information surface.** Before exposing
any platform-internal signal to a seller, buyer, agency or affiliate, write down what a purely
self-interested actor does with it. If the answer is unknown, it is not ready to ship.

### 2. The simultaneous-removal failure
Yum added the AI *and* removed the franchise's manual fallback in one move. We have already
done the right thing once here — `MATCHER` is deterministic today with the AI as a
hot-swappable socket. **Rule PR-3: never remove the fallback and add the AI in the same
change.** And **PR-1: parallel run, never a switch-over** — when the AI matcher replaces the
deterministic one, both run and their outputs are compared under real load first. This is the
single rule that would have saved both companies.

### 3. The complexity-vs-volume failure (Klarna)
"The AI handled volume. It could not handle complexity." Our exposure is `_classify_email`:
it triages support/billing/legal/spam and drafts replies. A legal notice classified as spam
*is* the Klarna failure. Existing defence is good — `escalation_brief.py` renders
LEGAL/MONEY/COST/TRUST for David. **Hard rule: nothing classified legal or billing ever
auto-sends.**

The three surfaces that emit **confident judgements with no declared fallback** are the
current soft spots: card condition grading, fair-price opinion, investor yield estimate. All
three present an AI opinion in the grammar of a fact. Yield in particular reads as financial
advice. These are the three AMBER warnings `human_seam_check.py` prints today.

### 4. The narrative failure
Klarna's most expensive loss was not operational, it was **narrative**: they went to the
public market on an AI-first thesis and reversed within ten weeks. The reversal was more
damaging than the original error.

For MarketSquare this cuts two ways. **PR-5: no public claim the machinery cannot yet honour.**
And **PR-6: hiring humans is a planned milestone, not a retreat.** Because we are AI-first *by
design* rather than by cost-cutting, adding a verification reviewer at a declared trigger is
the design *working*. Say so in advance, in the copy and internally, so the first hire never
reads as a U-turn. Klarna could not say this because they had already said the opposite.

---

## The pre-design rules (canon)

| | Rule | In one line |
|---|---|---|
| **PR-1** | Parallel run, never a switch-over | Both systems run and are compared under real load before the old one is decommissioned |
| **PR-2** | The seam is built empty | Every RED and AMBER surface names its human role and measurable trigger *before* a human exists |
| **PR-3** | Never remove the fallback and add the AI in the same change | One change at a time; the old lane stays until the new one has proven itself in production |
| **PR-4** | Run the Dragon Tail test on every new information surface | Write down what a purely self-interested actor does with it, or do not ship it |
| **PR-5** | No public claim the machinery cannot yet honour | Extend the vendor-neutral copy discipline (RG-0035) to capability claims |
| **PR-6** | Hiring humans is a planned milestone, not a retreat | Declared in advance, so the first hire is never read as a Klarna-style reversal |

---

## What is asserted, and how

`scripts/human_seam_check.py` reads `HUMAN_SEAM_REGISTER.json` and fails if:

- any surface is missing a field, or carries a blank one (a blank reads as answered);
- any **RED** surface — where a wrong answer cannot be undone by a refund — has no named
  human role, no measurable trigger, or no machine fallback;
- any declared information leak has no owner-action;
- any of PR-1…PR-6 has gone missing from the register.

AMBER gaps print as WARN and are the work queue; `--strict` promotes them to FAIL.

Current state: **14 surfaces — 5 RED, 7 AMBER, 2 GREEN. 9 of 14 seams built. 0 FAIL,
3 WARN.** The three warnings are HS-05 card grading, HS-06 price check, HS-07 yield estimate.

---

## The honest gap

`MAINTENANCE_AGENT.md` records the 29 Jul 2026 ruling: **TOTAL AUTONOMY, NO VETO** for the
fix agent. The human gate was deliberately retired as a single point of failure and replaced
by mechanical gates — ledger, predeploy, BIT, server auto-rollback, refuse-markers.

That reasoning is sound *while the mechanical gates are provably complete*. It is the highest
blast-radius surface in the system, and the video's whole argument is that the gate you removed
is the one you needed. **The condition to hold onto: any gate that stops asserting re-arms the
veto.** That is not a reversal of the ruling — it is the ruling's own premise, written down so
a future session cannot quietly lose it.

---

## Next actions, in order

1. **Authenticate `GET /tuppence/balance`** before the edge gate lifts. Launch blocker (IL-01).
2. **Decouple boost from relevance** — visibility up, threshold untouched (IL-03).
3. **Label the three opinion surfaces** — grading, price, yield — as AI-assisted estimates with
   a dispute or agency hand-off route (HS-05/06/07). This clears the three WARNs.
4. **Gate referrals on evidence** before the lane goes live (IL-02).
5. **Add ledger entries** for 1–4 so each fix is locked and cannot rot.
6. **Run `human_seam_check.py` alongside the regression ledger** each session.
