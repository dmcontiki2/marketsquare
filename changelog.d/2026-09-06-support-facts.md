## 2026-09-06 — SUPPORT-FACTS-1 + REF-HONESTY-1: the support AI was answering a money question from a guess

**Found by reading the reply we actually sent.** TS-0039 asked: *"how do I contact a seller about a
listing I am interested in? I cannot find a phone number anywhere on the listing page."* The AI
answered, and yesterday's record called that answer *"correct product behaviour"*. Half of it was.

**The half that was right.** It withheld the phone number and explained that sellers are anonymous.
That is the product working, and the listing page agrees: the detail screen carries a sticky
`Request Introduction · 1T on acceptance` button and a lock block reading *"Identity protected until
introduction"*. Nothing is missing from that page.

**The half that was wrong, and it was wrong about money.** It told the buyer to *"follow the prompts
to spend Tuppence"*. The app's own modal, two taps away, says **"1 Tuppence ($2) deducted only on
seller acceptance"** and **"If seller declines or ignores, you pay nothing"** — and EULA §5.4 says the
same in law: the Tuppence is HELD on request, BURNED only on delivery. So a buyer asking how to make
contact was told the charge is unconditional when it is not.

**It is wrong in our own favour, which is the direction that matters.** A buyer who believes they
must pay before anyone answers may simply not send the request, and we would never hear about it.
The pricing is the kindest thing about this product and the robot made it sound worse than it is.

**Why it guessed: the customer lane had no facts.** OUTREACH-TRIAGE-1 gave the *outreach* lane a
market-facts block and a set of universal facts on 1 Sep. The **customer** lane — the one answering
actual customers — got one sentence of context and was told to answer support questions. An AI with
no facts does not decline; it produces something fluent. Fixed: the customer prompt now carries the
introduction mechanics (anonymity by design, the button's real name, hold-not-charge, release on
decline or 48-hour silence, free listing, the withdraw route), a standing instruction never to tell
a buyer they must spend Tuppence to make contact, and an order to set `auto_safe=false` rather than
invent a fact that is not there. Asserted by **RG-0303 (LOCKED)**.

**Second fault in the same email — we promised a fix to someone who reported nothing.** Every
auto-sent reply ended with *"your report is logged in our fix queue. If our fix needs anything from
you, we'll write to this address."* TS-0039 filed no report. Nothing was broken, no fix was queued,
and nobody was ever going to write.

**The reasoning was already five days old and one branch away.** OUTREACH-TRIAGE-1 carved this exact
footer out of the outreach lane on 1 Sep with the comment *"a tutor asking whether we cover
Johannesburg has not filed a fault"*. A customer asking how introductions work has not filed one
either — it was written as a special case for one lane instead of as the rule. It also manufactures
the load RUL-087 exists to prevent: a promised fix invites the email asking what happened to it.

Fixed by `_ref_footer()`: the classifier now returns `is_report`, true only when someone reports
something broken, and the footer picks its wording. The reference is kept either way — MAINT-B1
promised a *reference*, not a fix pledge. **Fails safe**: no signal means the neutral line, because
its failure mode is being plain and the other's is a lie. The bare acknowledgement is covered too,
since a held legal complaint is not a fix-queue item. Asserted by **RG-0304 (LOCKED)**.

**Ledger note, recorded rather than tidied away.** RG-0303's first cut failed on its own fix: it
read raw source, where a sentence spanning two adjacent string literals is not one string. A false
RED costs a session exactly what a missed one does. The assertion now joins the literals before
checking, and the entry says so.

**The reading lesson.** Yesterday's proof read the phone-number half, found it right, and logged the
whole reply as correct. One half of an answer being right is not evidence about the other half —
especially when the other half states a price.
