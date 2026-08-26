- **Gemini canary NOT armed — waiting on David.** `GEMINI_API_KEY` does not exist yet. The
  one blocking step: create the key at aistudio.google.com/apikey **with a hard budget cap
  set first** (Google Places burned ~$360 silently), then paste it into
  `/var/www/marketsquare/.env` on the server as `GEMINI_API_KEY=` (never into a repo file).
  Nothing else in the chain needs him. RG-0121 OPEN; the RUL-033 reject-only bridge stays
  UP until it is armed — photos needing blur are still rejected, not blurred.
- **Then, in order:** `python3 scripts/eval_photo_anon.py --provider gemini --dir eval_photos/`
  and the same with `--provider openai` for the baseline. Bar is 100% plate recall and clean
  photos staying clean. Only on a pass: set `PHOTO_SCAN_CANARY=1` in the server .env and
  restart — that single flip arms the canary AND drops the bridge, no second deploy.
- **Before the eval can be believed:** the five `real_246_*` rows in `eval_photos/TRUTH.json`
  still say `expect: "unknown"` and the 19 Aug Maroushka failure photos are not in the set
  (they are server-side uploads). RG-0185 tracks both.
- **Price correction, 26 Aug:** the gemini row was $0.375/$1.50 from an aggregator; first-party
  standard is $0.75/$3.75 (and $1.50/$7.50 from 1 Jan 2027). Canary year-1 is ~$845, not $548 —
  still well under terra's $1,729, so RUL-032 stands. Card + workbook corrected; RG-0184 now
  stops a second-hand price backing a live lane.
- **Watch:** the 24 Aug deploy's migration chain JAMMED at `033_csp_verify_served.py` —
  later migrations were skipped (`post_deploy_status.json`). 033 restored cleanly and did not
  claim success, but nothing queued behind it has run.
