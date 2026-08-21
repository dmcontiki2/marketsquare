# Tuppence on termination — canon vs EULA reconciliation
**21 Aug 2026 · raised by David from memory · checked against disk · NOT YET APPLIED**

## What David remembered
"We do not forfeit a terminated user's Tuppence, it is kept for a period in accordance
with some regulations, and will even be available again to that same user if he signs up
again. But to comply with not being a financial institution, we cannot convert the
Tuppence back to money and pay it out."

## What is actually on disk — three layers, and they disagree

### 1. The principle (matches David) — LOCAL_MARKET_REQUIREMENTS.md
- **LM-14b:** "A suspended seller's Tuppence balance is **frozen but not forfeited**.
  **Purchased Tuppence is never confiscated — it was bought with real money.** The balance
  is restored in full when the seller restores their Trust Score above 30."
- **§359:** "Tuppence may be suspended (frozen) ... but is **never forfeited**. Frozen
  Tuppence is **restored automatically when the account is reinstated**."

### 2. The no-cash-out rule (matches David) — EULA §6.3, and it is load-bearing
- "Tuppence is not redeemable for cash under any circumstances." No interest. No seller
  settlement outside the introduction flow.
- BACKLOG O2 records why: "the no-refund / no-deposit / burn-on-service design is the
  load-bearing protection." CHANGELOG (Banks Act note): a contractual right of repayment
  would push Tuppence toward the statutory definition of a **deposit**.
- CCP_FABLE_RUN_PROMPT.md: "Never add, suggest, or implement any Tuppence refund /
  reversal / release-of-funds-back-to-buyer mechanism. Non-refundability is load-bearing
  (Banks Act + patent + CPA)."
- **David is exactly right here. This must not be touched.**

### 3. The retention period (matches David, directionally) — EULA §6.3
- "Unused Tuppence expires after **24 consecutive months of account inactivity** (no login,
  no Introduction, no purchase). The Platform will notify you by email **not less than 30
  days before expiry**."
- This is the "kept for a period" David remembered. It is dormancy, not termination.

### 4. WHERE THE EULA CONTRADICTS THE PRINCIPLE — the actual defect
The EULA forfeits unused Tuppence on **termination**, in three separate places:
- **§14.1 (user closes their own account):** "All unused Tuppence is forfeited (non-refundable)"
- **§14.2 (termination for breach):** "Upon termination for breach, all unused Tuppence is forfeited."
- **§14.3 (Platform terminates for CONVENIENCE, 30 days' notice, no fault by the user):**
  "all unused Tuppence in your account is forfeited."
- **§6.3** repeats it: "The Platform terminates your account for convenience under Section
  14.3 — unused Tuppence is forfeited."

§14.3 is the sharp one: **we take the user's purchased credit when WE end the relationship
for our own convenience and they have done nothing wrong.** That directly contradicts
LM-14b's "purchased Tuppence is never confiscated — it was bought with real money."

### 5. What the CODE does
- **No user-termination path touches Tuppence at all.** (`/admin/users/{id}` DELETE is for
  admin team members, not marketplace users.)
- **The 24-month dormancy expiry is NOT IMPLEMENTED** — no dormancy sweep, no 30-day notice
  job. We publish a promise to email before expiry that nothing on disk can keep.
- The only sweep that exists is the **monthly grant reset** (`grant_expiry`), which
  explicitly never touches purchased or earned Tuppence — i.e. the code already follows the
  "never confiscate what was bought" principle.

**So the code is on David's side; the EULA is the outlier.**

## Why fixing this HELPS the peer's BLOCKER
The OpenAI peer flagged §14 forfeiture as its BLOCKER for France and Portugal. Its concern
was EU consumer law. Aligning the EULA to our own canon resolves it on better ground:
a "retain, restore on return, never cash out" model is far more defensible under EU
consumer law than forfeiture — and it does NOT create a right of repayment, so the Banks
Act protection is untouched. Retention is not a deposit; it is continued access to a
non-monetary service credit.

## Proposed replacements — NOT APPLIED, awaiting David's go

**§14.1 — replace** "All unused Tuppence is forfeited (non-refundable);"
> Unused Tuppence is retained on your account record and is not converted to cash. If you
> register again using the same verified identity within 24 months, your retained balance is
> restored to you in full. Tuppence is not redeemable for cash or ZAR under any circumstance,
> and no payment is made to you on closure.

**§14.2 — replace** "Upon termination for breach, all unused Tuppence is forfeited."
> Upon termination for breach under B5 (payment fraud or chargeback abuse) or B6 (identity
> fraud), unused Tuppence is forfeited. On termination for breach under any other cause,
> unused Tuppence is retained and is restored if the account is reinstated. In no case is
> Tuppence converted to cash.

**§14.3 — replace** "all unused Tuppence in your account is forfeited."
> your unused Tuppence is retained for 24 months and is restored in full if you register
> again using the same verified identity. Tuppence is not redeemable for cash or ZAR under
> any circumstances. Because the Platform, not you, ended the agreement, no Tuppence is
> forfeited.

**§6.3 — replace** the termination-for-convenience bullet to match §14.3.

**Also needed (build item, not drafting):** implement the 24-month dormancy sweep and the
30-day pre-expiry email, or remove that promise from §6.3. Publishing a notice commitment
we cannot execute is worse than not promising it.

## Open question for David / counsel
Should breach-termination under B5/B6 (payment fraud, identity fraud) still forfeit? The
draft above says yes — confiscating credit obtained through fraud is a different act from
confiscating credit bought honestly. If David wants NO forfeiture in any circumstance, §14.2
simplifies further.
