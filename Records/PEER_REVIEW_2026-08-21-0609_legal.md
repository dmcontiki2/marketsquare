# Independent Peer Review — 2026-08-21-0609

*Peer: gpt-5.6-luna (second vendor, read-only) · Lens: legal · Author: Claude · System Engineer: David*

**Scope:**
  - OUTREACH_LAW_WORKING_NOTES_2026-08-20.md (67,055 chars)

**Usage:** 18513 in / 9090 out tokens · actual cost ≈ $0.0146

---

# Peer review — consent-model conclusions

**Scope and disclaimer.** This is a second independent reading of the supplied material, not legal advice, approval, or a substitute for jurisdiction-specific counsel. I have assessed the conclusions as at **20 August 2026**, but I cannot independently authenticate every future-dated Gazette, regulator page, or 2026 legislative development from the material alone.

## Executive conclusion

The headline conclusions are **not safe as written**.

- **US and UK:** broadly correct for **corporate** recipients, but not for sole traders, ordinary partnerships, or other individual subscribers.
- **France:** broadly correct only for genuinely professional B2B targeting and subject to several cumulative conditions. “Business recipients” is too broad.
- **Portugal:** probably correct for a message addressed to a **legal-person subscriber**, but materially unsafe for named employees and incomplete because the mandatory corporate suppression-list check is operationally decisive.
- **Australia and New Zealand:** the “published business address” route is not deemed consent in the ordinary sense. It is a narrow, rebuttable **inferred/deemed-consent** route with relevance, publication, and evidence conditions. “Sendable” is too confident, particularly for New Zealand.
- **Kenya and Botswana:** the opt-in conclusions are substantially right. The local registration/representative conclusions need narrower wording and better separation between data-protection obligations and electronic-marketing offences.
- **Egypt:** “do not cold email” is the prudent outcome, but several claimed 2025/2026 regulatory facts remain unverified in the supplied material. The extraterritorial criminal analysis is not a basis for confidently saying the regime applies.
- **Argentina:** “opt-out from public sources” is directionally right, but “SENDABLE” is too confident. The public-source condition, database/privacy duties, and foreign-jurisdiction question remain material.
- **Namibia:** “no rule in force at all” is literally wrong. The narrower proposition—no commenced, general anti-spam rule identified—is much more defensible.
- **Zimbabwe:** “low risk” is not justified for named-individual addresses because the notes themselves identify a potentially unlicensed offshore processing activity and inspections beginning in September 2026.
- **Mozambique:** the opt-in conclusion is likely right, but it is omitted from the user's headline list and should not be treated as a low-risk residual jurisdiction.

---

## Findings

### 1. **MAJOR — “Business recipient” is being used too imprecisely**

The conclusions need to distinguish at least:

1. a legal-person mailbox (`info@company.example`);
2. a named employee at a company domain (`jane.smith@company.example`);
3. a sole trader;
4. a partnership;
5. a mailbox that identifies an individual despite being labelled “business”.

This distinction changes the answer in the US, UK, France, Portugal, Australia, New Zealand, and under the privacy laws running alongside the email statutes.

The notes acknowledge this problem for Portugal and the UK, but the headline table still says:

> “US, France, UK, Portugal = OPT-OUT for business recipients”

That is too categorical. The campaign data model must not treat “business address” as a legal category.

---

### 2. **PRAISE — US CAN-SPAM conclusion is substantially correct, but the state-law and data-law qualifications need to remain prominent**

The Appendix correctly states that CAN-SPAM is an **opt-out** regime and that it applies to B2B email. The physical postal-address requirement is also correctly identified. The statement that California’s anti-deception provision survives CAN-SPAM pre-emption is directionally correct.

However, “no consent needed for B2B” should not be read as “no privacy or targeting restrictions.” The notes correctly mention that the CCPA B2B exemption ended in 2023, but they do not draw the practical consequence: scraped business contact information may still be personal information, and collection/use notices, sensitive-data rules where applicable, deletion requests, and other state privacy statutes may be relevant.

**Question:** Has counsel checked whether TrustSquare is subject to any US state privacy statute based on volume, revenue, or targeting thresholds? CAN-SPAM compliance does not answer that question.

---

### 3. **MAJOR — UK conclusion is correct only for corporate subscribers, not “business recipients” generally**

The Appendix says:

> “PECR opt-in for electronic mail DOES NOT APPLY to corporate subscribers…”

That is broadly right. The qualification immediately afterward is essential:

