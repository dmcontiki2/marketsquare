## 2026-08-30 — SYNC-PULLDOWN-1: server verdicts finally flow DOWN (RG-0220 LOCKED) · wave-2 truths read off the server

PROBED via the dashboard's own session (X-Launch-Key from David's browser, statuses only):
of wave 2's 15 sends — 6 now `emailed` server-side, **8 `rejected_wrong_geo`** (STAYS-GEO-1 had
already geo-rejected those rows ON THE SERVER: Kruger/Breede/Hondeklipbaai/Pongola lodges tagged
Pretoria locally), and **1 `opted_out`: johannesburg@cityrock.co.za's Resend "Clicked" was the
unsubscribe link** — the POPIA round trip passed its first live test same-afternoon. SANParks'
click was a genuine CTA click. Server totals: 94 emailed · 5 bounced · 3 opted_out. The sync's
`AND status='scraped'` guard CORRECTLY refused to mark geo-rejected rows as emailed — the
"stuck at 94/95" dashboard was the machinery being honest, not broken.

The defect underneath (third bite in 24h): the sync was one-way UP. Geo-rejections, bounces,
opt-outs and the suppression register all lived server-side while the SEND lane reads the LOCAL
store — which also had NO suppression table, so SUPPRESS-1's chokepoint was checking a register
that didn't exist locally. Fixed at the class:

- **pull_from_server.py** (new): pulls verdict rows + suppression down; precedence rules —
  opted_out wins over everything, bounced over scraped/emailed, rejected_* over scraped only
  (send history never rewritten); creates + fills the local suppression table (SUPPRESS-1 armed).
- **sync_to_server.bat** rewritten: [1/3] pull → [2/3] local report → [3/3] push, every step
  errorlevel-guarded with pause-on-fail (it printed SYNC COMPLETE over a failed apply today —
  same wrong-status class as SYNC-LOCKSAFE-1, now impossible in both the bat and the script).

RG-0220 LOCKED (needles on precedence rules + bat pull step + errorlevel guards). Run the bat
once BEFORE tomorrow's wave: batch-24 composition then reads a pool carrying every server
verdict. Wave-2 targeting note for the ramp read: 8 wrong-geo sends were local-pool pollution,
not template or guard failures; bounce count for wave 2 currently 0.
