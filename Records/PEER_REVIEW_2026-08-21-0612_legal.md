# Independent Peer Review — 2026-08-21-0612

*Peer: gpt-5.6-luna (second vendor, read-only) · Lens: legal · Author: Claude · System Engineer: David*

**Scope:**
  - /tmp/localize_country_layer.py (18,641 chars)

**Usage:** 6239 in / 9358 out tokens · actual cost ≈ $0.0125

---

# Peer review — Legal / regulatory assessment

**Scope and status.** This is an independent review of the supplied material, not legal advice, legal approval, or a substitute for jurisdiction-specific counsel. I have assessed the drafting and stated legal propositions against the law as identifiable from the material and my legal knowledge. Several 2026 commencement, agency-practice, and regulatory-status assertions cannot be verified from the files alone; those gaps are identified below.

## Executive conclusion

The fail-closed country selection is a useful engineering control, but the compliance layer is **not presently capable of proving that the claimed duties have been discharged**.

The most serious issues are:

1. The FR and PT footers plainly do **not** contain all required GDPR Article 14 information.
2. The GB implementation cannot distinguish corporate subscribers from sole traders and other individual subscribers, so it can send PECR-prohibited email to recipients for whom consent is required.
3. The system can still send without a footer or without the required subject modification, and several “mandatory configuration” checks validate only that an environment variable is nonempty—not that it contains a lawful, accurate address or representative.

The legal research also appears to omit the sender’s own South African direct-marketing obligations, especially **POPIA section 69**, which is a material omission.

---

## Findings

### 1. MAJOR — FR and PT footers do not discharge GDPR Article 14

**File:** `_FOOTER['FR']` and `_FOOTER['PT']`

The comment says these footers carry the Article 14 disclosures, but the text does not contain the required information.

The footers do provide, at least partially:

- **Controller identity:** “TrustSquare (Pty) Ltd”
- **Some controller contact information:** `privacy@trustsquare.co` appears only in the objection sentence
- **Purpose:** a vague description of a “single” professional introduction / commercial communication
- **Legal basis:** legitimate interest under Article 6(1)(f)
- **Source category:** “a public source,” with an optional `{source}` insertion
- **Objection right:** prominently presented
- **Complaint authority:** CNIL or CNPD

They do not provide, or do not provide sufficiently:

- **The controller’s complete contact details.** An email address alone may be a contact detail, but the footer does not clearly identify it as the controller’s privacy contact and does not consistently provide a physical or other complete contact channel.
- **DPO contact details, where a DPO is required.** The code assumes that the DPO item is satisfied by the controller’s ordinary email address. It is not. If no DPO is legally required, the notice should not imply that the ordinary privacy address is a DPO address.
- **The specific purposes of processing.** “One-time introduction to your business” is not a complete description of the purposes. It does not clearly state, for example, prospecting, direct marketing, maintaining suppression records, or processing objections.
- **The legitimate interests pursued.** Stating “legitimate interest” or “interesse legítimo” identifies a legal basis but does not state the actual interests being pursued, as Article 14(2)(b) requires.
- **The categories of personal data.** “Your contact details” is not necessarily enough, particularly where the data set may include name, job title, work email, telephone number, business address, source URL, and inferred business role.
- **Recipients or categories of recipients.** There is no disclosure of email service providers, CRM providers, hosting providers, suppression-list providers, or other recipients.
- **International transfers and safeguards.** TrustSquare is South African and the email infrastructure may involve non-EU providers. The notice says nothing about transfers outside the EEA, destination countries, adequacy decisions, SCCs, or other safeguards.
- **Retention period or retention criteria.** “We will not email you again” does not explain how long the address, source record, campaign record, or suppression record will be retained.
- **The full list of rights.** The footer mentions only objection. It does not explain access, rectification, erasure, restriction, portability where applicable, or the right to withdraw consent where consent is used.
- **The source with sufficient specificity.** `{source}` is optional. When it is absent, “a public source” is not a meaningful source disclosure. Article 14 requires the source, including whether it came from publicly accessible sources. The actual source should be stated, such as the particular website, directory, or other source, subject to counsel confirming the appropriate level of detail.
- **The timing requirement.** Article 14 information must be supplied within the Article 14 period and, at the latest, at the first communication. A footer can satisfy the timing aspect only if the message is actually sent and the footer is present and accurate.

