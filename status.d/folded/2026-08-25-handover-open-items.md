### HANDOVER — what is unfinished, written down so David does not have to carry it

*Session ended ~01:20, 25 Aug. Everything below is on disk; nothing depends on anyone remembering it.*

**1. ONE DEPLOY still owed, and it is the important one.** `migrations/033_csp_verify_served.py` carries
the real `script-src` CSP fix — migration 031 closed the naked-index half but reported `ok` on a policy
change that never took, because it checked its own file write instead of the served response. 033 proves
it against a live response or restores everything. The same deploy carries the corrected
`migrations/032` (its first fill died on `ModuleNotFoundError('data_flights')`; the cron was fine, so the
fare cache fills at 06:20 either way). **Deploys are David's (RUL-037).**

**2. Then the flag.** After that deploy, flip `data_flights` on the +1 page and indicative fares appear on
the 15 journey maps. Flipping before it is harmless — the card renders nothing.

**3. Ledger open, honestly:** RG-0178 (script-src not live — the real hole), RG-0180 (connect-src still
`https:`, post-launch job). 18 open total, 0 regressed.

**4. Travelpayouts: declined again**, same reason as 5 Aug. 26 programs usable; Booking.com, Viator and
GetYourGuide still blocked. Per RUL-041, never resubmit unchanged — **David picks the moment** (soft
launch, 29 Aug, is the natural one). Their dashboard is still pushing Drive; the answer stays no.

**5. WINDOW-ZORDER-2 — verify tomorrow.** Claude Desktop pins itself always-on-top (Anthropic bug
#87895, no in-app setting). The hidden watcher is running and PROVEN: after starting it, the topmost list
held only the two taskbars and their thumbnail helpers — Claude was gone from it. **It does not survive a
reboot on its own**; `start_session.bat` now starts it, so a normal `/start` covers it. If David ever
boots without `/start`, double-click `Projects\unpin_claude_watch.vbs`.

**Launch runway:** soft launch to public Fri 29 Aug, full Mon 1 Sep (RUL-001). Last ship day Wed 27 Aug.
