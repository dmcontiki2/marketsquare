# Independent Peer Review — 2026-08-22-0716

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: privacy · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40521 in / 4684 out tokens · actual cost ≈ $0.1372

---

# Independent Privacy Review — MarketSquare Launch Audit

## Overall assessment

The audit identifies a real credential/security HOLD condition, but its privacy treatment is materially too narrow. It equates privacy largely with “anonymous public endpoints do not expose emails or phones.” That is useful but insufficient for POPIA/GDPR: the supplied code processes emails, identity documents/ID numbers, images, marketplace text, transaction history, and behavioural/trust data; sends subsets to multiple processors; and does not provide evidence of a lawful-transfer, retention, deletion, or processor-governance design.

The stated anonymity doctrine is also stronger than the implementation supports.

---

## Findings

### [BLOCKER] KYC identity documents and ID numbers may be sent to whichever AI provider is active, including US providers, without demonstrated POPIA/GDPR transfer controls or a KYC-specific retention/deletion regime

**Evidence**

- `Records/PEER_PACK_BEA_EXTRACT.md`, `bea_main.py` lines **11112–11124** defines `_sonnet_verify_identity(doc_url, claimed_name, claimed_id, doc_type, email)`.
- Lines **11139–11164** construct a prompt containing the claimed **full name** and **ID/passport number**, instruct the model to extract the “FULL NAME” and “ID NUMBER / PASSPORT NUMBER” from the image, and assess authenticity.
- Lines **11166–11177** send the identity-document image as base64 to `ai_provider.complete(...)`, selecting `provider=_ts_active_provider()`.
- `bea_main.py` lines **15039–15047** identify the selectable providers as Anthropic (**US**), Scaleway (**EU · Paris**), and OpenAI (**US**).
- `FORENSIC_AUDIT_CYCLE1 — nice.docx` states that three AI lanes are live and that OpenAI serves “100% of live AI traffic”; Cycle 2 repeats that the base lane is OpenAI.
- The KYC code prevents fallback (`allow_fallback=False`, line **11177**), which limits accidental fan-out, but it does **not** prevent a selected US lane from receiving KYC data.

**Why this is blocking**

Identity documents, names, email addresses, and national ID/passport numbers are high-risk personal data. Under POPIA, unique identifiers and identity-document processing require particularly careful treatment; under GDPR, the processing requires a documented lawful basis, transparency, data minimisation, processor terms, retention/deletion controls, and an international-transfer mechanism where applicable.

The material provides no evidence of:

1. a KYC-specific provider approval matrix (e.g., “KYC may only use provider X in region Y”);
2. a DPA/operator agreement with each AI provider;
3. cross-border transfer safeguards and transfer-risk assessment for the US lanes;
4. a data-subprocessor notice;
5. vendor training/retention settings being disabled or contractually controlled;
6. retention, deletion, or access-control rules for original documents, downloaded image bytes, extracted ID numbers, model responses, and verification logs;
7. an appeal/manual-review process appropriate to an automated identity decision.

“Never fan out to standby vendors” is good engineering, but it does not make the remaining transfer compliant.

**Required discussion**

KYC should not launch on a general active-provider switch. It needs a dedicated, explicitly approved KYC processing lane, fixed jurisdiction, contractual/data-transfer evidence, and a documented retention/deletion path before identity verification is enabled.

---

### [MAJOR] The claimed “anonymous marketplace” and “nothing leaves TrustSquare except … never the address itself” doctrine is contradicted by the implementation

**Evidence**

- `bea_main.py` lines **5180–5185** state: “Nothing of the customer's leaves TrustSquare except a consented, revocable email channel — never the address itself.”
- The relay database schema at lines **916–925** stores `real_email` for each party in `intro_relay_aliases`.
- `bea_main.py` lines **5236–5263** forwards a relay message through Resend. The recipient’s real email address is placed directly in the Resend API request: `json={"to": [to_clean], ...}`.
- Lines **5258–5262** also send the free-text message body to Resend. The body is merely length-capped; there is no content minimisation, PII detection, attachment scanning, or redaction.
- `bea_main.py` lines **5770–5786** sends introduction events to `N8N_WEBHOOK_ACCEPT`. When relay is disabled, the payload contains raw `buyer_email` and seller email (lines **5777–5781**); even when relay is enabled, it still sends `buyer_name`, listing title, category, city, timestamps, and introduction IDs.
- The audit describes relay as a privacy mechanism but does not identify Resend or n8n as processors receiving personal data.

