## 2026-08-27 — Third-party sweep, 2 days out: three REDs closed on probes, deploy debt zero, and an instrument that was blaming the network

**PRESOFT-SWEEP-27AUG** · scheduled task `pre-soft-launch-third-party-check` · last ship day before soft-public (Fri 29 Aug, RUL-001)

Verdict held at **AMBER**, but the composition of it changed completely. Nothing left on the RED
list is code — every remaining item is a click, a key or a login.

### Closed on live probes, not on a file

- **The migration chain is UNJAMMED.** `/static/post_deploy_status.json` now reads
  `generated_at 2026-08-27T03:46:59Z` · seed ok · ladder_seed ok · **migrations ok, "none pending"**.
  RG-0125 `[ ok ]`. Yesterday it was the only real ledger red on the board.
- **A full `script-src` CSP is enforced at the edge**, on `/` **and** `/terms`. RG-0178 promoted to
  LOCKED. **Yesterday's CTO note hypothesised a Cloudflare-edge emitter — that is now DISPROVEN**;
  the emitter was nginx all along and migration 033 had been measuring the port-80 301 redirect.
  Recorded explicitly, because a hypothesis that outlives the probe that killed it is the next
  session's wrong turn.
- **Deploy debt is ZERO for the first time in this register's life.** `origin/deploy` = `2341ab6`
  (27 Aug 05:45 SAST); `git log origin/deploy..HEAD` = 0 commits. Both of yesterday's unpublished
  commits have ridden. Also closed: RG-0156 (orchestrator) and RG-0160 (dossier PDFs).
- **The Hetzner firewall self-heal is ARMED** — `.secrets/hetzner_token.txt` is populated and
  RG-0188 reads `[ ok ]`. Yesterday it exited "NO TOKEN, nothing changed".

### LEDGER-UNVER-CAUSE-1 — the ledger stopped blaming the network for a missing library

Found by being bitten by it in this run's first command. The `NOT EVALUATED` summary asserted,
unconditionally, *"this machine cannot reach https://trustsquare.co"* — and printed exactly that on
a run whose two UNVERIFIED entries were **`fastapi` dependency demotions**, on a machine that was
curling the site fine in the same minute. RG-0187 demoted them honestly; the *summary* then named
the wrong cause, which is the RG-0117 mistake one layer up: it sends the next session to fix the
wrong thing, and "re-run somewhere with a route to the site" is advice that cannot work.

The summary now reads the recorded reason back off each UNVERIFIED entry, names the entry ids, and
states the network verdict from the **measured** `_NET` preflight rather than from assumption.
Proven both ways in the same run: with `fastapi` blocked it prints the real cause plus *"This
machine CAN reach https://trustsquare.co, so the site is not the cause"*; with it present the board
is clean. **Asserted by an extension to RG-0187's scope** — demoting honestly is only half the job;
describing the limit accurately is the other half, and a fix without an assertion is half a fix.

### RG-0198 opened — the other half of the dashboard leak

`GET /dashboard/summary` answers an anonymous stranger with `redacted: "posture"`, so RG-0144's
security half is genuinely fixed. Beside it the same 1,360-byte payload still carries today's
internal engineering changelog verbatim (headline included), the session number, live counts, and a
`priorityItems` list whose first entry begins *"**DAVID — DEPLOY the 22 Aug work.**"*

Split into its own entry rather than folded into RG-0144, deliberately: one is a reconnaissance
control and the other is confidentiality, and a single assertion covering both would go green the
moment either half passed. **Not fixed this run, with the reason on the record instead of in
someone's head:** POSTURE-REDACT-1's own comment states both operator dashboards fetch this
endpoint with no credential and that "a fix that breaks the console will be reverted under
pressure". The honest fix is two-sided (consoles send the admin key; the anonymous payload keeps
its operational fields and withholds the narrative ones) and the second side cannot be verified
from this vantage. Quietly changing a live endpoint the operator console reads, on the last ship
day before a launch weekend, is how a console goes dark unwatched. Filed as machinery per RUL-037.

### Two instruments corrected for telling a session something untrue about themselves

- **RG-0144 promoted OPEN → LOCKED** (DW-079) — it was printing `READY TO LOCK`, and a fix that
  prints READY TO LOCK and is never promoted cannot trip red when it rots.
- **RG-0192 stopped printing `READY TO LOCK` while LOCKED** (DW-080) — now reads `holding -- …`.

### One misread corrected before it could be raised a third time

`bit_flags.auth_fail_closed: false` was flagged on 26 Aug as "worth one look before public
traffic". It is a **narrowing switch**, not the base auth control (`bea_main.py:155`:
*"when auth_fail_closed is ON the admin surface narrows to…"*; `ops/bit/bit_mitigator.py` lists it
as a SAFE mitigator flag bound to `B-NEG-AUTH`). The control itself is already fail-closed and
proven live — today's `/dashboard/bit` reports `B-NEG-AUTH` (S1) = **PASS, HTTP 401**.

Also retired: RDAP for `.co` was **not re-attempted**. Five endpoints across four sweeps plus an
IANA bootstrap with no `.co` service is a settled negative; the sweep stops paying for it.

### Ledger and rulings

`regression_ledger.py` exit **0** — 191 entries · 177 holding · **0 REGRESSED** · 14 open ·
0 READY TO LOCK · 0 UNVERIFIED. `rulings_check.py` — 58 rulings, 0 FAIL, 0 WARN.
`eula_sync.py --check` — in sync, 117,749 B, `/terms` serving v1.15.

### What is left, and it is all David's

External uptime watcher still undeployed (**day 5**, RG-0138, 3 commands) · the RED-alert Resend
key in `/etc/marketsquare/resend.watch.conf` still dead (**day 3**, DW-076) · Google consent screen
Published-or-Testing unrecorded (RG-0139) · domain registrar/expiry/auto-renew unrecorded (RG-0137).
