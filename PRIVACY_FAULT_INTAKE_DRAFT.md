# Privacy clause — in-app fault reporting (DRAFT, awaiting David · OPEN_LOOPS D10)

Raised 5 Aug 2026 with MAINT-B1b. The REPORT tab collects personal data, which makes
`privacy.html` a legally-worded surface under CHANGE_CONTROL_PROTOCOL Gate 1 — so it is
staged here, not shipped. The in-form notice IS live (testers see it before they submit);
this is the standing document version.

**Live in-form notice (already shipped in `ts_report.js`):**
> We store your report with the page address, your browser details and any screenshot you
> attach, so we can reproduce and fix the fault and reply to you. Testers only, and only
> until launch.

---

## Proposed clause for privacy.html

**Reporting a problem**

If you use the *Report a problem* button, we store what you tell us together with the
address of the page you were on, the version of the app you were running, your screen
size, your browser's identification string, the last few technical errors your browser
recorded, and any screenshot you choose to attach. We store your name and email address
so that we can reply to you.

We use this only to reproduce and fix the fault you reported, and to write to you about
it. We do not use it for marketing, we do not sell it, and we do not share it with anyone
outside TrustSquare except where a fix requires our hosting provider to investigate on our
behalf. A screenshot may capture whatever was on your screen when you took it — please
look before you attach.

We keep a fault report for as long as the fault is open and for twelve months after it is
closed, so that we can tell whether a fault has come back. You may ask us to delete your
report at any time by writing to [privacy contact], and we will do so unless we are
required to keep it.

---

## The three questions for David

1. **Retention — twelve months after close.** Chosen so recurrence counting works (a fault
   that returns in month nine is the whole point of the register). Shorter is possible; it
   costs the recurrence signal.
2. **Screenshots.** The honest risk is a tester screenshotting a page containing someone
   else's data. Options: keep as-is with the warning; strip screenshots entirely; or hold
   them in a separate bucket with a shorter life. Recommendation: keep, warn, and purge
   screenshots at fault close rather than at twelve months.
3. **Named privacy contact.** privacy.html needs a real address in the deletion sentence.

## What happens next

Nothing ships until you answer. The intake works today with the in-form notice; the
privacy.html clause is only *required* before the flag opens past the tester group at
launch — but the wording is easier to settle now than in launch week.
