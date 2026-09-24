# Independent Peer Review — 2026-09-24-0753

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: full · Author: Claude · System Engineer: David*

**Scope:**
  - genie/BUG_AUDIT_2026-09-23.html (12,387 chars)
  - changelog.d/2026-09-23-audit-fixes.md (2,826 chars)
  - ../CLAUDE.md (45,427 chars)
  - CLAUDE.md (25,416 chars)

**Usage:** 22954 in / 6426 out tokens · actual cost ≈ $0.1230

---

# Peer Review Report

## Part B — Plain-language explanation for David

- **MAJOR — Why these mistakes happened:** The AI treated an email typed into a page as proof of identity.  
  An email address is only a label.  
  It is not proof that the person using it owns it.

- **MAJOR — Why the delete flaw happened:** The app key was placed in `ms.js`, which every visitor can download.  
  The code then treated that public key as permission to delete adverts.  
  That means the lock was printed on the outside of the door.

- **MAJOR — Why the page-code flaw happened:** The AI stored user words and later placed them into web pages.  
  It did not consistently treat those words as untrusted.  
  A title, description, translation, or older saved record can all carry harmful page code.

- **MAJOR — Why the AI did not notice its own errors:** It mainly checked whether the normal journey worked.  
  It did not first try to act as a stranger.  
  For example, it should have tested: “Can I publish as an existing person by typing their email?”  
  It should have tested: “Can I delete an advert using only data found in the browser?”

- **MAJOR — Why fixes return as regressions:** The rules are spread across many files and have conflicting instructions.  
  One project rule still says seller edits use `?email=` authentication.  
  The audit says typed emails are no longer trusted.  
  A later AI can follow the old rule and rebuild the security defect.

- **MAJOR — Why the regression ledger has not been enough:** The ledger checks things that are already known.  
  It does not prove that every similar route, screen, old record, or special case was found.  
  It can stop an old known bug from returning.  
  It cannot find a bug nobody added to the ledger.

- **PRAISE — Rules that help:** The root `CLAUDE.md` requires a test before and after a fix.  
  It requires a ledger check for every fixed issue.  
  It says each check must state its scope.  
  It also says live claims need live evidence, not a document saying they are true.

- **PRAISE — Rules that help:** The root `CLAUDE.md` says a public browser key must not be treated as secret.  
  It also says fixes must be checked on the live site.  
  Those rules point in the right direction.

- **MAJOR — Rules that do not solve the real problem:** “Build first” encourages fast implementation.  
  It does not require someone else to challenge the design before it goes live.  
  Fast building is useful.  
  It is dangerous when identity, deletion, money, privacy, or public web pages are involved.

- **MAJOR — What is missing:** There is no hard rule that every action which changes or reveals private data must prove who the caller is on the server.  
  There is no hard rule that browser data is never permission.  
  There is no hard rule that all user-written text is safe only when displayed as text.

- **MAJOR — What is missing:** There is no required security test pack that tries the same action as a stranger, another signed-in user, an owner, and an administrator.  
  The audit found several of these only by accident during a normal publish test.

- **BLOCKER — The single structural change most likely to reduce regressions:** Do not let the same AI both write, approve, and deploy sensitive changes.  
  Put the deploy branch behind a required independent review and an automatic test gate.  
  The gate must test identity, ownership, deletion, private-data reads, and harmful text before code can ship.

- **MAJOR — What would make an audit trustworthy:** The auditor must be independent of the author.  
  The auditor must see the actual code, the list of all routes, the live responses, and the test results.  
  The audit must show failed tests before the fix and passing tests after it.  
  “Fixed” must mean evidence exists, not that the same author says it is fixed.

---

## Part A — Review of the audit and changelog

### Overall conclusion

**BLOCKER — The statement “17 of 17 fixed and live. Nothing is left open” is not supported by the supplied evidence.**  
**Lens: assurance, security, operability**

`genie/BUG_AUDIT_2026-09-23.html` makes a very strong claim:

> “Every confirmed defect is fixed, deployed and checked on the live site. Nothing is left open.”

