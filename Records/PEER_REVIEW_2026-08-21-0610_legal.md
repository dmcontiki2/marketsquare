# Independent Peer Review — 2026-08-21-0610

*Peer: gpt-5.6-luna (second vendor, read-only) · Lens: legal · Author: Claude · System Engineer: David*

**Scope:**
  - /tmp/eula_extract.md (35,205 chars)

**Usage:** 8193 in / 9185 out tokens · actual cost ≈ $0.0127

---

# Peer-review report — Legal / regulatory assessment

**Scope and status.** This is a second independent reading of the supplied extract, not legal advice, a legal opinion, or approval for launch. I have assessed the schedules and their interaction with the body, against law understood to be in force as at **21 August 2026**. Several points require confirmation by counsel in the relevant jurisdiction, particularly current French, Portuguese and Argentine administrative guidance.

## Executive conclusion

Schedules D–G do **not** presently achieve their stated objective of automatically preserving the mandatory protections of the consumer’s home country.

The most serious issues are:

1. **The prepaid Tuppence forfeiture is highly vulnerable in France and Portugal**, especially on platform termination for convenience under Section 14.3. The schedules do not cure it.
2. **The arbitration provisions remain materially defective.** D8/E9/G6 are savings clauses, not reliable exclusions of mandatory consumer court access, and G6 appears to cite the wrong Argentine provision for an ordinary platform dispute.
3. **Several country-law statements are incomplete or misapplied**, notably the French hidden-defects warranty, Portuguese conformity legislation, Argentine immediate-performance exception, New Zealand business exclusion, and the obsolete EU Online Dispute Resolution reference.
4. The drafting does not adequately distinguish **consumers, businesses, legal persons, professional users and marketplace sellers**. That matters substantially for consumer law, direct marketing, arbitration, unfair-term rules, privacy and tax/regulatory obligations.

---

# Findings

## 1. BLOCKER — Section 14 forfeiture is not adequately overridden for France or Portugal

**Relevant text:** Section 14.1, 14.2 and 14.3 provide that all unused Tuppence is forfeited on termination, including termination by the user and the Platform’s 30-day termination for convenience. Section 14.3 additionally states that Tuppence is never redeemable for cash or ZAR. Schedules D and E merely preserve mandatory rights generally.

This is the principal legal defect in the material.

Under the EU Unfair Terms Directive 93/13/EEC, implemented through French and Portuguese unfair-terms regimes, a term can be unfair if it creates a significant imbalance contrary to good faith. A supplier’s right to terminate for convenience while retaining the consumer’s unused prepaid balance is a particularly exposed term because:

- the Platform has elected to stop supplying the service;
- the consumer may have paid in advance for future introductions;
- the consumer receives no equivalent service for the retained value;
- the clause applies even where the consumer has not breached the contract;
- the forfeiture is not tied to the Platform’s actual loss or costs;
- the consumer appears unable to obtain cash, card, or original-payment-method reimbursement.

The risk is greater if Tuppence is purchased with money and is a functional prepaid service credit rather than a purely promotional, free, non-transferable benefit.

The clause may also be attacked under the applicable statutory conformity and service-performance rules. A generic sentence such as D6/E7 saying that unfair terms do not bind the consumer does not make the forfeiture clause safe. Courts and regulators assess the actual term, not the drafter’s statement of intention.

### France

D6 correctly acknowledges the French unfair-terms concept in **Code de la consommation article L.212-1**, but it does not neutralise Section 14. The clause is especially vulnerable under the “significant imbalance” analysis and potentially under rules concerning unilateral termination and retention of sums.

D3 also says that, if the consumer withdraws before full performance, “the held Tuppence is released to your balance.” That is not necessarily a statutory refund. A release to an account balance may leave the consumer unable to obtain repayment of money paid. The treatment should distinguish:

- cancellation during the withdrawal period;
- cancellation after lawful commencement of performance;
- failure or lack of conformity;
- Platform termination without consumer breach;
- consumer termination for the Platform’s breach;
- termination for consumer breach or fraud.

### Portugal

The same concern applies under **Decreto-Lei n.º 446/85**, especially its unfair standard-term rules. E7 is only a conclusion and does not address the substantive imbalance created by forfeiture.

