- Maintenance loop ran 2026-09-18 07:14Z. Fault queue empty: 0 new, 0 triaged, 0 fix-shipped,
  0 escalated (26 verified, 12 closed). No escalation brief — no escalations in 24h. Heartbeat
  on /dashboard/maint PROBED for this run.
- Regression ledger: before 385/367 holding/1 red; after 386/368 holding/**1 red — RG-0253, now
  both legs** (live ms.js moved v=685→v=686 mid-session as the design lane shipped SEAM-PROOF-1).
  The red is a window artefact: sobGoLive is now a wrapper around `_sobGoLiveInner`, where
  register still precedes the EULA stamp (PROBED live v=686: reg@869 < eula@1174); the assertion's
  6,000-char window from the `sobGoLive` anchor no longer reaches it. ms.js / bea_main.py /
  regression_ledger.py are under the RUL-140 work lock (design-review lane, 03:33Z), so this lane
  recorded the finding and did not edit. Owner to re-anchor RG-0253 on `_sobGoLiveInner`; until
  then the board says "do not deploy" over a fix that holds.
- Nightly TSL 05:45 was BLOCKED (deploy drift bea_main.py + ms.js local-ahead; CM gate wants the
  ship recorded). Same owner, same in-flight work.
- Committed fragments only; not pushed, not deployed.
