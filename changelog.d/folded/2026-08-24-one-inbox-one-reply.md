## 2026-08-24 — ONE-INBOX-1 + ONE-REPLY-1: customer email E2E-tested; personal-inbox routing and double-reply fixed

- Live E2E test (David's ask): mail to support@ triaged in <5s — classified, fault ref
  minted, branded reply from support@mail.trustsquare.co. billing@ test proved catch-all ON.
  Deployed user-visible surfaces carry ZERO personal addresses (support/legal/compliance/
  admin/billing/hello@trustsquare.co only).
- Two faults found and fixed on disk: (1) CF worker forwarded EVERY inbound to David's
  personal Gmail — now a dead-letter lane only (fires only when BEA triage unreachable, so
  nothing can be lost); (2) one complaint got TWO conflicting auto-replies (classifier draft
  + MAINT-B1 ack) — email_inbound now persists first and sends ONE reply carrying the fault
  reference; bare ack only when no auto-reply is safe. Reply-To support@trustsquare.co added
  to the shared transactional transport (signin/invite lanes, both Resend and Gmail paths).
- RG-0174 OPEN: promotes after app /ship + `wrangler deploy` of the worker + clean E2E
  re-test (one reply, no personal-inbox copy). Ops alert mail TO David (alert_email) is
  intentional and untouched.