E3’s “held Tuppence is released to your balance” presents the same refund problem. Portuguese consumer withdrawal rules generally require repayment of amounts due, subject to the statutory treatment of service already supplied. An internal, non-cash credit is not automatically equivalent to reimbursement.

### Required counsel focus

Counsel should review a replacement mechanism under which:

- unused **paid** Tuppence is refunded on Platform convenience termination;
- a proportionate refund is made where the Platform materially fails to provide the service;
- promotional or bonus credits are separately defined and treated transparently;
- amounts may be retained only to the extent expressly permitted by law and reasonably attributable to service already supplied;
- chargeback, fraud and sanctions cases are handled separately, with a proportionate right to suspend pending investigation rather than automatic forfeiture in every case.

**Severity: BLOCKER**

---

## 2. MAJOR — The French and Portuguese withdrawal clauses omit important formalities and overstate loss of withdrawal rights

**Relevant text:** D3 and E3 say that the consumer requests immediate performance and acknowledges that the right lapses once contact details are exchanged.

### France

D3 cites **Code de la consommation articles L.221-18 and L.221-28, 1°**, which are real and broadly relevant. However, the statutory exception for a fully performed service is not merely a general contractual acknowledgement. The consumer must make an express request for early performance and give the required express acknowledgement/waiver concerning loss of the withdrawal right. The interface and evidence of consent matter.

“By requesting an Introduction you expressly request…” may be insufficient if the request is embedded in general terms rather than presented as a separate, clear, affirmative step. The Platform should also provide the statutory pre-contract information and withdrawal form on a durable medium.

The wording also assumes that “contact details exchanged” equals complete performance. That is a factual and contractual question. If the Platform has promised additional functions—screening, messaging, verification, introduction support, or continued access—the service may not be fully performed merely because contact details were exchanged.

D2’s reference to **articles L.224-25-12 and following** is potentially relevant to digital-content/digital-service conformity, but it should be checked against the precise service classification. D2 also adds the hidden-defects warranty under **Code civil article 1641**. Article 1641 is principally a warranty for hidden defects in a sold thing. It is a poor fit for an online introduction service and may be legally irrelevant or misleading. The schedule should not import a goods warranty without explaining whether it applies to any particular digital product or only to the service.

### Portugal

E3 identifies the correct general instrument, **Decreto-Lei n.º 24/2014**, and the 14-day period is broadly correct. But the clause again needs the statutory formal requirements: clear express request to begin during the withdrawal period, appropriate confirmation on a durable medium, and the legally required treatment of payment for performance already supplied.

E2 cites **Decreto-Lei n.º 84/2021**. That instrument is principally associated with conformity of goods and certain digital-content/digital-service matters, but its application to this particular introduction service should not be assumed. A service-specific analysis under the Portuguese Civil Code, consumer law and the distance-contract legislation is required. As drafted, E2 may promise a statutory remedy regime that does not in fact apply to the service, while failing to state the regimes that do.

**Severity: MAJOR**

---

## 3. MAJOR — Arbitration is not reliably displaced for consumers in France, Portugal or Argentina

**Relevant text:** Section 10.4 requires English-language arbitration under SAAF rules, seated in Cape Town, with equal fee splitting and a South African arbitrator. D8, E9 and G6 state that Section 10.4 does not deprive consumers of the right to sue in their home courts.

These are not equivalent provisions.

### France and Portugal

For EU consumers, mandatory jurisdiction rules under the Brussels I Recast framework generally protect proceedings brought by a consumer in the courts of the consumer’s domicile in appropriate circumstances. A pre-dispute arbitration clause requiring a consumer to arbitrate in Cape Town is also vulnerable under national consumer and civil-procedure principles and may be treated as non-binding or abusive.

D8/E9 should therefore say directly that **Section 10.4 does not apply to consumer disputes where mandatory law gives the consumer access to national courts**, rather than leaving the issue to an interpretive “does not deprive” formulation.

The Cape Town seat, English language, South African arbitrator and equal fee split are independently problematic:

- a consumer may not realistically be able to participate;
- equal arbitrator fees may deter small claims;
- confidentiality may impede regulatory or collective redress;
- the clause could be characterised as creating a significant procedural imbalance;
- the body still says disputes “shall be resolved by binding arbitration.”

The contradiction cannot safely be left for a court to resolve.

### Argentina

