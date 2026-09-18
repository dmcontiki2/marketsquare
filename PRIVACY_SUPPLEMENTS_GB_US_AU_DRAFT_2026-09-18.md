# Privacy Policy — Country Supplements: United Kingdom · United States · Australia
**DRAFT 18 September 2026 · NOT APPLIED to the live policy.**

Scope ruled by David, 18 Sep 2026: **"all three"** (D4, open since 23 Jul 2026).

## Why this is a draft and not an edit

Routed the same way as the Buzz clause on 14 Sep: `privacy.html` is a published legal document
with an external review track, so it is not edited from a stand-up. This file is the text, ready
to drop in, plus the three findings below that a reviewer needs to see before it lands.

---

# FINDING 1 — the EULA already promises this text exists. It does not.

This is the part that changes D4's priority, and it was not visible until the two documents were
read against each other. **EULA v1.16 makes three explicit cross-references to privacy content that
has never been written:**

| EULA clause | What it tells the user | Reality on 18 Sep 2026 |
|---|---|---|
| **A5** (UK Schedule) | "Processing of your personal data is subject to the UK GDPR and the Data Protection Act 2018, **as described in the Privacy Policy.**" | `/privacy` does not mention UK GDPR, the DPA 2018, or the ICO. |
| **B4** (US Schedule) | "If you are a California resident, **the CCPA/CPRA notices in the Privacy Policy apply.**" | There are no CCPA/CPRA notices in the Privacy Policy. |
| **C4** (AU Schedule) | "Handling of your personal information is subject to the Privacy Act 1988 (Cth) and the Australian Privacy Principles, **as described in the Privacy Policy.**" | `/privacy` does not mention the Privacy Act 1988, the APPs, or the OAIC. |

So this is not a gap in coverage. It is **one live published document telling users that another live
published document says something it does not say** — and the EULA is the one a user accepts. The
site has served GB, US and AU since launch (the ledger's own RG-0005 lists server markets AU, BW,
DE, GB, KE, MZ, NA, US, ZA), so these are not hypothetical readers.

The supplements below close all three cross-references.

# FINDING 2 — the breach-notification clause is wrong for the UK, and it is wrong in the live policy today

`/privacy` §7 currently reads: *"we will notify affected users and the Information Regulator as
required by POPIA, and in any event **within 30 days** of becoming aware of the breach."*

Thirty days is the POPIA-shaped answer. It is not the UK answer. **UK GDPR Article 33 requires
notification to the ICO within 72 hours** of becoming aware, where the breach is likely to result in
a risk to individuals. A published commitment to 30 days is, for a UK user, a published commitment
to miss the statutory deadline by 27 days.

Australia is different again: the Notifiable Data Breaches scheme requires assessment to be
completed **within 30 days** and notification **as soon as practicable** after forming the belief —
so "within 30 days" is not wrong there, but it describes the assessment window, not the notice.

US state breach statutes vary and are generally "without unreasonable delay", several with outside
limits of 30/45/60 days.

**Recommended correction to the body of the policy** (§7), so the supplements do not have to
contradict the clause they sit under:

> **7. Data breach notification.** If a breach affecting your personal information occurs we will
> notify affected users and the relevant supervisory authority as required by the law that applies
> to you, and always within the shortest period that law requires. Where POPIA applies, notification
> is made to the Information Regulator as soon as reasonably possible after discovery. Where the UK
> GDPR applies, notification is made to the Information Commissioner's Office **within 72 hours** of
> becoming aware, unless the breach is unlikely to result in a risk to your rights and freedoms.
> Where the Australian Privacy Act applies, we complete our assessment within 30 days and notify you
> and the OAIC as soon as practicable after forming the belief that an eligible data breach has
> occurred. Where US state law applies, notification is made without unreasonable delay and within
> any outside period that state's law sets.

**This one is not merely a drafting improvement — the current clause is a false statement to UK
users of a live site, and it is live right now.** It is listed here rather than fixed in place only
because the document has a review track; if you want it changed ahead of the rest, it is a
self-contained edit.

# FINDING 3 — two things the supplements cannot decide, because they cost money or pick a jurisdiction

Both are reserved to you (RUL-009 / SO-4). Neither blocks the text below; both are load-bearing for
whether the text is fully true once published.

1. **UK representative (UK GDPR Article 27).** A controller outside the UK that offers services to
   people in the UK must appoint a UK representative unless its processing is occasional, low-risk
   and involves no special-category data at scale. TrustSquare takes **identity documents** for
   deferred KYC, which is hard to call low-risk. A representative is a paid service (typically a
   few hundred GBP a year). **This is a spend and a vendor selection, so it is yours.** The draft
   below carries a placeholder that stays empty until you decide, and says plainly that it is
   pending rather than inventing one.
