## 2026-08-26 — Pre-soft-launch third-party sweep: anonymous PII closed at the source, audit CRLF trap removed

Scheduled `pre-soft-launch-third-party-check`, 3 days to soft-public. Verdict **RED**. Probes ran
before any file was read; two files were corrected because a probe overruled them, and two defects
were fixed rather than reported.

**LAUNCH-API-FAILCLOSED-1 — the prospects gate now fails CLOSED** (`CityLauncher/api/server.py`).
PROBED anonymously this run: `GET https://trustsquare.co/launch-api/prospects/list` → **200,
146,226 bytes, 200 records** carrying `name`, `email`, `phone`, `business_name`, `city`, `country`
**and a pre-authenticated `magic_link`** (`/admin.html?magic=1&email=…`). A *bogus* `X-Launch-Key`
returned 200 as well — the gate was not merely unprovisioned, it was failing open **by design**:
LAUNCH-API-LOCK-1 (24 Aug) read `if LAUNCH_API_KEY and x_launch_key != …`, with the comment
"Unset = open with a loud warning (so the deploy does not break dashboards before David provisions
the key)". That trade is wrong: a broken internal dashboard costs one env var; a published prospect
list with entry links is not recoverable. `require_launch_key` now refuses with **403 when the key
is unconfigured**, which is the pattern `database_clear` already used ten lines further down the
same file. Decided and executed under **RUL-037** (CTO lane) — no fork handed over.
*Honest limit: the change is inert until the CityLauncher deploy rides. The exposure is LIVE until
David provisions `LAUNCH_API_KEY` and deploys.* Ledger **RG-0176** · watch **DW-068**.

**CRLF-DRIFT-1 — the audit's daily false drift finding is gone** (`scripts/audit_global_qa.py`).
`audit_drift()` md5'd served bytes against repo bytes; the repo lives on a Windows/FUSE mount and
`ms.js` carries **17,389 CR bytes**, so the compare failed every run. On 26 Aug it cost a live-drift
scare ("live 1156049B != repo 1173438B — a real deploy is staged"). PROVEN this run: delta is
1173438 − 1156049 = **17,389 = exactly the CR count**; raw md5 differs, CR-normalised md5 **matches**.
Both sides are now normalised before hashing and the finding's wording says so, so a future
MSJS-DRIFT means real drift. Raw byte counts still reported, so a genuine size change stays visible.
Same trap the FEA sensor hit in DW-061. Watch **DW-072**.

**Probes (all PROBED unless noted).** `/health` ok v1.3.1 · `/` 200 in 0.47 s · `/auth/providers`
`{google:true, apple:false}` · Google start 302 → accounts.google.com with a real client_id · Apple
start 503 (RUL-030 enforcing) · `/id-verify/status` `available:true`, `price_t:1` · `/payment/test`
`paystack_connected:true` · `/terms` EULA **v1.15** · `/dashboard/bit` **8/8 PASS** · TLS to
**2026-11-22 (88 d)** · CSP on `/` and `/terms` is `frame-ancestors 'self'` only — **no `script-src`,
no `connect-src`** · origin **port 22 unreachable** while `github.com:22` opens from the same shell
(so not a sandbox egress block) · RDAP for trustsquare.co dead on three endpoints, no `whois` binary.
EXECUTED: ledger **exit 1 — 181 entries, 156 holding, 3 REGRESSED, 20 open, 2 UNVERIFIED**;
`rulings_check` **56 / 0 FAIL / 0 WARN**; `eula_sync --check` in sync, 117,749 B.

**Deploy debt re-read, and yesterday's row was wrong.** The 24 Aug register called the debt "3
record-only commits, no app code". Today it is **one commit, `b77cd2b`, and it carries the rewritten
`migrations/033_csp_verify_served.py`** — i.e. the fix for the jammed migration chain (RG-0125,
DW-066) is sitting *in the debt*. Shipping it clears RED #2 and RG-0154 together. Row rewritten.

**Files corrected because a probe disagreed with them:**
- `THIRD_PARTY_LAUNCH_REGISTER.md` — rewritten from evidence: deploy-debt row, ledger/ruling counts
  (167→181, 51→56), Gemini row (key still absent, price corrected), RED list reordered around the
  live PII exposure.
- `OPEN_LOOPS.md` — **B1 (secrets) still sits under 🔴 BLOCKING NOW** while its own text has said
  ROTATION COMPLETE since 23 Aug and RG-0146/RG-0147 are LOCKED and green. Annotated with a dated
  note (additive only — this file has no compiler, CHANGELOG-COLLISION-1 class); it moves to CLOSED
  at the next attended reconciliation.

**Three rows of the scheduled task's own prompt are stale** and were not re-raised: secrets rotation
is not blocking (done 22 Aug), the Resend 422 is the *healthy* auth answer (INFRA-RESEND-1, disproven
22 Aug — there is no outage being masked), and the uptime monitor is built, not unbuilt. Refresh the
task prompt at the next edit.

**Not fixed, and why.** No ledger entry was added for either fix this run: a concurrent attended
session was writing `scripts/regression_ledger.py` minutes before this sweep started (`b77cd2b`,
02:22Z) and a whole-file read-modify-write on the project's most load-bearing instrument is exactly
the collision class CHANGELOG-COLLISION-1 was written about. Both fixes are already tracked by
existing entries — LAUNCH-API-FAILCLOSED-1 by **RG-0176** (its live half is the assertion) and
CRLF-DRIFT-1 by **DW-072**'s close condition — so nothing is untracked, but the CRLF fix deserves
its own entry in the next attended session.