G6 cites **Ley 24.240 article 36** as the basis for proceedings in the consumer’s domicile. Article 36 is principally concerned with consumer credit and financing transactions. It is not a sound general citation for every ordinary marketplace/service dispute. The schedule should be checked against the correct Argentine jurisdiction provisions and the nature of the transaction.

More importantly, G6 does not expressly exclude consumer arbitration; it merely says that Section 10.4 does not deprive the consumer of a home-court right. The operative body still mandates Cape Town arbitration.

### Recommended drafting approach

For consumer contracts, use an explicit hierarchy:

> “No consumer is required to arbitrate a dispute where applicable law gives that consumer a right to bring proceedings before a court. Section 10.4 does not restrict that right. Any arbitration option must be separately and lawfully agreed after the dispute arises, or otherwise only where local law permits the clause.”

The commercial/B2B arbitration position should be drafted separately, with a business-user definition and a compliant agreement to arbitrate.

**Severity: MAJOR**

---

## 4. MAJOR — Liability caps remain exposed despite D4, E4 and F4

**Relevant text:** Section 10.6 caps buyer and other-user liability at **ZAR 500**, excludes most categories of loss, and excludes platform unavailability, bugs and interruptions except gross negligence. D4, E4 and F4 merely preserve liability that cannot be excluded.

The schedules do not identify the statutory and contractual liabilities that may override the cap. “To the fullest extent permitted by South African law” is particularly incongruous for French, Portuguese and New Zealand users where the schedule is supposed to prevail.

### France

French law may invalidate or disregard a clause that deprives an essential contractual obligation of its substance, including under the Civil Code’s rules on clauses that substantially empty the principal obligation. A ZAR 500 cap may be disproportionate for a paid service, especially where the Platform controls the service and the consumer’s loss arises from non-performance.

D4 preserves death, personal injury, fraud and gross/fraudulent negligence, but does not expressly preserve:

- mandatory conformity remedies;
- intentional or serious breach of an essential obligation;
- statutory repayment or price-reduction rights;
- liability that cannot be contractually excluded under applicable French law.

### Portugal

E4 has the same structural deficiency. It is not enough to say that non-excludable liability is preserved while retaining a very low cap and broad exclusions. Portuguese unfair-term review may apply to the cap itself.

### New Zealand

F4 is a generic saving clause, while Section 10.6 may conflict with the Consumer Guarantees Act 1993 and Fair Trading Act 1986 in circumstances not captured by “liability that cannot be excluded.” The Platform should expressly preserve statutory remedies and avoid presenting the ZAR 500 cap as applying to consumer guarantees.

### Australia and body fit

Although outside the newly added schedules, C2 illustrates the issue: it limits ACL consumer-guarantee liability only in the manner permitted by section 64A. The body’s general exclusion for unavailability and defects should be expressly subordinated to each local statutory guarantee, not merely to a general schedule disclaimer.

**Severity: MAJOR**

---

## 5. MAJOR — New Zealand’s business exclusion is incomplete under section 43 of the Consumer Guarantees Act

**Relevant text:** F2 says that, where the service is acquired for business purposes, “the parties agree that the Consumer Guarantees Act does not apply, to the extent permitted by section 43.”

Section 43 does not operate simply because the EULA says so. The statutory conditions and formal requirements must be satisfied, including that the transaction is one between parties in trade and that the contracting-out agreement is in writing. The analysis also depends on who the contracting parties are and whether the acquisition is genuinely for business purposes.

The clause does not:

- define “business purposes”;
- require the necessary affirmative business representation;
- separate consumer and business onboarding;
- address whether the Platform and user are both in trade;
- explain which CGA rights are being excluded;
- preserve rights under the Fair Trading Act.

F3 is also too narrow. It refers to unfair terms in a **standard-form consumer contract**, but New Zealand’s unfair-contract-term regime has also been extended to certain standard-form small-trade contracts. The schedule should not imply that business users have no unfair-term protection.

**Severity: MAJOR**

---

## 6. MAJOR — The EU Online Dispute Resolution platform reference is obsolete by August 2026

**Relevant text:** D8 and E9 offer referral to the “European Online Dispute Resolution platform.”

The EU ODR platform was discontinued under the EU measures adopted in 2024, with the platform ceasing operation in 2025. It should not be offered as a live route in a contract effective in August 2026.

The reference is therefore either obsolete or factually misleading. D8/E9 should instead identify the legally applicable consumer-mediation route, the relevant mediator or Portuguese RAL entity, and the Platform’s required disclosures.