But the supplied material contains only prose assertions by the same author, a changelog fragment, and references to commits and ledger IDs. It does **not** provide:

- the changed server or browser code;
- the complete route inventory;
- the actual ledger entries and their assertions;
- the reported 427 test results;
- raw live request/response evidence for each fix;
- test evidence for negative cases;
- proof that the cited commits are deployed;
- proof that old database records were migrated or made safe.

The one live journey for listing `#394` is useful but narrow. It proves only a few specified routes and conditions for one test account. It cannot prove every audit item, much less that no related route remains exposed.

The audit should therefore be described as **“17 items claimed fixed; independently unverified”**, not closed with nothing open.

---

### Highest-priority findings

#### 1. Contradictory project instructions can directly recreate the reported authentication flaw

**BLOCKER — `CLAUDE.md` still instructs the author to use email-as-authentication for edits, contradicting the audit.**  
**Lens: security, maintainability, regression prevention**

The audit says, in `genie/BUG_AUDIT_2026-09-23.html`:

> “Publish, edit and ‘my adverts’ trusted a typed email… They now act only as the signed-in person.”

And `changelog.d/2026-09-23-audit-fixes.md` says:

> “PUT /listings/{id}/publish, PUT /listings/{id} and GET /listings/mine act as the proven session … not ?email=.”

However, the supplied project-level `CLAUDE.md` still says:

> “Edit-after-publish: sellers use `PUT /listings/{id}?email=` — email-auth, no API key; NULL seller_email accepts first caller and stamps it”

This is an explicit instruction to recreate the core defect described as `AUDIT-AUTH-1`. It also describes a dangerous “first caller claims an unowned listing” model.

This is not merely stale documentation. The project instructs AI agents to read and follow `CLAUDE.md`. A future session can reasonably restore email-based authorization while trying to follow project rules. That makes the claimed “locked” state unreliable.

**Required discussion:** Which document is authoritative for authorization? The incorrect instruction must not remain in any agent instruction, runbook, canon, comment, or test fixture.

---

#### 2. The audit groups several symptoms that share a single root cause: no server-side ownership model

**MAJOR — `AUDIT-Q1`, `AUDIT-AUTH-1`, and `DELETE-BIND-1` are one root-cause family, not three independent fixes.**  
**Lens: security, design, maintainability**

These findings all arise from the same design error: the server accepted caller-provided values as proof of identity or ownership.

- `AUDIT-Q1`: a stranger typed a member email and could publish as that member.
- `AUDIT-AUTH-1`: publish, edit, and “my adverts” trusted the email supplied by the page.
- `DELETE-BIND-1`: deletion trusted a public app key or owner email.

The common rule must be: **the server derives the acting person from a verified session, then checks that person is allowed to act on this specific listing.** The client must not select the actor by posting an email, user ID, trust score, status, owner ID, or secret-like browser value.

The changelog lists only the explicitly discovered endpoints:

> `PUT /listings/{id}/publish`, `PUT /listings/{id}`, `GET /listings/mine`  
> `DELETE /listings/{id}`, `DELETE /listings/{id}/seller`, `DELETE /listings/{id}/wonders/{wid}`

It does not establish that this rule has been applied across all routes. Likely missed routes and paths include:

- create or draft creation routes;
- draft retrieve, update, publish, discard, and resend-link routes;
- photo upload, replacement, and deletion routes;
- language and translation routes;
- listing versions/history/restore routes;
- “arrival card,” hub-card, and notification routes;
- status, trust score, moderation, plan, and quality-preview routes;
- user/profile routes keyed by email;
- admin routes that may accept a browser-supplied role, key, or email;
- bulk, background, migration, and internal-only routes that can be reached from the public app.

The audit needs a complete endpoint-by-endpoint access-control table. Without one, it cannot claim to have fixed the class.

---

#### 3. “New addresses still publish in one tap” remains an identity and abuse decision, not a resolved security claim

**MAJOR — `AUDIT-Q1` may still permit impersonation and spam for any email address not already registered.**  
**Lens: security, privacy, abuse prevention, operability**

