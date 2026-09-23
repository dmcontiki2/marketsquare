### Onboarding run 17 — the "registered" number was counting our own mailer (RG-0428)

`reconcile_conversions()` stamped `prospects.onboarded_at` on the mere existence of a row in
`marketsquare.users`. `/agencies/wave-prep` creates one of those rows *at send time* for every
agency-class prospect, so ONBOARDED had become a re-count of our own sending — and a false
"42 registered" had already reached David in the 20 September summary. Probed on the live
databases: all 40 non-test rows were Estate Agents, created inside the 22:10 UTC wave minute on
six consecutive nights, with every activation column NULL.

Now a prospect counts as onboarded only when the account has been used (last_seen, accepted
EULA, linked login, photo, buyer token) **or** they have built a listing in any status — the
second leg matters, because the app upserts a bare account row when a listing is created, and
without it the fix would have erased the one real seller in the funnel. Rows stamped under the
old rule are unstamped, and the status they return to is read from `email_events` so a
retraction cannot destroy a real open or click. Guard is RG-0428, which runs the reconciler over
a synthetic pair rather than grepping it; proven to fail on the pre-fix code and on a
leg-one-only variant.

Measured on a copy of the live pair: 45 stamped → 5, 41 retracted, 1 correctly added, clicks
preserved at 74, second pass a no-op. The goal number itself was never inflated — it demands
published_at AND emailed_at AND a non-test source AND a public probe — and remains 0.

Opened in the same run: RG-0429 (the publish wall — a seller can finish an entire advert as a
stranger and is then asked to build an account before it goes live), RG-0430 (every
wizard-created listing is born `country='ZA'`), RG-0437 (`rulings_check` can print a false FAIL
from a mid-write read; the file is owned by another lane, so recorded not edited).