The French footer also says “Nous ne vous écrirons pas une seconde fois,” while the system’s broader claim is that the message is a one-time message. That is not a substitute for a proper suppression mechanism and does not remove the requirement to explain retention and rights.

The Portuguese footer’s statement that the communication is directed to a “pessoa colectiva” is also unsafe where the underlying address is a named employee, sole trader, or other natural person.

---

### 2. MAJOR — GDPR Article 27 representative handling is overbroad and the footer does not clearly identify the representative

**File:** `EU_REP`, `_EU_REP_REQUIRED`, `localize_html()`, FR/PT footers

The implementation blocks all FR and PT messages unless `TS_EU_REPRESENTATIVE` is nonempty:

```python
_EU_REP_REQUIRED = ('FR', 'PT')
```

That is not automatically correct. Article 27 contains exceptions, including situations where processing is only occasional and does not involve large-scale processing or certain sensitive categories. Whether the exception applies requires factual analysis; the code cannot assume that every South African sender emailing a small number of business addresses must appoint a representative.

Conversely, if Article 27 does apply, merely inserting an arbitrary string from `TS_EU_REPRESENTATIVE` is insufficient. The notice should clearly identify the representative and provide the representative’s relevant contact details. The footer currently renders:

```html
{eurep}
```

with no label such as “EU representative,” no validation, and no assurance that the value identifies a qualifying EU-established representative.

This creates both **false positives**—unnecessary appointment and cost—and **false negatives**—a noncompliant notice if the variable contains an incomplete or unqualified value.

---

### 3. MAJOR — The extraterritorial analysis is incomplete for a South African sender

**File:** module docstring; `SUPPORTED`; comments referring to “cleared destinations”

The material treats the absence of a local establishment as an important fact but does not complete the analysis.

For GDPR purposes, a South African controller may still fall within Article 3(2) if its processing is connected with offering goods or services to individuals in the EU or monitoring their behaviour. A single unsolicited business email may or may not amount to “offering goods or services,” depending on the content, targeting, and facts. The code does not perform or record that analysis. It simply assumes that FR and PT require GDPR Article 14 and an Article 27 representative.

There are therefore two separate questions that the research must distinguish:

1. **Does GDPR apply to the processing at all?**
2. **If it applies, does Article 14 apply and is an Article 27 representative required?**

The absence of an EU establishment does not answer either question by itself.

The same issue arises outside Europe. Local electronic-marketing laws frequently apply based on the recipient, message, or destination—not only on the sender’s establishment. A South African sender cannot treat “no local establishment” as a general exemption.

---

### 4. MAJOR — The GB footer relies on a classification the data model cannot establish

**File:** `SUPPORTED`, GB comments, `_FOOTER['GB']`

The GB approach assumes that all scraped “business addresses” are corporate subscribers. That is not safe.

Under PECR, sole traders and some partnerships are treated as individual subscribers. The code has no field or decision path for:

- limited company versus sole trader;
- ordinary partnership versus qualifying corporate subscriber;
- named professional address versus generic company mailbox;
- an address belonging to an individual rather than a corporate subscriber.

`country_of()` returns only `GB`; it does not establish subscriber type. Consequently, a GB wave can send email using the corporate-subscriber exemption to recipients for whom consent is required.

The footer cannot cure that defect. “Sent to your published business address” is not consent, and “we will not email you again” is not a substitute for the PECR consent requirement where the recipient is an individual subscriber.

There is additional risk under UK data-protection law for named work addresses. Even where PECR permits email to a corporate subscriber, the associated name and address may still be personal data, triggering UK GDPR/DPA 2018 transparency, lawful-basis, objection, retention, and source obligations.

**Required counsel discussion:** GB should be either limited to demonstrably qualifying corporate subscribers or handled using a separate consent and UK privacy-notice path. A country code alone is not an adequate control.

---

### 5. MAJOR — NZ footer is not a complete IPP 3A notice

**File:** `_FOOTER['NZ']`

The footer says:

> “We collected these details from that public source rather than from you (Privacy Act 2020, IPP 3A).”

That is useful but does not, on its face, provide the complete indirect-collection information required by IPP 3A.

Material omissions or ambiguities include:

- no clearly stated **purpose or purposes** beyond the vague phrase that the message “relates to your business”;
- no **intended recipients or categories of recipients**;
- no clear statement of the individual’s **Privacy Act access and correction rights**;
- no clear identification of a privacy contact by email or other contact method;
- no reliable source identification where `{source}` is absent;
- no explanation of retention;
- no statement of the agency’s relevant contact details beyond the interpolated postal value.

