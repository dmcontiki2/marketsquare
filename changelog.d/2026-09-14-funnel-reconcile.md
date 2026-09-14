## 2026-09-14 — FUNNEL-RECONCILE-1: two true funnels, one word, and why they differed (RG-0369)

David put the CityLauncher Overview tiles beside the new comms panel and asked why they disagree:
**1,569 vs 1,671 emailed · 3 vs 5 onboarded · 5,052 vs 3,941 scraped.** Neither was wrong, which is
exactly what made it dangerous.

- **The Overview counts `prospects.status` — where somebody is NOW.** Its buckets empty as people
  progress. The 102 gap on emailed is people who have since opened, clicked, bounced or opted out;
  the 2 gap on onboarded is the two who went on to publish.
- **The comms panel counts the timestamp columns — what has EVER happened.** Those never move
  backwards, which is the right basis for a funnel.
- **The scraped gap is a different thing again.** The Overview adds 1,111 phone-only Gumtree
  contacts to SCRAPED. No email wave can ever reach them, so quoting 5,052 as outreach supply
  overstates it by 28%.

Every figure reconciled exactly on probe: 3,941 + 1,111 = 5,052, and the status buckets sum to
the full 6,748 rows.

**The fix is not to pick a winner** — both questions are worth asking. Each number now says which
question it answers and names the other panel's figure: "People emailed — ever" and "Onboarded —
ever" carry the current-state number and the reason it is lower, "Opened" says plainly that it IS
a current-state count (there is no `opened_at` column), and the raw-pool tile names the 1,111
phone-only rows. **RG-0369 LOCKED** over all three. A dashboard showing two different numbers for
one word without explaining itself spends its authority — the same instrument-honesty line RG-0133
draws, applied to a second surface rather than a second colour.