> “sole traders and some partnerships are INDIVIDUAL subscribers”

The headline must therefore say **corporate subscribers only**. It should also identify the relevant PECR provisions precisely. The notes cite **PECR regulation 23** for concealed identity and a valid opt-out address; that appears to be the correct anti-concealment/valid-address provision. The prior-consent rule is principally **regulation 22**, which should be cited in the headline analysis.

The UK GDPR point is independent: public availability does not eliminate Article 14 duties or the absolute direct-marketing objection right.

**Extraterrestrial assessment:** The notes are too silent on PECR territorial reach. UK GDPR Article 3(2) may apply where TrustSquare is offering services to people in the UK, but that does not automatically resolve the territorial scope of PECR itself. Counsel should separately confirm whether PECR applies to an offshore sender targeting UK corporate subscribers and what enforcement route is realistically available.

---

### 4. **MAJOR — France is not simply opt-out “for business recipients”**

The French conclusion is directionally plausible, but the three cumulative conditions quoted in the Appendix are important:

> “recipient contacted in a professional capacity, message concerns their professional activity, address is professional”

This is not a blanket corporate exemption. A named person at a company can still be an individual recipient, and an address scraped from a website does not by itself prove that the specific solicitation concerns the person’s professional activity.

The statement:

> “CNIL's Aug 2026 tightening to explicit opt-in applies to B2C ONLY”

is unsupported in the supplied material. No legal instrument, CNIL decision, or identifiable citation is provided. It should not be used as a premise until counsel verifies it.

**Citation concern:** The Appendix refers to “LCEN: €375/message sent without retraction option.” The notes do not identify the actual provision. The relevant French electronic-communications rule is generally associated with **Code des postes et des communications électroniques, Article L34-5**, not a generic LCEN provision. The amount and whether it is calculated per message, per breach, or under a particular administrative sanction should be checked before relying on it.

---

### 5. **MAJOR — Portugal’s corporate opt-out conclusion is plausible, but the headline overstates certainty**

The notes quote **Lei 41/2004, Article 13-A(2)** as expressly disapplying the prior-consent rule for legal-person subscribers. If that quotation and current-law status are correct, the conclusion for a message sent to a **company as subscriber** is sound.

But the notes also admit the decisive uncertainty:

> “whether the corporate exemption covers a named individual at a corporate address”

That uncertainty makes the headline “OPT-OUT for legal persons” acceptable only if the campaign excludes named-individual addresses. It is not safe to convert it into “opt-out for business recipients.”

The notes correctly identify the **DGC corporate opt-out list** and the obligation in Article 13-B(5) to consult it. This is not a minor administrative nicety: failing to screen the list can make an otherwise permissible corporate campaign unlawful. The fact that only 184 email records were observed does not reduce the legal duty.

The statement that a role address is “arguably not personal data at all” is too confident. A role mailbox can still be personal data where it is attributable to an identifiable employee or is accessible only to one person. That question requires a fact-specific assessment.

**Extraterrestrial assessment:** GDPR Article 3(2) is a strong basis for applying GDPR obligations to a South African sender offering services to Portuguese businesses. It does **not automatically establish** that every Portuguese ePrivacy rule, including Article 13-A, applies extraterritorially to a sender with no Portuguese establishment. The notes appropriately call Lei 41/2004 unsettled, but the headline “GDPR art.3(2): yes” should not be read as resolving the ePrivacy question.

---

### 6. **MAJOR — Australia and New Zealand are not “deemed consent” in a way that makes scraped-address campaigns generally sendable**

The Appendix describes Australia as:

> “Opt-in, BUT Sch.2 inferred consent where a work address was CONSPICUOUSLY PUBLISHED…”

and New Zealand as:

> “Opt-in, BUT deemed consent for conspicuously published business addresses”

That is broadly the right statutory structure. The practical conclusion is too permissive.

In both jurisdictions, publication is only one element. The sender must be able to show, address by address, that:

- the address was conspicuously published in the relevant business or official capacity;
- there was no contrary “no unsolicited” statement;
- the message was relevant to the role or business;
- the recipient could reasonably expect such communications;
- the source and decision process can be evidenced.

A bulk scrape from OpenStreetMap and company websites does not automatically establish those facts. A generic company address may be easier than a named address, but “business address” is not itself a statutory safe harbour.

For New Zealand, the notes say:

> “s.8 reach arguable”

but then recommend:

> “SENDABLE with discipline”

