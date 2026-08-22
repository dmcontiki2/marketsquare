## 2026-08-22 — Travelpayouts tours review resubmitted, and the token found to be unrotatable

**Resubmitted (RUL-041).** OPEN_LOOPS D10 had reserved the resubmit moment to David — scheduled
1 Sep, "earlier on David's word". He gave it. The project went back for review on 22 Aug with
`/flags` reporting `mode: live`, the gate down (RUL-029/034) and the 5 Aug objection —
*"website under development or not yet ready"* — answered by real change: EULA v1.14 live,
the honesty labelling built, the site publicly reachable. 26 programs auto-connect on approval,
including GetYourGuide, Viator and Booking.com, at ~8% commission against 1.1-1.3% on flights.
Timing was the argument for going now rather than waiting: a few days' review lands approval
near SOFT LAUNCH (29 Aug) instead of starting the clock after it.

**The decision inside it.** RUL-040's labelling — AI EXAMPLE GENERATED ADVERT ribbons, "not a
real listing" pills, red DEMO tabs — is not yet live (RG-0140/0141 both report their live halves
failing, pending deploy). It is also *exactly* what "not ready" looks like to a reviewer. Claude's
call, put to David in business terms and agreed: **submit now, do not hold the deploy.** The labels
exist because an exemplar must never be mistaken for a buyable listing. An affiliate reviewer's
impression does not outrank a promise to buyers, and a decline on those grounds gets answered in
writing rather than by hiding the label.

**TRAVELPAYOUTS_TOKEN cannot be rotated.** Checked on the page during the secret rotation
(Programs → Aviasales → API): one permanent token per account, a copy button and nothing else —
no regenerate, no roll, no second token. It is therefore moved from "still burnt" to
**UNROTATABLE-ACCEPTED** in `SECRETS_REGISTER.md`, with the reasoning recorded: read-only cached
fare data, no customer data, no money, no write path, no billing exposure (marker 758984, no
contract), server-side only, and RG-0025 already forbids any TP script on app pages so it cannot
leak through the front end again. Quota exhaustion degrades exactly the way the SUPPLIER FALLBACK
DOCTRINE already handles — no indicative fare, fall back to the agency card.

**RG-0146 was strengthened rather than allowed to go quieter.** Moving a row out of "still burnt"
would otherwise reduce the red count for free, so the entry now polices the new category: an
UNROTATABLE row must carry a DATED decision and real reasoning, or it fails as "a burnt credential
with a nicer label".