2. **The same question for the EU, which is larger than you asked about.** The EULA already carries
   **France and Portugal** schedules, which means EU data subjects, which means **GDPR Article 27
   applies too**, and the France schedule (D5) makes its own "as described in the Privacy Policy"
   cross-reference. I have not drafted an EU supplement — you scoped this to three — but you should
   know the same defect exists for France and Portugal and I have opened it as a loop rather than
   silently widening the job.

---

# SUPPLEMENT A — United Kingdom

*To be inserted after §14, as "Country Supplement A — United Kingdom".*

**This Supplement applies if you are in the United Kingdom.** It sits alongside the policy above and
prevails over it to the extent of any conflict. It corresponds to Schedule A of the Terms of Use.

**A1 · Applicable law and controller.** Where you are in the UK, your personal data is processed
under the **UK General Data Protection Regulation and the Data Protection Act 2018**. The controller
is TrustSquare (Pty) Ltd, 6 Villa Christiaan, 98 Manie Road, Elarduspark, Pretoria, Gauteng, 0181,
South Africa. Data-protection contact: **legal@trustsquare.co**.

**A2 · UK representative.** [PENDING — Article 27. Not yet appointed; see Finding 3. Either insert
the appointed representative's name and UK address here, or replace this paragraph with the
exemption being relied on. Do not publish this Supplement with this bracket still in it.]

**A3 · Our lawful bases.** We rely on:

| What we do | Lawful basis (UK GDPR Art 6) |
|---|---|
| Operating your account and delivering Introductions you request | Contract — Art 6(1)(b) |
| Marketing emails you opted into | Consent — Art 6(1)(a), withdrawable at any time |
| Securing the Platform, preventing fraud, and defending claims | Legitimate interests — Art 6(1)(f) |
| Identity and credential verification | Legal obligation and contract — Art 6(1)(c) and (b) |
| Keeping records after your account closes | Legal obligation — Art 6(1)(c) |

Where we rely on legitimate interests you may object at any time (see A5).

**A4 · Identity documents are special-category-adjacent and treated accordingly.** Identity and
credential documents you upload for verification are used **only** to verify you, are not used to
train any AI model, are not disclosed to other users, and are retained only as long as the
verification and our statutory record-keeping require. Where such a document reveals data falling
within Article 9 UK GDPR, we process it only to the extent Article 9(2)(g) (substantial public
interest — fraud prevention) or your explicit consent permits.

**A5 · Your rights.** You have the right to: be informed; **access** your data; have inaccurate data
**rectified**; have data **erased** where the grounds in Article 17 apply; **restrict** processing;
**data portability** for data you provided to us by contract or consent; **object** to processing
based on legitimate interests and, absolutely and at any time, to direct marketing; and to withdraw
consent without affecting prior processing. Requests go to **legal@trustsquare.co** and are answered
**within one month**, extendable by two further months for complex requests, in which case we will
tell you within the first month. There is no charge unless a request is manifestly unfounded or
excessive.

**A6 · Automated decision-making.** We do not make decisions producing legal or similarly significant
effects about you by automated means alone. AI is used for listing assistance, moderation, pricing
guidance and support triage; where an outcome affects your account, **a human reviews it before it
takes effect** (Terms of Use §7.6). The Trust Score influences listing visibility and is not used to
make an automated decision with legal effect about you.

**A7 · International transfers.** Your data is processed in South Africa, the European Union
(Hetzner hosting), and the United States (Anthropic, OpenAI) and France (Scaleway) for AI features.
The UK has not issued adequacy regulations for South Africa. Transfers out of the UK are therefore
made under the **International Data Transfer Agreement, or the UK Addendum to the EU Standard
Contractual Clauses**, together with a transfer risk assessment. You may request a copy of the
safeguards used by writing to legal@trustsquare.co.

**A8 · Retention.** Account data is deleted or anonymised within 30 days of closure, except where a
longer period is required by law (tax and financial-reporting) or to resolve a live dispute.
Verification documents are deleted once verification is complete and any statutory retention period
has expired.

**A9 · Cookies.** The Platform uses only functional browser storage — session state and preferences.
We run **no advertising or third-party tracking cookies**, so no consent banner is required under the
Privacy and Electronic Communications Regulations. If that ever changes, we will ask for your
consent first.

**A10 · Complaints.** Please raise concerns with us first at legal@trustsquare.co. You also have the
right to complain to the **Information Commissioner's Office** — ico.org.uk, 0303 123 1113, Wycliffe
House, Water Lane, Wilmslow, Cheshire SK9 5AF.

---

