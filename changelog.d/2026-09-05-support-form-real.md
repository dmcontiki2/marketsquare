## 2026-09-05 — SUPPORT-FORM-REAL-1: the support form was a hole that said "thank you" (DW-100)

**David raised it, from the right question.** 134 people had opened the app, a listing failure was
live and already fixed, and not one complaint had arrived. He read that as a broken channel rather
than as good news. He was right.

**What was live.** `support.html`'s `submitForm()` carried, verbatim:

```
// In production this would POST to the BEA or a form handler
// For now show success message and send email
```

It hid the form, showed **"✅ Message sent — we'll be in touch within one business day"**, then set
`window.location.href` to a `mailto:` link. Nothing was posted. Nothing was stored. On a desktop with
no mail client registered the mailto did nothing at all; on mobile it opened a draft the visitor still
had to send themselves — after they had already been thanked. The form's inputs carried **no `name`
attributes**, so even a real POST would have submitted empty fields.

**Why it was load-bearing.** From 29 Aug (RUL-064) the in-app tester reporter is deliberately off for
customers and complaints route to this page and to support@. For a week this WAS the customer complaint
lane. We cannot know how many messages it swallowed, because nothing was recorded — and that
unknowability is the damage.

**What was already fine, checked rather than assumed.** support@trustsquare.co delivers: a probe sent
to it landed in David's Gmail 12 seconds later via Cloudflare Email Routing. The mailto links pointed
somewhere real; the form was the hole. Also confirmed: the last fault anyone filed was **TS-0035 on
15 Aug**, and all 35 rows come from three internal tester addresses. No public user had ever
successfully reported anything.

**The fix.** `POST /support/message` stores the message in `app_faults` (source `support-form`, so it
inherits the existing triage board and close-draft/close-send reply flow rather than becoming a second
inbox), emails David a copy, and acks the sender with a reference. **Anonymous by design** (RUL-100):
the person who cannot list, cannot sign in, or never registered is exactly the one most likely to need
it, so abuse is handled by rate limit + honeypot + length caps, never a login wall. The row commits
**before** either email is attempted — a mail failure must never lose a customer's message. The page
now only claims success when the server confirms, prints the reference, and on failure says so and
**keeps the user's words on screen**.

**Proven, not inferred.** After deploy: anonymous POST accepted · 1-character message refused 400 ·
missing email refused 400 · honeypot accepted-and-dropped · a real submission returned **TS-0036**,
the row is in the live table with `source=support-form, ack_sent=1`, and both emails were read back out
of Gmail at 12:04:29Z — the notification carrying the full message text, and the acknowledgement to the
sender. Locked as **RG-0282**, whose live leg re-posts an anonymous `.invalid` probe every run and also
proves the validation is real rather than a rubber stamp.

**Second fault found on the way — TOAST-DURATION-1 (RG-0283).** `showToast(msg, ms)` accepted a
duration at **13 call sites and silently ignored it**: messages written to need 6 s got 2.6 s, including
"Add TrustSquare to your home screen: tap Share then Add to Home Screen" and "Publish failed: <reason>".
An instruction nobody can finish reading is an instruction nobody follows, and a failure message that
vanishes is a failure the user cannot report. Fixed and clamped 1.2–12 s. The three hard publish
failures were also dead ends — they now name trustsquare.co/support, which as of today receives.

**Not changed, deliberately.** RUL-064 stands: the tester fault tab stays off for customers. This fixes
the lane David chose rather than reversing his ruling.

**Residual, stated rather than glossed.** The Support Centre is reachable from the Me tab and the legal
pages. Discoverability at the moment of failure is improved (the publish toasts) but not solved.
