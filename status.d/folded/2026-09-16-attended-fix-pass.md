## 2026-09-16 — The board is green, and two of the four reds were the instrument

Attended fix pass ("fix what is fixable"). **366 entries · 344 holding · 0 REGRESSED ·
0 UNVERIFIED · exit 0.** Rulings 108 checked, 0 FAIL. Coverage map: **79 green · 2 blue ·
1 amber · 0 red · 10 grey**.

Closed: **DW-123** (ref locks now swept on both lanes — GIT-LOCK-5, sabotage-proven,
RG-0379 LOCKED), **DW-124** (pg-readiness — the SQLite surface shrank 25 → 15 through a
portable `_sql_since()` helper; baseline tightened, not raised), **DW-125** (fault-report
widget on the three new Quick-door pages, RG-0377 LOCKED), **DW-126** (Model Register
re-verified after ageing to 46 days; `gpt-5.6-sol` corrected $5/$30 → $4/$20),
**DW-127** (RG-0347's red was a lexical-window fault; the buyer-facing list was correct all
along, and the assertion is now a stronger reachability check).

Still open: **DW-010** (CC-002 97d / CC-005 14d — David's canon call), **DW-087** and
**DW-121** (Monday deep-scan lane), **DW-111** — the Resend lane that fails every five minutes
and leaves no trace this watch can read, because `msdeploy` is in neither `adm` nor
`systemd-journal`. That one needs a server-side grant or a lane that writes its own result
file; it is the only item on the board nobody can see.

For David, information not a task: `gpt-5.6-sol` is 20% cheaper on input and 33% on output
than the register said, promotionally until 21 Nov 2026; and `gemini-3.7-flash` doubles on
1 Jan 2027. No model choice was changed — RUL-009 reserves that to him.