# SUPPLEMENT B — United States

*To be inserted as "Country Supplement B — United States".*

**This Supplement applies if you are in the United States**, and corresponds to Schedule B of the
Terms of Use. Sections B2–B7 are the notices required for **California** residents by the CCPA as
amended by the CPRA; B8 covers other states with comprehensive privacy laws.

**B1 · No sale, no sharing, no cross-context behavioural advertising.** TrustSquare **does not sell
your personal information and does not share it for cross-context behavioural advertising**, as
those terms are defined by the CCPA/CPRA. We have not done so in the preceding 12 months. We run no
advertising or tracking cookies. Because we do not sell or share, there is no "Do Not Sell or Share
My Personal Information" link; if that ever changes we will add one before it does.

**B2 · Notice at collection — categories, sources, purposes, recipients.**

| CCPA category | Do we collect it? | Source | Why | Disclosed to |
|---|---|---|---|---|
| Identifiers (name, email, account ID, IP) | Yes | You; your device | Run the account, deliver Introductions, security | Hosting, email delivery |
| Customer records (contact details, payment status) | Yes | You; Paystack | Payments, support | Paystack |
| Commercial information (Introductions, Tuppence ledger, listings) | Yes | Your use of the Platform | Operate the marketplace | Hosting |
| Internet activity (device/browser, logs, error reports) | Yes | Your device | Security, fault diagnosis | Hosting |
| Geolocation | **Coarse only** (city/suburb you enter on a listing) | You | Show local results | Hosting |
| Government identifiers / ID documents | Yes, at verification | You | Deferred KYC, fraud prevention | AI verification provider, under contract |
| Audio/visual (listing photos, screenshots you attach) | Yes | You | Display listings; reproduce reported faults | Hosting, AI moderation |
| Inferences | **Trust Score only** | Your Platform conduct | Listing visibility, reliability | Not disclosed |
| Biometric information | **No** | — | — | — |
| Education / employment information | Only if you submit a credential | You | Credential verification | AI verification provider |

We do not collect personal information from anyone we know to be under 18.

**B3 · Sensitive personal information.** Government identifiers and identity documents are
**sensitive personal information** under the CPRA. We use them **solely** to verify identity or a
credential, to prevent fraud, and to meet legal obligations — that is, only for purposes the CPRA
permits without a right to limit. We do not use or disclose sensitive personal information to infer
characteristics about you, and we do not use it for advertising of any kind.

**B4 · AI providers are service providers, not recipients for value.** Listing rewrites and audits,
price checks, photo drafting and moderation, identity-document verification and support triage are
performed by **Anthropic, OpenAI and Scaleway** under written contracts that (i) restrict them to
performing the service, (ii) **prohibit use of your content to train their models**, and (iii)
prohibit retention or disclosure for any other purpose. Disclosure to a service provider under such
a contract is not a sale or a share.

**B5 · Your California rights.** You have the right to **know** what we collect and why; to obtain a
**copy** of the personal information you gave us in a portable form; to **correct** inaccurate
information; to **delete** your personal information, subject to the exceptions in the statute
(legal obligations, security, completing a transaction you requested); to **opt out** of sale or
sharing (inapplicable — see B1); and to **limit** the use of sensitive personal information
(inapplicable as we use it only for exempt purposes — see B3).

**B6 · How to exercise them, and non-discrimination.** Email **legal@trustsquare.co** from the
address on your account, or write to the postal address in §1 of the policy. We confirm receipt
within **10 business days** and respond within **45 calendar days**, extendable once by a further 45
days where reasonably necessary, in which case we will tell you. We verify requests against the
account before acting. An **authorised agent** may submit a request with your written permission and
proof of identity. **We will not discriminate against you for exercising any of these rights** — no
denial of service, no different price, no reduced quality.

**B7 · Electronic contracting and auto-renewal.** You consent to transact electronically under the
E-SIGN Act and applicable UETA. Where a subscription renews automatically, the renewal terms are
disclosed clearly and conspicuously before purchase and you may cancel online at least as easily as
you subscribed.

**B8 · Other US states.** If you are a resident of a state with a comprehensive consumer privacy law
— including **Virginia, Colorado, Connecticut, Utah, Texas, Oregon, Montana and Delaware** — you
have rights of access, correction, deletion, portability, and opt-out of targeted advertising,
sale, and profiling with legal effects. We do not conduct targeted advertising, do not sell personal
data, and do not profile in a way that produces legal or similarly significant effects. We honour
access, correction, deletion and portability requests from residents of those states on the same
terms as B5–B6, and we offer an appeal: if we decline a request, you may reply to our decision and a
different reviewer will reconsider it within 45 days and tell you the outcome in writing, along with
how to contact your state Attorney General.

