## 2026-10-18 -- BUG-AUDIT-1016 follow-up: send a held support reply from the dashboard (cloud lane, with David)

- **HELD-REPLY-SEND-1** (bea_main.py POST /dashboard/email-triage/{tid}/send; dashboard.server.html loadEmailTriage + sendHeldReply;
  scripts/regression_ledger.py RG-1029; BA-035) -- David, 18 Oct: "Please add the button Claude, support should not go through my
  inbox." A reply the support agent holds back (or fails to send) now shows on the Ops Dashboard as an editable box with a Send reply
  button. It leaves from the support address with Reply-To support@, so the sender's answer comes back to the support agent, never
  to David's mailbox (RUL-069). Admin only (the page's existing credential); the row is claimed atomically (drafted/failed ->
  sending) so a double click or two open dashboards cannot send twice; a failed send returns the row to 'failed' with the text kept.
  The triage feed now returns the whole draft for waiting rows (the 600-character preview stays for the rest), so the button sends
  exactly what is shown.
