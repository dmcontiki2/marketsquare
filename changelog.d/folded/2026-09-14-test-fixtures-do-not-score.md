## 2026-09-14 — TEST-FIXTURE-EXCLUDE-1: the two who "published" were our own test accounts (RG-0370)

David asked to see the two people who had published — the one number that says whether any of this
works. Both are end-to-end test fixtures. So are all five "onboarded".

| id | name | source | channel | emailed | published |
|---|---|---|---|---|---|
| 6688 | David Conradie | e2e_test | test | never | — |
| 6689 | David Conradie Jnr | e2e_test | test | never | — |
| 6690 | Maroushka Conradie | e2e_test | test | never | 2026-08-03 |
| 6691 | Maurice Conradie | e2e_test | test | never | — |
| 6692 | Marietjie Marais | e2e_test | test | never | 2026-07-20 |

**Not one of the five has an `emailed_at` value.** None came through the funnel this board exists to
measure. Their dates do not even order — one is published 20 July on a row scraped 29 August.

**The true figures from cold outreach: 1,671 emailed → 354 opened → 63 clicked → 0 onboarded →
0 published.**

This is the RG-0133 fault in its worst form. Not an instrument defaulting to a health colour — a
real measurement of the **wrong population**, reading as success for six weeks on the single number
that decides whether the business works.

- **The fixtures are not deleted.** They are the end-to-end path and must keep working, and the
  listings those two accounts hold on the live site are real content (18 live between them).
- **They no longer score.** Both boards now count real people only: `dashboard_comms()` in the app
  and `prospects_stats()` in the CityLauncher API. Excluding them on one board and counting them on
  the other would be the same lie with a second opinion.
- **They are reported openly**, under their own name — "Test accounts (not customers)". Quietly
  removing them would be its own dishonesty.
- **RG-0370 LOCKED** across both boards.

### Two board faults found by the same run, both fixed

- **AGENT-HEARTBEAT-2.** The deploy-pending check aged `autodeploy_agent_log.txt` and called a
  pending flag with a quiet log a dead task. The agent writes to that log only when it has queue
  work, but stamps its heartbeat on *every* tick. A CityLauncher deploy flag raised 8 minutes
  earlier painted "pending 125 min — task not registered or stopped" while the heartbeat was 8
  minutes old. This is the identical misread AGENT-HEARTBEAT-1 corrected on 5 Sep and AGENT-ASLEEP-1
  refined on 12 Sep — it was simply never applied to this leg. It now reads the heartbeat for
  aliveness and the flag's own age for lateness, and distinguishes "agent stopped" from "gate is
  blocking it".
- **RG-0369's onboarded needle superseded, not deleted.** It fired correctly when the tile was
  renamed hours after it was written. The newer wording is better — the honest distinction on that
  tile is real-vs-test, not ever-vs-now — so the assertion moved to RG-0370 and the reason is
  recorded in place rather than the needle quietly vanishing.