---

# SUPPLEMENT C — Australia

*To be inserted as "Country Supplement C — Australia".*

**This Supplement applies if you are in Australia.** It corresponds to Schedule C of the Terms of
Use. Where you are in Australia, we handle your personal information under the **Privacy Act 1988
(Cth)** and the **Australian Privacy Principles (APPs)**.

**C1 · Open and transparent management (APP 1).** This policy and this Supplement together are our
APP 1 privacy policy. The entity responsible is TrustSquare (Pty) Ltd at the address in §1. Privacy
enquiries: **legal@trustsquare.co**.

**C2 · What we collect and why (APP 3, APP 5).** As set out in §§2–3 of the policy: your email and
listing content as a seller; your contact details as a buyer when you request an Introduction;
transaction and Tuppence records; support correspondence; and technical logs. Where verification
applies we collect identity or credential documents. We collect this directly from you. **If you do
not provide it, we may be unable to create your account, verify you, or deliver an Introduction.**
We do not collect personal information from a third party about you without telling you.

**C3 · Sensitive information (APP 3.3).** We do not seek sensitive information as the Privacy Act
defines it. Where an identity document you upload happens to disclose sensitive information, we
collect it only with your consent, given by uploading it for verification, and use it only to verify
you.

**C4 · Anonymity and pseudonymity (APP 2).** The Platform is anonymity-first by design: **you may
browse without an account, and sellers remain unidentified to buyers until both parties accept an
Introduction.** This is how we give practical effect to APP 2, not merely a product feature.

**C5 · Use and disclosure (APP 6).** We use your personal information for the purpose you gave it to
us and for directly related purposes you would reasonably expect. We do not sell it. We disclose it
only to the service providers named in §5 of the policy, under written agreements.

**C6 · Direct marketing (APP 7).** You opt in to Platform emails when you create an account. Every
promotional email contains an unsubscribe facility, and we act on opt-outs within 5 business days.
You may ask us at any time not to use your information for direct marketing, and to tell you where
we obtained it.

**C7 · Cross-border disclosure (APP 8) — and what it means for you.** Your personal information is
stored and processed **outside Australia**: in South Africa; in the European Union (Hetzner hosting,
Cloudflare R2 backups); and, for AI features, in the United States (Anthropic, OpenAI) and France
(Scaleway). Before disclosing, we take reasonable steps to ensure each overseas recipient does not
breach the APPs, by written agreement. **Under APP 8.1 we remain accountable to you for their
handling of your information as though we had handled it ourselves** — so if an overseas provider
mishandles it, your recourse is with us, and you do not have to pursue them.

**C8 · Security, and destruction when no longer needed (APP 11).** TLS 1.3 in transit, encryption at
rest, role-based access control, and daily encrypted backups with 14-day retention. When we no
longer need your information for any purpose for which it may be used or disclosed, and we are not
required by law to retain it, we destroy it or de-identify it.

**C9 · Access and correction (APP 12, APP 13).** You may request access to the personal information
we hold about you and ask us to correct it. Write to legal@trustsquare.co. We respond **within 30
days**. Access is free; we do not charge for correction. If we refuse access or correction we will
tell you in writing why, and how to complain.

**C10 · Notifiable data breaches.** If we suspect an eligible data breach we assess it **within 30
days**. If we conclude one has occurred and it is likely to result in serious harm, we notify you and
the **Office of the Australian Information Commissioner as soon as practicable**.

**C11 · Complaints.** Write to legal@trustsquare.co; we respond within 30 days. If you are not
satisfied you may complain to the **Office of the Australian Information Commissioner** —
oaic.gov.au, 1300 363 992, GPO Box 5218, Sydney NSW 2001.

---

# What a reviewer should check before this goes live

1. **The A2 bracket must be resolved or removed.** Publishing a supplement containing "[PENDING]" is
   worse than publishing none.
2. **The §7 breach clause** (Finding 2) should be corrected in the same revision, or Supplement A is
   internally inconsistent with the body it sits under.
3. **`legal@trustsquare.co` must actually receive mail.** The body of the policy routes privacy
   requests to `support@trustsquare.co` (§9) and the EULA's contact table routes them to
   `legal@trustsquare.co`. These supplements use `legal@`, matching the EULA. **Pick one and make
   both documents agree** — a rights request sent to a dead address is a rights request denied. Not
   verified as deliverable by this draft.
4. **France and Portugal have the same defect** (Finding 3.2) and are not drafted here.
5. This is a draft prepared against the published statutes as I understand them; it is not legal
   advice, and it is the kind of text that benefits from the counsel review the EULA already has.