For France, a trader offering services to consumers generally needs to provide the identity and contact details of the competent **médiateur de la consommation**, not merely state that the consumer “may refer” a dispute to a mediator. The schedule does not name the mediator or explain the selection process.

For Portugal, E9 should identify the relevant authorised RAL entity or provide the legally required information about the competent entities. “An authorised alternative dispute resolution entity” is too vague for a consumer-facing disclosure.

**Severity: MAJOR**

---

## 7. MAJOR — The language clauses are not a safe “English governs” model

**Relevant text:** D7, E8 and G7 state that English governs, translations are informational, and a local-language version will be supplied only “where” local law requires it.

### France

This is high risk. French consumer-facing contractual and pre-contractual information is subject to French-language requirements, including the Loi Toubon framework and provisions of the Consumer Code. The Platform should not offer a consumer contract in France while assuming that an English master will govern until a later legal trigger occurs.

D7’s conditional promise to supply French “where French law requires” is not an adequate operational rule. If the contract and mandatory information must be made available in French before contracting, the French version must exist and be presented before acceptance. “English governs” may also be ineffective where the French version is the legally operative consumer document.

### Portugal

E8 presents a similar risk under Portuguese consumer and standard-term rules. A Portuguese consumer contract and mandatory pre-contract information may need to be supplied in Portuguese, particularly for standard terms and consumer information. The clause should not make Portuguese availability contingent on an undefined later determination.

### Argentina

G7 is materially unsafe. **Ley 24.240 article 10** requires important consumer contractual information to be clear and sufficiently documented; Argentine consumer contracting practice and enforcement strongly favour Spanish-language terms and disclosures. The schedule’s position that an English version governs, with Spanish supplied only if required, is unlikely to be a defensible consumer-market launch position.

At minimum, the operative consumer terms, price/credit disclosures, withdrawal information, complaint route, privacy notices and material service limitations should be in Spanish before acceptance.

**Severity: MAJOR**

---

## 8. MAJOR — The schedules do not contain a coherent B2B/corporate-subscriber model

**Relevant text:** Section 13.5 says all users are responsible for their own laws. Section 13.6 applies schedules based on habitual residence. D/E/F/G then use consumer-focused language without defining “consumer,” “business,” “legal person,” or “professional user.”

This creates uncertainty in all four jurisdictions.

### France

French consumer protections generally concern consumers and, in some contexts, non-professionals or very small businesses. A company’s habitual residence does not automatically make it a consumer. The schedule should distinguish:

- individual consumer;
- non-professional;
- professional seller;
- company buying introductions for business;
- seller receiving business leads.

D5’s legitimate-interest wording for professional contact details does not itself address French electronic direct-marketing rules. For professional email prospecting, consent may not always be required where the message relates to the recipient’s professional activity, but identification and an easy opt-out are still required. A public source does not eliminate those obligations.

### Portugal

E6 is directionally based on the Portuguese e-privacy rules, and **Lei n.º 41/2004 article 13-A(2)** is a real provision relevant to communications to legal persons and/or existing customer relationships. But the clause is too broad as a blanket statement that unsolicited direct marketing to any legal person is permitted until objection. The actual sender, message type, recipient category, existing relationship and opt-out mechanism must be tested.

The DGC list reference should also be checked operationally; a contract should not imply that registration on a particular list is the only or complete opt-out mechanism.

### New Zealand

F6’s “consent, including deemed consent” formulation is not a substitute for a documented analysis under the Unsolicited Electronic Messages Act 2007. Deemed or inferred consent depends on the circumstances; it is not automatically created merely because an address is public or a user is corporate. The message must contain the sender identification and a functioning unsubscribe facility.

### Argentina

G4 deals with publicly accessible data under Ley 25.326 article 27, but that is not a general authorisation for all marketing. The Platform must also assess the Argentine Do Not Call regime, direct-marketing consent/opt-out requirements and the distinction between a corporate address and personal data relating to an identifiable individual.

**Severity: MAJOR**

---

## 9. MAJOR — Extraterritorial analysis is incomplete and Section 13.5 understates the consequences of targeting these markets

**Relevant text:** Section 13.5 says the Platform is “offered in” the listed countries, while Section 13.5 also says the Platform is operated from South Africa and users remain responsible for local law.