**Why this matters**

The relay can successfully hide counterparties’ email addresses **from each other**, but it does not mean personal data never leaves TrustSquare. At minimum, real recipient email addresses leave to Resend, and n8n receives introduction metadata and sometimes raw contact addresses. Message content can contain names, addresses, phone numbers, transaction terms, and other information voluntarily supplied by users.

The statement is therefore misleading in privacy notices, audit records, and product communications. It risks invalid transparency and consent wording because users are told a stronger privacy property than the system delivers.

**Required discussion**

Revise the doctrine and privacy notice to distinguish:

- hiding identities from the other marketplace user;
- disclosure to service providers/processors (Resend, Cloudflare Email Routing, n8n, hosting);
- optional disclosure initiated by a user in message content; and
- legacy behavior when `intro_relay` is disabled.

Also establish whether n8n receives data under a processor agreement, where it is hosted, who can access it, and its retention/logging behavior.

---

### [MAJOR] The 30-day relay “TTL” is not evidence of personal-data deletion; real email addresses and introduction data appear to be retained indefinitely

**Evidence**

- `bea_main.py` lines **5190–5194** set `_RELAY_TTL_DAYS` to 30 days by default.
- Lines **5210–5228** store each alias, `intro_id`, party, `real_email`, counterparty alias, creation time, and expiry time in SQLite.
- The supplied relay endpoint only checks whether an alias is active and whether `expires_at` is in the past (lines **5321–5333**).
- No supplied code deletes, anonymises, encrypts, or otherwise purges `intro_relay_aliases` after expiry.
- No retention mechanism was supplied for `intro_requests`, `transactions`, AI spend logs (which include `email`, lines **1769–1817**), logs, KYC data, or n8n/Resend records.

**Why this matters**

Expiry of a communication channel is not deletion of the underlying personal data. The code as supplied establishes that expired aliases cease working, but not that real email addresses, relationship metadata, or message delivery records are deleted. This is especially important because the claimed privacy benefit depends on storing a mapping from a public alias to a real email address.

The same concern applies to data subject access, correction, objection, and deletion requests: the material gives no record-location map or operational deletion procedure across the primary SQLite database, backups, Resend, Cloudflare, n8n, and AI providers.

**Required discussion**

Define and evidence a retention schedule for each data class and processor, including:
- active/expired relay aliases and introductions;
- user and listing data;
- KYC documents, extracted ID fields, and verification results;
- transaction/financial records, which may have legally required retention;
- audit/application logs and AI spend logs;
- backups and deletion propagation.

---

### [MAJOR] AI product features transmit user-supplied listing text and images to external AI processors without demonstrated minimisation, content screening, or jurisdiction-aware routing

**Evidence**

- `bea_main.py` lines **16297–16327** send listing category, city, title, description, and price to the selected AI provider for rewriting.
- Lines **16398–16431** send the same data plus intro-request count and seller trust score for an AI seller audit.
- `bea_main.py` lines **17518–17564** accept up to ten base64 images and send them to the selected AI provider for batch-card processing.
- The batch-card endpoint’s system prompt (lines **17510–17515**) does not prohibit processing faces, identity documents, addresses, children, or other incidental personal information contained in uploaded images.
- The listing rewrite/audit prompts prohibit the **model output** from including identifiers (e.g., lines **16303–16310** and **16404–16411**), but that restriction does not prevent a user’s source listing text from being sent to the provider as input.
- The active provider is dynamically selected and can be US or EU (`bea_main.py` lines **15039–15047**).

**Why this matters**

