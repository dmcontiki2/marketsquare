### AI EXAMPLE GENERATED ADVERTS + DEMO banner (RUL-040, 22 Aug)

The exemplar ribbon no longer says "★ SUPER ADVERT" anywhere — all four ms.js renderers
say **AI EXAMPLE GENERATED ADVERT**, and the detail pill leads with "not a real listing".
A red **DEMO** tab (`ts_demo_banner.js`, new, in the manifest) now sits in the REPORT
tab's right-edge slot on all 15 adventures demo maps; it is ungated, so it survives Soft
Launch when the tester REPORT tab is removed, and re-centres itself in the slot when that
happens.

State: **in the repo, NOT yet live.** Ledger RG-0140 and RG-0141 are OPEN — repo halves
pass, live halves fail until the next deploy places the new ms.js and ts_demo_banner.js.
Promote both to LOCKED on the first run after the deploy that reports READY TO LOCK.
Ledger run 22 Aug after the change: 0 REGRESSED, 126 holding, RG-0014 HOLDING.
