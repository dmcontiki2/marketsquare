## 2026-08-05 — The REPORT tab made findable (MAINT-B1b addendum)

**What happened.** David deployed three times and still could not see the tab, then asked the
question that mattered: *"if I can't find it, how can I expect my testers to see it? I can't even
show them."*

**The diagnosis, read from his live browser rather than guessed:** `fault_report: false`. The
script was deployed and loaded, he was recognised as a tester, and the tab was correctly not
rendering. No deploy could ever have shown it — deploying ships code, the launch switch opens the
door, and the switch had never been flipped. That confusion is itself a finding: *"deploy it"* and
*"turn it on"* are two different acts and nothing on screen said so.

**What changed, because his point was right.**
- The tab is **gold**, not navy — larger padding, stronger shadow. Navy-on-white was too polite for
  something a tester must notice without being told.
- A **one-time coach mark** on first load: *"Something wrong? Tap REPORT any time, on any page. We
  fix it and write back so you can check it."* Dismissed with a button, remembered in
  `localStorage.ts_report_seen`, and self-fading after 12 seconds so it can never nag.
- `window.tsReportWhere()` — a console hatch that re-shows the pointer and flashes the tab, for the
  next time anyone asks where it is.

**The failure this prevents.** A tester who never notices the tab reports nothing — and silence
from testers reads exactly like *no faults found*, which is the most expensive wrong conclusion
available to us in the month before launch.
