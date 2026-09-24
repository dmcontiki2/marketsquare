## 2026-09-24 — SIM-CASUALS-1: Contagion Model v1.9, the Services lane re-based on the casual-workers research

David, 24 Sep: *"audit the apps simulation and update it with the latest information, our new target group of
prospects, a re-assessment of the contributing variables and statistics ... a much larger prospect group ... a
better user / employer referral component."* Done in `docs/TrustSquare_Contagion_Model_v0.2.html` (deployed as
`/orchestrator/simulation.html`); report `Visuals/MarketSquare/CONTAGION_V19_AUDIT_2026-09-24.html`.

**Re-based (lo · mid · hi), grounded in CityLauncher/CASUALS_REACH_PROPOSALS_2026-09-23 and its sources:**
svcDen 6·18·45 → 15·40·110 (854k domestic workers employed, 1.1m in private households, ~1.6m with the informal
tail; gardeners, piece jobs, day labour, EPWP leavers, informal trades); svcInc .40·.65·.85 → .25·.45·.65;
empSize 8·60·900 → 8·120·1,500 (estate gate desks 300–800 workers); svcRef .01·.05·.15 → .05·.20·.50 (the Status
card + wa.me self-send; RUL-142 pays points, never cash); svcRefTake .15 → .18; svcPay .10·.35·.80 → .03·.12·.30
($5 ≈ R82 against a R94 median monthly data spend). Lever svcLangW 13 → 3 (languages shipped 23 Sep, RUL-164/165).

**New:** `svcMail` (share of invited casual workers who can finish an e-mail step, .15·.35·.60 — the RUL-166
gate, multiplies the publish rate until a phone/link key ships); lever `svcKeyW` (week the phone / link key
ships, 157 = never = today's truth); `svcChanW` / `svcChanN` / `svcChanConv` (the ground + air channels of
proposals 4–6: ranks, listing mornings, radio, SA Youth, job groups — 157 = never until David decides).
Six presets replace the four of 19 Sep; the with/without strip shows arrivals from the channels.

**What it says (mid run, week 156):** e-mail key kept → 1,653 service workers listed; phone/link key wk 6 →
99,771; + channels wk 8 → 108,319; + Growth Partner doubling the employer pace → 130,449. By March 2027 every
scenario is under 600 workers — the lane is slow money and its revenue is the household's introduction.

**Calibration recorded, not applied:** at week 3 the model expected 67 sellers (40 from letters); measured
2,491 letters, 534 opened, 2 human clicks, 1 draft, 0 published. Pinning click at the measured 0.37% of openers
is David's decision (it moves the BEAT THE MODEL card).

**OFF is v1.7 draw for draw** — verified headless: identical series (91 / 150,917 / 168,093 sellers at weeks
8 / 52 / 156) and identical stats apart from the new `svcChan` counter. Dashboard pin string moved to v1.9.
Backup: `docs/TrustSquare_Contagion_Model_v0.2.html.bak-v18-20260924`.
