## 2026-08-26 — Third-party sweep, second pass: three "do not deploy" reds were the instrument, not the app

**SWEEP-26AUG-2** · commit `da85045` · 3 days to soft launch (Fri 29 Aug, RUL-001)

The pre-soft-launch third-party sweep ran a second time today (the 02:5x pass and the 06:30 daily
watch preceded it). It re-PROBED their third-party rows independently rather than reading them, and
found that **four of the ledger's REGRESSED entries were three false alarms and one real one**.
That matters more than the count: a REGRESSION prints *"Do not deploy over this"*, and the last ship
day is Wed 27 Aug. Three false reds two days out is a deploy that does not happen.

### LEDGER-VANTAGE-1 — RG-0099 (SSH lockout detector)

Port 22 at the origin was demonstrably **OPEN** — 8/8 probes, 0.48 s, banner
`SSH-2.0-OpenSSH_9.6p1` — at the same minute two consecutive full ledger runs called it a
REGRESSION. Calling the entry's own function standalone returned *"both management lanes clear"*.
LEDGER-FLAP-1 (19 Aug) had already widened this probe to 3 tries × 8 s for a dropped packet; the
failure is not a dropped packet, it is this vantage's port-22 lane under full-run load.

A **control probe** (`github.com:22`, `gitlab.com:22`) now runs before the verdict:

- origin dead **+ control dead** → `NOT EVALUATED` → UNVERIFIED. The run measured its own socket
  lane and says nothing whatsoever about the Hetzner firewall.
- origin dead **+ control alive** → still **RED**, still naming the runbook line.

The assertion is not weakened — a genuine lockout still fails the origin while control hosts answer.
Same family as LEDGER-DEPS-1/RG-0187 and RG-0186: *an instrument that cannot see the subject has not
measured it.*

### HARNESS-TMPDIR-1 — RG-0182 (indicative-fare lane)

`scripts/prove_fares_lane.py` hardcoded `/tmp/prove_fares.db` and swallowed `OSError` on cleanup.
A previous run had left that exact path owned by `nobody:nogroup`, so the remove failed **silently**,
sqlite opened the stale file read-only, and the harness died with *"attempt to write a readonly
database"* — which the ledger read as *"RG-0182 has come back"*. `mkdtemp` per run cannot collide,
honours `TMPDIR`, and needs no cleanup guard to be correct. Same treatment for `data_flights.py`'s
selftest. **13/13 passing.** RG-0181 was the plain missing-`fastapi` case RG-0187 was written for —
installed, **9/9**, every refusal refusing.

### CSP-VERIFY-GUARD-3 — RG-0186 (migration proof method)

The guard matched the call site spelled `served_csp()` **with empty parens**, and went red the
moment 033 legitimately grew an argument (`served_csp(settle=15)`, added by CSP-SCRIPT-SRC-5 so the
probe stops racing nginx's asynchronous reload). This is the **third** cut of one mistake — the two
earlier ones matched the prose *"Not claiming success"* — and the file's own comment already warns
that a guard matching wording rather than behaviour breaks the moment someone re-wraps a line. This
cut matched a *spelling*. Now matches `served_csp(`.

### RG-0176 promoted OPEN → LOCKED

The ledger had been printing `>>> now passing — change state to LOCKED` and nobody had promoted it.
Re-probed independently first: anonymous `GET /launch-api/prospects/list` answers **HTTP 401**, where
at 04:20 the same morning it served **146,226 bytes of prospect PII plus pre-authenticated
`admin.html?magic=1&…` entry URLs**. A fix that prints READY TO LOCK and is never promoted cannot
trip red when it rots — which is the precise failure the ledger exists to prevent. The n8n
cross-store suppression half is still proven only by hand and is named in the scope rather than left
to weaken the assertion.

### SECRETS_REGISTER.md — a new "Out-of-band copies" table

The daily watch tried to send a real RED alert this morning and Resend answered
`401 "API key is invalid"`. The watch's key in `/etc/marketsquare/resend.watch.conf` (mtime
**5 Aug**) was orphaned by the 22–23 Aug rotation, which deleted both old keys — and **nothing
noticed for four days**, because only a real RED exercises that path and the register knew only the
app's copy in `secrets.env`. Every second copy of a rotated credential now has a row, with the rule
that **a rotation is not finished until every row carrying that credential is updated and
re-probed**. Pasting the current key in is David's (root on the box) — DW-076.

### Board

**183 entries · 165 holding · 1 REGRESSED · 17 open · 0 UNVERIFIED** (opened at 4 REGRESSED +
2 UNVERIFIED). The survivor is **RG-0125** — `migrations/033` failed on the 04:05:08Z deploy and
jammed the chain — and it is blocked on a deploy, not on work: the fix rides in `97f8168`, still
unpublished. `rulings_check.py` 56/56, `eula_sync.py --check` in sync (117,749 B, v1.15).

**CTO note recorded for the next session:** if 033 goes `ok` on the next deploy but RG-0178 stays
red, the CSP header is being emitted at the **Cloudflare edge**, not by nginx — 033 verifies at the
origin and cannot see a Transform Rule. That cannot be discriminated from a sandbox vantage, because
the origin's :443 accepts only Cloudflare IPs.

**RDAP for `.co` is now recorded as permanently machine-unanswerable** — five endpoints, four
sweeps, and an IANA bootstrap listing no `.co` service. The four `DOMAIN_*` fields need one glance
at the registrar login, not another sweep.
