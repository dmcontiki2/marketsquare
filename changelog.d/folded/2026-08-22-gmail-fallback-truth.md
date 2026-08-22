## 2026-08-22 — the Gmail fallback had NEVER worked, and a Google account password was burnt without anyone counting it

Follow-on to the same morning's secret rotation, recorded separately because the finding
outlives the rotation. Supersedes the "leave the Gmail fallback dark" call in that entry —
evidence overtook it inside the hour.

**The fallback had never authenticated once.** David's app-password list at Google was
**empty**, and had always been. The 15-character value the server carried as
`GMAIL_APP_PASSWORD` was his Google **ACCOUNT** password, which Gmail refuses over SMTP —
code 534, "application-specific password required", which is Google saying precisely that.
So every review-link and sign-in email that ever fell through to the SMTP path failed, was
logged, and was swallowed. The lane reported healthy because nothing ever asserted it.

Same class as RG-0143's placebo breaker: **a fallback nobody has exercised is decoration
until it is proven.** And a second lesson with teeth: **a credential named for what it is
supposed to be tells you nothing about what it is.** `GMAIL_APP_PASSWORD` held something
that was not an app password, in a variable read by code that assumed it was, for months.

**Fixed:** a real app password (16 lowercase, Google-generated, named `TrustSquare SMTP
fallback`) created and installed via `install_gmail_password.py`. **PROBED: SMTP LOGIN
ACCEPTED** — the first successful authentication in the app's life. `GMAIL_ADDRESS` is
now set explicitly in the same 0600 drop-in instead of relying on a hardcoded default.

**The exposure nobody counted.** Because that value was his account password, and
`/etc/environment` was mode 0644 and is loaded by the unit via `EnvironmentFile`, his
**Google account password was printed into the DW-057 transcript dump on 20 Aug** along
with the eight credentials that were counted. It was invisible to every review because it
was wearing the wrong name. 2-Step Verification is ON, which is what keeps this out of
emergency territory — the password alone does not grant sign-in. The change is outstanding
and is David's; it is recorded in `SECRETS_REGISTER.md`, not left in a sentence.

**How the session went wrong, recorded so the next one does better.** David said three
times, in different words, that he was using a password he had CHOSEN — "I always start my
gmail passwords with a capital letter and it works". Claude read that as a transcription
slip and sent him back for a cleaner copy three times, when the honest reading was that he
was looking at a different screen entirely. The tell was in the data too: 15 characters
where the format is 16, and an SMTP code that names the exact fault. **When a user's
description of what they are doing conflicts with the assumption, the assumption is what
should be tested first.**
