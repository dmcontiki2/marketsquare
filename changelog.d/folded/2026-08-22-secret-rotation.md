## 2026-08-22 — SECRET ROTATION: nine credentials replaced, and the exposure register found to have been under-counting for fifteen days

David drove the DW-029 / DW-057 rotation attended, one step at a time. Nine credentials
rotated and PROBED, two structural defects found and fixed, one credential class
deliberately left dark, and the inventory given machinery so the count can never drift again.

### Rotated and proven (not "written" — proven at the point of use)

`ROTATE_SECRETS.bat` did the five self-issued ones (MS_ADMIN_KEY, MS_DEPLOY_KEY,
MS_MAINT_KEY, MS_ADMIN_PASSWORD, LAUNCH_CODE_SECRET) and moved them out of inline
`Environment=` lines into `/etc/marketsquare/secrets.env` (0600) — the structural half of
the fix, since `systemctl cat` printing them is how they leaked.

- **RESEND_API_KEY** — new key installed, both old keys deleted at Resend. PROBED: the
  empty-body send probe returns **422** (auth passed, nothing sent).
- **PAYSTACK_SECRET_KEY / PAYSTACK_WEBHOOK_SECRET** — found to be the SAME credential:
  Paystack signs webhooks with the live secret key. So the burnt value was not
  "someone could forge a webhook", it was a credential that can charge cards and move
  money. Rolled and installed. PROBED: `GET /transaction/totals` returns **200**.
- **MS_JWT_SECRET** — never in `rotate_secrets.py`'s set, and it signs every auth token
  the app issues: holding it means forging an admin JWT. Rotated
  (`ec305410` → `7fc37454`), moved out of the box-wide file into `secrets.env`, with
  automatic rollback armed. `/health` 200 after restart; the reviewer cookie was
  re-minted in the same session because rotation invalidates it.

### Two structural defects, both found by probing rather than reading

**1. `/etc/environment` was mode 0644 — world-readable — holding nine live secrets.**
`HETZNER_S3_ACCESS_KEY`, `HETZNER_S3_SECRET_KEY`, `ANTHROPIC_API_KEY`, `COMMAND_SECRET`,
`EMAIL_INBOUND_SECRET`, `GMAIL_APP_PASSWORD`, `MS_JWT_SECRET` and both Paystack values.
The `msdeploy` account has a login shell, so the reader was real, not theoretical. Now
0600, with `MS_JWT_SECRET` and `GMAIL_APP_PASSWORD` removed from it entirely.
**The exposure inventory in DW-029/DW-057 listed eight credentials; the same
`systemctl show -p Environment` dump printed these nine too.** The register had been
under-counting the leak for fifteen days.

**2. The Paystack rotation reported success while production was down.** The new key was
written to a correct 0600 drop-in, the service restarted and reported `active` — and the
RUNNING PROCESS still held the old, just-revoked key, because `/etc/environment` is loaded
via `EnvironmentFile` and won on precedence. Disk said rotated, Paystack said 401, card
payments were down and nothing reported it. Fixed by `scripts/fix_paystack_env.py`, which
walks the unit, every drop-in, every referenced `EnvironmentFile` and the known env files,
puts them all on one value, and reads back from `/proc/<pid>/environ`.

### Left dark on purpose: the Gmail SMTP fallback

`GMAIL_APP_PASSWORD` is REMOVED, not rotated. The fallback sends sign-in links from a
personal Gmail account, which is a deliverability and blast-radius problem independent of
today's leak. Resend is the primary sender and is proven, and the code degrades honestly
(it logs and drafts rather than pretending to send). Restoring a fallback is a
post-rotation job and should not come back as a personal account. `GMAIL_ADDRESS` was
restored explicitly to the drop-in so the app stops depending on a hardcoded default.

**Incident inside the rotation, recorded because it cost real risk:** David pasted his
Google ACCOUNT password (not an app password) three times — the tell was there in his own
words (chosen by him, starts with a capital, 15 characters) and Claude read it as a
transcription slip for three round trips instead of asking what screen he was reading.
SMTP code 534 was Google saying "that is an account password" the whole time. The value
reached the server and was passed as a command-line argument, briefly visible in the
process list to `msdeploy`. Purged from the drop-in and from root's shell history
(`scripts/purge_gmail_password.py`); changing the Google account password is David's call
and is recorded in the register.

### New machinery

- **`SECRETS_REGISTER.md`** — every credential, its holder, its status
  (ROTATED / BURNT / REMOVED / PUBLIC / UNKNOWN) and a dated verification. Ten are still
  BURNT and say so.
- **RG-0146 (OPEN)** — the register is current and nothing in it is still BURNT. Honestly
  red today; it goes green when the remaining ten are done.
- **RG-0147 (LOCKED, 22 Aug)** — a credential is verified where it is USED, never from the
  file it was written to. Born from the Paystack outage above.
- Tooling, all logging to files Claude reads directly so nothing depends on David pasting
  a window that may close: `fix_paystack_env.py`, `rotate_jwt_secret.py`,
  `audit_env_file.sh`, `check_email_keys.sh`, `check_resend_live.sh`, `diag_gmail.py`,
  `install_gmail_password.py`, `purge_gmail_password.py`.

### Still burnt — the rotation is NOT finished

`HETZNER_S3_ACCESS_KEY` + `HETZNER_S3_SECRET_KEY` (read AND delete your backups),
`ANTHROPIC_API_KEY`, `CF_CACHE_TOKEN`, `COMMAND_SECRET`, `EMAIL_INBOUND_SECRET`,
`RELAY_INBOUND_SECRET`, `TRAVELPAYOUTS_TOKEN`, `NUMISTA`/`JUSTTCG`, and `MS_DEPLOY_TOKEN`
(status UNKNOWN). `FOUNDERS_ID_SALT` needs a decision — rotating it invalidates every
existing ID hash. `MS_API_KEY` is public by design and needs nothing.

Ledger after the session: **no regressions**; every LOCKED fix holding.
