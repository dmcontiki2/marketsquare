## 2026-10-17 — BUZZ-WHY-1 + the four ledger reds cleared (RG-0189, RG-0264, RG-0344, RG-0403)

David, 19:54 SAST: "we do need to explain it to the users so that understand why they are limited? Please fix all 4 of the failed checks Claude."

- **BUZZ-WHY-1 (RG-1058, LOCKED; first written as RG-1057, renumbered because goal run 42 took RG-1057 on main the same evening):** the Send and Specials panes each carry a one-tap "Why the limits?" line; the Needs-a-subscription note says why service lines are free and specials are paid; every Buzz Board refusal from the server now names its reason (spam leads to muting; specials stay worth opening; an old price never looks current; Buzz is a doorbell, not a chat). Limits themselves unchanged.
- **RG-0189:** `.secrets/deploy_keys.txt.bak-20261017-0345` held three credentials at rest (two duplicated the live file, the third was the retired deploy token). Neutralized in place with a dated note and pre-wipe fingerprint, as RG-0190 did on 2 Sep. Source closed: `rotate_keys.ps1` no longer copies deploy_keys.txt to a local .bak; RG-0189 now also fails if it ever does again.
- **RG-0264:** the 15 LETTER-V2 outreach letters (built 15 Oct) never stated the anonymity. Fixed at the source: `CityLauncher/emailer/build_letters_v2.py` shared layout now carries "You stay anonymous. People see your advert, never your name, number or address, until you decide to accept their introduction." All 15 .v2 letters and previews rebuilt; each differs from before by exactly that line. Nothing was sent.
- **RG-0344:** Email Templates page rebuilt (`scripts/build_email_templates_page.py`); the services_technical_outreach mirror was stale.
- **RG-0403:** CHANNELS-1 (14 Oct) dropped the raw-count label and the funnel's stage chooser. `CityLauncher/dashboard/citylauncher.html` again shows the raw opened/clicked counts as "incl. scanners" chips, and the funnel bars choose their figure through `stageVal()` (graded people for opened/clicked). The assertion was not changed.

Cost model impact: none. Schema: none.