The audit says:

> “Now a stranger only gets a draft, and the real owner gets an email to publish it. New addresses still publish in one tap.”

The changelog repeats:

> “a new address still publishes in one tap”

This stops one narrow case: impersonating an **existing** account. It apparently does not stop someone from entering a victim’s email address that has not registered yet and publishing an advert under that address.

The report does not explain whether “new address” means:

1. an address verified by a login link or emailed code before publishing; or
2. merely an address that is absent from the database.

If it is the second, a stranger can still claim another person’s email address, create a public advert under it, trigger emails, and possibly prevent the actual owner from using the address later.

The “5 per connection per day” control is not a sufficient identity control. Connections/IP addresses can be shared, mobile, masked, or rotated. It may also unfairly block people behind a shared network.

**Question that must be answered:** Does every first-time address prove control of that mailbox before any public listing is created, shown, emailed, or associated with the address?

---

### Detailed review of individual audit claims

#### 4. Deletion changes are credible in direction but incomplete in scope and potentially inconsistent in design

**MAJOR — `DELETE-BIND-1` describes a sensible route change but does not prove all delete-like operations are protected.**  
**Lens: security, design, operability**

The changelog says:

> “`DELETE /listings/{id}` now requires admin credentials for every advert”  
> “`DELETE /listings/{id}/seller` and `DELETE /listings/{id}/wonders/{wid}` are bound to the signed-in session”

The test also reports:

> “owner session delete -> 200”

This is compatible if the owner uses `/listings/{id}/seller`, while ordinary `DELETE /listings/{id}` is admin-only. But the audit does not say this clearly. A reader could conclude that owner deletion via the ordinary route is allowed, contradicting the changelog.

More importantly, deletion is broader than a route named `DELETE`. The audit needs to cover:

- unpublish/archive/hide actions;
- status changes that remove or suppress listings;
- media deletion;
- draft deletion;
- version rollback/restore;
- wonder deletion;
- bulk administrative deletion;
- deletion through alternate API versions or internal endpoints.

**Question:** What exact server-side function performs ownership checks, and do all deletion or removal paths call it?

---

#### 5. An “admin token” sent by the browser would repeat the public-key flaw

**QUESTION — The audit does not establish where the new admin credential lives or how it is protected.**  
**Lens: security**

The changelog says:

> “Admin console delete sends its admin token”

That is not enough information to assess safety. If this “admin token” is embedded in browser JavaScript, local storage, a page response, or a predictable request header, it is again public to a visitor and is not an admin credential.

A secure design would use a verified administrator session, preferably with server-side role checks, secure cookies, short-lived session state, and audit logging. A browser must not hold a permanent all-powerful shared secret.

**Question:** Is the token ever shipped to a non-admin browser, stored in static files, logged, sent in URLs, or reused as a long-lived bearer credential?

---

#### 6. XSS remediation is not demonstrably complete

**MAJOR — `AUDIT-XSS-1` and `AUDIT-S4` treat a system-wide output-encoding problem as a limited storage/input problem.**  
**Lens: security, privacy, maintainability**

The audit says:

> “Titles and descriptions are now saved as plain text wherever they are written.”

It also says:

> “Translated text went into the page unescaped. It is now escaped the same way seller text is.”

This is directionally correct, but incomplete as evidence and likely incomplete as design:

1. **Existing data:** “now saved” does not prove existing listings, drafts, versions, translations, search copies, emails, cached pages, or database backups no longer contain hostile markup.
2. **All fields:** Titles and descriptions are not the only displayable strings. Relevant fields include seller names, locations, category labels, image captions/alt text, specifications, plan messages, language fields, notification text, and admin notes.
3. **All output contexts:** HTML text, HTML attributes, URLs, JavaScript strings, email HTML, and JSON embedded in pages require different safe handling. One generic “escaped” helper may be correct in one context and unsafe in another.
4. **Storage versus display:** Storing plain text is helpful, but safe display must still be the default at every output point. Future imports, migrations, translations, or API integrations can bypass input cleaning.
5. **Rich text ambiguity:** The phrase “plain text” needs a specified implementation. If it only strips obvious tags, malformed markup or encoded payloads may still survive. If it destroys meaningful text, it can create user-data loss.