The South African sender’s lack of a local establishment does not prevent foreign law from applying.

### France and Portugal / EU

A South African operator can be subject to GDPR where it offers services to, or monitors, individuals in the EU. Consumer law and jurisdiction protections can also apply where the service is directed at EU consumers. The fact that the company has no French or Portuguese subsidiary is not a safe harbour.

The material appears to have missed at least:

- the EU Digital Services Act, if the Platform is an online intermediary or marketplace;
- trader traceability and marketplace transparency duties;
- notice-and-action and content-moderation transparency obligations;
- required platform terms and explanations concerning suspension/termination;
- GDPR representative requirements where applicable;
- cross-border VAT and invoicing analysis;
- DAC7 reporting obligations if the Platform facilitates reportable rental or personal-service activity;
- French and Portuguese consumer pre-contract information and complaint disclosures;
- sector licensing issues for property rental, tutoring and other advertised activities.

The ECT Act safe-harbour language in Section 10.7 is not a substitute for EU intermediary obligations. Nor does the statement that users are responsible for local laws remove the Platform’s own obligations.

### Argentina

Offering the Platform to Argentine consumers may trigger Argentine consumer-law, e-commerce, privacy, tax and electronic-marketing obligations despite no local establishment. The schedule does not address local notices, refund mechanics, Spanish disclosures, consumer complaint channels, or tax collection/reporting.

### Tax and establishment

Naming a country in Section 13.5 does **not by itself** create a permanent establishment, branch, or tax nexus. It is, however, evidence of deliberate market targeting and can support jurisdictional and regulatory application. Actual exposure depends on conduct, including:

- local agents or staff;
- dependent representatives;
- local payment or support operations;
- inventory or premises;
- contract conclusion and fulfilment;
- platform control over local sellers;
- revenue and transaction thresholds;
- local VAT/GST/IVA rules.

The present wording should not be relied upon as a tax or licensing analysis.

**Severity: MAJOR**

---

## 10. MAJOR — G2 adds an Argentine “fully performed service” exception that is not safely supported by the cited law

**Relevant text:** G2 says the consumer has a 10-day revocation right under article 34 of Ley 24.240, but loses it once contact details are exchanged because the service is fully performed.

The 10-day citation to **article 34** is real and broadly relevant. The problem is the second sentence. Argentine law is not simply an EU-style transposition of the rule in which a consumer expressly requests immediate performance and loses revocation rights automatically upon full performance.

The schedule appears to import the French/Portuguese model into Argentina without citing a clear Argentine statutory basis for:

- an express early-performance request;
- an express waiver;
- automatic loss of the right upon exchange of contact details;
- treating exchange of details as complete performance.

This could be viewed as an attempt to contract out of a consumer right. The safer position is to obtain Argentine counsel’s specific analysis of article 34, its implementing rules and current e-commerce regulations, and to provide the statutory revocation mechanism without assuming the exception.

As with D3/E3, releasing Tuppence to an internal balance is not necessarily the same as refunding the consumer.

**Severity: MAJOR**

---

## 11. MINOR — D2’s hidden-defects warranty reference is likely irrelevant and may create unintended obligations

**Relevant text:** D2 states that the consumer has the guarantee against hidden defects under **Code civil article 1641**.

The citation is real, but the application is doubtful. Article 1641 concerns hidden defects in a sold item. The Platform’s Introduction service is not obviously a sale of goods. Including it may:

- confuse the consumer about available remedies;
- create an unnecessary representation that the Platform accepts a goods-style warranty;
- distract from the actual digital-service conformity regime;
- complicate the legal classification of Tuppence and the service.

This should either be removed or expressly limited to any goods transaction to which it legally applies.

**Severity: MINOR**

---

## 12. MINOR — D5, E5 and G4 conflate data-source transparency with a complete marketing/privacy compliance model

**Relevant text:** D5, E5 and G4 state that the Platform may use publicly sourced professional/business contact details and rely on legitimate interest or a statutory public-source provision.

These clauses do not solve the full compliance problem:

- GDPR legitimate interest requires balancing and documentation; it is not self-proving through contract text.
- Article 14 GDPR information duties may apply when data is obtained from elsewhere.
- France and Portugal have electronic-communications marketing rules separate from GDPR.
- Argentina’s public-source exception under article 27 is limited and should not be presented as a universal marketing permission.
- The schedules do not address retention, objection handling, suppression lists, or proof that an address is genuinely professional rather than personal.