The statement that the address remains valid for 30 days is not enough by itself. The code checks only:

```python
if country in _POSTAL_REQUIRED and not POSTAL:
```

It does not verify that the address is real, reachable, accurate, or the address at which the sender can actually be contacted. Nor does the code demonstrate that the unsubscribe link will continue functioning for at least 30 days.

The UEMA and Privacy Act requirements are separate. A footer can contain an indirect-collection notice and still fail the UEMA requirements, or vice versa.

I am also not able, from the material alone, to verify the asserted **1 May 2026 commencement date for IPP 3A** or the precise final wording of the amendment. Counsel should verify the commencement instrument and current consolidated Act before relying on that date.

---

### 6. MAJOR — The AR citation and drafting require primary-source verification; the footer may be incomplete even if the quoted provisions are correct

**File:** `_FOOTER['AR']`, `localize_subject()`

The following citations are identifiable and appear facially plausible:

- Ley 25.326, Article 27(3);
- Decreto 1558/2001, Article 27, third paragraph;
- Disposición DNPDP 4/2009.

However, the material does not provide the title, official publication, current agency status, or current consolidated text for Disposición 4/2009. I cannot confidently verify from the supplied file that:

1. the citation is correctly styled;
2. the cited provision remains operative in August 2026;
3. the requirement is exactly that the literal word `publicidad` must appear in the subject/header;
4. the quoted language is an accurate and complete transcription.

This must be checked against the official Argentine primary sources. The former DNPDP framework and subsequent AAIP institutional changes make reliance on an old agency disposition without a current-status check particularly risky.

Even assuming the citations and quotations are correct, the footer has weaknesses:

- the subject modification occurs only if `localize_subject()` is called;
- the code does not verify that the subject remains visibly and clearly marked after other subject transformations;
- it does not verify that the removal/blocking mechanism actually works;
- “use the unsubscribe link above” assumes a valid link exists and remains functional;
- it does not clearly identify all relevant database/controller information;
- it says the data came from “a source of unrestricted public access,” but `{source}` is optional and unvalidated.

The footer also says “No volveremos a escribirle.” That is not the same as ensuring that the address is removed or blocked from all applicable databases and suppression systems.

---

### 7. MAJOR — US CAN-SPAM controls are materially incomplete

**File:** `_FOOTER['US']`, `POSTAL`, `localize_html()`

The code’s refusal to send when `TS_POSTAL_ADDRESS` is empty is a good control, but it does not establish compliance.

CAN-SPAM applies to B2B commercial email as well as consumer email. The implementation does not demonstrate controls for:

- accurate, nondeceptive header information;
- nondeceptive subject lines;
- required clear identification of the message as an advertisement, where applicable;
- a functioning opt-out mechanism;
- processing opt-outs within the statutory period;
- keeping the opt-out mechanism functional for the required period;
- not requiring a fee, account, or excessive steps to unsubscribe;
- suppression across future campaigns;
- vendor/agency monitoring and responsibility.

The footer says:

> “Unsubscribe instantly with the link above.”

But the supplied file does not prove that there is an unsubscribe link, that it is functional, that it requires no login, or that “instantly” is operationally true.

The statement that the message is sent because business details are publicly listed is not a CAN-SPAM substitute for the required disclosures. The “one-message” promise also does not remove CAN-SPAM obligations for the message that is sent.

I also disagree with the comment that a valid address must be a US address. CAN-SPAM requires a valid physical postal address; it does not generally say that the street address must be located in the United States. A legitimate South African street address may be capable of satisfying the physical-address requirement, whereas USPS-specific rules apply to the PO-box/private-mailbox alternatives. The current check is nevertheless inadequate because it tests only nonemptiness and does not verify validity or accuracy.

---

### 8. MAJOR — The system can send a message with no compliance footer

**File:** `localize_html()`

The function injects a footer only under this condition:

```python
if footer and '</body>' in html:
    ...
```

If the rendered HTML lacks a literal lowercase `</body>` tag, `localize_html()` returns the transformed HTML without raising an exception and without adding the footer.

This directly defeats the stated fail-closed design. It is especially significant for:

