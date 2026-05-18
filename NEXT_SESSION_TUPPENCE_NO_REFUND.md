# Next-Session Action: Purge Tuppence Refund Language

**Created:** 2026-05-12 (Session in progress)
**Priority:** HIGH — execute before patent filing and before public launch
**Owner:** Architect agent (rule arbitration) → Frontend / Admin agents (execution)
**Estimated effort:** 1 focused session

---

## The policy (canonical)

**Tuppence is non-refundable under any circumstance, in any form, ever.**

This is not a negotiation. It is a load-bearing design decision with four independent justifications:

1. **Commitment signal integrity.** A refundable Tuppence is not a commitment signal. The "buyer pays to contact" mechanic is the spam filter; if every unsuccessful intro is refunded, there is no cost to spamming.
2. **Banks Act safety.** A "conditional repayment of money paid" is the statutory definition of a deposit under s 1 of the Banks Act 94 of 1990. Removing every refund mechanism removes every Banks Act argument. SARB cannot reach what does not exist.
3. **Patent novelty.** Claim 2 of the provisional recites "atomic restitution-on-decline" as a distinguishing feature against Bark.com. We are dropping this from the claim — the novelty argument repositions onto buyer-side spend + no inter-user transfer endpoint, both of which remain strong differentiators.
4. **Operational simplicity.** No refund queue, no FICA-failure handling code, no cooling-off accounting, no seller-closure buyer-credit logic. The simplest possible product.

The canonical statement of the policy already lives in `LOCAL_MARKET_REQUIREMENTS.md` §11.1 (lines 357-359):

> Tuppence is a platform introduction currency purchased with real money. Tuppence balances are non-refundable in cash under any circumstances. Tuppence may be suspended (frozen) if a seller's account is suspended due to Trust Score violations, but is never forfeited. Frozen Tuppence is restored automatically when the account is reinstated.

Everywhere else in the codebase that contradicts this must be brought into alignment.

---

## Inventory of leaks (current state, 12 May 2026)

### EULA v1.0 Draft (currently in `uploads/`, not yet in repo)
| Line | Current text | Status |
|---|---|---|
| L126 | "If the Seller declines or does not respond within the applicable window, the 1T is refunded to the Buyer's account." | DELETE / REWRITE |
| L145 | "Upon cancellation within 7 days, the 1T charged is refunded to your account within 3 business days." | DELETE / REWRITE |
| L155 | "6. Fees, Refunds, Subscriptions & Payment" — section header | RENAME to "6. Fees, Subscriptions & Payment" |
| L167 | "6.3 Refunds" — sub-section header | DELETE entire sub-section |
| L168-174 | Five-bullet enumeration of refund circumstances | DELETE all five bullets |
| L385 | "All unused Tuppence is forfeited (non-refundable);" | KEEP — this is the correct stance |
| L388 | "Buyers with open Introduction requests are notified that the Seller is no longer available and Tuppence is refunded." | DELETE / REWRITE — buyer Tuppence remains spent; the listing closure does not trigger refund |
| L498 | "AI Feature Tuppence is non-refundable once an AI interaction is completed and a response is delivered, except where a material technical fault prevented delivery of the response." | NARROW — remove the technical-fault exception |

### Whitepaper v3
| Line | Current text | Status |
|---|---|---|
| L31 | "Burned on introduction request (non-refundable unless seller declines — partial refund policy)" | REWRITE: "Burned on introduction request; non-refundable under any circumstance. Buyer commitment signal is the price of contact." |

### marketsquare.html (buyer app — DO NOT use Edit/Write tool; Python open/replace only)
| Line | Current text | Status |
|---|---|---|
| L3056 | FICA-failure refund language | REWRITE: "If verification fails or is not completed, the Introduction is cancelled. Tuppence already spent remains spent." |
| L3097 | "If the Seller declines or does not respond ... the 1T is refunded to the Buyer's account." | REWRITE: "If the Seller declines or does not respond within the applicable window, the Introduction closes. Tuppence spent on the request is consumed and is not refundable. This is the platform's spam-prevention mechanism." |
| L3140 | 7-day cooling-off refund | DELETE the sentence about refund timing; CPA s 16 does not apply (user-initiated purchase, not direct marketing) |
| L3155-3156 | AI feature refund | NARROW: AI feature Tuppence is non-refundable under any circumstance. |
| L3165 | "6. Fees, Refunds, Subscriptions & Payment" | RENAME to "6. Fees, Subscriptions & Payment" |
| L3184-3191 | §6.3 Refunds | DELETE entire section. Replace with one paragraph: "**6.3 No Refunds.** Tuppence is non-refundable, non-transferable, and non-redeemable for cash, goods or services other than the platform Introduction feature. Spending Tuppence on an Introduction request consumes the Tuppence regardless of the outcome. This is the consideration for the buyer-commitment signal that underpins the platform's anti-spam design." |
| L3461 | "Tuppence is refunded" on seller account closure | REWRITE: "Buyers with open Introduction requests are notified that the Seller is no longer available. Tuppence spent on closed Introductions is consumed; no refund is issued." |