Output-prompt instructions are not input-data controls. A seller can place a phone number, address, personal name, or sensitive narrative in a listing; a photo may include a face, house number, vehicle registration, or document. The application then forwards that content to an external model provider. The supplied code contains no demonstrated pre-transfer redaction, file-type/metadata stripping, face/document detection, per-feature consent, or routing policy based on content sensitivity and region.

This is a data-minimisation and transparency problem even if the AI vendor contractually does not train on API inputs.

**Required discussion**

Establish a feature-by-feature data map and decide whether:
- AI features are opt-in with clear provider/region disclosure;
- uploaded images undergo metadata stripping and abuse/PII controls;
- marketplace text is redacted before inference;
- high-risk image classes are rejected or routed only to an approved region/provider; and
- each provider is covered by appropriate processor and transfer terms.

---

### [MAJOR] The audit’s conclusion that “PII exposure is low” is too broad and can create false launch confidence

**Evidence**

- `FORENSIC_AUDIT_CYCLE2_PEER — nice.docx`, “Coverage gaps,” says it probed `/listings` and `/dashboard/summary`, finding “0 emails, 0 phones, no street_address,” then concludes: “PII exposure is low; the disclosure risk is operational, not personal-data.”
- That probe is valuable for **anonymous HTTP response exposure**, but the same review material includes substantial backend personal-data processing:
  - KYC documents and ID/passport numbers (`bea_main.py` lines **11112–11197`);
  - relay mapping of aliases to real emails (lines **5210–5228**);
  - Resend API delivery to real addresses (lines **5236–5263**);
  - n8n introduction webhook data (lines **5770–5786**);
  - AI service inputs containing listings, images, trust scores, and behavioural data.

**Why this matters**

The public endpoint result supports only a narrow claim: *the specific unauthenticated responses tested did not expose the particular PII fields searched for*. It does not measure privacy exposure in storage, logs, processors, backups, authenticated API endpoints, staff/admin access, or data-subject rights handling.

I disagree with the audit’s broader privacy characterization. It has tested anonymous data display reasonably well, but it has not established a privacy posture.

---

### [QUESTION] What is the lawful basis, controller/processor allocation, and transfer basis for each personal-data flow?

**Evidence**

The material identifies multiple third parties and jurisdictions but does not provide privacy governance evidence:
- AI providers: US and EU (`bea_main.py` lines **15039–15047**);
- Resend relay delivery (`bea_main.py` lines **5249–5263**);
- Cloudflare Email Routing (`bea_main.py` lines **5183–5185**);
- n8n webhooks (`bea_main.py` lines **5770–5786**);
- Hetzner is named as production infrastructure in Cycle 2’s `/dashboard/summary` disclosure.

Cycle 2 additionally states that `privacy.html` has a “pending attorney review” provenance flag.

**Questions for the System Engineer**

1. Who is the POPIA responsible party / GDPR controller, and which entities are operators/processors?
2. What lawful basis applies separately to account creation, marketplace introductions, payments, AI assistance, KYC, anti-fraud, and marketing/analytics?
3. Which vendors receive each category of personal data, in what country, and under what DPA/transfer mechanism?
4. Is cross-border transfer disclosed in the privacy notice in a way that matches the dynamic provider routing?
5. Does “pending attorney review” mean the privacy notice is not legally approved for launch? If so, why is this not a launch gate?

---

### [QUESTION] Is anonymised/alias-based communication genuinely consented, revocable, and safe after a user chooses to reveal themselves?

**Evidence**

- Relay comments call the channel “consented, revocable” (`bea_main.py` lines **5180–5183`).
- The shown implementation mints aliases on accepted introductions (lines **5750–5769**) and expires them after the configured TTL.
- No consent capture, consent version, opt-out/revocation endpoint, channel-close endpoint, or evidence of deletion on revocation is supplied.

**Question**

Where are the affirmative consent record, timestamp, privacy-notice version, withdrawal mechanism, and downstream deletion process implemented? A 30-day automatic expiry is not necessarily consent withdrawal or deletion, and the user may not understand that relay messages are processed by Cloudflare and Resend.

---