The audit needs tests using stored old records and malicious payloads across public listing pages, browse cards, edit forms, translations, seller panels, emails, and administrative views.

---

#### 7. Translation and search-copy invalidation likely share one data-lifecycle root cause

**MAJOR — `AUDIT-L2/L3`, `AUDIT-L4`, `AUDIT-L6`, `AUDIT-L7`, and `AUDIT-S4` are a related translation pipeline class, not isolated defects.**  
**Lens: correctness, cost, security, maintainability**

The audit reports:

- old translations stayed after source text changed;
- the photo marker was translated;
- any language was accepted;
- spend was counted before a successful call;
- translated output was not escaped;
- English search copy had links removed.

These point to a translation system with unclear data ownership, input preparation, caching, invalidation, validation, cost accounting, and output safety.

The statement:

> “Editing now clears the translation, its check-back and the English search copy, but only after the owner check passes.”

is reasonable, but it raises missing cases:

- Does it clear derived content on **every** source field that affects translation?
- Does it run for changes from admin edit, import, migration, quick publish, draft promotion, restore, and API clients?
- Does it clear or version any cached translations on the public page?
- What happens if an edit occurs while a translation call is in progress?
- Is the outdated translated text still visible before replacement?
- Does clearing search copy make the listing temporarily unsearchable, and is that intended?
- Can a stale translation be restored through listing version history?

The audit needs one source-of-truth model: derived translation/search data must be tied to the exact source revision, not merely “cleared in one edit handler.”

---

#### 8. “Spend counted after success” does not necessarily prevent cost overruns

**MAJOR — `AUDIT-L7` lacks concurrency, retry, timeout, and provider-billing evidence.**  
**Lens: cost, performance, operability**

The audit says:

> “Spend is now counted after a successful call. Each advert gets at most 5 AI drafts a day.”

This could improve incorrect local accounting, but it does not prove actual external cost is controlled.

Important unaddressed cases include:

- Two requests start simultaneously when the counter is at four.
- A call times out locally after 18 seconds but succeeds at the provider and is billed.
- The client retries after a timeout while the first call continues.
- A provider returns a partial result or an ambiguous error.
- One listing is recreated to evade the five-drafts-per-listing limit.
- A caller creates many listings, sessions, or IP addresses.
- Per-advert limits are not a total budget limit for the business.

The language gate (`AUDIT-L6`) is also a product-limit check, not a complete spending control. A hard server-side global daily/monthly provider budget, idempotency key, queue/concurrency limit, and monitoring of provider-reported usage are needed to make cost claims credible.

---

#### 9. The 18-second timeout is not enough to show pages cannot hang

**MAJOR — `AUDIT-S1` may move the failure from an indefinitely waiting request to a repeated expensive failure.**  
**Lens: performance, cost, operability**

The audit says:

> “AI calls now time out after 18 seconds.”

This needs clarification:

- Is the timeout applied server-side to the outbound provider request?
- Is the provider request actually cancelled, or does it continue consuming capacity and money after the client receives a timeout?
- Does the browser receive a clear retry-safe response?
- Are retries bounded?
- Are concurrent AI calls per account/listing limited?
- Is the service protected when the AI provider is slow for many users at once?

An 18-second timeout can be appropriate, but its value depends on cancellation, queueing, retry behavior, and capacity limits. None are shown.

---

#### 10. The privacy fix is insufficiently scoped and may expose data in other representations

**MAJOR — `AUDIT-L1` only names one public detail endpoint and one owner-only language endpoint.**  
**Lens: privacy, security**

The changelog says:

> “GET /listings/{id} hides the seller's email from everyone but the seller, and never returns language working data”

This does not establish that the email and language work data are absent from:

