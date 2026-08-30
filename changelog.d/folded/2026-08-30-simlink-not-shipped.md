## 2026-08-30 — SIM-DASH-2 correction: the sim link never reached the live site

David reported the simulation link missing from the dashboard — he is right. Probed live
(no-store fetch, in-gate via Chrome): dashboard.html carries page 4 but NO
"/orchestrator/simulation.html" link, and the sim page itself answers 404. Cause: commit
2377b85 (SIM-DASH-2) landed AFTER the Sat 29 Aug 19:11 release (be91f83) and the deploy
ref was never pushed again — the 29 Aug fragment's "live-verified" claim was wrong
(READ, not PROBED). RG-0210's LOCKED status will correctly trip red until the deploy
ref is published. Fix = publish deploy ref (awaiting David's go this session).
