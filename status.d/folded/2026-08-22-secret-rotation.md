## 2026-08-22 — secret rotation (attended, DW-029 / DW-057)

Nine credentials rotated and PROBED: the five self-issued via `ROTATE_SECRETS.bat`, plus
RESEND_API_KEY (422 auth), PAYSTACK_SECRET_KEY + PAYSTACK_WEBHOOK_SECRET (200 auth — one
credential, not two) and MS_JWT_SECRET (fingerprint changed, /health 200, reviewer cookie
re-minted).

Two structural defects fixed: `/etc/environment` was 0644 world-readable holding nine live
secrets (now 0600, with `msdeploy` confirmed as a real potential reader), and a correct
rotation reported success while the running process still held the revoked Paystack key —
card payments were down with nothing reporting it. Both now have assertions (RG-0146 OPEN,
RG-0147 LOCKED) and a `SECRETS_REGISTER.md` that names all 22 credentials with dated status.

The DW-029/DW-057 exposure list was incomplete: it named eight credentials, the same
environment dump printed nine more.

Gmail SMTP fallback deliberately left dark — Resend is the proven primary sender, and the
fallback should not return as a personal Gmail account.

**NOT finished — ten credentials still BURNT**, including both Hetzner S3 keys (backup
read/delete) and ANTHROPIC_API_KEY. RG-0146 stays red until they are done. Reserved to
David: the vendor dashboards, the Google account password change, and the FOUNDERS_ID_SALT
decision.