- browse/list/search endpoints;
- JSON embedded in public HTML;
- API caches;
- listing version/history endpoints;
- export and feed endpoints;
- error responses;
- page source and browser state;
- emails, notifications, logs, analytics, or monitoring;
- the new `/listings/{id}/lang` endpoint when authorization fails.

The live test for `#394` says the email was not visible on the public page. That is not equivalent to confirming it was absent from network responses and other public APIs.

**Question:** Does the public `GET /listings/{id}` omit the fields entirely, or merely hide them in the user interface? The former is required.

---

#### 11. The “quality preview never 500s” fix may hide invalid input instead of defining correct validation

**MINOR — `AUDIT-Q4` lacks a stated contract for invalid data.**  
**Lens: correctness, operability**

The audit says:

> “The preview now converts field types instead of failing with a server error.”

Avoiding a server crash is good. However, automatic conversion may silently change values or accept malformed data. The expected behavior should be explicit: either a valid preview or a clear user-facing validation error. A 500 response is wrong, but silently converting `null`, arrays, objects, or unusual numbers can create misleading quality scores.

---

#### 12. Language re-rendering needs an idempotency and analytics test, not only a UI assertion

**MINOR — `AUDIT-L5` is plausible but weakly evidenced.**  
**Lens: correctness, analytics, maintainability**

The audit says:

> “Changing language now redraws the page without logging a view or changing where Back goes.”

The likely root issue is client-side navigation/render code treating a language presentation change as a new page visit. The regression test should show:

- a language switch does not create a new history entry;
- browser Back returns to the previous actual page;
- repeated language switches do not increment view count;
- a direct refresh in a translated language still works;
- analytics distinguishes a language preference event from a listing view.

No such evidence is supplied.

---

#### 13. The live test is useful, but it is not a comprehensive security test

**PRAISE — The `#394` test is the strongest evidence in the supplied material.**  
**Lens: assurance**

The audit performed a real, end-to-end flow:

> “Signed in as the approved tester … published … signed out … deleting it with only the right email was refused … deleting it with the public key was refused … owner’s signed-in delete worked.”

This is better than a code-only claim. It tested both a normal user journey and two negative deletion cases.

However:

**MAJOR — The live test tests only one listing, one owner, one public key path, and one email path.**  
**Lens: security, assurance**

It does not test a second signed-in non-owner, a stale session, a forged cookie, alternate delete paths, altered listing ownership, admin access, drafts, translations, email links, or old stored data. The audit should not generalize this one scenario into “nothing left open.”

---

### Regression ledger and evidence concerns

#### 14. The ledger is valuable but cannot establish completeness

**MAJOR — The audit overstates what “427 entries, 0 regressed” means.**  
**Lens: assurance, maintainability**

The audit says:

> “The full board ran clean, with 0 regressions.”

The root `CLAUDE.md` correctly describes the ledger as a system for known facts:

> “the ledger answers ‘is anything we already fixed BACK’.”

That is valuable. But a clean ledger does not mean no open defects exist. It means the tests in that ledger did not fail under the conditions tested.

The root `CLAUDE.md` also acknowledges an important reliability limitation:

> “Until that is fixed: run the board from the working tree, and treat any board run elsewhere as unusable.”

The audit does not say where the 427-entry board ran, whether all entries were actually evaluated, whether any were skipped, whether it was the authoritative working tree, or whether the test board includes the newly discovered endpoint families.

The footer’s:

> “142 rulings checked, 0 failing”

is likewise not evidence that application security is complete. Rulings checks validate whether decisions are reflected in selected files; they do not prove access control is correct in production.

---

#### 15. The audit’s own source hierarchy is internally contradictory

**MAJOR — The two supplied `CLAUDE.md` files conflict on file writes, deployment, commits, and authorization-adjacent operating practices.**  
**Lens: maintainability, operability, regression prevention**

Examples:

- Root `../CLAUDE.md` says:
  > “File writes on this mount: NEVER use Edit/Write”
  
  Project `CLAUDE.md` says:
  > “Use the Read→Edit file-tools for doc/code edits”

