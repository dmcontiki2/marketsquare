
## 2026-08-26 (evening) — STAYS-GEO-1 executed live · RUL-058 ladder re-order

**The geo fix ran, and the truth arrived.** Live adventures/accommodation pass (`dc641865`)
after a clean dry run. National Stays went from 223 rows "sendable" to **64 coordinate-proven**;
**180 quarantined** as `rejected_wrong_geo` (never deleted, restored the moment they are
re-proven); 16 already invalid.

| City | Before | After |
|---|---|---|
| Pretoria | 217 | **6** |
| Johannesburg | 0 | **1** |
| Cape Town | 4 | 23 |

Pretoria collapsing 217 → 6 is not a loss, it is the fault being removed: those lodges were
never in Pretoria. Cape Town and the Garden Route now lead, which is what SA guest-house
inventory actually looks like. Johannesburg's single row is *Jumbo House, Roodepoort* —
correctly placed, with a real suburb instead of the `accommodation_only` placeholder.

**Two bugs of mine, both found the hard way and both now covered:**
1. `lat`/`lon` were added to the prospect dict but not to the CSV writer's FIXED fieldnames,
   so `csv.DictWriter` raised and killed the run **at the CSV step, before city assignment** —
   the run looked like it produced nothing for three hours. Fixed with the fields added plus
   `extrasaction='ignore'`. RG-0193 now asserts both.
2. An earlier `max_results=40` "test" hit `[SKIP] already at 223/40` and never scraped, so it
   never touched the failing path. A skip is not a pass. `tests/test_stays_geo.py` now proves
   the whole path offline in two seconds — resolver, CSV, repair, quarantine, country scoping —
   and must be run BEFORE requesting a deploy.

**RUL-058 — ladder re-ordered by measured inventory.** With real numbers in hand, Stays could
not lead: 6 Pretoria / 1 Johannesburg against a 30 target, i.e. Gate 1 would have read almost
nothing. New order on all ladders: **Tutors → Services casual → Services technical →
Experiences → Collectors → Stays**. Only Tutors clears 30 in both proving cities (72 / 82).
Global launch day now sends TUTORS; the global three hold on Tutors to 4 Sep. Board is v3.2.
Order change only — same six sends, same days, ceiling untouched.

**CONSOLE-QUICKEDIT-1 (RG-0195).** `deploy_citylauncher.bat` sat frozen mid-scp for over an
hour and was diagnosed as a stalled SSH connection. It had been clicked: Windows QuickEdit
blocks a process on its next stdout write until Enter is pressed. `fix_console_freeze.bat`
disables it; `show_launch_key.bat` now copies to clipboard because with QuickEdit off you
cannot drag-select. The lesson recorded with it: ask what the window SAYS before inferring a
cause from server-side evidence.
