All nine jurisdictions researched, and I independently re-verified the six highest-risk claims against primary sources. Report follows.

---

# B2B COLD EMAIL — 9 JURISDICTIONS
**Verified 20 August 2026. Sender assumed: South African company, no local establishment, emailing business addresses.**

## HEADLINE TABLE

| Country | Consent model for B2B cold email | Binds an SA sender? | Verdict |
|---|---|---|---|
| **New Zealand** | Opt-in, BUT **deemed consent** for conspicuously published business addresses | NZ link near-certain; s.8 reach arguable | **SENDABLE with discipline** |
| **Argentina** | **OPT-OUT** — publicly accessible sources may be used without consent | No express clause; AAIP asserts reach in practice | **SENDABLE** (but "publicidad" header rule) |
| **Portugal** | **OPT-OUT for legal persons** — express corporate exemption + mandatory registry check | GDPR art.3(2): yes. ePrivacy: unsettled | **SENDABLE with discipline** |
| **Namibia** | **No rule in force at all** | No | **SENDABLE — but latent risk** |
| **Kenya** | **Opt-in, two independent statutes. No exemption** | **Yes, expressly (s.4(b)(ii))** + must register with ODPC | **DO NOT COLD EMAIL** |
| **Egypt** | **Opt-in + State LICENCE + Egyptian representative** | Yes for regulatory; criminal limb needs dual criminality | **DO NOT COLD EMAIL** |
| **Zimbabwe** | Notice-of-objection duty only; legitimate-interests available | Only if "means located in Zimbabwe" — arguably not | **SENDABLE, low risk** |
| **Botswana** | **Opt-in (ECTA s.38 soft opt-in). No exemption** | **Yes, expressly (DPA s.4(2)(b)(i))** + local rep required | **DO NOT COLD EMAIL** |
| **Mozambique** | **Opt-in (Lei 3/2017 art.40)** | No express hook — unverified | **Technically unlawful, unenforceable** |

---

## 1. NEW ZEALAND — confidence HIGH (except extraterritoriality)

**Statute/regulator:** Unsolicited Electronic Messages Act 2007 (UEMA) + Regulations 2007 (SR 2007/271). Enforced by **Department of Internal Affairs (DIA)**. Privacy Act 2020 runs in parallel under the **Privacy Commissioner (OPC)**.

**CONSENT MODEL — opt-in with a de facto B2B gateway.** There is no corporate-subscriber exemption of the EU kind. s.9(1) bans unsolicited commercial messages with a NZ link. But s.4 "consented to receiving" includes **deemed consent**, requiring all three cumulatively:
1. the address was **conspicuously published by a person in a business or official capacity**;
2. publication is **not accompanied by a statement** that they don't want unsolicited messages;
3. the message is **relevant to the business, role, functions or duties** of that person.

**s.9(3) puts the onus of proof on the sender**, per address. No regulations have ever been made under the s.4(ii)(B) or s.4(b) limbs, so the three-condition test is the whole test.

**Scraped addresses:** Permitted — DIA expressly blesses website/brochure/trade-directory sourcing. Two traps: (a) **purchased lists do not inherit consent** (DIA guidance); (b) **s.13** bans address-harvesting software, but s.13(2) binds only individuals physically in NZ or organisations carrying on business in NZ — an SA scraper is on its face outside it.

**Mandatory content:** s.10 — clearly and accurately identify the person who authorised the sending, plus contact information **valid for at least 30 days**. **No CAN-SPAM-style physical postal address required.** s.11(1) — functional unsubscribe, clear and conspicuous, same communication method, free, **valid ≥30 days**. **Opt-out honoured within 5 working days (s.9(2))**, clock starting the day after use.

Note s.6(a)(iii): a mere hyperlink to marketing content — including in an email signature — makes a message commercial.

**Penalties:** Unit is the "civil liability event" (s.18) — one per non-compliant message, and s.10/s.11 breaches stack on an s.9 breach. Infringement notices: **NZ$200 individual / NZ$500 organisation PER EVENT** (reg 7). Court pecuniary penalty (s.45): **up to NZ$200,000 individual / NZ$500,000 organisation** — an aggregate cap per proceeding, not per message. Any affected person may sue directly (s.19, s.46). Real outcomes: *DIA v Atkinson* NZ$100k each; Image Marketing Group NZ$120k.

**EXTRATERRITORIALITY — genuine unresolved conflict, flagging it.** The "New Zealand link" (s.4) is vast and you will trigger it (recipient organisation carrying on business in NZ; `.nz` address; NZ device). **But s.8** extends the Act to conduct outside NZ only by a "relevant person" = an individual **resident in NZ** or an organisation that **carries on business or activities in NZ**. An SA company with neither is arguably outside s.8. **DIA's public guidance ignores this limit** ("sent to, from, or within New Zealand"). No case law resolves it. Assume it applies — soliciting NZ customers commercially is a low bar for "activities in New Zealand."

**⚠️ FLAG — CHANGED 1 MAY 2026 (independently verified).** The Privacy Amendment Act 2025 introduced **IPP 3A**, in force **1 May 2026**: where you collect personal information from a source **other than the individual**, you must take reasonable steps to make that individual aware of prescribed matters, as soon as reasonably practicable after collection. **This is aimed squarely at scraped and purchased B2B lists.** UEMA deemed consent may make the *send* lawful while IPP 3A independently obliges you to *notify*. Two regulators, two breaches, one campaign. Privacy Act s.4 reaches an overseas agency carrying on business in NZ regardless of place of business or profit.

