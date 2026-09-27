## 2026-09-27 — RUL-185: Local Market seller pays; low-balance seller is told (LM-LOWBAL-1, LM-429-WORDING-1)
- David ruled: Local Market keeps "the seller pays" (1T, 2T boosted, once per listing, first buyer), as Terms v1.19 says; agents pay 1T to accept a free request. PRINCIPLE_REQUIREMENTS.md A8 now lists both as (iv) and (v); mirrors propagated.
- bea_main.py lm_create_intro: when the seller cannot pay, the turned-away buyer now triggers `_lm_low_balance_notice` (e-mail, SMS for a key identity; once a day per listing).
- bea_main.py lm_create_listing + ms.js: a seller who publishes with less than 1T gets a warning on the spot (`low_tuppence_warning`).
- ms.js lmSubmitIntro: a 429 from the daily limit now says "try again tomorrow" instead of "wait 7 days".
- host_queue: AdvertAgent added to the git_push allowlist; the worker pushes to `master` where the remote has no `main` (PUSH-BRANCH-1). The 27 Sep AdvertAgent push had been refused for that reason; CityLauncher's had landed (2e07478 on GitHub main).
- Ledger RG-0522, RG-0523 (OPEN until live), RG-0524 (LOCKED). rulings_check RUL-185.
