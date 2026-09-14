## 2026-09-14 — The Quick Listing flow, as one comic engine for all eight categories

**What was asked.** A comic-book flow of the phone screens, end to end from an email send-out: the
email arriving, choosing housekeeping, onboarding her employer, the two streams, her listing, and
both sides using the comms. Then: should there be one per email type, and does it go in the email?

**What was built.**
- `genie/build_comic.py` — reads `genie/HARNESS.html` directly (CATS, COMMS, and a faithful port of
  the listing scorer) and writes `genie/EMAIL_TO_TWO_USERS.html`, sixteen panels for each of the eight
  categories from one renderer. Styling in `genie/comic.css`. Verified on David's own Python: the
  rebuild reproduces the page exactly (990,130 bytes).
- `genie/build_email_strip.py` + `genie/email_strip/` — three phone screens per category as JPEGs,
  wrapped in table-based inline-styled HTML on the same 600px / 176px pattern as
  `agency_outreach.html`, with `PREVIEW.html` showing each block as sent and with images blocked.

**Decisions taken (CTO, RUL-037).**
- One comic per email type: yes in effect, no as eight pages. The screens do not differ; four lines
  do (who the other person is, how they met, who paid, how many pairs). Those four already live in one
  table, so the comic is generated from it and a ninth category is a data row.
- The comic does NOT go in an email. Email renders in Word and clips over ~102 KB, and a twenty-panel
  page is the sign-up wall in another costume. The email carries three panels, alt text that reads with
  images off, and one button to the spreader.
- Nothing is wired into a wave. `LAUNCH_EMAILS.md` rule 3 stands: an email is built when its wave has
  a date. The strip images are ready to deploy to `/static/qstrip/` on that day and not before.

**Standing context.** Today's funnel reading was 1,671 emailed, 354 opened, 63 clicked, 0 onboarded,
0 published. The loss is on the far side of the click, which is the exact stretch these screens specify.

**Names.** Every worked pair keeps both names in one naming tradition (14 Sep rule) — the COMMS table
already satisfies this and the generator uses it verbatim.
