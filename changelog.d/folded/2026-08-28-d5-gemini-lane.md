## 2026-08-28 — D5 in flight: Gemini key shipped, eval truth labels set, arming path clear

- David created the key (project trustsquare-gemini) and shipped it via the new gitignored
  `add_gemini_key.bat` (server env +1, restart, health ok — his transcript). Billing attach +
  AI Studio's native monthly SPEND CAP ($10) are the remaining David steps — the cap is a true
  hard stop, seen live 28 Aug, superseding the old quota-workaround advice.
- **The RG-0185(b) blocker cleared:** the five `real_246_*` rows in eval_photos/TRUTH.json were
  graded by eye from the originals (RUL-037 delegated grading, vetoable): 1385/1387/1389 clean
  (0 plates; 1389's licence disc is ~4px text — unrecoverable, blurring it protects nothing),
  1388 redact (1 plate, HP-class frontal), 1386 redact (**2 plates** — own rear + background red
  SUV's: the tiny-background syn_02 class on real evidence). 0 unknown rows remain; set still
  NOT FROZEN (RG-0185(a): Maroushka real_0819_* + 3 'inappropriate' samples outstanding).
- Arming stays RUL-032's bar: eval at 100% plate recall (gemini vs openai baseline), only then
  PHOTO_SCAN_CANARY=1 — which also drops the RUL-033 reject-only bridge, no second deploy.
- Price honesty (26 Aug correction stands): first-party Gemini is $0.75/$3.75 per Mtok — canary
  year-1 ≈ $845 at modeled volume, still ≪ terra's $1,729 (RUL-032 unchanged). Founding-month
  spend remains small; the $10 cap fails SAFE (cap trip → reject-only returns, never a leak).
