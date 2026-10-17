## 2026-10-17 — BUZZ-BOARD-1 (RUL-238): the Buzz Board — People, Send and Specials on one screen

David, 17 Oct 2026 09:20 SAST, on mockups/BUZZ_BOARD_MOCKUP_2026-10-17.html: *"the basic service for free and the
marketing for paid subscriptions ... greyed out and when pressed saying they require a subscription ... not to pay for
any emails or SMS's as far as this Buzz comms is applicable."*

- **My Space > Buzz now has three tabs.** People (the page as it was, plus her own nickname and tags per person, a tag
  filter, "+ Add people" = her existing Buzz link by WhatsApp with no number, plus a QR code drawn on our own server,
  and Remove with a 10-second undo before anyone is told). Send (one person / a tag / everyone; six ready-made service
  lines; 120 characters). Specials (label + end date on her own listing, a pointer buzz, a SPECIAL line on the card and
  detail that drops off by itself after the end day).
- **Free vs paid (RUL-238(b)(c)):** Free sends the service lines to a tag or everyone; free text to a group and Specials
  are Starter/Pro/Agency — greyed with a lock on Free, tapping says "Needs a subscription" and names Starter. Enforced
  server-side (402).
- **No per-message cost (RUL-238(d)):** a group send is separate one-to-one buzzes, run off the request path, PUSH ONLY
  (no email, no SMS). The one-to-one email backup now has a daily ceiling (BUZZ_EMAIL_DAILY_CAP=500, inside the flat
  Resend plan); past it the sender is told "held".
- **Limits (Claude's technical call, David may veto):** 1 send to everyone a day, 3 tag sends a day, 3 special buzzes a
  week, a special ends within 14 days. Group sends no longer count against the one-to-one hourly cap.
- "Today's bookings" from the mock-up is NOT built: there is no bookings data yet, so it was omitted rather than invented.
- New routes declared in route_policy.json (stranger test PASS, 351 routes). Schema: buzz_people, buzz_group_log,
  listings.special_label/special_until (migration 083 + created on first use). Ledger RG-1051 (live routes, OPEN until
  deployed) and RG-1052..1054 (LOCKED). 24 functional checks passed on a scratch database.

Cost model impact: none (push is free; email stays inside the flat plan). Schema: additive only.
