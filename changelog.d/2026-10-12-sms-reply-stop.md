## 2026-10-12 — "Reply STOP" now reaches us; the SMS wave runs itself from the server (SMS-REPLY-1, RUL-226)

David, 12 Oct 2026, on the SMS wave readiness board: *"G5 pilot go - approved"*, *"Agreed"* (cap 40 -> 200 after a clean
48 h read), *"Yes"* (casuals search plan), and *"Make 'Reply STOP' true"*.

- **SMS-REPLY-1 (sms_provider.py):** every BulkSMS text now goes from BulkSMS's reply number (`from: {type: REPLIABLE}`).
  Before, no sender was set, so whether a reply reached us depended on an account setting nobody had checked. New
  `received()` reads the replies (read-only, no cost). Proven: a REPLIABLE send to BulkSMS's free test number answered
  201 at 0 credits; `received()` answered 200 on the live account.
- **CityLauncher (same evening, its own deploy):** the daytime wave runs on the server only (Mon-Sat 09:10 SAST) and only
  while an ARM file holds David's words; replies are read before every send (a STOP stops that number and her e-mail);
  the 48 h reading rule is applied by machine; the Gumtree pool was refreshed from the city's own shelf. Details in
  CityLauncher/CHANGELOG.md and STATUS.md.
- Regression ledger RG-0969; rulings_check RUL-226.
