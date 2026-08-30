## 2026-08-30 — FIDE-TRAINERS-1: dedicated pipeline built AND run; credential registry live

David asked whether existing pipelines serve the chess lane or a dedicated one was needed
— dedicated, built, executed same session. CityLauncher/harvesters/fide_trainers.py
(resumable chunked crawl — sandbox kills background jobs, learned the hard way) crawled
all 209 FIDE seminar-report posts and populated new prospects.db table fide_trainers:
4,237 unique titled trainers (NI 1,680 / FI 1,126 / DI 1,023 / FT 408), federations
normalized — IND 934, RUS 93, RSA 23. Registry not outreach: no emails, wave machine and
prospects (1,519) untouched. Copy-back md5-verified, integrity ok,
prospects.db.bak-20260830-fide kept, raw harvest archived .jsonl.gz. Consumer = signup
claim-your-FIDE-ID → verified tier (RUL-072). Coverage honest: post-2022 awards (the
growing edge), grows on idempotent re-runs — candidate for the /housekeep cadence.
