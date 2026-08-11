## 2026-08-11 — The probe tripped the guard, and the guard was right

- **What happened:** the first real-repo probe run returned
  `PROBE-MECH -> ESCALATE (touches a protected surface (card))`. The probe's own fault text said
  *"when I tap a card"* — meaning a listing card. `card` is a **payment** marker. The refuse
  guard escalated the whole thing and the patch path was never exercised.
- **Measured before reacting.** Across all 30 real faults in the live queue, substring matching
  produces exactly **one** difference from word-boundary matching — `anonym` inside `anonymity`,
  which is semantically correct anyway. The standalone word `card` appears **zero** times in the
  real corpus, in either sense. So this was the probe's unlucky wording, not a guard defect.
- **Deliberately NOT fixed by narrowing the marker.** The tempting change was `card` →
  `credit card|debit card|card number`. Rejected: over-refusing costs a human glance;
  under-refusing costs a payment surface. Weakening a guard so that one's own test passes is
  the same error as arming past a red rehearsal, which was refused earlier today. The probe was
  reworded instead, and every string in `DEFECTS` is now checked against the full marker list
  before use — both targets verified clean.
- **The probe now distinguishes INVALID from FAIL.** An `ESCALATE` result means the guard ate
  the probe's wording and the patch path was never reached — that is the guard working, not a
  verdict on patch quality. It says so and tells you to reword, rather than reporting a failure
  the agent never had a chance to avoid.
- Also fixed: seven literal `\n` sequences leaking into the probe's output (heredoc escaping).
- **Latent risk worth noting, not acting on yet:** this app's entire browse UI is built from
  "cards". A tester who writes "the card doesn't show the price" will be escalated as a payment
  issue. It has not happened in 30 faults. Word-boundary matching would be a pure win for
  `tax`/`syntax`, `vat`/`private`, `auth`/`author` — none of which has occurred either. Worth
  doing when there is evidence, not on speculation.
