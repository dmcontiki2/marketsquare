- **The experiment loop is built, because the low cost base is only an advantage if experiments are
  cheap to run AND cheap to read.** The letter can now be A/B split per category
  (`defaults.email_variants` in waves_policy), the arm rides the existing `?src=` tag so signups
  attribute themselves with no app change, and `emailer/funnel_report.py --by variant --server` reads
  the result off GRADED human clicks with a guard that refuses to call a winner under ~30 per arm.
- **Caught before it shipped:** the first cut assigned arms with `pid % len(arms)`, which put four
  consecutive Durban prospects in the same arm because the scraped ids are all odd — a split that
  silently does not split and then reports a confident result. Hashed instead; 294/306 over 600 real
  rows. Asserted so it cannot return.
- **The local mirror understates engagement about fourfold** (48 human opens / 2 clicks locally against
  186 / 4 on the server) because pull_from_server carries verdicts down but not engagement. Hence
  `--server` on the readout. Worth closing properly in the sync at some point.
- **First experiment armed and waiting on the queue:** tutors arm 'b' drops the money ask out of a first
  cold email and shortens the request to "your listing is written, check it". It ships with the next
  wave, which the domain bounce gate is holding until the address list is cleaned.
- RG-0313 LOCKED alongside RG-0312. Both verified in isolation; the full board run did not finish inside
  the session.