That is internally inconsistent. The author describes a statutory extraterritoriality conflict, no controlling case law, and DIA guidance that may not match the text. In that posture, New Zealand should be classified **“legally uncertain / counsel required,”** not sendable.

For Australia, the extraterritorial analysis is also underdeveloped. The Spam Act’s “Australian link” framework and its application to messages accessed in Australia should be analysed separately from whether the South African sender is established in Australia. The absence of an Australian establishment is not, by itself, a reliable safe harbour.

---

### 7. **MAJOR — Kenya’s opt-in conclusion is strong, but the registration conclusion is stated more broadly than the material proves**

The Kenya conclusion is one of the stronger parts of the report:

- **DPA section 37(1)(a)** supports express consent for direct marketing;
- the 2010 Consumer Protection Regulations, **regulation 17**, appears to impose prior consent and an opt-in principle;
- the notes identify no corporate exemption in regulation 17;
- a generic `info@` address may escape the DPA’s natural-person scope but not necessarily the communications-regulation rule.

The correction from regulation 12 to **regulation 17** is plausible and appears important.

However, the conclusion that TrustSquare “must register with ODPC” needs to distinguish:

- processing personal data of Kenyan data subjects;
- conducting a business “wholly or mainly in direct marketing”;
- whether a campaign consisting solely of non-personal corporate role addresses is within the registration trigger;
- whether registration applies to an offshore entity before it has any Kenyan establishment.

The notes cite ODPC guidance for offshore controllers, but regulator guidance is not the same as a settled judicial interpretation. The “DO NOT COLD EMAIL” recommendation remains prudent, but the registration proposition should be expressed as **ODPC’s stated position / high compliance risk**, not as an uncontested legal conclusion.

**Penalty citation caution:** The notes expressly admit uncertainty on the mapping of regulation 17 to KICA section 27(4). That uncertainty should prevent the report from presenting the KES 300,000 / three-year figure as verified.

---

### 8. **MAJOR — Egypt is correctly treated as a no-send jurisdiction, but the claimed 2025/2026 citations require primary-source verification**

The result—do not cold email Egypt—is sensible even without resolving every extraterritorial question. The notes identify the relevant direct-marketing provisions as **PDPL Articles 17 and 18**, which is plausible, and they correctly focus on consent, sender identification, opt-out, licensing, and cross-border transfer issues.

But the report calls the following “verified” while also relying heavily on secondary sources:

- **MCIT Decree No. 816 of 2025**;
- its 1 November 2025 Gazette date;
- PDPC establishment;
- the 31 October/1 November 2026 grace-period end;
- detailed licence-fee percentages;
- the dedicated electronic-direct-marketing guideline.

The notes themselves state that the licensing portal could not be verified and that the PDPC site was a JavaScript application that did not render. Those facts do not prove the instruments are wrong, but they mean the “independently re-verified” label is too strong. Counsel should obtain the Arabic Gazette and the operative Regulations before relying on the detailed article and penalty mapping.

The extraterritorial analysis is appropriately cautious as to the **dual-criminality language**, but too confident as to the regulatory consequences. Saying that importing Egyptian contacts into a South African CRM is “exactly” a regulated cross-border transfer assumes that the PDPL first applies to TrustSquare as controller and that the contacts are personal data under the law. That is likely for named addresses, but not necessarily for a genuinely generic corporate mailbox.

---

### 9. **MAJOR — Argentina is opt-out in principle, but “SENDABLE” is unjustified**

The quoted provisions—**Ley 25.326 Articles 5.2, 27.1, and 27.3**, together with **Decreto 1558/2001 Article 27**—appear to support use of publicly accessible data for advertising without prior consent, subject to withdrawal/blocking and other data-protection duties.

The notes are right to reject the proposition that **Ley 26.951’s No Llame registry** governs email. That correction appears sound: it concerns telephone services, including VoIP, not email.

Nevertheless, “OPT-OUT from public sources” should be qualified:

- the source must genuinely be unrestricted public access;
- the collection and use must satisfy data-quality, proportionality, purpose, and information duties;
- a company website may contain personal data even where the intended commercial target is the company;
- the data subject’s withdrawal/blocking request must be acted on immediately or at least without avoidable delay;
- the foreign-company territorial question is unresolved.

The notes cite *Tanús c. Cosa* as support for a database/direct-marketing theory, but do not explain whether that decision establishes a rule applicable to a South African sender. The AAIP’s asserted jurisdiction over Worldcoin is evidence of enforcement posture, not a definitive territorial holding.

