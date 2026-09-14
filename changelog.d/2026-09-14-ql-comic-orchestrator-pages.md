## 2026-09-14 — The comic and the email strip as two Orchestrator pages, and the email switch

**David:** "add these two visuals inside the Ops Dashboard in the Orchestrator tab as a separate
2 pages" and "update the emails for all of the categories".

**Dashboard — done and shipped.** The Quick Listing view now carries a three-page rail, each page a
real standalone page under the Orchestrator sign-in:

| page | served | source |
|---|---|---|
| Flow board | /orchestrator/quick_listing.html | genie/QUICK_LISTING_ORCH.html |
| The comic, all eight categories | /orchestrator/quick_comic.html | genie/EMAIL_TO_TWO_USERS.html |
| The emails, three panels each | /orchestrator/quick_emails.html | genie/email_strip/ORCH_PREVIEW.html |

`qlPage()` sits at top level (the first attempt nested it inside `switchView`, where the inline
`onclick` could not see it — caught by driving the rendered page, not by reading the diff). The
heading, the blurb and the open-full-page link follow the chosen page, and the view remembers which
page you were on. 26 manifest rows added: the two pages plus the 24 strip images to
`orchestrator/qstrip/`.

**Emails — built, and deliberately NOT armed.** `CityLauncher/emailer/apply_qstrip.py` inserts the
three-panel strip into 14 letters across all seven lettered categories, keeping a timestamped backup
of each, with `--off` to revert. It REFUSES to arm while the front door is missing, and today it is:

    trustsquare.co/q/homehelp … /q/adventures  →  404, all seven (PROBED 14 Sep, browser UA)

The strip shows the Quick Listing screens and its button points at `/q/<category>`. The Quick Listing
is harness-only — not deployed, phase two, deferred. Putting those pictures in a live letter would
spend our one click on a door that is not there, so the guard is machinery rather than a note: the day
`/q/` answers 200, `python3 apply_qstrip.py --on` arms all fourteen.

**The decision that is David's:** ship the Quick Listing front door. Everything else is ready for it.
