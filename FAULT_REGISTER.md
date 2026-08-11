# FAULT REGISTER — the Maintenance Agent's memory (B1, 29 Jul 2026)

Every complaint (user email, in-app complaint, or the app's own error log) gets ONE
failure code, joins ONE bin, and increments its recurrence counter. The register is
the dedupe boundary ("50 complaints, one master incident") and the recurrence watch
that triggers Path B design-change dossiers.

## Failure-code taxonomy  (code = BIN-nnn, assigned at triage)
| Bin | Prefix | Covers |
|---|---|---|
| Sign-in & accounts | AUTH- | magic links, sessions, profile, sign-out |
| Listings & adverts | LIST- | create/edit, photos, publish bar, badges, archive |
| Trust & ranking | TRUST- | scores, evidence ledger, tiers, rank order |
| Introductions & payments | INTRO- | requests, accept/decline, Tuppence, Paystack |
| Search & browse | BROWSE- | filters, categories, cards, deep-links |
| Adventures & maps | ADV- | tour maps, country pickers, journey pages |
| Email estate | MAIL- | outreach, transactional, acks, unsubscribe |
| Performance & availability | PERF- | slow loads, timeouts, outages (Pulse feed) |
| Content & copy | COPY- | wrong text, brand, typos (Path A fast lane) |
| Other / unclassified | MISC- | triage could not bin — reviewed at stand-up |

## Register rules
1. New incident → next free code in its bin (e.g. TRUST-004), one row below.
2. Same fault reported again → SAME code, recurrence +1 — never a new row.
3. recurrence ≥ 3 after a shipped fix → automatic Path B design-change dossier.
4. Every fix that closes a code names its deploy + tripwire test in the row.
5. The 21h00 stand-up reads this file; safety/legal/cost rows float to the top.

## Sources (MAINT-B1b, 5 Aug 2026)
| Lane | Where it lands | Reference the reporter sees |
|---|---|---|
| Email (Cloudflare Worker -> /email/inbound) | `email_triage.fault_code` | `BIN-nnn`, in the ACK |
| **In-app tester report (the REPORT tab)** | **`app_faults`** | **`TS-nnnn`, in the ACK; the `BIN-nnn` code is assigned at triage** |
| The app's own error log | (B1, still to wire) | n/a — the app reports itself |

Status ladder for `app_faults`: `new -> triaged -> fixing -> fixed -> verified -> closed`,
plus `rejected` and `duplicate`. NO-RETEST-1 (David, 11 Aug 2026, completes AIK-VERIFY-1
of 5 Aug): **there are no retests.** A complaint is fixed by us, VERIFIED by us on named
machine evidence (reproduced-clean, tripwire, or live probe — named in fix_note), and
CLOSED with a letter telling the reporter what changed
(`/admin/faults/{id}/close-draft` -> David approves -> `close-send`; the send closes and
stamps verified_at). The retest-wait status is retired — legacy rows migrated by
migrations/012. People report; machines verify; the reporter's "still broken" always
reopens — their word outranks our evidence.

## Open incidents
| Code | Opened | Source | Summary | Recur | Status | Fix / tripwire |
|---|---|---|---|---|---|---|
| TRUST-001 | 2026-07-28 | David (tester) | Base-40 missing from seller panel; self-heal wrote base-less scores (40→5) | 3 | CLOSED 29 Jul | _trust_math + test_trust_base40.py (deploy gate) |
| TRUST-002 | 2026-07-28 | David (tester) | LM credential cap drift: ledger 100 vs feed 85 | 2 | CLOSED 29 Jul | LM-uncapped in _trust_math + case/listings-sync heal fixes |
| LIST-001 | 2026-07-29 | David (tester) | Showcase adverts unmarked as SUPER (SO-1) | 1 | CLOSED 29 Jul | one-shot applied + ladder seed; all 9 verified live (banners + ledgers 60/81/96 · 60/80/92 · 90) |
| MAIL-001 | 2026-07-28 | E2E test | Resend 403 — root domain never verified | 1 | CLOSED 28 Jul | FROM → mail.trustsquare.co (canon in LAUNCH_EMAILS.md) |
| PERF-001 | 2026-07-22 | Pulse | Homepage load over 3s (AMBER) | 1 | OPEN | unassigned — candidate for first autonomous fix |