- CAN-SPAM postal-address and unsubscribe disclosures;
- FR/PT Article 14 information;
- NZ IPP 3A and UEMA information;
- AR Article 27(3) notice.

The function should not be considered fail-closed unless absence of the insertion point is itself an error, or the output is independently verified to contain the required disclosures.

Related problems:

- `footer` could theoretically be absent for a supported country without an exception;
- no postcondition asserts that the final HTML contains the expected identity, address, source, and opt-out text;
- no postcondition checks that placeholders such as `{postal}`, `{source}`, or `{eurep}` remain unresolved;
- no postcondition checks that the rendered text is visible rather than hidden or malformed.

---

### 9. MAJOR — `localize_subject()` is not fail-closed and can be called independently of country resolution

**File:** `localize_subject()`

This function deliberately returns the original subject for unresolved countries:

```python
if country in (None, '', 'ZA'):
    return subject
```

For Argentina, the required subject marker is applied only if this function is called. There is no assertion in the supplied material that every send path calls both `country_of()` → `localize_html()` and `localize_subject()` in that order.

Therefore:

- an unresolved country can pass through subject localization unchanged;
- an AR email can be sent without `PUBLICIDAD` if the caller omits `localize_subject()`;
- direct callers can invoke `localize_subject(subject, 'AR')` without having passed through the fail-closed HTML function;
- there is no final send-time assertion that the AR subject contains the required marker.

This is a material gap because the AR requirement is claimed to depend on a literal subject word.

---

### 10. MAJOR — “Publicly listed” or “conspicuously published” does not automatically establish consent or permission

**File:** module comments; FR/PT/NZ/AU/AR footers

The source material repeatedly treats a business address appearing on OpenStreetMap or a company website as sufficient legal basis or consent:

- AU: “inferred consent via conspicuously-published business address”;
- NZ: “deemed consent for conspicuously published business addresses”;
- FR: public professional address;
- AR: unrestricted public source;
- PT: public source.

That is too categorical.

The legal effect depends on facts such as:

- whether the address was published for business contact rather than marketing;
- whether the publication included a statement or indicator not to use it for unsolicited marketing;
- whether the address is generic or identifies an individual;
- whether the message is relevant to the recipient’s professional role;
- whether the source terms restrict scraping or reuse;
- whether the address was copied from a third-party directory rather than directly from the business;
- whether the data is still current;
- whether the intended message is direct marketing.

OpenStreetMap is particularly important: its data licence governs reuse of the database, but does not itself establish electronic-marketing consent or override privacy and anti-spam laws. A company website’s publication of an email address likewise does not universally amount to consent.

The footer cannot retroactively create consent where the governing law requires prior consent.

---

### 11. MAJOR — The research appears to omit South African POPIA and sender-side obligations

**File:** entire module; `SUPPORTED` and launch-plan comments

TrustSquare is a South African company processing contact information for direct marketing. The material does not discuss:

- **POPIA section 69** and electronic direct marketing;
- whether the addresses are personal information under POPIA;
- the requirements for an unsolicited electronic communication;
- the first-communication exception, if any, and its conditions;
- the required opportunity to object;
- POPIA transparency and source obligations;
- cross-border transfer issues under POPIA section 72;
- operator/vendor arrangements and information-security duties;
- retention and deletion/suppression-list treatment.

The fact that the recipients are businesses does not automatically mean that the information is not personal information. Named employee work addresses and sole-trader addresses are obvious examples.

This is a central legal omission: a South African sender may remain subject to South African law even when emailing foreign recipients. The destination-country footer does not discharge the sender’s home-country obligations.

Counsel should treat this as a priority issue rather than limiting review to the destination countries.

---

### 12. MAJOR — The source field is optional even where source disclosure is expressly claimed

**File:** `localize_html()`, all `{source}` footers

The code constructs the source text as:

```python
src_txt = f' (source: {source})' if source else ''
```

When `source` is absent, the footer says only “a public source,” “a publicly listed” address, or “a conspicuously published” address.

That is insufficient for a system that claims to provide source disclosure. It also creates an accuracy problem: the source may be the website, OSM, an enrichment provider, or an internal scrape, but the footer does not ensure that the stated source corresponds to the actual provenance of the address.

The system should not claim Article 14, IPP 3A, or similar source compliance unless source provenance is mandatory input and is preserved per recipient.

---

### 13. MAJOR — City fallback can misclassify a recipient and apply the wrong legal regime

