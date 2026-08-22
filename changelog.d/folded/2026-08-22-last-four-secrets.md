## 2026-08-22 — the last four self-issued credentials, and a false green caught before it was reported

Closes the DW-029 / DW-057 rotation. **Zero credentials remain marked BURNT.**

- **COMMAND_SECRET — DELETED, not rotated.** No reference in the repo, none in the deployed
  code, and the running process never carried it. Rotation would have preserved a thing with
  no purpose; a burnt secret nothing reads is pure liability.
- **MS_DEPLOY_TOKEN** — minted fresh server-side (e205259d → 76b30e21), local copy updated in
  the same run.
- **RELAY_INBOUND_SECRET** (b454baa6 → 16bbb094) and **EMAIL_INBOUND_SECRET** (→ 66ead77c),
  both pasted into their Cloudflare Workers.

### Two tooling faults this exposed, both mine

**A variable must be placed where THE CODE reads it.** `EMAIL_INBOUND_SECRET` is read by a
plain module-level `os.getenv()` (process env only); `RELAY_INBOUND_SECRET` goes through
`ai_provider.envkey()` (process env OR the app `.env`). The first pass wrote email to `.env`,
where its reader never looks, and skipped relay entirely as "not set" because the check only
consulted the process environment. Four attempts, three different values live in three files
at once, and the 2-minute autodeploy timer restarting the service underneath. Resolved by
abandoning precedence reasoning altogether: **one value written to EVERY location** — drop-in,
`/etc/environment` and the app `.env` — so whichever systemd prefers, they agree.

**A verification that cannot fail is not a verification.** The first inbound-auth probe sent a
payload FastAPI rejected at validation, so every call returned **422 before the auth check ran** —
and the checker counted any non-401 as "accepted". It would have reported a confident green
without ever testing the secret. David caught the class before the run: *"We have seen many
things today which has been assumed as ok for months, with nothing there?"* Rewritten to send
schema-valid payloads, and the result is real: `/email/inbound` answers **401 'Invalid inbound
secret'** rather than the **503** the code returns when the variable is empty — proof the secret
is loaded and compared.

**Stated at its true grade, not rounded up:** the relay door answers 401 for a wrong secret AND
for an empty one, so its server half is READ-grade (process fingerprint), not PROBED. And no
check run from our side can prove the Worker halves match — only real inbound mail can. Recorded
as a limit rather than papered over.

### Also surfaced, not yet fixed

`demand.conf:5` carries `Environment=<...@mail.trustsquare.co>` with no variable name. systemd
reports "Invalid environment assignment, ignoring" — so whatever mail-from setting that was
meant to be has never taken effect. Found by running `systemd-analyze verify` in passing.
