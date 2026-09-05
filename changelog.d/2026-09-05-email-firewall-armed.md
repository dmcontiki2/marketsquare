## 2026-09-05 — EMAIL-FIREWALL-1 ARMED: no customer mail reaches the personal inbox by any route (DW-103, RG-0212)

**David, 5 Sep:** *"Please close that door for me Claude, i appreciate it."* — the explicit
authorisation RUL-069 had been waiting on since 30 August.

It stayed his act for six days for a good reason: the armed worker **rejects mail it cannot triage**,
so a mistake here bounces real customers rather than merely inconveniencing us.

**Armed:** worker `trustsquare-email-triage`, version `7f44030f-d236-4fde-8608-c878d7745dcd`, deployed
16:31:46 SAST through the host queue. `CUSTOMER_FIREWALL = "1"` lives in `wrangler.toml`, **in git** —
not as a command-line flag. That is this morning's stale-`LAST_HEARTBEAT` lesson applied the same day: a
setting that depends on what somebody last typed is a memory, not a setting. A deploy from a clean
checkout now comes up armed.

**Three pre-flights, because arming can bounce real customers.**

1. `/email/inbound` was proven to accept the worker's **exact payload**, including the
   `has_attachments` field the Pydantic model had never declared. Extra fields are ignored, not
   rejected — had it returned 422, arming would have bounced **every** customer email.
2. The deploy bat refuses to arm unless `/health` answers 200. It logged `health=200` before proceeding.
3. **ATTACHMENT-TRUTH-1 shipped first.** The firewall ends the forward that used to carry attachment
   mail to a human mailbox. So attachment mail is now marked in the record and **held** for the admin
   queue rather than auto-answered without the document the sender actually attached. The worker had
   been sending `has_attachments` since 30 August and the app had been silently dropping it.

**Proven after arming, with a before/after four hours apart.** A message to support@ was recorded by the
pipeline (`email_triage` row 24) and **did not appear in David's Gmail** — searched, empty. The
identical test at 11:54 the same morning *did* land in his inbox. Same path, opposite outcome.

**The first attempt failed safely, and that is worth recording.** The bat died `rc=255` on a cmd parse
error — *"--- was unexpected at this time"* — because an `echo` inside a parenthesised `if` block
contained literal parentheses, which closes the block early. **Nothing was deployed**, verified by
grepping the deploy log for any upload, so the failure cost nothing but a cycle. Rewritten with `goto`
labels, which cannot be broken that way — this bat runs unattended, where a parse error is a silent
no-op.

**RG-0212 promoted OPEN → LOCKED**, and strengthened while promoting: it now asserts `wrangler.toml`
carries the var, not merely that a record file says somebody once typed a command.

**Reversal is one line:** set `CUSTOMER_FIREWALL = "0"` and re-run `deploy_email_worker.bat`.

**Both doors are now closed.** The in-app support form goes to the AI lane (SUPPORT-AI-LANE-1, RUL-102,
earlier today); inbound email to support@ is triaged and never forwarded. Legal and compliance are still
held for David in `/admin/email-triage` — that gate is not what today relaxed.
