## 2026-09-01 — Child-safety screening: what is actually POSSIBLE, and the word we must never use

David: *"we should also preferably be able to establish if any listing tutor or teacher ... not be
on any governmental furnished pedophile/child molesters databases?"* Right instinct. Searched, not
recalled, because a confident wrong answer here would be the most damaging kind.

**The direct answer is NO in three of our four markets — and the "no" is deliberate policy, not an
oversight we can route around.**

- **South Africa** (launch market): the NRSO is **closed by statute** — confidential, not public.
  Employers in schools, crèches and hospitals may check; a marketplace may not. Minister Kubayi has
  a THREE-PHASE plan to widen it (phase 2 = institutions working directly with children, phase 3 =
  employers generally), but the Chief State Law Adviser's constitutionality opinion on public
  access had not been obtained as at the Apr 2026 reporting. Direction of travel is favourable;
  today it is shut. Sibling register: the NCPR under the Children's Act.
- **UK**: there is **no public sex offender register, by design**. Sarah's Law (Child Sex Offender
  Disclosure Scheme) is police-mediated, requires a SPECIFIC named person AND a SPECIFIC child, and
  disclosure goes only to the parent/guardian/carer best placed to protect that child. General
  enquiries are expressly refused. A platform can never be the applicant.
- **Australia**: ANCOR is **police-only**; there is no publicly accessible registry. WA's Community
  Protection Website offers limited disclosure in defined circumstances only — not a screening tool.
- **United States**: NSOPW **is** genuinely public — and its Conditions of Use **strictly prohibit
  automated searching**. So no scraper, no API lane, and the commercial-screening restrictions must
  be read directly before any use at all.

**THE RESOLUTION, and it is better than what was asked for:** we do not need register access,
because the CLEARANCE IS THE REGISTER CHECK — performed by the state, on our behalf, lawfully.

- UK **Enhanced DBS with barred-list check** = the state has checked the Children's Barred List.
- AU **WWCC / Blue Card** = state criminal-history check PLUS continuous monitoring — a holder
  charged after issue has the clearance revoked, which a one-off register lookup could never catch.
- SA = the sector-clearance route today, widening under the NRSO phases above.

Holder-consented, lawful for us to receive, continuously re-verified, and already the credential
parents recognise. Strictly better than a scrape, and it needs no register access at all.

**PRODUCT INVARIANT — the word "safe" is banned from any listing surface.** David's framing was
*"classifying as safe based on our assessment of what they upload."* We must not. "Safe", "vetted",
"child-safe" and every synonym are representations about a person's FUTURE CONDUCT. If a tutor
carrying our "safe" badge harms a child, that badge is the plaintiff's first exhibit. The defensible
pattern is a DATED, SOURCED FACT — never a conclusion:

- CORRECT: "WWCC 1234567E — verified current with NSW Office of the Children's Guardian, 1 Sep 2026"
- CORRECT: "Teaching qualification certificate uploaded — not independently verified"
- BANNED:  "Safe" · "Vetted" · "Child-safe verified" · "Background checked" (unqualified)

**Also banned: a "not on the register" badge.** Absence of a record is not evidence of safety; it is
unprovable, and asserting it invites both a negligence claim and a defamation claim from anyone we
get wrong. We state what we verified, with its date and its source, and nothing beyond it.

Needs to become a RULING — David's act (RUL-037). Recorded here so no session invents a "safe"
badge in the meantime; RG-0237 makes it a tripwire.


## RUL-088 — a Trust Score is a SCORE, never a statement of fact about a person

David, same session, drawing the line himself: *"a trust score is based on given information, some
verified and some searched, but never with enough concrete and irrefutable backed up evidence to
state it as a fact. It is a 'Score' and not a statement of fact."*

Seven consequences, recorded so they are buildable rather than merely agreed:

1. **The score is the artefact** — a number and its inputs, never an adjective about the person.
2. **It must be decomposable on the surface where it appears.** A score whose inputs are hidden is
   a verdict wearing a number, which is precisely what this bars.
3. **Every input carries its evidence grade** — the ladder applied to trust:
   verified-against-a-named-source-with-a-date · attested-by-seller-unverified ·
   inferred/searched-unconfirmed · absent. A score mixing grades must show them.
4. **No band may be named for a quality of the person.** Bands name the EVIDENCE — "ID, phone and
   address verified" — not the character.
5. **No threshold unlocks safety language.** A 100 is still not a statement that a person is safe.
6. **A low score means LITTLE EVIDENCE SUPPLIED, never suspicion**, and is never surfaced to a
   buyer as an accusation. Absence of evidence reads as absence of evidence — the mirror of the
   barred "not on the register" badge, and the defamation guard of this ruling.
7. **A score is a dated snapshot that can go down.** Never "certified", never permanent.

**Found live the same day.** The score itself is built correctly — `trust_score` column, buyer-side
filtering, 87 references in `ms.js`. But the 90–100 band ships as **"Highly Trusted"**, with copy
reading *"Highly Trusted sellers have verified ID, phone, and…"*. That is a verdict about people
sitting on top of an honest score — the exact confusion this ruling separates. The band keeps its
gold tier, its filter and its "recommended for high-value items" role; it gets **renamed for what
was evidenced** rather than for a judgement of the human being.
