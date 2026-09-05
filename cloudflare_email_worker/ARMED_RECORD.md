# CUSTOMER-EMAIL FIREWALL — ARMED

**EMAIL-FIREWALL-1 · RUL-069 (30 Aug 2026) · ledger RG-0212**

```
ARMED_ON:   2026-09-05
VAR:        CUSTOMER_FIREWALL=1
WORKER:     trustsquare-email-triage
VERSION_ID: 7f44030f-d236-4fde-8608-c878d7745dcd
DEPLOYED:   2026-09-05 16:31:46 SAST, via host queue (deploy_email_worker.bat, rc=0)
```

## Why it was armed today

David, 5 Sep 2026: *"Please close that door for me Claude, i appreciate it."* — the explicit
authorisation this ruling had been waiting on since 30 August. It had stayed his act because the
armed worker **rejects mail it cannot triage**, and a mistake there bounces real customers.

## What changed at the edge

Armed (`CUSTOMER_FIREWALL="1"`, set in `wrangler.toml` so it is in git and survives every future
deploy — not a CLI flag somebody has to remember):

- Customer mail is triaged and **never forwarded to a personal inbox**. The dead-letter forward to
  `dmcontiki2@gmail.com` now sits only inside the unarmed branch, which no longer runs.
- Mail that **cannot** be triaged is **rejected at SMTP time**, so the sender's own server tells them
  it failed. A bounce is honest; silent loss is not, and this worker has no storage to hold mail in.
- Escalation reaches David through the admin surfaces — `/admin/email-triage`, the fault queue, the
  escalation brief — never by forwarding a customer's email.

## Pre-flight, because arming can bounce real mail

1. `POST /email/inbound` was proven to accept the worker's **exact payload shape**, including the
   `has_attachments` field the model had never declared (HTTP 200 — an extra field is ignored, not
   rejected). Had it 422'd, arming would have bounced *every* customer email.
2. The bat itself refuses to arm unless `https://trustsquare.co/health` answers **200**. It did
   (`health=200` in the deploy log).
3. **ATTACHMENT-TRUTH-1** shipped first: the firewall ends the forward that used to carry attachment
   mail to a human, so attachment mail is now marked in the record and **held** for the admin queue
   rather than auto-answered without the document.

## Proven after arming

A message sent to `support@trustsquare.co` at 16:33 SAST was **recorded by the triage pipeline**
(`email_triage` row 24) and **did not appear in David's Gmail** — searched and empty. The identical
test before arming (11:54 SAST, "ROUTING TEST 1") *did* land in his inbox. Same path, opposite
outcome, four hours apart.

## To reverse

Set `CUSTOMER_FIREWALL = "0"` in `cloudflare_email_worker/wrangler.toml` and re-run
`deploy_email_worker.bat`. The pre-launch dead-letter forward returns.
