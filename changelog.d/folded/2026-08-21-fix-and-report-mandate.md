## 2026-08-21 — RUL-036: the fix-and-report mandate, and the open-action queue worked down to two

David: *"I am stuck in the details here... assume the task of resolving the open actions where the
required approval to fix them already directionally agree with our requirements and goals, please
fix those ones and just report the solutions to me; this will then allow me a veto at that point."*

Recorded as **RUL-036** and written into **STANDING_ORDERS.md as SO-3**, so it survives the
session. In scope without asking: any open ledger entry, wrong assertion, unreflected ruling, or
defect that contradicts existing canon — the intended end-state is already written down, so
executing it is not a new decision. Out of scope and still batched to David: deploys, money,
deletions, sending on his behalf, anything that could lock him out (RUL-027), and anything that
would *change* a decision rather than execute one. Declining is allowed; silence is not.

Worked down this session:

- **RG-0077 "regression" was not one.** The 03:56 run reported the EULA body missing from
  terms.html. It exited **3**, which LEDGER-STABLE-1 already defines as "read from a moving
  target — re-run": another writer was mid-file. Re-run clean, anchors intact, body byte-identical
  to eula_clean.html. No fix needed and none invented — the machinery already caught it and the
  session simply had to read its own exit code.
- **RG-0101 LOCKED.** Gzip was live and correct since the 18 Aug deploy; the entry sat OPEN for
  three days because its probe judged `/ops/selfcheck` as a stand-in, and when the gate came down
  `/wonders` became readable while the stand-in stayed 401. Assertion corrected to measure the
  artefact it is named after, with fallback lanes so one gated endpoint can never decide the
  verdict again. Live: `/wonders` = 160,022 B gzipped vs ~485 KB raw.
- **RUL-023 was contradicted by its own canon file.** FINANCE_CANON §4 still read "the model
  budgets R2,000/mo from Year 2" — the exact wording David's 18 Aug ruling overturned. Corrected
  to month-1 engagement, with the assertion now forbidding the old sentence from returning.
- **RUL-025 had nowhere to bite.** `canon.yml` carried `server_eur_month: 15.49` with no hint it
  is grandfathered, so any session costing infrastructure would have read it as the current price.
  Now carries the €35.49 new-order price, the rescale-repricing warning and the CX43 target.
- **RUL-024** reflected against the DB decision record.
- rulings_check: **36 rulings, 0 FAIL, 0 WARN** — the three "note, not a guarantee" warnings are
  gone. Ledger: 120 entries, 0 regressed, 2 open.

**Not done, deliberately — RG-0075** (the admin-gate script duplicated across five files). The
direction is agreed and the fix is a clean extraction to `/static/ts_gate.js`, following the
existing `ts_report.js` pattern. It is held because its failure mode is David locked out of his
own admin and dashboard — the exact class RUL-027 exists to prevent — and it wants a session where
a real login can be tested the moment it lands, not one run while he is at work. First item next
session.

RG-0121 (photo-anon canary) stays open by design: it waits on the Gemini key on the 25th (RUL-032/033).
