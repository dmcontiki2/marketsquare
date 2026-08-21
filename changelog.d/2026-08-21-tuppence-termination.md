## 2026-08-21 — EULA §6.3/§14: Tuppence is RETAINED on termination, not forfeited (fraud excepted)

David, from memory: "we do not forfeit a terminated user's Tuppence, it is kept for a period
and will even be available again to that same user if he signs up again — but to comply with
not being a financial institution we cannot convert it back to money and pay it out."

Checked against disk. He was right on the principle and the EULA was the outlier:
- **Canon agreed with David** — LOCAL_MARKET_REQUIREMENTS.md LM-14b: "Purchased Tuppence is
  never confiscated — it was bought with real money," restored in full on reinstatement.
- **The code agreed with David** — no user-termination path touches Tuppence at all; the only
  sweep (monthly grant reset) explicitly never touches purchased or earned Tuppence.
- **The EULA disagreed** — forfeiture in FOUR places: §6.3 bullet, §14.1 (user closes),
  §14.2 (breach), §14.3 (Platform terminates for convenience). §14.3 was the sharp one: we
  took purchased credit when WE ended the relationship and the user had done nothing wrong.

Root cause of the drift: the "frozen, restored on return" rule was written for SUSPENSION
(LM-14b) and the equivalent was never written for TERMINATION, so older forfeiture language
survived there.

CHANGED (David's express ruling, incl. keeping fraud forfeiture):
- §14.1 — retained, not converted to cash; restored in full on re-registration with the same
  verified identity within 24 months; no payment on closure.
- §14.2 — forfeiture ONLY under B5 (payment fraud/chargeback abuse) and B6 (identity fraud).
  Every other breach cause: retained, restored on reinstatement. Never converted to cash.
- §14.3 — retained 24 months, restored in full on re-registration; states expressly that
  because the Platform and not the user ended the agreement, no Tuppence is forfeited.
- §6.3 — the termination-for-convenience bullet rewritten to match §14.3.

UNTOUCHED AND LOAD-BEARING: "Tuppence is not redeemable for cash under any circumstances."
Retention is continued access to a non-monetary service credit, not a right of repayment, so
the Banks Act deposit-definition protection is unaffected (BACKLOG O2, CCP_FABLE_RUN_PROMPT).

Also resolves the OpenAI peer review's §14 BLOCKER for France and Portugal on better ground
than a savings clause: "retain, restore on return, never cash out" is materially more
defensible under EU consumer law than forfeiture.

STILL OPEN (flagged, not fixed here): the 24-month dormancy expiry and its promised 30-day
pre-expiry email are declared in §6.3 but NOT IMPLEMENTED anywhere in the code. That promise
predates this change (it was already live in v1.13), so publishing does not increase exposure
— but it is a commitment we currently cannot keep, and now the retention model leans on the
same 24-month clock. Either build the sweep + notice, or drop the promise.

Synced across eula_clean.html, terms.html and ms.js via scripts/eula_sync.py (--check green,
113,253 bytes identical); RG-0077 green.