**Severity: MINOR**

---

## 13. QUESTION — Is Tuppence a prepaid service credit, electronic money, payment instrument, or promotional coupon?

**Relevant text:** Section 10.6 values Seller Tuppence at USD $2 each; Sections 14.1 and 14.3 say Tuppence is non-refundable and never redeemable for cash or ZAR.

The legal treatment of the forfeiture and the regulatory perimeter depends heavily on what Tuppence is:

- Is it purchased for money?
- Can it be transferred?
- Can it be used only for introductions?
- Is it accepted by anyone other than the Platform?
- Does it represent a monetary value or merely a contractual entitlement?
- Is “USD $2” a real purchase value or only a liability-calculation fiction?
- Are Tuppence balances held customer funds?
- Can sellers earn them and later spend them?

If Tuppence is a stored-value instrument or payment-like balance, the analysis may include payment-services, e-money, consumer-credit, AML/FICA, safeguarding, expiry and tax issues. If it is only a non-transferable service entitlement, the contract should say so consistently and avoid language suggesting monetary value.

**Severity: QUESTION**

---

## 14. QUESTION — Does the extracted schedule structure accurately reflect the production document?

**Relevant text:** Immediately before Schedule A, the extract repeats Sections 14 and 15 in full, then introduces Schedule A. The heading says “Country Schedules A–G,” but the repeated termination and miscellaneous clauses are not labelled as belonging to any particular schedule.

This may be an extraction artefact, but if present in the EULA it creates a material document-integrity problem:

- users may see a second set of governing terms;
- it is unclear whether 14.1–15.9 are body terms or part of a country schedule;
- the schedule precedence mechanism becomes ambiguous;
- the Platform may inadvertently present duplicate or conflicting operative text.

The final rendered and accepted version should be checked, including mobile presentation, language versions and the version actually captured in acceptance logs.

**Severity: QUESTION**

---

## 15. MAJOR — Section 13.2’s “mandatory South African law” list does not establish foreign-law compliance

**Relevant text:** Section 13.2 lists POPIA, CPA, ECT Act, FICA, NCA, FSRA, the Constitution and then says the mandatory laws in the applicable schedule prevail.

The list is not inherently wrong, but it creates a misleading architecture. Foreign mandatory law does not become applicable merely because the contract says it prevails, and the schedules do not identify the operative conflict rule with enough precision.

Examples:

- EU consumer rights can apply regardless of South African governing-law wording.
- A choice of South African law cannot remove non-derogable consumer protections applicable in the consumer’s habitual-residence jurisdiction.
- Arbitration and forum rights are not cured merely by listing them as “mandatory.”
- Privacy obligations arise from processing conduct and territorial scope, not from the schedule’s declaration.
- The statement that the schedules automatically supply “mandatory consumer, privacy and fairness protections” is too broad: the schedules omit many obligations and cannot replace operational compliance.

**Severity: MAJOR**

---

# Citation and status check

The following citations appear real and broadly current, subject to application-specific verification:

- France: Code de la consommation **L.221-18**, **L.221-28**, **L.212-1**.
- France: Code civil **article 1641**.
- Portugal: **Decreto-Lei n.º 24/2014**.
- Portugal: **Decreto-Lei n.º 446/85**.
- Portugal: **Lei n.º 41/2004**, article 13-A.
- New Zealand: **Consumer Guarantees Act 1993**, section 43.
- New Zealand: **Privacy Act 2020**, IPP 3A.
- New Zealand: **Unsolicited Electronic Messages Act 2007**.
- Argentina: **Ley 24.240**, articles 34, 36 and 40.
- Argentina: **Ley 25.326**, article 27.
- Argentina: **Código Civil y Comercial**, articles 1117–1122.

The following require correction or particularly careful confirmation:

1. **EU Online Dispute Resolution platform** — obsolete by August 2026 and should not be described as an available route.
2. **French article 1641** — real, but likely misapplied to an online introduction service.
3. **Portuguese Decreto-Lei n.º 84/2021** — real, but its application to this service should not be assumed merely because it concerns conformity/digital matters.
4. **Argentine article 36** — real, but apparently an unsuitable general citation for the consumer’s domicile forum in an ordinary platform dispute.
5. **Argentine article 34 “full performance” exception** — the 10-day revocation reference is real, but the imported EU-style loss-of-right wording is not adequately supported by the cited provision.
6. **French and Portuguese language position** — the statutes and consumer rules should be checked against the precise contract, interface, pre-contract information and version supplied before acceptance; the conditional wording is not a safe compliance position.

