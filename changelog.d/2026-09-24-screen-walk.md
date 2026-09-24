## 2026-09-24 — SCREEN-WALK-1: the daily loop now looks at the live app, in every language, the way a person does

**24 Sep 2026 · scripts/screen_walk.py · scripts/maintenance_agent.py · RG-0456 · MAINTENANCE_AGENT.md**

David, after the Afrikaans zero-tiles fix: building on a live app with constant change breaks things,
and testing while live is hard -- "if we know what happens ... we can design for it and even leverage
the new AI improvements to automate for it". The gap was specific: the regression ledger guards faults
already NAMED; nothing looked at the screen a person sees, so David was the detector.

**Built:** a real headless browser (Playwright + Chromium headless shell, cached outside the repo at
`Projects/.tools/screen_walk` so no session downloads anything) opens the live app in en, af, zu, xh and
nso and reads the home tiles, Featured count and each Browse screen's card count off the screen, plus
any page error. English is the reference; a translation changes words, never quantities.

**Paid for inside the hour (RETURNING-READER-1):** the first version walked a first visit and PASSED the
broken build -- a cold dictionary paints late, so the counts came out right by luck. It now warms the
dictionary, reloads and judges the returning visit. **Proof mode** (`--serve-ms-js=`) served the pre-fix
ms.js through the walk: MISMATCH in all four languages, every tile 0 -- David's screenshot, found by a
machine. Against the live build: OK, all five agree (19/3/2/29/1/4). ~30 s for five languages.

**Wired so it cannot stop quietly:** `_screen_walk_lane()` runs inside every maintenance-agent run
(Linux sandbox only; skipped on the origin and the Windows host; 120 s cap; never raises). RG-0456 reads
the witness: MISMATCH or older than 72 h = red; NOT MEASURED = not evaluated, never green. Sabotage-tested
both ways. Sibling of QA-BOT-1 (RG-0454, same day): that bot attacks the routes; this one reads the screens.