**Recommended classification:** “Permissible in principle, but counsel review required for source, database duties, and cross-border exposure”—not “SENDABLE.”

---

### 10. **MAJOR — Namibia’s “no rule in force at all” statement is literally incorrect**

The report says:

> “Plainly: there is no enforceable Namibian rule against B2B cold email today.”

That narrower statement may be defensible if **ETA Act 4 of 2019, Chapter 4, including section 36**, is genuinely uncommenced. But the headline says:

> “No rule in force at all”

which is too absolute. The report itself identifies:

- Constitution Article 13(1);
- possible common-law claims;
- the Communications Act;
- the commenced portions of the Electronic Transactions Act;
- the possibility of an imminent ministerial commencement notice.

The correct conclusion is not “no rule”; it is:

> “No commenced, general opt-in anti-spam provision has been verified; residual privacy, communications, common-law, and imminent-commencement risks remain.”

The claimed commencement position for Chapter 4 is one of the seven corrections that deserves primary Gazette verification. The report relies on a Laws.Africa consolidation and states that **GN 182 of 2026** commenced sections 20 and Chapter 5 but not Chapter 4. That may be right, but the author should provide the Gazette notice itself, not only a consolidation, because commencement status is dispositive.

---

### 11. **MAJOR — Zimbabwe is not properly described as “low risk”**

The notes correctly question the commonly cited “unsolicited communications” provision and identify **Criminal Code section 164D** as a header-forgery/relay-abuse offence rather than a general cold-email prohibition. The correction that the direct-marketing objection duties are in **sections 14–16**, not section 24, appears plausible.

However, the headline verdict:

> “SENDABLE, low risk”

does not follow from the rest of the analysis. The notes identify:

- **SI 155 of 2024**, section 3(1), stating that no person may process personal information unless licensed;
- no foreign carve-out;
- uncertainty whether POTRAZ will license or enforce against an offshore sender;
- an extraterritorial means-based test under section 4(2)(b);
- a local-representative requirement under section 4(3);
- compliance inspections beginning 1 September 2026.

That is not low risk for named-individual addresses. It may be lower risk for truly generic, non-personal role addresses, but that depends on the factual and legal classification of the mailbox. The licensing issue is not cured by saying the Act may fail the “means located in Zimbabwe” test; that is an unresolved jurisdictional defence, not a safe harbour.

---

### 12. **PRAISE / MAJOR — Mozambique’s opt-in conclusion appears right, but extraterritorial uncertainty does not make the conduct “technically unlawful” without qualification**

The notes’ reading of **Lei 3/2017, Article 40(3)–(5)** is coherent: direct-marketing email requires prior consent, with a narrow existing-customer soft opt-in. The conclusion that a scraped cold list does not satisfy Article 40(5) is sound on the stated facts.

The phrase:

> “Technically unlawful, unenforceable”

conflates two different questions. If Article 40 applies territorially, the conduct may be unlawful. But the notes admit that territorial application to an offshore sender is unverified. The better formulation is:

> “Likely prohibited under Article 40 if the provision applies; offshore application and enforcement are unresolved.”

The future-dated **Lei 13/2026** and **Lei 14/2026** should not be used until their operative texts are reviewed after the stated 29 September 2026 commencement date.

---

## The seven claimed corrections

### 1. Egypt — “executive regulations were issued”

**QUESTION / MAJOR.** The assertion may be correct, but the supplied material does not establish it to the standard claimed. The report should cite the Arabic Gazette and the exact issuing authority, instrument title, publication date, commencement provision, and relevant articles. Secondary law-firm alerts are not enough for a conclusion that the entire prior premise is superseded.

### 2. Botswana — 2018 Act repealed and replaced by 2024 Act

**QUESTION.** This is potentially decisive and should be verified against the repeal and commencement clauses in the official Gazette. The stated commencement date of **14 January 2025**, rather than publication on 29 October 2024, is legally plausible. The conclusion should not rely on DLA Piper’s outdated 2018 summary.

### 3. Zimbabwe — no general unsolicited-communications section

**PRAISE, subject to primary-text confirmation.** The distinction between Criminal Code section **164D “Spam”** and a general commercial-email prohibition is important. The report should avoid saying the Act contains no direct-marketing controls: sections 14–16 apparently impose objection and notice obligations even if they do not create a prior-consent spam rule.