### marketsquare_admin.html
| Line | Status |
|---|---|
| L1298, L1302 | **No change** — already says "non-refundable platform currency" and "non-refundable if you decline or ignore" (seller-pays-on-receive model in Local Market). |

### Backend
No changes required. `bea_main.py` does not implement any refund path. The `tuppence_ledger` table accepts deltas of any sign but the code never writes a positive delta on intro decline. Confirmed by grep on 12 May 2026.

---

## Consumer Protection Act 68 of 2008 — defence notes

A reviewer may ask whether the CPA forces refunds. It does not, on the present design:

- **s 16 cooling-off right** applies only to "direct marketing" transactions (where the supplier initiates contact with the consumer). Tuppence purchases occur when a user voluntarily visits trustsquare.co; s 16 does not apply.
- **s 54 implied warranty for services** requires "timely performance" and "quality of services". The platform's service is the issuance of an Introduction request to the seller. That service is delivered the moment the seller receives the notification. The seller's decline is not a failure of the platform's service.
- **s 56 implied warranty for goods** does not apply — Tuppence is a platform service credit, not goods.
- **s 47 unfair pricing / oppressive terms** would only bite if a court found the no-refund rule "unconscionable". The defence: the price per Introduction is low (~R5-R10), the buyer is informed before spending (anonymous browsing + Trust Score), the rule is uniform (applies to everyone equally), and the rule serves a legitimate platform purpose (spam prevention). This is not unconscionable on any reasonable test.

The EULA should include an express CPA acknowledgement: "I understand that Tuppence is a service credit, not goods, and is non-refundable. I acknowledge that this is the consideration for the platform's anti-spam Introduction-gating service."

---

## Execution sequence (next session)

1. **EULA first.** It is the legal artefact. Strip §6.3 entirely, rewrite the disclosed clauses per the inventory above. Save the cleaned EULA as `MarketSquare_EULA_v1_1_Final.docx` and commit.
2. **Whitepaper second.** One-line edit on L31. Re-version to v3.1.
3. **Buyer app HTML third.** Use Python `open/replace/write` (never Edit tool on marketsquare.html). After each replace, verify the file still ends with `</html>` per the existing rule. Six discrete edits; do them as one focused session.
4. **Provisional patent claims.** When the redrafted Claim 2 is being lodged, ensure clause (e) (restitution logic) is removed. The amended claim language in the Pre-Filing Patent Consultation memo at §8.2 includes this clause — it must be dropped. The novelty argument is unaffected; the differentiation rests on (a) buyer-side spend, (b) absence of any inter-user transfer endpoint, and (c) trust score input. All three remain.
5. **CHANGELOG entry.** "Removed all Tuppence refund language across EULA, whitepaper, and buyer app. Confirmed BEA backend implements no refund path. Tuppence is now strictly non-refundable in all circumstances. Cost model impact: none (BEA already implements this; revenue recognition simplifies)."
6. **Update Pre-Filing Patent Consultation memo.** Section 5.3 Banks Act analysis must be updated — the "partial-refund-on-decline" risk no longer exists. The opinion strengthens from "LOW RISK (but not no risk)" to "NO RISK on the refund vector". Issue as an Erratum to the original memorandum so the handover packet to Adams & Adams / Spoor & Fisher contains both.

---

## Definition of done

- [ ] EULA v1.1 saved, contains zero refund clauses
- [ ] Whitepaper v3.1 line 31 rewritten
- [ ] `marketsquare.html` six edits applied; file ends with `</html>`; node --check passes on inline scripts
- [ ] Patent memo Section 5.3 updated as Erratum
- [ ] CHANGELOG and STATUS updated
- [ ] git committed (from PowerShell, per CLAUDE.md rule)
- [ ] Live BEA: `tuppence_ledger` audited for any historic refund entries — should be zero; if non-zero, escalate

---

*This action is the load-bearing pre-launch cleanup. Do not file the provisional patent or publish the EULA externally until this is complete.*
