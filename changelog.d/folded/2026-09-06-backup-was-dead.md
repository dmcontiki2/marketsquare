## 2026-09-06 — the nightly database backup had been dead for two weeks (DW-105, RG-0306)

Found by accident, and the accident is the point. David asked which of his queue items was easiest
to do next; his screenshot of the Cloudflare token list showed two R2 tokens reading *last used —*;
pulling that thread reached `/var/log/r2_backup.log`.

**Fifteen consecutive nights of `ERROR: R2 credentials not found in environment — aborting`.** The
newest database copy anywhere was **30 August**, and even that was incidental — a snapshot a migration
happens to take, not the backup lane doing its job.

**What made it look fine.** A second job at 03:17 ran nightly and logged START then DONE three seconds
later. Genuinely successful — and meaningless: it syncs a **July baseline folder that never changes**,
so the off-site copy was a two-month-old snapshot the entire time. A green that means nothing.

**The cause is a class we have met before.** The 22–23 August rotation deliberately removed these keys
from the box-wide `/etc/environment` and placed them in the systemd drop-in for the marketsquare
service. Correct hardening for the app — and it blinded a **cron** job, which reads neither the service
drop-in nor `/etc/environment`. The app kept working, so nothing looked wrong. That is the same shape as
DW-076, where the same rotation orphaned the Resend watch key. RG-0201 asserts the rotation refreshes
every copy listed in SECRETS_REGISTER's table; this consumer was never in the table.

**Fixed in two places.**

1. The job resolves credentials `env → service drop-in → /etc/environment`. No second copy of the
   secret, no relaxing of the hardening. **Proven by running it under `env -i`, exactly as cron does** —
   both databases uploaded, and the objects are in the bucket (marketsquare.db 2.9 MB,
   citylauncher-prospects.db 4.5 MB).
2. It now publishes `/static/backup_status.json` over plain HTTP, so the backup is observable from
   outside the machine it protects.

**The actual fix is the second one.** New ledger entry **RG-0306** reads that file every run and goes red
if the last success is over 48 hours old, if it reports failure, or if it claims success having uploaded
nothing. The credentials broke in one night; the *silence* lasted two weeks.

**Two bugs in my own fallback, both caught by running it the way cron runs it rather than the way a
shell does.** systemd writes `Environment="KEY=value"` with the quote around the *whole* assignment, so
stripping it from the value alone compared `"KEY` with `KEY` and never matched. And the endpoint was
never in the drop-in at all — only in `/etc/environment` — so two of the three values were still missing
after the first attempt.

**Separately, and it is mine: I exposed two live credentials (DW-106).** Masking a config file for
display, my `sed` was wrong and the full R2 access key and secret printed into the session. Scope is
David's own stored transcript, not a public place, and there is no sign of misuse — but the safe
assumption after any exposure is that the credential is burned. Rotation is his act; raised as its own
item rather than buried inside a backup story. The backup lane now reads the drop-in first, so it will
follow the rotation automatically — and RG-0306 will go red within 48 hours if it does not.