**File:** `_CITY_COUNTRY`, `country_of()`

The fallback resolves country solely from a city name when the country field is absent. This is not a reliable legal-jurisdiction control.

Examples include:

- cities with the same name in multiple countries;
- prospect records containing a city without a country;
- foreign businesses whose city text is translated, abbreviated, or misspelled;
- addresses with a business location in one country but an email recipient physically located elsewhere.

A wrong city fallback can cause the system to send:

- a GB corporate-subscriber footer to an individual subscriber;
- a US footer where CAN-SPAM applies differently or additional state rules are relevant;
- no GDPR/UK/NZ notice where one is needed;
- an AR subject that is or is not marked incorrectly.

Unknown-country fail-closed behavior is helpful, but **incorrectly resolved country is not fail-closed**. Destination resolution needs confidence and provenance, not merely membership in a city dictionary.

---

### 14. MINOR — The postal-address checks are configuration checks, not legal checks

**File:** `POSTAL`, `_POSTAL_REQUIRED`

The code blocks only an empty environment variable. It does not establish that the value is:

- a real physical postal address;
- current and accurate;
- an address at which TrustSquare can receive correspondence;
- correctly rendered and visible in the final message;
- consistent with the sender identity;
- suitable for the applicable jurisdiction.

This is particularly important because the comments describe the value as “valid,” while the code has no validation beyond `.strip()`.

The same criticism applies to `EU_REP`: nonempty is not the same as appointed, qualified, located in the EU, and correctly identified.

---

### 15. QUESTION — Is the “one message per address” assumption operationally enforceable?

**File:** US/GB/AU/NZ/AR/FR/PT footers; module description

The footers repeatedly promise:

> “We will not email you again.”

The material does not show a durable global suppression list, deduplication across aliases, handling of role changes, or suppression propagation across all campaigns and vendors.

Questions for counsel and the System Engineer:

- Is suppression keyed only to the exact email address?
- Does it cover aliases, alternate addresses, and the underlying business?
- Does an opt-out in one jurisdiction suppress future messages globally?
- Are bounced, forwarded, or recycled addresses handled?
- Is the “one message” promise accurate if another campaign later uses the same contact from a different source?

An inaccurate promise is counterproductive: it can make a later lawful or unlawful contact evidence of a misleading practice.

---

### 16. QUESTION — What exactly is the unsubscribe link and what legal action does it perform?

**File:** all footers referring to “the link above”

The supplied file does not define the link, its endpoint, or its processing behavior.

Please establish:

- whether it is one-click or requires a form;
- whether it works without login;
- whether it is available for at least the legally required period;
- whether it records an immediate suppression;
- whether it suppresses all marketing channels;
- whether it exposes the recipient’s email address in a URL;
- whether it is secure and does not permit unauthorized third parties to opt out or access data;
- whether it is present in plain-text email as well as HTML email.

The footer claims immediate honoring, but no mechanism is shown to support that claim.

---

### 17. MINOR — The ZA and NA treatment does not mean that no legal rule applies

**File:** `SUPPORTED`, ZA/NA footers

The module leaves ZA unchanged and describes Namibia as having “no marketing rule in force.” Those are broad propositions requiring verification.

For South Africa, the unchanged ZA output may mean that the new system provides no additional privacy or marketing disclosure despite TrustSquare being subject to South African law.

For Namibia, “no marketing rule in force” does not resolve:

- data-protection or privacy-law exposure;
- common-law or consumer-protection constraints;
- telecommunications or electronic-communications requirements;
- contractual or website terms governing scraping;
- the legal status of a named individual’s work address.

The NA footer’s “unsubscribe instantly” statement is also unsupported by the supplied implementation.

---

## Citation and current-law assessment

### PRAISE — Several core provisions cited are real and directionally relevant

The following references are facially legitimate and relevant to the issues described:

- GDPR Articles 6(1)(f), 14, 21, and 27;
- Portugal Law 41/2004, Article 13-A;
- Argentina Law 25.326, Article 27;
- Argentina Decreto 1558/2001, Article 27;
- US CAN-SPAM, although the actual statutory citation is not included in the file;
- New Zealand Privacy Act 2020 and the stated IPP 3A concept, subject to commencement verification.

That said, relevance is not the same as completeness, and several propositions in the comments are more categorical than the law permits.

### MAJOR — The file does not provide a sufficient “current as at August 2026” citation record