- Root `../CLAUDE.md` says:
  > “ONE DEPLOY — code ships ONLY by publishing the deploy ref”
  
  Project `CLAUDE.md` provides direct `scp` deployment commands for individual application files.

- Root `../CLAUDE.md` says commits and pushes are already permitted through the host queue.  
  Project `CLAUDE.md` says:
  > “Always ask David to run git add/commit/push from PowerShell”

- Root `../CLAUDE.md` makes ledger coverage and live evidence mandatory.  
  Project `CLAUDE.md` defines “done” as working code plus a changelog paragraph, without requiring a security review or ledger entry for every sensitive change.

These are not harmless historical notes. They are active conflicting instructions to an AI. Such conflicts explain why a regression ledger can coexist with repeated regressions: different sessions can follow different “authoritative” rules.

There needs to be one short, current, precedence-controlled operating agreement. Superseded instructions must be removed or mechanically marked unusable.

---

#### 16. The audit should have identified the insecure historical route note as an open regression risk

**MAJOR — The audit misses the highest-risk documentation residue: the old email-authentication instruction in `CLAUDE.md`.**  
**Lens: security, maintainability**

Given that the audit specifically found and fixed typed-email authorization, it should have searched all source, tests, documentation, comments, route notes, and AI instructions for terms such as:

- `?email=`
- `seller_email`
- `_actor`
- `app key`
- `admin token`
- `DELETE /listings`
- `PUT /listings`

The supplied material proves this sweep was not complete, because `CLAUDE.md` still documents `?email=` as the seller authentication mechanism. This finding alone invalidates the “nothing left open” claim.

---

### Likely missed paths by defect class

#### Authentication and ownership class

**MAJOR — Audit scope should explicitly include every route that takes an email, listing ID, owner ID, or privileged field from the client.**  
**Lens: security**

Search and test all routes in these categories:

- listing create, edit, publish, unpublish, archive, restore, delete;
- drafts, scheduled publication, resend and magic-link flows;
- “my listings,” arrival card, hub card, notifications;
- media and photo operations;
- translations, language panels, search-copy generation;
- versions/history and rollback;
- trust, quality, status, plan, and moderation fields;
- user/profile functions keyed by email;
- admin and support endpoints;
- background-job callbacks and internal maintenance endpoints.

For each, test as anonymous stranger, unrelated signed-in user, correct owner, and administrator.

#### Public-data and privacy class

**MAJOR — Audit scope should cover every public representation of a listing, not only `GET /listings/{id}`.**  
**Lens: privacy**

Check browse, search, maps, feeds, static HTML, embedded JSON, page source, cached CDN responses, exports, notification emails, logs, and error bodies. Verify sensitive fields are absent, not merely hidden in the visible user interface.

#### Untrusted-text class

**MAJOR — Audit scope should cover every field and output surface, including old records.**  
**Lens: security**

Test hostile stored text in title, description, translations, seller data, locations, specifications, image fields, history records, emails, and administration pages. Test actual browser execution, not only string matching.

---

## What the System Engineer should discuss first

1. **The contradiction that can recreate the central defect:**  
   `CLAUDE.md` still tells agents to authorize edits with `?email=`, despite the audit claiming this is fixed. Resolve and remove the conflicting instruction everywhere.

2. **The absence of a complete server-side ownership review:**  
   Treat publish, edit, delete, draft, media, translation, version, and admin operations as one access-control problem. Require a complete route inventory and stranger/non-owner/owner/admin tests for every route.

3. **The unsupported closure claim:**  
   Replace “17 of 17 fixed, nothing left open” with evidence-backed status. Require raw test results, endpoint coverage, deployment proof, and an independent reviewer before closing an audit.

---

## What I could not verify from the supplied material

I could not inspect the actual application code, commit contents, deployed server configuration, database schema, route inventory, live API responses, browser network traffic, ledger entries, ledger execution output, rulings output, deployment logs, authentication/session implementation, admin-token handling, old stored records, or provider billing records.

I therefore cannot confirm that any individual fix is actually deployed or complete. I can only assess whether the audit’s written claims are technically credible and whether the supplied rules and documents support those claims.
