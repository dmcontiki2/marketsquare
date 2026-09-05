## 2026-09-05 — All 50 states in one register, a domain-wide daily cap, and the US scraper's fix round (RRCA-1, DAILY-CAP-1, SCRAPER-LOCALE-1, SCRAPER-USQ-1)

David, 20:26: *"are we reading registers for the full 50 states of the US, if yes can you then in
parallel fill up the database for us to also start emailing them?"* Honest answer at that
minute: no — one register, one region (USATF Pacific, 88 clubs). By 20:35, yes.

**RRCA-1.** The Road Runners Club of America publishes its member clubs for every state:
`POST /clubs/` with `drpState=<ST>` returns the whole state as a table, and each `/club/<slug>/`
page carries the club's website and one mailbox behind Cloudflare's email obfuscation (decoded
from `data-cfemail`). Verified on Texas (60+ clubs) and Wyoming (5 of 5 with a mailbox:
windycitystriders@gmail.com, rcrgillette@gmail.com …). New adapter `rrca` in
`us_register_reader.py`, resumable per club and per state, ~2,500 clubs. The reader now honours
a row-level city, so a national register buckets **one policy city per state** ("Texas",
"New York State" …) while a regional one keeps its single bucket. **51 state buckets armed** in
`waves_policy.json`, Sports Clubs only. `run_us_registers.bat` (allowlisted, RUL-096 supply
class) harvests every adapter and imports host-side; queued 20:33, about 50 minutes. The 00:10
wave visits whichever states have people.

**DAILY-CAP-1.** The 16:10 plan said it plainly: reputation depends on total volume from the
domain, not on how it is split between cities. 51 new buckets at 12 each could mean 600 in one
night from a domain whose best day is 246. `defaults.daily_send_cap = 250`;
`wave_runner.gate_check` counts today's sent events (send-timezone calendar day) and blocks a
city's wave once reached. Probed: 152 sent today, cap 250. A real gate on the real dimension —
raised on measured clean days, never on a date.

**The scraper's US failure is now a task, as David asked.** `RG-0297` (OPEN) reads the latest
host result for `run_us_scraper.bat` and fails until a run pushes ≥ 10 in-country addresses
with no foreign-ccTLD row; it prints READY TO LOCK the day it passes. First fix round, same
evening: SCRAPER-LOCALE-1 — DuckDuckGo `kl=us-en` and Bing `cc=US` so a search for Austin is
answered from the US, not from Pretoria (the measured cause of the one wrong row);
SCRAPER-USQ-1 — US query templates that ask for pages which PRINT a mailbox (the quoted
`"@gmail.com"` term), because the old '<trade> <city> email contact' returned Yelp/Angi/Thumbtack,
which the block list then discarded. DuckDuckGo refuses the sandbox, so the fixes are unmeasured
until the queued host run; if it still reads under 10, the next moves are listed in the entry.

**Today's sends, for the record (server, 5 Sep SAST):** 00:10 — 11 (New York university
tutors); 09:31 — 129 across 38 cities; 19:31 — 12 (Pretoria clubs, the first club wave).
Total 152. Against the 16:10 plan's 55 for tonight: Pretoria's 12 went eight hours early and
Pretoria doubles at 00:10 if its bounces stay clean; the other 43 are still due at 00:10.
