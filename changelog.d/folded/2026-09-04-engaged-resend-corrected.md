## 2026-09-04 — ENGAGED-RESEND-1 corrected: the roster came from the wrong column

The apology lane ran, exited 0, and mailed **18 people when 140 qualified**. Nothing
errored. The pull ran and worked. The lane simply asked the wrong question.

`prospects.status` is a SEND-STATE machine, not an engagement record. `pull_from_server.py`
carries opens and clicks down into `email_events` and **deliberately never writes them back
over send history** — its own comment says "never rewrite send history, only stop future
sends". So `status='opened'` held 18 stale rows from an old wave while `email_events` held
**157 engaged people**. Selecting on the column reached the wrong 18.

**My own assertion passed on the wrong thing.** RG-0265 leg (a) checked that the pull
PRECEDED the pick — which was true — and never checked that the pick read what the pull had
delivered. *An ordering assertion is not an outcome assertion.* That is the transferable
lesson from today, and it is the second time in one session the same shape appeared: a run
that completes, returns 0, and did not do the thing (WAIT-REDIR-1 was the first).

Corrected: the roster now comes from `email_events` (opened or clicked), restricted to
still-mailable states. **NEVER-TWICE-1** added at the same time — the lane had no memory, so
running unattended it would apologise to the same people on every tick. It now reads the
sent log and excludes anyone already contacted by *either* follow-up lane
(`CTA-URL-1-relink`, `HUMAN-CLICKS-1-followup`), and **fails closed** if the log cannot be
read rather than risk a second apology.

Roster after correction: 140 engaged, minus 29 already followed up, **111 to send**. The 18
already contacted are excluded by the new guard and will not hear from us twice.
RG-0265 leg (b) now demands the roster be built from the evidence table, so this exact miss
trips the board red rather than passing quietly.
