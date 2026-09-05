## 2026-09-05 — SELF-REPLY-GUARD-1: the support AI was answering our own robot (DW-101)

Found within the hour it was created, while answering David's question about who handles complaints.

**What is actually live** (PROBED from the running process env, not read off the code):
`support@trustsquare.co` is AI-triaged with `EMAIL_AUTO_SEND=1`. Categories **support** and **billing**
are auto-answered; **legal** and **compliance** are drafted and held for David. That part of the design
works and has worked since May — `email_triage` carries a real "Complaint of fraudulent seller" held as
*legal*, and a "How do I contact a seller?" auto-answered as *support*.

**The fault.** SUPPORT-FORM-REAL-1, shipped 90 minutes earlier, notified that same mailbox whenever
somebody used the support form. So the app's own notification arrived from
`010201…@send.mail.trustsquare.co`, Claude classified it as a customer support message, and **auto-sent
a reply to a bounce address**. Observed, not theorised: `email_triage` row 18 — category `support`,
status `sent`, draft opening *"Thanks for testing the TrustSquare support form."*

Harmless that once, because the recipient was a return-path. The shape is not: an autoresponder whose
input queue can receive its own output is one bad classification away from a loop, and every such
message costs an AI call and a send.

**Fixed in both places, deliberately.**
- **Cause** — the support form now notifies David's inbox directly rather than the triaged address, so
  system mail never enters the customer lane. He still reads it in the same inbox `support@` forwards
  to, so it remains one inbox.
- **Class** — `_is_own_system_mail()` refuses auto-send for any sender on our own domain or a subdomain
  of it. Domain-anchored, never substring: `evil-trustsquare.co` is deliberately not us (unit-checked
  over 7 cases). The mail is still stored and visible with status `system`, because a guard that
  silently drops mail is its own blind spot.

**Proved after deploy:** a further support-form submission (TS-0038) left `email_triage` unchanged at 19
rows, where the two earlier ones had each created one. Locked as **RG-0285**, which checks the guard
actually gates the send decision rather than merely existing.

**Also done:** the three internal test rows (TS-0036/0037/0038) were closed via the maintenance
credential — no closure letters sent — and the fault queue is back to **0 new**.

**Worth recording for the next session, because it is the honest state of the design:** the AI *email*
lane is armed and working. The AI *fix-agent* (`scripts/maintenance_agent.py`) is **not** — the live
heartbeat reads `mode: SHADOW (kill switch OFF — default, cannot commit), armed: false, live: false`.
That is the deliberate default and arming it is David's single lever. So messages arriving through the
support FORM land in `app_faults`, where no armed agent works them; they wait for a human.