### 4. New Zealand — no Schedule 1; section 4 and section 8 are the relevant provisions

**PRAISE.** This correction is internally consistent with the quoted UEMA structure. It does not, however, resolve the section 8 extraterritorial issue.

### 5. Kenya — regulation 17, not regulation 12

**PRAISE / QUESTION.** Regulation 17 appears to be the relevant provision based on the supplied text, but the report should reproduce the official regulation and its enabling provision. The claimed criminal penalty mapping remains expressly unverified.

### 6. Portugal — DL 7/2004 Article 22 repealed; regime moved to Lei 41/2004 Articles 13-A/13-B

**QUESTION / likely correct but requires Gazette verification.** The proposition is plausible and may well be right. The author should show the exact text of **Lei 46/2012 Article 5(b)** and the current consolidated text of DL 7/2004. The report should not merely say “repealed” if the provision was instead amended, renumbered, or rendered inapplicable by a cross-reference.

### 7. Argentina — No Llame does not cover email

**PRAISE.** On the described statutory scope—telephone services, including VoIP—this correction appears right. It does not eliminate Argentina’s separate data-protection and direct-marketing obligations.

---

## Extraterritoriality: where the analysis is too confident and too cautious

### Too confident

1. **Kenya:** the statutory reach under DPA section 4(b)(ii) is strong for personal data of persons located in Kenya, but the notes move too quickly from that to automatic ODPC registration and all licensing consequences for an offshore campaign, especially where the address is a generic corporate mailbox.

2. **Egypt:** the regulatory licensing and transfer conclusions assume PDPL applicability before resolving whether generic corporate addresses are personal data and before confirming the 2025 Regulations from the official Arabic source.

3. **Botswana:** DPA section 4(2)’s “offering goods or services” hook appears strong for a sales solicitation, but ECTA’s separate territorial reach is expressly admitted to be untested. The report should not describe the combined result as fully settled.

4. **Portugal / GDPR:** GDPR Article 3(2) likely applies to targeted offers to Portuguese recipients, but it does not automatically settle the extraterritorial application of Lei 41/2004’s corporate-email rule.

5. **France and UK:** the notes assert the substantive consent position but do not separately establish the territorial application of the national electronic-marketing statutes to a South African sender.

### Too cautious

1. **New Zealand:** the notes identify a real section 8 conflict but then call the campaign “sendable.” If section 8 excludes a sender with no NZ residence, establishment, or business activities, the statutory result could change materially. This requires counsel, not a low-friction operational verdict.

2. **Argentina:** the absence of an express extraterritorial clause does not make the risk negligible where the sender intentionally targets Argentine businesses and processes Argentine contact data. The “SENDABLE” label understates enforcement and private-action uncertainty.

3. **Zimbabwe:** the means-based section 4(2)(b) argument may be a meaningful defence, but it is not a reason to call the campaign low risk while the licensing rule and offshore application remain unresolved.

4. **Mozambique:** lack of a general extraterritorial clause lowers enforcement confidence, but it does not justify calling the underlying conduct only “deliverability risk,” particularly if the recipient is in Mozambique and Article 40 expressly regulates email.

---

## Material legal risks missed or underdeveloped

### 13. **BLOCKER — South African law is not a safe foundation for this campaign**

The Appendix says:

> “POPIA extends to juristic persons but conditionally (‘where it is applicable’). … role-based addresses … fall outside the strictest s69 consent requirement”

This is a potentially dangerous operational premise. **POPIA section 69** is a South African restriction on electronic direct marketing, and the campaign is being conducted by a South African company using data processed in South Africa. The claim that role addresses fall outside the consent requirement is not equivalent to a statutory exemption. It appears to rely on a regulator guidance note whose precise status, wording, and applicability should be checked by South African counsel.

The report should separately analyse:

- whether the address is “personal information” under POPIA;
- whether the recipient is a juristic person, an individual employee, or both;
- whether section 69 requires consent for the particular message;
- whether the public-source method satisfies any applicable lawful-processing conditions;
- ECTA section 45 and its opt-out requirements;
- cross-border transfers and operator arrangements.

A foreign jurisdiction’s opt-out rule does not cure a possible **South African-originating-sender violation**.

### 14. **MAJOR — Website terms, scraping restrictions, and source-law issues are omitted**

The campaign uses addresses:

> “scraped from OpenStreetMap and company websites”