The module refers to:

> “Outreach Law by Jurisdiction 2026-08-20”

but that research document is not included. As a result, I could not independently verify:

- whether every cited provision remains in force on 21 August 2026;
- the exact final text and commencement of NZ IPP 3A;
- the current status and operative text of Argentine Disposición DNPDP 4/2009;
- current French CNIL guidance and any applicable French ePrivacy interpretation;
- current Portuguese DGC-list rules;
- current UK PECR treatment of all relevant partnership forms;
- current Namibian law;
- whether any 2026 amendments or enforcement guidance change the stated conclusions.

The AR disposition and NZ IPP 3A date deserve particular primary-source verification. I am not asserting that either citation is invented; I am saying the supplied material does not establish that the proposition and current status are correct.

---

## Fail-closed design assessment

### PRAISE — Unknown and expressly uncleared countries no longer silently default to ZA

The change from an implicit ZA default to:

```python
return None
```

followed by `UnsupportedCountry` is a sound correction. It addresses the documented prior failure in which a French prospect could receive a South African message with no GDPR notice.

### BLOCKER — The design is not fail-closed at the final-send boundary

The stated guarantee is stronger than the implementation.

Specific escape paths include:

1. **No `</body>` tag:** `localize_html()` returns HTML without a footer and without raising.
2. **Subject path omitted:** `localize_subject()` is separate and does not fail for unresolved countries.
3. **Manual country value:** the caller can pass a supported country without demonstrating that it came from `country_of()`.
4. **Incorrect country resolution:** city fallback can produce a wrong but “supported” country.
5. **Optional source:** messages can be sent without actual source disclosure.
6. **Unvalidated configuration:** nonempty postal and representative variables pass.
7. **Unverified unsubscribe:** no final assertion proves the link exists and functions.
8. **Placeholder leakage:** no check prevents `{postal}`, `{source}`, or `{eurep}` from appearing literally in the message.
9. **Missing footer map:** a supported country with no footer would silently proceed because `if footer` is conditional.
10. **Case/format assumptions:** the insertion depends on an exact lowercase `</body>` string and may fail on otherwise valid HTML.

The system should be described as **country-selection fail-closed**, not **legal-message fail-closed**, unless the final send operation rejects any output that fails jurisdiction-specific postconditions.

---

## Material legal risk missed entirely

### BLOCKER — South African direct-marketing and privacy law

As noted above, the most material omission is the law applicable to TrustSquare itself. The module is designed around recipient-country rules but does not assess South African POPIA section 69, transparency, data-source, retention, cross-border, or suppression requirements.

Other material omissions include:

- website and OpenStreetMap licence/terms restrictions on scraping and reuse;
- UK GDPR/DPA obligations for GB named contacts, independent of PECR;
- state-level US privacy and telemarketing/contact-list rules where applicable;
- recordkeeping needed to prove the source, professional capacity, consent/inference, notice, and opt-out history;
- data-broker/enrichment-provider liability if scraped data is supplemented;
- controller/processor and international-transfer arrangements with email, CRM, hosting, and unsubscribe providers;
- security and breach obligations;
- treatment of sole traders and named employees across every jurisdiction, not merely GB;
- language and accessibility requirements where a notice is intended to be legally intelligible to the recipient.

---

## Three findings the System Engineer should discuss first

1. **BLOCKER — The apparent fail-closed design is not fail-closed.** A missing `</body>` tag can remove the footer silently, and the subject-localization path is independently bypassable.
2. **MAJOR — FR/PT do not satisfy the claimed GDPR Article 14 disclosure.** The notices omit recipients, transfers, retention, most rights, detailed purposes/interests, complete categories, and reliable source disclosure.
3. **MAJOR — GB recipient classification is absent.** The system cannot distinguish corporate subscribers from sole traders and other individual subscribers, so the PECR exemption cannot safely be applied.

## What I could not verify from the material provided

I could not verify the current August 2026 consolidated text or status of every cited provision because the referenced legal-research document was not supplied. In particular, counsel should verify the commencement and exact requirements of NZ IPP 3A, the current force and precise wording of Argentine Disposición DNPDP 4/2009, the detailed Portuguese DGC-register position, and the current treatment of all UK partnership categories. I also could not inspect the rendering pipeline, unsubscribe implementation, send orchestration, source-provenance records, suppression database, or the actual email headers and plain-text version.