---

# Specific conflicts with the EULA body

## Arbitration

**Conflict:** Section 10.4 says disputes “shall be resolved by binding arbitration” in Cape Town. D8/E9/G6 say the consumer may sue at home.

**Assessment:** The schedules do not clearly override the mandate. The body should contain an explicit consumer carve-out, not a general saving sentence. The same issue affects Section 13.3.

## Liability

**Conflict:** Section 10.6 imposes the ZAR 500 buyer/other-user cap and broad exclusions. D4/E4/F4 only preserve liability that cannot be excluded.

**Assessment:** The schedules preserve the minimum but do not affirmatively preserve all statutory service, conformity, refund and essential-obligation remedies. The cap should be made expressly subordinate to each local regime and tested for unfairness.

## Governing law

**Conflict:** Section 13.1 selects South African law; Section 13.2 gives South African statutes supremacy; Section 13.6 says schedules prevail.

**Assessment:** Section 13.6 is directionally correct but legally incomplete. A choice of South African law cannot contract away foreign mandatory consumer protections. The drafting should state that clearly and identify the consumer’s local mandatory rights without implying that the schedule is exhaustive.

## Termination and forfeiture

**Conflict:** Section 14 is repeated in the extracted schedule area and says forfeiture applies universally. No D/E/F/G schedule expressly modifies it.

**Assessment:** This is the most commercially and legally exposed provision. The general unfair-terms disclaimers do not cure it. France and Portugal should be treated as high-risk until the refund/credit mechanics are redesigned.

---

# What the Author has missed entirely

**MAJOR — EU platform regulation and marketplace obligations.** The material focuses almost exclusively on consumer contract terms, but a marketplace offered in France and Portugal may face obligations under the Digital Services Act, including intermediary transparency, notice-and-action, reasons for restrictions or termination, trader traceability and marketplace disclosures.

**MAJOR — DAC7 and tax reporting.** If the Platform facilitates reportable property rentals or personal services for EU sellers, DAC7 analysis is essential. Section 13.5’s user-law disclaimer does not address operator reporting duties.

**MAJOR — Local refund and payment handling.** “Tuppence released to your balance” is not a complete refund policy and may be unlawful or commercially misleading where money must be returned to the consumer.

**MAJOR — Local-language pre-contract information.** The issue is not limited to translating the EULA. Price, credit value, withdrawal, cancellation, refund, identity, complaint and service-performance information may also need local-language presentation before acceptance.

**MAJOR — Formal consumer-mediation disclosures.** D8/E9 omit the concrete mediator/entity information required for a usable compliance process.

---

# Three findings to discuss first with the Author

1. **BLOCKER — Section 14 forfeiture:** redesign the paid-credit termination and refund model for France and Portugal; do not rely on D6/E7 or a balance-credit release.
2. **MAJOR — Arbitration and forum:** replace the current “shall arbitrate in Cape Town” structure with an express consumer carve-out and correct the Argentine citation.
3. **MAJOR — EU/market-entry exposure:** obtain counsel on GDPR territorial scope, DSA marketplace duties, VAT/DAC7, French/Portuguese language requirements and consumer-mediation disclosures before treating the countries as “offered” under Section 13.5.

# What I could not verify from the material supplied

I could not verify:

- the full EULA, especially the definitions of **User, consumer, Seller, Buyer, Tuppence, Wallet, Introduction and Platform**;
- the purchase flow, checkbox wording, withdrawal-flow evidence and durable-medium confirmations;
- whether Tuppence is paid, promotional, transferable, refundable or payment-like;
- the actual Privacy Policy, marketing notices and data-retention schedule;
- whether the Platform is legally the contracting supplier, an intermediary, an agent, or a payment facilitator;
- the final rendered document structure, including whether the repeated Sections 14–15 are an extraction error;
- current regulator guidance and local counsel positions on the exact French, Portuguese and Argentine language, mediation, marketing and marketplace requirements;
- the factual activities of the Sellers, including property rental and tutoring, which may materially change licensing, tax and reporting conclusions.
