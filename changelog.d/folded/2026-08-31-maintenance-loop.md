## 2026-08-31 — Maintenance loop: a customer-data leak found and closed on the eve of launch, and the brain taught to read the lane that is actually open

**Queue: empty, and that was the finding.** 0 new / 0 triaged / 0 fix-shipped; 26 verified,
7 closed. The shadow agent ran clean (`.maint_agent/run_20260831T053704Z.json`, 0 seen) and
its heartbeat reached `/dashboard/maint` at 05:37:21Z. But an empty queue on the day before
full launch (RUL-001) is a claim worth probing rather than reporting, and probing it produced
three defects — none of them filed by anyone, all of them found by looking at why nothing
was filed.

**DASH-TRIAGE-REDACT-1 — `GET /dashboard/email-triage` was serving customer identities to
strangers (RG-0222).** Probed anonymously, no cookie and no key: the endpoint returned
`from_addr`, `subject` and 600 characters of `draft_reply` for every inbound email. Its own
docstring explained why — *"mirrors /dashboard/summary's no-auth posture (security = obscure
dashboard URL)"* — and it did mirror it, right up until DASH-SUMMARY-REDACT-1 (RG-0211) cut
that sibling to a heartbeat on 30 Aug and left this one behind. Today the queue holds only
test rows carrying David's own address; from tomorrow it is customer mail, which RUL-069's
firewall doctrine exists to keep between the user and the triage AI. An obscure URL is not a
control for personal data. Counts now answer anonymously (the page's tiles need nothing
more); the rows need `X-Admin-Token`/`X-Admin-Key` through `_summary_caller_is_admin` — the
credential the dashboard already holds via `omTok` — and the row list degrades to a sign-in
note rather than breaking (RG-0133). Both loaders (`dashboard.server.html`, which ships, and
the local `dashboard.html`) now attach the token, so RG-0075's drift line holds.
**Evidence:** the real function source lifted out of `bea_main.py` and exercised over a stub
DB seeded with `angry.customer@example.com` — the anonymous payload contained zero of the
three PII strings and `items == []`; the admin payload carried the full row. A live sweep the
same run probed every other unauthenticated `/dashboard/*` route (fixed-costs, bit, presence,
cost, scan, maint) and found no other leaking sibling.

**MAINT-INTAKE-2 — the maintenance brain was reading a door that RUL-040 closed (RG-0223).**
The agent's only intake is `GET /admin/faults?status=new`, fed by the in-app REPORT tab — and
RUL-040 *removes* that tab at soft launch, when customer complaints take over. `/flags` reads
`fault_report=false`, which is correct and deliberate since soft-public opened on 29 Aug. So
every run since has honestly reported "0 seen" while the lane actually carrying customer
complaints — inbound mail → `POST /email/inbound` → `email_triage`, 15 rows — was never
looked at by the brain at all. A loop that reports an empty queue because it is reading a
closed door is worse than one that reports nothing: it manufactures a green day. The agent
now censuses the email lane on every run and says what it holds, in the report and on the
heartbeat. Deliberately a census and not a fix lane — it counts and speaks, it never drafts
or sends; email replies stay behind `EMAIL_AUTO_SEND` and legal/compliance stay excluded.
**Evidence:** the patched agent at 05:43Z printed `email lane 15 total, 1 held (30d {other:1,
support:4})` against the live site.

**LEDGER-PENDING-BUILD-1 — the board was printing an instruction the canon forbids obeying.**
RG-0221 (ZOOM) has reported READY TO LOCK on every run since it was written, because while
the build has not started its harness can only reach the pre-build half — the spec is intact,
the prototypes are on disk — and that half passes on day one. RG-0221's own ref says promote
only *when built*, and extend the assertion to eight shipped-code properties. Obeying the
print would lock the spec-only assertion and retire the strong one: weakening an assertion to
make it pass. Ignoring it daily is worse — it teaches sessions that READY TO LOCK is noise,
and the next real one gets skipped, which is the DW-079 failure arrived at backwards. A
harness that can only reach its pre-build half now says PENDING BUILD, and the runner reads
that as OPEN-with-a-reason, never an invitation to promote. Sibling of LEDGER-FAULT-1, found
the same way: by the board printing something that was wrong.

**Ledger:** green before (after `scripts/maint_deps.py` restored `httpx`/`fastapi`, which had
demoted RG-0181/RG-0182 to NOT EVALUATED and exit 2) and green after — every locked fix
holding, 19 known defects open. Rulings check: 76 checked, 0 FAIL, 0 WARN. Escalation brief:
none written — no escalations in 24h.

**Not deployed.** RG-0222's source half passes and its live half is correctly red until the
change ships; RG-0223's heartbeat half reads PENDING BUILD until `_MAINT_HB_FIELDS` deploys.
Both ride NIGHTLY-SHIP-1. The privacy fix is the one to watch land.
