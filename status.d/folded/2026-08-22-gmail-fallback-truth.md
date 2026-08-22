## 2026-08-22 — Gmail fallback proven for the first time; an uncounted exposure found

The SMTP fallback had NEVER authenticated: the stored `GMAIL_APP_PASSWORD` was David's
Google ACCOUNT password (15 chars, Gmail 534), and the account had no app passwords at all.
A real one was created and installed — **PROBED: SMTP LOGIN ACCEPTED**, first success ever.

Consequence worth carrying: that account password sat in `/etc/environment` (0644) and was
therefore printed into the DW-057 transcript dump on 20 Aug — an exposure no review counted,
because the variable name said "app password". 2FA is on; the account password change is
outstanding and is David's. Recorded in `SECRETS_REGISTER.md`.
