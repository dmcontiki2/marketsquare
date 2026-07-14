# Reply to Paystack (Evelyn) — wallet questions of 9 Jul 2026
Drafted 13 Jul 2026. Every claim verified against PRICING_CANON.md, FINANCE_CANON.md, bea_main.py and the live Terms. Gmail draft created in-thread, ready to send.

---

Dear Evelyn,

Thank you for the follow-up — happy to set out the wallet mechanics in full. The headline, expanding on Section 5 of our 5 July response: the "wallet" is not a monetary wallet. It is a closed-loop balance of prepaid service credits ("Tuppence", fixed at 1T = US$2) that can only be consumed against TrustSquare's own services and can never be converted back into money by any path. TrustSquare is the only merchant in every transaction, and no value can exit the platform to a user.

Taking your four questions in turn:

1. HOW USERS FUND THEIR BALANCE

There is one funding route: an ordinary first-party card payment to Trustsquare (Pty) Ltd through Paystack checkout, via the in-app "Buy Pack" flow. Packs start at 1 Tuppence (US$2, charged in rand at R36). The minimum purchase is therefore R36; we impose no separate maximum of our own — each top-up is a standard Paystack transaction subject to Paystack's normal transaction limits, and the product gives users no reason to hold large balances: an introduction costs 1T and our most expensive AI feature is capped at 5T. If your team would prefer a formal per-transaction or monthly top-up cap, it is a one-line change on our side — happy to implement whatever you recommend.

Credits are applied only after Paystack confirms the payment (webhook plus server-side verification), with idempotent processing — a payment reference can never be credited twice. The only other issuance route is the monthly allowance included in our paid subscription plans (Starter US$5/mo includes 2T; Pro US$20/mo includes 10T). Plan allowances refresh monthly and do not accumulate; purchased Tuppence is never swept and has no expiry.

2. HOW TUPPENCE IS ISSUED, TRACKED AND SPENT

Every unit of Tuppence in existence was either paid for through Paystack or granted with a paid plan — there is no other minting path, and our payment gate is fail-closed in code: test-mode keys cannot credit real balances.

Every movement is recorded in an append-only transaction ledger — credit, hold, settle (burn), release — with each purchase keyed to its Paystack reference, so every balance movement traces back to a specific confirmed payment and reconciles one-to-one against Paystack settlement reports and our FNB corporate account statements.

Spending works on a hold-and-deliver model. An introduction costs 1T: the Tuppence is held when the buyer requests the introduction and burned only when it is delivered (the seller accepts); if the seller declines or does not respond within 48 hours, the hold is released automatically and the buyer has spent nothing. AI features are priced per use (free up to a 5T cap), with the price displayed before the user confirms; if a run fails, the hold is released and no Tuppence is used.

Our accounting mirrors this: Tuppence sold is carried as a liability (unearned revenue) and recognised as income only when the service is actually delivered.

3. WITHDRAWAL, TRANSFER OR REDEMPTION FOR CASH OR OTHER VALUE

There is no scenario — none — in which a user can withdraw, transfer or redeem Tuppence for cash or any other value. Tuppence is non-withdrawable, non-transferable between users (no user-to-user transfer endpoint exists in our API — it is impossible by construction, not merely prohibited by policy), non-redeemable, and strictly non-refundable (Terms of Use §5.2, §5.6 and §12). A released hold returns unspent Tuppence to the user's balance — never cash. Money flows one way only: customer to Trustsquare (Pty) Ltd to our FNB corporate account. Tuppence is prepaid consideration for platform services — not a deposit, not stored funds, and not a financial product or instrument.

4. COMPLIANCE AND CONSUMER PROTECTION MEASURES

- Charge-on-delivery by design: a buyer's credit is only consumed when the paid service is actually delivered (see the hold model above).
- Fixed, transparent pricing: 1T = US$2, and every paid action shows its price before the user confirms.
- Balances are never confiscated on account suspension — they are frozen and restored in full on reinstatement.
- Full audit trail: the append-only ledger records every credit, hold, burn and release, tied to Paystack references.
- Terms of Use: the Consumer Protection Act override (§10) expressly preserves all statutory consumer rights; the ECT Act cooling-off position is addressed at §5.4; privacy is governed by our POPIA policy at trustsquare.co/privacy.
- Because the credits are closed-loop, first-party and non-redeemable, the wallet holds no customer funds — no deposit-taking, stored-value or e-money activity arises.
- Finally, while we are in gated pre-launch, paid spending is enabled only for a small set of internal test accounts — so this review is running ahead of any live customer exposure.

ON TIMING

May I also, respectfully, flag where this review now sits for us. Our activation request has been in review since early May — our KYC response went in on 11 May — and we have answered each round of questions within a day or two of receiving it. TrustSquare's public launch is gated on this activation: our founding sellers are onboarded and waiting, and each additional round of questions moves their launch back. I appreciate that your team must be thorough, and I hope the detail above closes out the wallet topic completely. If anything further is needed, could I ask that remaining points be consolidated into a single list — or, if quicker, I would gladly take a short call with your compliance team this week to resolve everything in one pass. An indication of the expected completion date following this response would be greatly appreciated.

The reviewer access code (TSR-86HV-ZR33) remains available to your team; it is time-limited, so if it expires before the review concludes, just say and I will reissue it.

Best regards,

David Conradie
Trustsquare (Pty) Ltd · Reg 2026/340128/07