Sources: [UEMA full text](https://www.legislation.govt.nz/act/public/2007/0007/latest/whole.html) · [Regulations 2007](https://www.legislation.govt.nz/secondary-legislation/pco-drafted/2007/271/en/latest/) · [DIA FAQ](https://www.dia.govt.nz/Spam-Frequently-Asked-Questions) · [DIA for businesses](https://www.dia.govt.nz/Spam-NZ-Spam-Law-for-Businesses) · [OPC IPP 3A guidance](https://www.privacy.org.nz/resources-and-learning/a-z-topics/ipp3a/) · [PwC NZ on IPP 3A](https://www.pwc.co.nz/insights-and-publications/2026-publications/new-indirect-collection-notification-obligations-privacy-act-2025.html) · [Hunton](https://www.hunton.com/privacy-and-cybersecurity-law-blog/new-zealand-privacy-amendment-act-2025-introduces-new-notification-requirements)

---

## 2. ARGENTINA — confidence HIGH on the law, LOW on extraterritoriality

**Statute/regulator:** **Ley 25.326** (2000) + **Decreto 1558/2001** + **Disposición DNPDP 4/2009** (still in force — confirmed absent from the repeal clause of Res. 126/2024 art.8). Regulator: **AAIP** (Agencia de Acceso a la Información Pública) via the Dirección Nacional de Protección de Datos Personales. **There is no spam-specific statute in Argentina.**

**⚠️ NEW LAW STATUS — VERIFIED NOT ENACTED.** The Executive bill (Mensaje 87/2023) **lost parliamentary status at end-2024**. Three successor bills sit in Congress — Carro (1948-D-2025), Doñate (S-644/25), Yeza (1751-D-2026, which would expressly repeal Ley 25.326). **None enacted.** A 7 April 2026 *Diario Judicial* analysis still frames reform as prospective.

**CONSENT MODEL — OPT-OUT. This is the most permissive of the nine.** Art. 27.1 permits processing data for advertising/direct-sales profiling **"cuando éstos figuren en documentos accesibles al público"** — no consent needed. Reinforced by art. 5.2(a) (unrestricted public-access sources) and art. 5.2(c) (name, ID, **occupation**, DOB, address lists). Decreto 1558/2001 art.27 confirms data may be collected, processed and transferred for advertising **"sin consentimiento de su titular."** Art. 27.3 gives an unconditional right to demand *retiro o bloqueo* at any time.

**⚠️ Scope trap running the other way: Argentina protects LEGAL PERSONS.** Art.1 and art.2 extend the law to *personas de existencia ideal* with legal domicile, branches or subsidiaries in the country. So `ventas@empresa.com.ar` is *not* outside the law the way a generic mailbox is in the EU or NZ.

**Scraped addresses:** Yes, if genuinely from an **unrestricted** public source — behind a login, paywall or restrictive terms is not "irrestricto." Art.4 (not excessive) and art.6 (information duty) still apply.

**Mandatory content — unusually prescriptive, and almost no sending platform does this by default:**
- **The literal word "publicidad" must appear in the email header/subject** (Disp. 4/2009 art.2).
- Prominent notice of the right to total or partial *retiro o bloqueo*, **plus the verbatim transcription of art.27 inc.3 of Ley 25.326 and the third paragraph of art.27 of Decreto 1558/01** (Disp. 4/2009 art.1).
- The opt-out mechanism must be described, and verified to have real operational capacity (art.3).
- **On request, disclose who supplied the data** (Decreto art.27 ¶3).
- No fixed statutory deadline to honour opt-outs — art.27.3 says "en cualquier momento." Treat as immediate.

**Penalties:** Statutory ceiling art.31.1 — **ARS 1,000 to ARS 100,000**, plus apercibimiento, suspension, closure or **cancellation of the database**. Res. 126/2024 (as amended by Res. 179/2025) grades: leve ARS 1,000–80,000; grave ARS 80,001–90,000; muy grave ARS 90,001–100,000. **Per infraction, not per day.** **Ignoring an email opt-out is expressly classified GRAVE** (Anexo I(k)). Note: after inflation the peso cap is nominally trivial and AAIP itself acknowledges weak deterrence — **the real exposure is private habeas data actions plus damages** (*Tanús c. Cosa*, 2006, held that a profession-classified email collection is a database and unsolicited sending breaches the law).

**"No Llame" registry (Ley 26.951): TELEPHONE ONLY.** Confirmed from the statute — scope is "servicios de telefonía" including VoIP. **Email is outside it.** No registry to check.

**Extraterritoriality:** No express clause. Art.44 gives federal jurisdiction over databases "interconectados en redes … internacional," the usual hook. AAIP *has in practice* asserted jurisdiction over a foreign entity with no Argentine branch (Worldcoin Foundation). But no resolution or case squarely holds the law binds a foreign company merely emailing in. **Unsettled.**

Consumer law (Ley 24.240) is largely irrelevant — B2B buyers are not *destinatarios finales*.

Sources: [Ley 25.326](https://servicios.infoleg.gob.ar/infolegInternet/anexos/60000-64999/64790/texact.htm) · [Decreto 1558/2001](http://servicios.infoleg.gob.ar/infolegInternet/anexos/70000-74999/70368/norma.htm) · [Disp. DNPDP 4/2009](https://servicios.infoleg.gob.ar/infolegInternet/anexos/150000-154999/151221/norma.htm) · [Res. AAIP 126/2024 texto actualizado](https://servicios.infoleg.gob.ar/infolegInternet/anexos/395000-399999/399750/texact.htm) · [Res. 179/2025](https://www.boletinoficial.gob.ar/detalleAviso/primera/332082/20250930) · [Ley 26.951](https://servicios.infoleg.gob.ar/infolegInternet/anexos/230000-234999/233066/texact.htm) · [Diario Judicial Apr 2026](https://www.diariojudicial.com/news-103126-proteccion-de-datos-personales-sigue-siendo-suficiente-la-ley-25326-en-2026)

---

## 3. PORTUGAL — confidence HIGH on the exemption, MEDIUM on named individuals

**Statutes:** GDPR + **Lei 41/2004** (ePrivacy, republished by Lei 46/2012) arts. **13.º-A and 13.º-B** + Lei 58/2019 + DL 7/2004 art. 21.º. Checked currency: the only later amendment, Lei 16/2022, touches **only arts. 7.º and 10.º** — 13.º-A/13.º-B untouched.

**Regulators — the split matters.** **CNPD** has exclusive competence to fine breaches of arts. 13.º-A(1)–(4) and 13.º-B(1)/(3) (art. 15.º(1)). **ANACOM does not fine spam** — it routes complaints to CNPD. **DGC** maintains the corporate opt-out registry.

**✅ CONSENT MODEL — YES, THERE IS A CORPORATE EXEMPTION. B2B email to a company subscriber is OPT-OUT.** Art. 13.º-A(1) requires prior express consent of "the subscriber who is a **natural person**, or of the user." **Art. 13.º-A(2):** *"The provisions of the preceding paragraph do not apply to subscribers who are **legal persons**, unsolicited direct-marketing communications being permitted until such subscribers refuse future communications and register on the list provided for in art. 13.º-B(2)."* ANACOM confirms: legal persons are subject to the *sistema de opção negativa*. Independently verified.

The art. 13.º-A(3) soft opt-in (existing customers, analogous products) is separate and unusable for cold prospects.

**⚠️ THE DGC REGISTRY IS REAL, LIVE, AND CHECKING IT IS A HARD STATUTORY DUTY.** Art. 13.º-B(5): entities promoting direct marketing **"são obrigadas a consultar a lista,"** updated monthly. Live at [consumidor.gov.pt — lista de pessoas colectivas](https://www.consumidor.gov.pt/informacao-publicidade/lista-de-pessoas-coletivas-para-nao-rececao-de-comunicacao-nao-solicitadas-marketing-direto), with downloadable tables. Counts read off the live page 20 Aug 2026: **fax 37, mobile 140, e-mail 184 records.** Tiny list, free, mandatory. **Do not confuse with the "Lista Robinson"** (AMD, Lei 6/99) — natural persons only, postal and telemarketing only, explicitly NOT electronic communications.

**⚠️ THE BIGGEST LIVE UNCERTAINTY — `joao.silva@empresa.pt`.** Two layers:
- *ePrivacy:* art. 13.º-A(1)'s "or of the **user**" limb (defined in art. 2.º(1)(c) as a **natural person** using a service "for private or **commercial** purposes") arguably still catches a named employee. Art. 13.º-A(2) disapplies all of (1) where the subscriber is a legal person — the mainstream and ANACOM reading. **CNPD expressly refused to rule on this**: Diretriz/2022/1 fn.2 states the B2B regime of arts. 13.º-A/13.º-B "não é abordado." No CNPD decision, ANACOM decision or court ruling found either way.
- *GDPR applies regardless* and is not switched off by the exemption: you still owe a lawful basis, the art. 14 notice, the art. 21(2)–(3) objection right, and **art. 27 EU representative**.

**Practical consequence, and the cheapest risk reduction available:** prefer role addresses (`geral@`, `info@`, `comercial@`). They sit squarely inside the corporate exemption and are arguably not personal data at all, which also takes you outside GDPR art. 3(2).

**Scraped addresses:** Permitted under art. 6(1)(f) + Recital 47, with a documented LIA. But **GDPR art. 14(3)(b) requires the notice at the latest at the time of the first communication** — and art. 14(2)(f) requires you to state **from which source the data originate, and whether it came from a publicly accessible source**. Art. 21(4) requires the objection right be presented **"clearly and separately from any other information."** **Do not buy Portuguese lists:** CNPD Diretriz/2022/1 §62 holds broker-sourced data may be used for **postal marketing only, not electronic communications**.

**Mandatory content:** Do not conceal the identity of the person on whose behalf the communication is made; a valid contact means for a stop request (art. 13.º-A(4)); advertising nature ostensibly identified and the advertiser identified (DL 7/2004 art. 21.º(a)(b)); the GDPR art. 14 notice including data source and EU representative; the art. 21 objection right presented separately. Maintain a provable suppression list (art. 13.º-B(1) — burden of proof on the sender). **Physical postal address is not expressly required** in the message (medium confidence) — include it anyway.

**Opt-out timeframe: IMMEDIATE. No grace period exists.** GDPR art. 21(3): on objection the data "shall no longer be processed" for marketing. Lei 41/2004 sets no numeric deadline; there is no Portuguese CAN-SPAM 10-day equivalent.

**Penalties:** Lei 41/2004 art. 14.º(1): **€1,500–€25,000 (natural persons) / €5,000–€5,000,000 (legal persons)** — limb (f) covers breach of art. 13.º-A(1)&(2), limb (h) concealed identity / no opt-out contact. Halved for negligence (art. 14.º(5)). Periodic penalty payments up to **€3,000,000, max 30 days** (art. 15.º-C) — the only day-based mechanism. **Per infringement, not per message.** GDPR art. 83: **€20m / 4%** — and note **CNPD Deliberação/2019/494 disapplies** Lei 58/2019 arts. 37(2)/38(2), so the SME-friendly Portuguese caps are dead letter and the full GDPR maxima apply. DL 7/2004 art. 21 breaches: €2,500–€50,000, raised by one third for legal persons → **€3,333–€66,667** (ANACOM).

**⚠️ Statutory gap worth knowing:** art. 14.º(1) lists 13.º-B(1) and (3) but **NOT 13.º-B(5)** — failing to consult the registry carries no direct fine on the face of the statute. Exposure arises only once you email a listed company.

**Extraterritoriality:** **GDPR art. 3(2)(a): YES**, almost certainly — EDPB Guidelines 3/2018 list "marketing and advertisement campaigns directed at an EU country audience" as an evidencing factor. **You must appoint an art. 27 EU representative** and name it in the art. 14 notice. **Lei 41/2004: UNSETTLED** — no territorial-application clause; cross-border cooperation runs through the EU IMI system, which does not reach South Africa. **DL 7/2004 art. 5.º(3) does have an express hook**: non-EU-origin information-society services are subject to Portuguese law.

**Enforcement reality:** CNPD fines collapsed — 2024: 23 fines, €138,375 total, of which **11 spam fines = €50,000 (avg ~€4,545)**; **2025: 2 fines, €47,000 total**, against **1,254 spam complaints**, with CNPD blaming insufficient staff. It has a Sept 2025 legislative proposal pending to speed throughput. **Do not price 2025 as the steady state.**

**✅ ePrivacy Regulation CONFIRMED WITHDRAWN** — Commission approved 16 July 2025, published OJ **C/2025/5423 on 6 October 2025**; EP Legislative Train file 2017/0003(COD) reads "Withdrawn." Directive 2002/58/EC and Lei 41/2004 stay in force indefinitely, so **the Portuguese corporate exemption is now the settled long-term position, not a transitional one.**

Sources: [Lei 46/2012 DR text (arts. 13.º-A, 13.º-B, 14.º, 15.º)](https://www.uc.pt/site/assets/files/475840/20120829_lei_46_2012_altera_lei_41_2004_protecao_dados_comunicacoes_eletronicas.pdf) · [ANACOM Lei 41/2004](https://www.anacom.pt/render.jsp?contentId=944401) · [ANACOM spam FAQ](https://anacom.pt/render.jsp?contentId=1140912) · [DGC opt-out list](https://www.consumidor.gov.pt/informacao-publicidade/lista-de-pessoas-coletivas-para-nao-rececao-de-comunicacao-nao-solicitadas-marketing-direto) · [CNPD Diretriz/2022/1](https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/121958) · [CNPD Deliberação/2019/494](https://www.cnpd.pt/umbraco/surface/cnpdDecision/download/121704) · [CNPD Relatório 2025](https://www.cnpd.pt/media/v50frkwy/relatorio-atividades-de-2025.pdf) · [EDPB Guidelines 3/2018](https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_3_2018_territorial_scope_after_public_consultation_en_1.pdf) · [EP Legislative Train — ePrivacy withdrawn](https://www.europarl.europa.eu/legislative-train/theme-connected-digital-single-market/file-jd-e-privacy-reform)

---

## 4. NAMIBIA — confidence HIGH

**Plainly: there is no enforceable Namibian rule against B2B cold email today.** No data protection Act, no consumer protection Act, no data protection authority, and the one spam provision on the books has never been switched on.

**Data Protection Bill: STILL A BILL.** NamibLII's 2026 legislation index shows only one 2026 Act of Parliament (the Appropriation Act). Minister Emma Theofelus, **26 Jan 2026**: the Bill is "ready for re-submission to the cabinet committee on legislation before being tabled in parliament" — i.e. not yet at Cabinet committee. DLA Piper (modified 20 Mar 2026): *"Namibia has not enacted comprehensive data privacy legislation… There is no national data protection authority… **There are no electronic marketing regulations.**"* The Sept-2025 tabling promise was missed. ⚠️ *Distrust dataprotection.africa/namibia — its footer reads "last updated 29 November 2022" and still names Hage Geingob as President.* **Gap stated plainly: no source found between 18 Feb and 20 Aug 2026; laws.parliament.na is login-gated. Current stage unverified.**

**⚠️ THE BIGGEST LATENT RISK IN THIS ENTIRE REPORT — and I verified it directly from the primary consolidation.** The **Electronic Transactions Act 4 of 2019** contains **s.36 "Unsolicited goods, services or communications"** inside **Chapter 4**. The commencement table (Laws.Africa consolidation, PDF generated 20 Aug 2026, updates checked to 14 Aug 2026) reads:

- Ch 1–3 (part), Ch 6, Ch 7 — **commenced 16 March 2020** (GN 75 of 2020)
- s.20 and **Chapter 5** — **commenced 15 June 2026** (GN 182 of 2026)
- **Chapter 4 (ss. 34–40) — "not yet commenced."**

**MICT issued a fresh commencement notice two months ago and deliberately left Chapter 4 out.** Chapter 4 is the last one remaining, and it needs only **one ministerial gazette notice — no Parliament** — to switch on:
- **s.36(2): opt-in only.** s.36(3) soft opt-in requires the address collected **in the course of a sale or negotiations for a sale**, similar products only, opt-out offered and declined at collection, opt-out in every subsequent message. **Cold email would not qualify.**
- **s.36(1) mandates:** originator's identity and contact details **including place of business, email, addresses and telefax number**; a valid and operational opt-out facility; and **the identifying particulars of the source from which the address was obtained**.
- **It would catch B2B.** "Consumer" is limited to natural persons, but s.36(1) is drafted wider ("to a consumer **or any other person**") and ss.36(2)–(3) operate on "addressees" = "a **person**", which under the Interpretation of Laws Proclamation 37 of 1920 s.2 includes companies and bodies corporate.
- **s.36(8): fine up to N$500,000 or 2 years imprisonment, or both** — and **s.36(7) makes the advertiser liable, not just the sender.**

**Monitor** [LAC's 2026 gazette index](https://www.lac.org.na/index.php/laws/gazettes-2026/) and the [Laws.Africa commencement table](https://commons.laws.africa/akn/na/act/2019/4).

**Communications Act 8 of 2009: no spam provision.** Full-text search returns zero hits for "unsolicited" or "spam." Only s.117 (general offences) is adjacent, and it requires **intent to annoy, abuse, threaten or harass** — commercial cold email does not meet it. **CRAN has no spam or electronic-marketing regulation** (index scan; medium confidence).

**Constitution art. 13(1)** protects privacy of "correspondence or communications," with qualified horizontal effect via art. 5. But it has historically been read as an interception/surveillance protection; an unwanted-but-readable business email is a very thin case, and **no Namibian judgment applying it to marketing was found.** Roman-Dutch *actio iniuriarum* exists in principle but needs *animus iniuriandi*, and **a juristic person cannot sue for iniuria to dignity/privacy**.

**Access to Information Act 8 of 2022: gazetted but NOT COMMENCED**, and on 4 March 2026 Parliament **suspended recruitment of the Information Commissioner**. It imposes no obligations on private senders — relevance to cold email: none.

**Extraterritorial reach: nothing bites today.** ETA has no general extraterritoriality clause; s.30 (in force) would supply a nexus only if Chapter 4 commenced. The draft Bill's **s.2(4)** is expressly extraterritorial and its **s.10(4) requires PRIOR CONSENT for electronic direct marketing with no soft opt-in** — stricter than Portugal or NZ if enacted.

Sources: [ETA 4/2019 consolidation with commencement table](https://commons.laws.africa/akn/na/act/2019/4/eng@2019-11-29.pdf) *(directly verified this session)* · [LAC annotated ETA](https://www.lac.org.na/laws/annoSTAT/Electronic%20Transactions%20Act%204%20of%202019.pdf) · [DLA Piper Namibia](https://www.dlapiperdataprotection.com/index.html?t=law&c=NA) · [Xinhua/Theofelus Jan 2026](https://english.news.cn/africa/20260127/4452afcddec14561a1b5db32cbedc433/c.html) · [NamibLII 2026 index](https://namiblii.org/legislation/?years=2026) · [Draft Data Protection Bill](https://www.civic264.org.na/images/pdf/Data_Protection_Bill_final_draft_bill.docx)

---

## 5. KENYA — confidence HIGH. **DO NOT COLD EMAIL.**

**Statutes/regulators:** Data Protection Act No. 24 of 2019 + **Data Protection (General) Regulations 2021** (LN 263/2021) + Registration Regulations 2021 (LN 265/2021) — **ODPC**. Plus **KICA** + **Kenya Information and Communications (Consumer Protection) Regulations 2010, reg. 17** — **Communications Authority (CA)**. *(Correction to the brief: the unsolicited-communications rule is reg. 17, not reg. 12.)*

**CONSENT MODEL — opt-in, and TWO INDEPENDENT statutes stack. No B2B or corporate exemption in either.**
1. **DPA s.37(1)(a):** no commercial use of personal data unless you "sought and obtained **express consent**." s.2 defines consent as "express, unequivocal, free, specific and informed… by a clear affirmative action" — opt-in by construction. Reg 15(1)(a) further contemplates data **collected from the data subject**, which a scraped list is not by definition. Reg 4(4) deems consent **not** freely given where "presumed on the basis that the data subject did not object."
2. **KICA CP Reg 17(1):** using email for direct marketing **without the prior consent of the subscriber is an offence.** Reg 17(4): all automated direct-marketing schemes used in Kenya "shall be based on an **opt-in principle**." Reg 17(3) soft opt-in is narrow — details obtained **in the context of a sale**, own similar products only.

**⚠️ The natural-person escape works for the DPA but NOT for KICA.** DPA s.2 protects natural persons only, and reg 14(3) says "marketing is **not direct** where personal data is not used or disclosed to identify or target particular recipients" — so a genuinely generic `info@` with no personalisation is arguably outside the DPA. **But KICA reg 17 protects "subscribers," defined in reg 2 as "any person" who buys a communications service — no natural-person limit, no corporate carve-out.** So even a pure `info@` blast is on its face an offence under reg 17(1).

**Drafting conflict, flagged:** reg 15(1) joins limbs (d) and (e) with "**or**" (the 2021 draft used "and"), which read disjunctively would look like an opt-out regime — contradicting the parent Act s.37(1)(a). CIPIT concluded the opt-out mechanism was intended as a *withdrawal* mechanism, not a lawful basis, and **ODPC's determinations enforce opt-in**. Treat opt-out-only as untenable.

**Scraped addresses: not usable.** Publication does not create consent. Indirect collection is a permitted *mode* (reg 6(1)(b): "publications or databases") but **reg 6(3) requires you to inform the data subject within 14 days**, and reg 15(1)(a) still points at data collected from the data subject. ODPC has repeatedly held data obtained for one purpose cannot be repurposed for marketing without fresh express consent.

**Mandatory content:** true undisguised sender identity; a **valid address** for a stop request (an email address suffices — no physical postal address mandated); free-of-charge restriction particulars; a prominent opt-out statement in **every** message with an "opt out of **all** future direct marketing" option; opt-out accessible to persons with disability. **Timeframe: third-party direct-marketing restriction within 7 days (reg 18(3)); general opt-out — cease immediately (reg 16(2)).**

**Penalties:** ODPC administrative fine s.63 — **KES 5,000,000, or 1% of preceding-year turnover, whichever is LOWER**. Compensation s.65 — uncapped, per complainant. Commercial use without consent, reg 15(4) — KES 20,000 and/or 6 months. General penalty s.73 — **KES 3,000,000 and/or 10 years**. KICA reg 17 via s.27(4) — KES 300,000 and/or 3 years *(penalty mapping medium confidence: the Regs draw on six enabling sections)*. **Per contravention/complaint, not per message or per day.**

Live enforcement is real and accelerating: *Antonate Aiko v Goodtimes Africa (Blankets & Wine)*, ODPC/COMP/2175/2025, determination **8 April 2026** — s.37 breach, **KES 300,000**. *Rocketpesa* (2024) **KES 2.6m** cumulative. *Pepinos Pizza Inn* (2025) KES 250,000. ~96 complaints determined and 76 fines in 2025.

**EXTRATERRITORIAL — YES, EXPRESSLY.** **s.4(b)(ii)**: the Act applies to a controller "not established or ordinarily resident in Kenya, but processing personal data of data subjects **located in Kenya**."

**⚠️ AND YOU MUST REGISTER.** ODPC's own Guidance Note confirms controllers **located outside Kenya** processing data of individuals in Kenya must register. The small-entity exemption (turnover < KES 5m AND < 10 employees) **never applies to Third Schedule categories, item 10 of which is "Businesses that are wholly or mainly in direct marketing."** A cold-outreach business must register **regardless of size**. Fees KES 4,000/16,000/40,000; certificate valid 24 months. **No local representative requirement** (unlike GDPR art. 27) — Kenya requires registration, not a rep. Separately, pulling Kenyan data to South Africa is a cross-border transfer under ss.48–50.

**Change watch:** the **Data Protection (Amendment) Bill 2025** is **pending, not enacted** (independently verified — still under parliamentary review as of May 2026). It would flip s.63 from "whichever is **lower**" to "**higher**", materially raising exposure. No s.37(3) practice guidelines exist — ODPC has 22 guidance notes and **none on direct marketing** (page last modified 27 Jul 2026).

Sources: [DPA 2019](https://www.kentrade.go.ke/wp-content/uploads/2022/09/Data-Protection-Act-1.pdf) · [General Regulations 2021](https://www.odpc.go.ke/wp-content/uploads/2024/03/THE-DATA-PROTECTION-GENERAL-REGULATIONS-2021-1.pdf) · [Registration Regulations 2021](https://www.odpc.go.ke/wp-content/uploads/2024/03/THE-DATA-PROTECTION-REGISTRATION-OF-DATA-CONTROLLERS-AND-DATA-PROCESSORS-REGULATIONS-2021.pdf) · [KIC (Consumer Protection) Regs 2010 — CA](https://www.ca.go.ke/sites/default/files/2023-06/Consumer-Protection-Regulations-2010-1.pdf) · [ODPC registration guidance](https://www.odpc.go.ke/wp-content/uploads/2024/02/ODPC-Guidance-Note-on-Registration-of-Data-Controllers-and-Data-Processors.pdf) · [Aiko v Goodtimes determination](https://www.odpc.go.ke/wp-content/uploads/2026/04/ANTONATE-AIKO-VS-GOOD-TIMES.pdf) · [CIPIT opt-in/opt-out](https://cipit.strathmore.edu/opt-in-or-opt-out-demystifying-proposed-consent-requirements-for-direct-marketing-in-kenya/)

---

## 6. EGYPT — confidence HIGH. **DO NOT COLD EMAIL.**

### ⚠️ THE POSITION HAS COMPLETELY CHANGED — the brief's premise is out of date. I verified this independently.

**The Executive Regulations HAVE been issued and the Personal Data Protection Center HAS been established.**
- **MCIT Decree No. 816 of 2025**, gazetted **1 November 2025**, in force 2 November 2025. (Only circulated to Egyptian firms on 25 December 2025 — the discrepancy is flagged by Soliman, Hashish & Partners and unexplained by any authority.)
- **PDPC established**, chaired by the Minister of Telecommunications and IT; site live at **pdpc.gov.eg** carrying the Regulations and ~10 guidelines including a dedicated **Electronic Direct Marketing** guideline.
- **⏰ COMPLIANCE GRACE PERIOD ENDS 31 OCTOBER / 1 NOVEMBER 2026 — about ten weeks away.** (Firms differ by one day: Baker McKenzie and SH&P say 1 Nov; Amereller says from 31 Oct. Assume 31 Oct.)

**Statutes/regulator:** PDPL No. 151 of 2020 + Executive Regulations (Decree 816/2025) — **Personal Data Protection Center (PDPC)**. Jurisdiction: economic courts. Backstops: Telecom Law 10/2003 (NTRA), Cybercrime Law 175/2018.

**CONSENT MODEL — prior opt-in PLUS a State licence PLUS a registered DPO PLUS an approved Egyptian representative. No opt-out route, no B2B exemption of any kind.** Egypt is materially stricter than the GDPR because consent alone is not enough — **the activity itself is licensed.** Note there is **no legitimate-interests basis in the statute** (art. 2 requires explicit consent).

**Art. 17 (the direct-marketing article — it is 17, with 18):** electronic communication for direct marketing is **prohibited unless** all five: (1) consent of the data subject; (2) identity of the sender included; (3) sender has a **valid and complete address** to be reached; (4) **a clear indication that the purpose is direct marketing**; (5) clear and uncomplicated opt-out/withdrawal mechanisms. **Art. 18:** specify a defined marketing purpose; **do not disclose the recipient's contact details**; and **maintain electronic records evidencing consent for 3 years from the last communication.** The PDPC guideline reportedly treats an unsubscribe that "exists in form but is ineffective in practice," or marketing "disguised as personal messages," as unlawful.

**⚠️ THE LICENCE — the sharpest point.** Art. 4(10) requires a **licence or permit from the Center to handle personal data**; art. 26(3) requires the Center to **issue licences or permits specifically for direct electronic marketing**. Fee ceilings: licence ≤ **EGP 2,000,000**, permits ≤ EGP 500,000. Executive Regulations tier the base fee by record count (1–100,000 records = fee-exempt, rising to ~EGP 666,666/yr above five million), then set the **direct-marketing licence at 10% of the base fee for your own products, 25% marketing on behalf of others**; cross-border transfer licence = 50%. A PDPC-accredited **DPO is a prerequisite** for any licence. PDPC targets 90 working days to decide.

**Natural persons only?** Yes — promulgating art. 1 and the art. 1 definitions confine the law to natural persons. So a genuinely generic corporate mailbox with no personal data used to target anyone arguably falls outside the PDPL and outside the marketing licence. **But** "Electronic Marketing" is defined as content "addressed to **specific persons**," any named-individual address or personalisation brings you squarely in, and holding *any* Egyptian personal data triggers the base licence + representative + transfer licence. *Medium confidence — this is a reading of the definitions; no PDPC ruling on role addresses found.*

**Scraped addresses: effectively unusable.** Art. 2 (explicit consent to collect), art. 3, art. 4(1), and art. 18(3)'s three-year consent register that you cannot possibly hold for a scraped list. The Regulations reportedly require **prior PDPC approval of data-collection mechanisms**, and an intermediary must verify valid consent exists or **immediately cease** using the data.

**Penalties (criminal fines; economic courts):**
- **Art. 43 — violating the marketing provisions (arts. 17–18): EGP 200,000 – 2,000,000. Fine-only, no imprisonment.**
- Art. 38 — breach of controller obligations, **including failure to obtain a licence and failure to appoint an Egyptian representative: EGP 300,000 – 3,000,000.**
- **Art. 45 — violating licence/permit provisions: EGP 500,000 – 5,000,000.**
- **Art. 42 — violating cross-border transfer conditions: imprisonment ≥3 months and/or EGP 500,000 – 5,000,000.**
- Art. 47 — the de facto manager is personally liable if he knew; company jointly liable for damages.
- **Art. 48 — the court publishes the sentence in two widespread newspapers and on the internet at the convict's expense; recidivism DOUBLES both minimum and maximum.**
- **Per offence, not per message or per day.** Settlement available (art. 49).

**EXTRATERRITORIAL — YES, but the criminal limb carries a DUAL-CRIMINALITY condition. Read this carefully.** Promulgating **art. 2** applies the law to "a non-Egyptian **outside** Egypt **provided that the act is punishable under any legal form in the country where it occurred**, and the data subject … belongs to Egyptians or foreigners residing inside Egypt." For an SA sender both limbs must hold. Limb (a) is arguable: South Africa's POPIA s.69 imposes opt-in electronic direct marketing and ECTA s.45 criminalises failure to give an unsubscribe opportunity — a prosecutor would say it is satisfied, a defence would say it is not "punishable" directly. **Genuinely unsettled — flag to counsel.**

**The regulatory reach is NOT so conditioned. Art. 4(11): a controller outside Egypt MUST appoint a representative in Egypt**, which the Regulations require to be a branch, an Egyptian legal entity, or an attorney under power of attorney, **approved by the PDPC**. And **art. 14 requires a licence/permit for any cross-border transfer** — art. 15's exceptions do not cover marketing. **An SA sender pulling Egyptian contacts into a CRM in South Africa is performing exactly this transfer.**

**Backstops:** Telecom Law 10/2003 art. 76 (misuse of telecom equipment to harass — EGP 500–20,000, trivial by comparison; NTRA has referred unlicensed bulk-SMS senders to prosecution). **Cybercrime Law 175/2018 contains NO unsolicited-email offence** — I confirmed "unsolicited", "advertising", "spam", "bulk" do not appear.

**⚠️ Could not verify:** whether the PDPC licensing **portal actually went live**. Last statement found is SH&P, 6 May 2026 ("around mid-June 2026"); pdpc.gov.eg is a JS app that would not render. Treat as unverified.

Sources: [PDPL 151/2020 English text](https://www.acc.com/sites/default/files/program-materials/upload/Data%20Protection%20Law%20-%20Egypt%20-%20EN%20-%20MBH.PDF) · [PDPC official site](https://pdpc.gov.eg/home) · [Baker McKenzie alert (PDF)](https://www.bakermckenzie.com/-/media/files/insight/publications/2026/01/egypt--important-data-protection-update.pdf) · [Soliman Hashish & Partners — Executive Regulations](https://www.shandpartners.com/insights/briefings/telecoms-media-technology/the-issuance-of-the-executive-regulations-of-the-data-protection-law-and-the-establishment-of-the-data-protection-centre/) · [SH&P — May 2026 compliance developments](https://www.shandpartners.com/insights/egypt-personal-data-protection-law-compliance-developments/) · [Amereller — ahead of 31 Oct 2026](https://amereller.com/publication/the-egyptian-personal-data-protection-regime-what-you-need-to-know-ahead-of-31-october-2026/) · [CMS](https://cms.law/en/int/legal-updates/egypt-s-pdpl-executive-regulations-issued-one-year-compliance-countdown-begins) · [Kennedys](https://www.kennedyslaw.com/en/thought-leadership/article/2026/egypt-s-personal-data-protection-law-the-compliance-countdown-has-begun/)

---

## 7. ZIMBABWE — confidence HIGH on text, LOW on licensing/enforcement

**Statute/regulator:** **Cyber and Data Protection Act [Chapter 12:07], Act 5 of 2021**. Regulator: **POTRAZ**, designated Data Protection Authority by s.5. Plus **SI 155 of 2024** (Licensing of Data Controllers and Appointment of DPOs), gazetted 13 September 2024. Also Consumer Protection Act [Ch 14:44] ss.49, 50, 54.

**⚠️ CORRECTION TO THE BRIEF — there is NO "unsolicited electronic communications" section.** The word "unsolicited" **does not appear anywhere** in the Act. What exists:
- **s.164D "Spam"** (inserted into the Criminal Code) is a **header-forgery / relay-abuse** offence only — it bites relaying multiple messages "with intent to deceive or mislead recipients … as to the origin," or materially falsifying header information. **Ordinary honestly-headed cold email does not engage it.** Penalty: level 5 (US$200) and/or 1 year.
- **Direct marketing appears only twice**, in ss.15(1)(c) and 16(1)(d): a duty to **tell** the data subject of the right to object free of charge. Where data was **not** collected from the data subject (s.16(1)(d)), notice must be given **before the first use for direct marketing**.

*Conflicting sources flagged: several practitioner blogs place the objection right in "s.24" — wrong; s.24 is Accountability. It is s.14(c) with notice duties in ss.15–16.*

**CONSENT MODEL — formally opt-in for the personal data, with a legitimate-interests escape hatch. No B2B exemption (none needed).** s.10(1) requires consent; **s.10(3)(e) permits processing without consent where necessary for the legitimate interests of the controller or a third party**, subject to a balancing test. s.10(2) allows consent to be implied for adult natural persons. Net: named-individual B2B email is realistically defensible on legitimate interests **plus** the s.16(1)(d) objection notice on first use.

**Natural persons only?** Yes — "data subject" = "an individual who is an identifiable person." **Generic role addresses fall outside the Act.** (s.10(2) has a sloppy "or has a legal persona" phrase; it does not convert this into a juristic-person law.) *Medium-high confidence.*

**Scraped addresses:** Permitted in principle, subject to purpose limitation (s.9), the s.16 notice (name and address of the controller, purposes, objection right **before first marketing use**), and the s.10(3)(e) balancing test. Do not lean on the s.16(2)(a) "disproportionate effort" exemption — it is aimed at statistical/research/public-health processing.

**Mandatory content:** The Act prescribes no email-format rules. Derived from ss.15–16: identify the sender by **name and address**, state the purpose, give a free objection route. **No statutory timeframe to honour opt-outs** — s.11(2) (withdrawal "at any time, without explanation and free of charge") implies without delay.

**Penalties:** Zimbabwe uses the Standard Scale of Fines, **SI 14A of 2023**, **expressed in USD and payable in local currency at the prevailing interbank rate** — which insulates them from ZWL/ZiG collapse. Level 5 = US$200; level 7 = US$400; level 11 = US$1,000; level 14 = US$5,000. Act s.33(2): contravening ss.11, 13, 18(4), 24 or 28 — **level 11 (US$1,000) and/or up to 7 years**. SI 155 offences mostly level 11 / 7 years; failure to appoint a DPO level 7 (US$400) / 2 years. **Per offence. No administrative-fine regime.**

**⚠️ LICENSING — the sharpest exposure, and genuinely unsettled.** SI 155 s.3(1): "**No person** shall process personal information … unless they are licensed with the Authority" — including processing "to obtain a commercial gain," **with no territorial qualifier and no foreign carve-out**. s.6 tiers by data subjects: **Tier 1 = 50–1,000** (so a list of ≥50 Zimbabwean individuals crosses the threshold), Tier 2 = 1,001–100,000, Tier 3 = 100,001–500,000, Tier 4 = >500,000. **Fees:** application US$30 (Tiers 2–4); initial/renewal **Tier 1 US$50, Tier 2 US$300, Tier 3 US$500, Tier 4 US$2,500**, 12 months. *(The widely-quoted "US$50–2,000" range is wrong.)* Only exemptions (s.8): personal/household, law enforcement, journalistic/archival. Form DP1 asks "Is your data located in Zimbabwe? If No, state the Country," so POTRAZ contemplates non-residents — **but nothing states whether an offshore-only sender must license.**

**EXTRATERRITORIAL — s.4(2)(b):** the Act applies to a controller "**not permanently established in Zimbabwe, if the means used, whether electronic or otherwise, is located in Zimbabwe**." This is a **means-based test, not a targeting test.** An SA sender with no servers, agents or equipment in Zimbabwe has a real argument the Act does not reach it. If it does apply, **s.4(3) requires designation of a local representative.**

**⚠️ FLAG — deadlines passed, enforcement starting.** Licence applications were due within 6 months (→ **12/13 March 2025**); DPO appointments within 90 days (→ ~12 Dec 2024). **No extension was granted.** **POTRAZ Regulatory Notice 2 of 2026: mandatory compliance inspections begin 1 September 2026**, risk-ranked starting with financial institutions.

Sources: [Cyber and Data Protection Act](https://zimlii.org/akn/zw/act/2021/5/eng@2022-03-11) · [SI 155 of 2024 (Veritas)](https://www.veritaszim.net/sites/veritas_d/files/SI%202024-155%20Cyber%20and%20Data%20Protection%20(Licensing%20of%20Data%20Controllers%20and%20Appointment%20of%20Data%20Protection%20Officers)%20Regulations,%202024.pdf) · [SI 155 (POTRAZ mirror)](https://www.potraz.gov.zw/wp-content/uploads/2025/02/sI-155-of-2024-Cyber-and-Data-Protection-Normal_240913_1250178.pdf) · [SI 14A of 2023 Standard Scale](https://www.veritaszim.net/sites/veritas_d/files/SI%202023-014A%20Criminal%20Law%20%28Codification%20and%20Reform%29%20%28Standard%20Scale%20of%20Fines%29%20Notice%2C%202023.pdf) · [POTRAZ Regulatory Notice 2 of 2026](https://www.veritaszim.net/node/8052) · [Techzim on inspections](https://www.techzim.co.zw/2026/07/potraz-starts-data-protection-inspections-on-1-september-here-is-what-it-means-for-you/) · [Consumer Protection Act](https://zimlii.org/akn/zw/act/2019/5/eng@2019-12-10)

---

## 8. BOTSWANA — confidence HIGH. **DO NOT COLD EMAIL. Highest combined exposure of the nine.**

### ⚠️ THE 2018 ACT IS GONE — verified independently
The **Data Protection Act 2018 (Act 32 of 2018)** was given a commencement order for 15 Oct 2021 but had its effective date repeatedly pushed back by Ministerial Orders and **never became operative in practice**. It has been **repealed and re-enacted** by the **Data Protection Act, 2024 (Act 18 of 2024)** — published in the Government Gazette Extraordinary **29 October 2024**, **commenced 14 January 2025** (Minister's order gazetted 13 Jan 2025). *(DLA Piper's "came into effect 29 Oct 2024" is the publication date; use 14 January 2025.)* Regulator: **Information and Data Protection Commission (IDPC)**.

**⚠️ But the controlling instrument for cold email is NOT the DPA — it is ECTA.** **Electronic Communications and Transactions Act, Act 14 of 2014 (Cap. 43:12)**, commenced 1 April 2016, Part VII "On-line Marketing", **section 38 "Unsolicited commercial communications"**. Regulator: **BOCRA**.

**CONSENT MODEL — OPT-IN with a soft opt-in (SA ECT Act s.45 lineage). NO B2B or corporate exemption.** Unsolicited commercial communication is permitted only where **all four** hold:
1. the address was collected by the originator **in the course of a sale or negotiations for a sale**;
2. the marketing relates to **similar** products or services;
3. at collection a free opt-out was offered and the addressee **declined to opt out**;
4. an opt-out is provided with **every subsequent message**.

**Cold email off a scraped or purchased list satisfies none of these — limb 1 fails at the outset. Including an unsubscribe link does not cure it.**

**⚠️ AND ECTA REACHES CORPORATE MAILBOXES.** "Addressee" is defined as "**a party** intended by the originator to receive the electronic communication" — not limited to natural persons. So `info@company.co.bw` is **inside ECTA even though it is outside the DPA**. This asymmetry is the single most important finding for Botswana.

**Natural persons only (DPA 2024)?** Yes — s.2 "'data subject' means a **natural person**"; s.3(b) objects refer to natural persons. *⚠️ Conflict flagged: ALT Advisory's dataprotection.africa/botswana codes "Applies to juristic persons: Yes" — that page describes the **repealed 2018 Act**, last updated 23 May 2022. Prefer the statute.*

**DPA 2024 direct marketing — s.48(3)–(5):** right to object **at any time**, including to related profiling; on objection the data **"shall not be processed"** for those purposes (absolute, no balancing test); and **at the time of the first communication** the objection right must be "explicitly brought to the attention of the data subject and presented **clearly and separately** from any other information."

**Scraped addresses — s.41 (GDPR art. 14 equivalent):** where data is not obtained from the data subject you must supply the s.39/s.40 information **plus (s.41(1)(b)) the source, and whether it came from a publicly accessible source**, plus the categories of data — within a reasonable period not exceeding one month, **or at the time of the first communication** if used to contact the person. **But even a fully s.41-compliant email still fails ECTA s.38.**

**Mandatory content:** ECTA s.38 — originator's **identity and contact details including place of business, email address(es) and telefax number**; a **valid and operational opt-out facility**; and **the identifying particulars of the source from which the address was obtained**. DPA ss.39–41 add controller and DPO contact details, purpose and legal basis, legitimate interests where relied on, recipients, retention, rights and source. **No statutory timeframe to action an opt-out**, but the ECTA offence bites on *persisting* after opt-out — treat as immediate.

**Penalties:**
- **ECTA (criminal, per offence):** failure to provide an opt-out facility — **BWP 10,000 and/or 5 years**. **Persisting** in sending to someone who has opted out — **BWP 50,000 and/or 8 years**.
- **DPA 2024 (administrative, verified in the gazette):** up to **BWP 10,000,000 or 2% of total worldwide annual turnover, whichever is HIGHER**, for ss.29/52 obligations; **up to BWP 50,000,000 or 4% of total worldwide annual turnover, whichever is HIGHER**, for the basic processing principles, conditions for consent, **data-subject rights (Part VIII — which includes s.48 direct marketing)**, cross-border transfers and Commission orders. Obstruction: BWP 500,000 and/or 10 years. Multi-breach total capped at the gravest contravention.
- *⚠️ DLA Piper's Botswana chapter still quotes 2018-Act figures (BWP 500,000 / 9 years; BWP 20,000; BWP 100,000) despite an 18 March 2026 stamp. **Do not rely on it for penalties or registration.***

**EXTRATERRITORIAL — YES, EXPRESSLY. DPA s.4(2)**, verbatim from the gazette: where a controller is not established in Botswana the Act applies where processing activities relate to "the **offering of goods or services to data subjects in Botswana**, irrespective of whether payment … is required," or monitoring of behaviour in Botswana. **An SA company cold-emailing Botswana businesses to sell them something is squarely within s.4(2)(b)(i).** **s.54 then requires a written local representative** in Botswana; designating one does not shield you from proceedings (s.54(5)).

**Registration:** no general controller registration found in the 2024 Act (unlike Zimbabwe). Mandatory **DPO** where s.69(1) triggers, with name and contact submitted to the Commission. *Medium confidence — I could not locate any 2025/2026 IDPC registration regulations; a duty could sit in regulations not found.*

**Could not verify:** the **verbatim wording of ECTA s.38** — the official BOCRA PDF is a scanned image with no machine-readable text, so the substantive four limbs above come from DLA Piper's Botswana chapter; the section number and title were confirmed against the official arrangement of sections. **ECTA extraterritoriality is untested (low confidence).**

Sources: [Data Protection Act 2024 — Extraordinary Gazette 29 Oct 2024 (full text)](https://www.datalaw.africa/wp-content/uploads/2024/12/Extraordinary-Gazette-29-10-2024.pdf) · [Botswanalaws — Act 18 of 2024](https://botswanalaws.com/bulletin/principal-legislation/bulletin-2024/act-18-of-2024---data-protection-act) · [CIPIT — Botswana's 2018 and 2024 Acts](https://cipit.strathmore.edu/understanding-botswanas-2018-and-2024-data-protection-acts/) · [Michalsons](https://www.michalsons.com/blog/botswanas-data-protection-act-grace-period-extended/60775) · [ECTA consolidated arrangement of sections](https://botswanalaws.com/consolidated-statutes/principle-legislation/electronic-communications-and-transactions) · [DLA Piper — Botswana electronic marketing](https://www.dlapiperdataprotection.com/index.html?t=electronic-marketing&c=BW)

---

## 9. MOZAMBIQUE — confidence HIGH on the law, LOW on extraterritoriality

**No comprehensive general data protection law is in force as at 20 August 2026 — verified independently.** The *Proposta de Lei que estabelece o Regime Jurídico de Protecção de Dados Pessoais* was approved by the **Council of Ministers in early March 2026** and sent to the Assembleia da República, where it **awaits debate and final vote**. Drafted by INTIC with Council of Europe, AU, Brazil and US support; would create an **ANPD**. **Not law — do not plan against it.**

**What IS in force:** Constitution **art. 71** (computerised processing of convictions/private life; right of access and rectification) and — the operative instrument — **Lei n.º 3/2017, de 9 de Janeiro (Lei das Transacções Electrónicas)**.

**CONSENT MODEL — OPT-IN with a soft opt-in. Artigo 40 ("Publicidade e marketing electrónicos"), verified verbatim from the Boletim da República:**
- **40(3):** use of automated calling systems without human intervention, **expressly including "correio electrónico"**, for direct marketing **"só pode ocorrer com consentimento prévio dos subscritores."**
- **40(4):** no unsolicited direct-marketing email unless the recipient has previously notified the sender and consented.
- **40(5) soft opt-in:** details obtained **in the course of a sale or negotiations for a sale**, **similar** products, refusal offered at collection and not taken, and not refused subsequently.
- **40(2):** must be identifiable as to the commercial activity on whose behalf it is conducted.

**Cold email off a scraped list fails 40(3)/(4) and cannot use the 40(5) exception.** Same SA ECT Act s.45 lineage as Botswana.

**⚠️ Natural persons only? SPLIT — and this matters.** The **data protection chapter** protects natural persons only ("Dados pessoais: qualquer informação relativa a uma **pessoa singular**"). **But art. 40 does not use "dados pessoais" as its trigger** — it regulates communications to "o receptor" / "uma pessoa", and art. 2 applies the Law to "pessoas singulares, colectivas públicas ou privadas." **So art. 40 covers B2B email to corporate role addresses.** *Medium-high confidence — my reading of the Portuguese text; no case law found.*

**Mandatory content (art. 40):** identifiable as advertising and identifying the business on whose behalf it is sent; **true identity, not disguised or concealed (40(7))**; **a valid address for cessation requests (40(7))**; a **free email unsubscribe option (40(6)(a))**; and **disclosure of the source from which the recipient's personal information was obtained (40(6)(b))**. **40(9) requires regular consultation of opt-out registers (*registos de opção negativa*) — I found NO evidence that any such register actually exists in Mozambique.** 40(8): failure to reply to an unsolicited communication concludes no agreement. **No statutory opt-out timeframe**, but art. 67(i) makes it an offence to send to someone who has said the communications are unwanted — treat as immediate.

**Penalties:** **Art. 67(i)** — sending unsolicited commercial communications to a person who has informed the sender they are unwanted. **Art. 68(c) — fine of 30 to 90 *salários mínimos da função pública***. On the MZN 8,758.00 TSU floor (public-service salaries **kept unchanged for 2026**, approved late April 2026) that is roughly **MZN 262,740 – MZN 788,220 (~US$4,100 – US$12,400)**. *Treat the conversion as indicative — confirm the current TSU floor.* **Per offence, not per message or per day.** The *entidade reguladora* prosecutes; appeal to the Tribunal Judicial.

**Regulator name check:** it is **INCM** (Instituto Nacional das Comunicações de Moçambique). **ARECOM** was the 2019 rename and was **reversed back to INCM in 2022** — the arecom.gov.mz domain still resolves and serves legislation pages, which causes confusion. INTIC is the ICT policy body driving the bill, not a DPA. *Medium confidence on the rename/reversal — documented in trade sources rather than a diploma I could read.*

**EXTRATERRITORIAL — weak / unverified.** Art. 2 applies the Law to "pessoas singulares, colectivas públicas ou privadas que apliquem tecnologias de informação e comunicação, nas suas actividades" — **no express territorial clause and no "offering goods or services in Mozambique" hook.** I could not verify any provision binding a foreign sender emailing in. In practice: no DPA exists, no opt-out register appears to exist, and enforcement against an offshore sender would be novel. **Residual legal risk low; deliverability risk is the real one.**

**⚠️ FLAG — 2026 changes I could not fully assess.** **Lei n.º 13/2026 (Segurança Cibernética)** and **Lei n.º 14/2026 (Crimes Cibernéticos)** were published **1 July 2026** and **enter into force 29 September 2026**. **I could not verify whether either contains an unsolicited-communications offence or amends Lei 3/2017's sanctions. Re-check after 29 September 2026.** Separately, INCM issued **Resolução n.º 2/BR/CA/INCM/2026** establishing an **A2P (Application-to-Person) SMS** regime aimed at curbing spam — **SMS-specific, no email equivalent found** (low-medium confidence; page would not render).

Sources: [Lei 3/2017 Transacções Electrónicas (official BR text)](https://www.dataguidance.com/sites/default/files/electronic_transactions_law.pdf) · [INTIC — proposta segue para debate](https://intic.gov.mz/proposta-de-lei-de-proteccao-de-dados-pessoais-segue-para-debate-na-assembleia-da-republica/) · [Integrity Magazine — aprovada nova proposta](https://integritymagazine.co.mz/arquivos/58645) · [PLMJ — Mozambique Personal Data Protection Bill](https://www.plmj.com/en/knowledge/informative-notes/Mozambique-Personal-Data-Protection-Bill/34166/) · [INTIC — Leis 13/2026 e 14/2026 publicadas](https://intic.gov.mz/mocambique-publica-no-boletim-da-republica-as-leis-da-seguranca-cibernetica-e-dos-crimes-ciberneticos/) · [Constituição art. 71](https://www.parlamento.mz/wp-content/uploads/2022/08/Constittuicao_Republica.pdf) · [Portal do Governo — salários 2026](https://portaldogoverno.gov.mz/2026/04/29/governo-aprova-novos-salarios-minimos-e-mantem-funcao-publica-inalterada/) · [INCM](https://www.incm.gov.mz/)

---

# CROSS-CUTTING FINDINGS

**1. Three of the nine are effectively closed to cold email: Kenya, Egypt, Botswana.** Each combines opt-in with **express extraterritorial reach over a foreign sender** and a **local registration/licence/representative requirement**. Botswana is the worst single exposure — GDPR-grade turnover-based fines (up to 4% of worldwide turnover), an express "offering goods or services to data subjects in Botswana" hook, **and** an opt-in spam offence that reaches corporate `info@` addresses, all at once.

**2. Two are genuinely permissive: Argentina (opt-out from public sources) and Portugal (express legal-person exemption).** New Zealand is a qualified third via deemed consent.

**3. The recurring pattern that trips up international senders — "disclose your source."** Portugal (GDPR art. 14(2)(f)), Botswana (ECTA s.38 + DPA s.41(1)(b)), Mozambique (art. 40(6)(b)), Namibia's dormant s.36(1)(c), Zimbabwe (s.16(1)(d)), Argentina (on request) and now **NZ's IPP 3A from 1 May 2026** all require you to tell the recipient where you got their address. Almost no sending platform does this by default.

**4. Two mandatory registry/list checks exist and are free:** Portugal's DGC list of opted-out legal persons (mandatory monthly consultation, 184 email records) and Mozambique's art. 40(9) registers (which appear not to exist).

**5. Two quirks no standard template covers:** Argentina requires the literal word **"publicidad"** in the email header; Egypt requires an express statement that the message is for direct marketing.

**6. Timing flags:**
- **Egypt — 31 October 2026** (≈10 weeks): PDPL grace period ends.
- **Zimbabwe — 1 September 2026** (≈2 weeks): POTRAZ compliance inspections begin.
- **Mozambique — 29 September 2026**: Leis 13/2026 and 14/2026 in force, contents unassessed.
- **Namibia — any day**: ETA Chapter 4 needs only one ministerial gazette notice, no Parliament, to impose an opt-in, B2B-inclusive, N$500,000 regime with **liability extending to the advertiser, not just the sender**.
- **New Zealand — already live (1 May 2026)**: IPP 3A.

# WHAT I COULD NOT VERIFY — stated plainly

- **NZ:** whether UEMA s.8 reaches a sender with no NZ residence or business. Statute and DIA guidance **diverge**; no case law. *Low confidence.*
- **Argentina:** whether Ley 25.326 binds a foreign company with no Argentine establishment. AAIP has asserted reach in practice (Worldcoin) but no resolution or case squarely holds it. Also, precise committee stage of the three reform bills. *Low confidence.*
- **Portugal:** whether the corporate exemption covers a **named individual** at a corporate address. CNPD **expressly declined to decide** (Diretriz/2022/1 fn.2); no decision or ruling either way. This is the main open legal risk. Also: how CNPD counts a mass campaign as one or many infringements; whether a postal address is required in the message.
- **Namibia:** Data Protection Bill stage between March and August 2026 — six months of silence, tracker login-gated. Consumer Protection Bill 2024 text (server refused all fetches). CRAN regulations — index scanned, not exhaustively read. No Namibian case law read (NamibLII returns 403).
- **Kenya:** exact penalty mapping for KICA CP reg 17 (the reg states "commits an offence" with no penalty; KICA s.27(4) is the natural default but the Regs draw on six enabling sections). No CA enforcement precedent found against any email marketer.
- **Egypt:** whether the PDPC **licensing portal actually went live** (last statement: "mid-June 2026"). Whether the PDPC marketing guideline addresses role-based mailboxes (Arabic, JS-rendered site). Whether the dual-criminality limb would be held satisfied against a South African sender — **genuinely unsettled, flag to counsel.**
- **Zimbabwe:** whether POTRAZ would license or enforce against a purely offshore emailer — no published guidance either way.
- **Botswana:** **verbatim wording of ECTA s.38** (official PDF is a scanned image); ECTA extraterritoriality; whether IDPC registration regulations have been issued since Jan 2025.
- **Mozambique:** extraterritorial application; whether Leis 13/2026 and 14/2026 add spam offences from 29 Sept 2026; whether any art. 40(9) opt-out register exists; the INCM/ARECOM rename reversal (trade sources only).

# CORRECTIONS TO PREMISES IN THE BRIEF

1. **Egypt is NOT "awaiting executive regulations."** They were issued 1 Nov 2025 (Decree 816/2025), the PDPC exists, and the compliance deadline is 31 Oct 2026.
2. **Botswana's Data Protection Act 2018 was repealed** and replaced by Act 18 of 2024, in force 14 Jan 2025. The 2018 Act never operated.
3. **Zimbabwe's Cyber and Data Protection Act has no unsolicited-communications section.** The word "unsolicited" does not appear in it.
4. **NZ UEMA has no "Schedule 1"** — all three consent limbs are in the s.4 definition. The "New Zealand link" is defined in s.4, not s.6; s.8 is the extraterritorial provision.
5. **Kenya's unsolicited-communications rule is reg. 17**, not reg. 12, of the 2010 Consumer Protection Regulations.
6. **Portugal: DL 7/2004 art. 22 was REPEALED** by Lei 46/2012 art. 5.º(b). Secondary sources still citing "art. 22 + €2,500–€100,000" for unsolicited email are wrong; the regime moved to Lei 41/2004 arts. 13.º-A/13.º-B.
7. **Argentina's "No Llame" registry (Ley 26.951) does not cover email** — telephony services only, including VoIP.

**Independently re-verified this session:** Egypt's Decree 816/2025 and the 31 Oct 2026 deadline; Botswana's 2024 Act repealing the 2018 Act with 14 Jan 2025 commencement; Portugal's art. 13.º-A(2) corporate exemption and the DGC registry; **Namibia's ETA commencement table read directly from the Laws.Africa consolidation (Chapter 4 "not yet commenced"; s.20 and Chapter 5 commenced 15 June 2026 by GN 182 of 2026)**; NZ's IPP 3A in force 1 May 2026; Mozambique's bill still awaiting a vote; Kenya's Amendment Bill 2025 still pending.
---
# APPENDIX — primary-market research (US / UK / AU / FR / ZA)
Researched 20 Aug 2026 alongside the nine-jurisdiction study above.

**UNITED STATES — CAN-SPAM.** Opt-out regime; no consent needed for B2B. Seven duties: accurate from-line,
non-deceptive subject, ad disclosure, valid PHYSICAL POSTAL ADDRESS, opt-out mechanism, honour within 10
business days, responsibility for third parties. Penalty up to $53,088 per email (FTC 2026 inflation
adjustment), uncapped aggregate. STATE LAYER: CAN-SPAM preempts state email statutes EXCEPT those targeting
fraud/deception — California B&P 17529.5 survives on that basis and carries a PRIVATE RIGHT OF ACTION at up
to $1,000/email plus fees. CCPA B2B exemption ENDED 2023, so scraped business contact data is covered.

**UNITED KINGDOM — PECR + UK GDPR.** PECR opt-in for electronic mail DOES NOT APPLY to corporate subscribers
(any body with separate legal status + own internet connection). Soft opt-in irrelevant for a limited company.
CARVE-OUT: sole traders and some partnerships are INDIVIDUAL subscribers -> consent/soft opt-in required.
PECR reg.23 still binds for corporates: no concealed sender identity, valid opt-out address. ICO guidance
updated 28 Apr 2026. UK GDPR art.14 applies to scraped data independently — public availability does not lift it.

**AUSTRALIA — Spam Act 2003.** Opt-in, BUT Sch.2 inferred consent where a work address was CONSPICUOUSLY
PUBLISHED in a business capacity, no 'no unsolicited email' notice present, and the message is RELEVANT TO THE
ROLE. Burden of proof on sender, per address. Sender ID + functional unsubscribe honoured within 5 business
days. Penalties day-based: ~AUD 3.13m/day corporations (10,000 penalty units @ AUD 313), ~AUD 444k individuals.

**FRANCE — CNIL / GDPR / LCEN.** OPT-OUT for B2B on three CUMULATIVE conditions: (1) recipient contacted in a
professional capacity, (2) message concerns their professional activity, (3) address is professional. Generic
addresses (contact@, info@) freely prospectable subject to unsubscribe duty. CNIL's Aug 2026 tightening to
explicit opt-in applies to B2C ONLY — B2B position undisturbed. GDPR applies in full: documented LIA, art.14
notice at first contact naming source, absolute right to object, source traceability. LCEN: €375/message sent
without retraction option. GDPR ceiling €20m / 4%.

**SOUTH AFRICA — POPIA s69.** Prohibits electronic direct marketing absent consent or existing-customer status.
POPIA extends to juristic persons but CONDITIONALLY ('where it is applicable'). Information Regulator Guidance
Note, Dec 2024: role-based addresses (info@, sales@) directed at the legal entity rather than a natural person
fall outside the strictest s69 consent requirement — this is the basis current ZA sending rests on.

## ENGINE GAPS IDENTIFIED (verified against code, 20 Aug 2026)
1. localize.py country_of() supports ZA/US/GB/AU only; ALL other countries DEFAULT TO 'ZA' silently.
   FR (153 prospects) and PT (26) would render as South African — no GDPR art.14 notice, no source
   disclosure, no EU representative. Most serious gap; fails silently, nothing errors.
2. TS_POSTAL_ADDRESS defaults to 'Pretoria, South Africa' — NOT a valid CAN-SPAM physical postal address.
3. No GDPR art.14 source-disclosure block for FR/PT/GB.
4. No GDPR art.27 EU representative designated.
5. Portugal DGC opted-out legal-persons registry never consulted (mandatory monthly, free, 184 email records).
6. No Argentina 'publicidad' subject prefix / verbatim art.27.3 transcription.
7. NZ IPP 3A indirect-collection notification (in force 1 May 2026) not implemented.
8. Named-individual vs role addresses not distinguished in the data model.
