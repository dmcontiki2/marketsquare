## 2026-08-03 — Evidence-true applied to legal credentials and the mandate (EVIDENCE-TRUE-1, EVIDENCE-TRUE-2)

**David's ruling:** "we need to apply the current rules" · "Re-queue them please."

The rules already existed. `TRUST_SCORE_CRITERIA.md`, Addendum 2026-07-21 §1 (David's ruling, 20 Jul):
*"every point of a displayed trust score must map to a specific certificate, accreditation, experience
or platform-recorded result"* — and the buyer-visible ledger that must satisfy it is served **per
listing**, `GET /sellers/credentials/{listing_id}`. Two things in the code contradicted that.

**EVIDENCE-TRUE-1 — the mandate was inherited across every listing.** A mandate authorises *one*
property; `bea_main.py:8049` says so in its own words ("Prevents fraudulent listings"). But
`seller_documents` was keyed on email alone and `user_credentials` is `UNIQUE(email, signal_id)`, so
the first mandate an agent ever uploaded earned +8 on listings 2…n with no document behind them — on
the per-listing ledger a buyer reads. A mandate credential with no mandate behind it is precisely the
fraud the signal exists to stop.

*Fix.* Additive nullable `seller_documents.listing_id` (+ index). Per-listing signals count only on the
listing whose document covers them. In South African practice the mandate is signed between the seller
and the **agency**, and any agent of that firm may market it — so the check resolves through agency
membership, and a colleague covering a listing does not trip the anti-fraud signal they are satisfying.
FFC and PPRA are deliberately unchanged: one certificate, one person, one year, genuinely covering
every listing that agent makes — evidence-true is already satisfied there.

**EVIDENCE-TRUE-2 — legal credentials were auto-earned by any file.**
`POST /users/{email}/documents` carried `# All other doc types: auto-earn immediately
(self-attestation)`, so an uploaded FFC awarded its full 10 points with nobody having opened it. That
contradicted §4a ("checked against the PPRA public register", "uploaded and reviewed"), §7's
verification workflow, and the app's own promise to the agent in `ms.js` — *"ops verifies before
points"*. An ops queue already existed (`GET /trust-score/credentials/pending`) and simply was not used
for these.

*Fix.* `_LEGAL_SIGNALS` (PPRA, FFC, mandate, MIRA dealer reg, ASATA, trade licence) land `pending` on
upload and go through the existing queue. `migrations/006_requeue_legal_credentials.py` applies the same
rule backwards — dry-run by default, `--apply` to re-queue — so credentials already earned under the old
path return to `pending` for a human to check. Declared and rejected rows are left alone; non-legal
credentials keep self-attestation by design. **Trust scores will move down for affected sellers until
ops verifies. That is the point: the score was asserting something nobody had checked.**

**Status.** Local. Migration 006 not yet run against the live database.