The consent analysis treats public accessibility as sufficient or highly relevant in several jurisdictions. Public visibility does not necessarily authorize automated extraction, repurposing, or commercial use. Counsel should check:

- OpenStreetMap’s applicable licence and attribution requirements;
- website terms of use and anti-scraping clauses;
- database-right or contract theories where relevant;
- whether the source represented that addresses were for customer contact, support, or another limited purpose;
- whether the addresses were obtained through APIs with usage restrictions.

This issue is separate from whether the eventual email is opt-in or opt-out compliant.

### 15. **MAJOR — The one-message campaign still creates collection, notice, and suppression obligations**

“One message per address” does not eliminate:

- indirect-collection notices;
- source disclosure;
- records of the legal basis or inferred consent;
- suppression-list maintenance;
- proof that the address was not previously opted out;
- evidence of the publication context and relevance determination.

The notes recognize this in individual jurisdictions, but the headline “one message per address” risks making the campaign sound legally trivial. A single email can establish a regulatory breach and can trigger a private complaint or damages claim.

### 16. **MAJOR — No comprehensive treatment of recipient classification**

The source data apparently does not distinguish named people from role accounts. This is not merely an engineering gap; it is a legal prerequisite to selecting the consent model. The author’s own Appendix identifies:

> “Named-individual vs role addresses not distinguished in the data model.”

That should be treated as a **blocking legal control**, not an implementation improvement.

---

## Recommended jurisdiction disposition

| Jurisdiction | Independent disposition |
|---|---|
| United States | **Opt-out for corporate and individual recipients under CAN-SPAM**, subject to physical-address, state-law, and privacy-law checks |
| United Kingdom | **Opt-out for corporate subscribers only**; opt-in generally required for sole traders and other individual subscribers |
| France | **Opt-out may be available for genuine professional B2B targeting**, but not a blanket business-recipient exemption |
| Portugal | **Likely opt-out for legal-person subscribers**, subject to DGC-list screening; named employees unresolved |
| Australia | **Inferred consent may be available**, but publication and role-relevance evidence are mandatory; not automatic |
| New Zealand | **Deemed consent may be available**, but section 8 extraterritoriality makes “sendable” too confident |
| Kenya | **Opt-in; do not cold email** |
| Egypt | **Opt-in and additional regulatory requirements likely; do not cold email pending primary-source verification** |
| Botswana | **Opt-in for corporate mailboxes under ECTA on the supplied reading; do not cold email** |
| Argentina | **Opt-out from genuinely unrestricted public sources in principle**, but counsel required before calling it sendable |
| Namibia | **No verified commenced general anti-spam rule, not “no rule at all”; monitor commencement and residual claims** |
| Zimbabwe | **Legitimate-interest route may exist for named individuals, but licensing and territorial risks make “low risk” unjustified** |
| Mozambique | **Opt-in under Article 40 on the supplied reading; offshore reach unresolved; do not treat as clear** |

---

# Three findings to discuss first

1. **BLOCKER — South African-law premise:** whether POPIA section 69 and ECTA section 45 permit TrustSquare, as a South African sender, to conduct this campaign at all. The role-address guidance is not an obvious statutory exemption.

2. **MAJOR — Recipient classification:** stop treating “business address” as a single legal category. Separate corporate role accounts, named employees, sole traders, partnerships, and generic addresses before selecting an opt-in or opt-out model.

3. **MAJOR — Overstated low-risk/sendable labels:** obtain counsel’s view first on New Zealand section 8, Argentina’s foreign-jurisdiction exposure, Portugal named-employee addresses, Zimbabwe licensing, and the unverified Egypt/Botswana/Namibia 2025–2026 legislative claims.

## What I could not verify

I could not independently authenticate from the supplied material alone:

- the official Gazette text and current status of Egypt’s **Decree 816/2025** and its grace-period provisions;
- Botswana’s **Act 18 of 2024**, commencement order, and exact ECTA section 38 wording;
- Namibia’s **GN 182 of 2026** commencement position;
- whether Portugal **Lei 46/2012 Article 5(b)** repealed rather than amended the cited DL 7/2004 provision;
- the precise territorial application of UEMA, Lei 41/2004, UK PECR, French electronic-marketing law, Argentina’s Ley 25.326, and Zimbabwe’s licensing regulations to a South African sender with no local establishment;
- the precise 2026 French CNIL B2C change;
- the exact penalty mapping for Kenya regulation 17;
- the proposition that South African regulator guidance exempts all role-based business addresses from POPIA section 69.