### [MINOR] Logging appears likely to create additional personal-data copies, while the supplied material offers no log-retention or redaction controls

**Evidence**

- `bea_main.py` line **16352** logs the email address for listing rewrite activity.
- Line **16460** logs seller email and intro count.
- Lines **1769–1817** persist AI usage records including email and endpoint.
- Lines **5166–5170** log passed and session email addresses in account-binding shadow mode, including mismatches.
- Relay logging includes operational information and can include alias references (`bea_main.py` lines **5292–5294**, **5330–5332**).

**Why this matters**

Logging email addresses may be defensible for security, billing, and audit purposes, but it expands the system’s data footprint and potentially places data in systemd/journald, centralized logging, backups, and developer-accessible logs. The supplied material does not show minimisation (e.g., hashed identifiers), access controls, or retention limits.

---

### [PRAISE] The implementation contains several privacy-positive technical controls, though they are not a complete privacy programme

**Evidence**

- Cycle 2 probed public `/listings` and found no emails, phone numbers, or street addresses, and found no demo data bleed.
- The relay uses random aliases rather than embedding personal data in aliases (`bea_main.py` lines **5210–5228**).
- The relay sanitises subjects against header injection (`bea_main.py` lines **5231–5233**) and limits message body size.
- The relay validates that the sender matches the enrolled counterparty before forwarding (`bea_main.py` lines **5304–5339**).
- KYC explicitly disables provider fallback (`bea_main.py` line **11177**), reducing unnecessary replication of ID documents across vendors.
- Listing AI prompts attempt to prevent personal identifiers from appearing in generated output (`bea_main.py` lines **16303–16310**, **16404–16411**).

These are meaningful safeguards. The gap is that they are framed as sufficient anonymity/privacy guarantees without equivalent controls for processor disclosure, retention, and international transfers.

---

## Internal contradictions and documentation concerns

1. **“Nothing … leaves TrustSquare … never the address itself” conflicts with the Resend implementation.**  
   The real recipient email is explicitly sent to Resend (`bea_main.py` lines **5236–5263**). The claim could be true only in the narrower sense that the address is not disclosed to the *counterparty*, not that it never leaves the platform.

2. **“PII exposure is low” is based on narrow endpoint testing but is stated broadly.**  
   Cycle 2 correctly checked public responses, but the supplied source shows high-risk backend and third-party processing. The conclusion needs scope qualification.

3. **Dynamic multi-provider failover is in tension with data-location predictability.**  
   The audit presents three live AI lanes as robustness strength. For ordinary text tasks that may be acceptable with proper vendor governance, but it conflicts with a privacy posture requiring users to understand where their data goes—especially because active provider selection is runtime-configurable.

---

## The three findings the System Engineer should discuss first

1. **KYC must be treated as a launch-blocking privacy flow**: identity documents and ID/passport data can be transferred to dynamically selected US/EU AI providers, with no supplied proof of KYC-specific processor, transfer, retention, or deletion controls.

2. **Correct the anonymity/privacy claims and map all processors**: Resend receives real addresses; Cloudflare and n8n process introduction data; AI providers receive listing text/images and potentially identifiers. The current “nothing leaves TrustSquare” doctrine is factually overbroad.

3. **Define enforceable retention and data-subject-rights operations**: a 30-day relay expiry does not delete `real_email` mappings; no evidence was supplied for deletion/anonymisation across SQLite, logs, backups, AI vendors, Resend, Cloudflare, or n8n.

---

## What I could not verify from the material given

I could not verify the actual contents or legal approval status of the privacy notice, terms, or consent UX; any DPAs, operator agreements, vendor no-training terms, SCCs/transfer mechanisms, or POPIA cross-border-transfer assessment; hosting and processing locations for Hetzner, n8n, Resend, Cloudflare, and AI tenants; encryption at rest/in transit and key-management arrangements; backup contents/retention/restore access; actual production feature-flag states for KYC, account binding, and relay; full database schemas and deletion jobs; access controls for staff, developers, vendors, and logs; or whether data subject access/deletion/correction requests are operationally supported.
