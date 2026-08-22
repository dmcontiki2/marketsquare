## 2026-08-22 — maintenance-loop (B2b brain, shadow run 05:33Z)

**Quiet run — no faults in the queue, nothing shipped.** Register rows in → gate-passing
commits out; with zero rows in, the honest output is a report, not a change.

- **Fault queue (live, `GET /admin/faults`, X-Maint-Key):** new 0 · triaged 0 ·
  fix-shipped 0 · rejected 0 · verified 26 · closed 7. Nothing to bin, nothing to fix,
  no Path A/Path B routing decisions owed.
- **Shadow agent:** `MS_BEA_URL=https://trustsquare.co python3 scripts/maintenance_agent.py`
  ran in the FOREGROUND (BRAIN-DEPS-2) and completed in ~15 s. Mode
  `SHADOW (kill switch OFF)`, phase postlaunch, trust-core GUARDED, brain KEYED:anthropic.
  0 seen, 0 acted. Report: `.maint_agent/run_20260822T053356Z.json`.
- **Heartbeat PROBED, not assumed:** `GET /dashboard/maint` returns this run —
  `run 2026-08-22T05:33:56Z`, `received_at 2026-08-22T05:34:12Z`, `armed false`,
  `brain_keyed true`. The endpoint now answers ANONYMOUSLY (no ts_review cookie needed),
  so migration 018 is on the box — the task note that it still needs the cookie is stale.
- **Ledger both passes GREEN:** `RESULT: every locked fix is holding. 11 known defect(s)
  still open.` (exit 0) before and after. No LOCKED entry red, so no regression was the
  session's top item.
- **Escalation brief:** `scripts/escalation_brief.py` → "no escalations in the last 24h --
  no brief written". Nothing for David.

### Finding worth the next session's attention — reviewer-lane budget spent by the ADMIN lane (owes a ledger entry)

Not a fault-queue item; found while probing the heartbeat. Stated at its evidence grade.

- **PROBED 05:35Z:** `POST /review/login` with the code in `.secrets/review_code.txt` →
  **429 "Too many failed attempts. Try again in 2m 34s."**
- **PROBED 05:37:57Z:** the SAME code → **200, token minted (151 chars, 365 d)**. So the
  on-disk reviewer code is VALID — the 429 was not a stale credential, and the success
  cleared the counter (ADMIN-NOLOCK-2 change 2 behaving as designed).
- **READ:** `Records/FORENSIC_C1C2_BRIEF.md` lines 92/120 — the concurrent D-7 forensic
  Cycle 2 probed **`/admin/login`** with 7 wrong credentials to a 429, same morning, same
  egress IP. It records no `/review/login` probe.
- **READ:** `bea_main.py` (HEAD and worktree both carry ADMIN-NOLOCK-2) separates the
  buckets — `_review_attempts` for the reviewer lane, its own counter for admin — and
  counts FAILURES only.

**The discrepancy:** a *valid* reviewer code was refused as "too many failed attempts"
while the only recorded failures that morning were on the ADMIN door. If the live box
shared the bucket, RG-0134's separation half has rotted in production even though the
source is right and the ledger's source-side assertion passes green. The innocent
alternative — an unrelated wrong code hit `/review/login` inside that window — is possible
but unevidenced.

**Not settled, and deliberately not settled here.** The decisive probe is: spend one WRONG
credential on `/admin/login`, then immediately present the VALID reviewer code to
`/review/login`; refusal proves a shared bucket. That spends David's admin-door lockout
budget with him absent, which RUL-027 reserves to him — an unattended session must not.

**Owes a regression-ledger entry** (LIVE half of RG-0134: a valid credential in one lane is
never refused for failures in another). NOT written this session: `scripts/regression_ledger.py`
had 201 uncommitted lines from the in-flight forensic session (RG-0142/0143/0144) at 05:35Z,
and appending to a file another session is actively editing is the CHANGELOG-COLLISION-1
failure class. Next session that owns the ledger file should add it.

_Nothing pushed, nothing deployed — NIGHTLY-SHIP-1 owns that lane._
