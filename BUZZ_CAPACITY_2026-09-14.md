# Buzz — what it can cost if it escalates
**14 Sep 2026. David: *"How much resources could it need if it escalates? What could the traffic
become and how will it then effect the apps traffic?"***

Every input below is stated so the input can be argued with rather than the conclusion. Box:
Hetzner CPX22 — 3 shared vCPU, 4 GB RAM, 80 GB NVMe, 20 TB traffic included. FastAPI + SQLite (WAL,
synchronous=NORMAL) + nginx behind Cloudflare.

**Assumption:** a pair buzzes ~4 times a week (late, sick, swap, thanks). Request 350 B; one push
out ~4 KB with TLS amortised; one `buzz_log` row ~220 B; 35% of a day's buzzes land in the two-hour
06:00–08:00 window, because "running late" is a correlated event — everybody is late at the same
time, and that is also when the app is busy.

| active pairs | buzzes/day | avg/sec | peak/sec | MB/day | GB/month | log GB/yr |
|---:|---:|---:|---:|---:|---:|---:|
| 1 000 | 571 | 0.01 | 0.0 | 2.5 | 0.07 | 0.0 |
| 10 000 | 5 714 | 0.07 | 0.3 | 24.9 | 0.75 | 0.5 |
| 50 000 | 28 571 | 0.33 | 1.4 | 124.3 | 3.73 | 2.3 |
| 100 000 | 57 143 | 0.66 | 2.8 | 248.6 | 7.46 | 4.6 |
| 500 000 | 285 714 | 3.31 | 13.9 | 1 242.9 | 37.29 | 22.9 |

## Bandwidth and CPU are not the question

At half a million active pairs Buzz uses **37 GB a month against 20 000 GB included — under 0.2%**.
A buzz is a few hundred bytes in and one small encrypted payload out; there is no page render, no
image, no query of any size. Whatever eventually strains that server, it will not be this.

## The real ceiling is THREADS, and that is exactly how it would have hurt the app

`/buzz` is a synchronous endpoint, so it runs on the shared worker threadpool — roughly 40 slots —
and **those are the same threads that serve listing pages**. A slow push vendor therefore would not
have made Buzz slow. It would have made the SITE slow, which is the answer to the second half of
David's question and the only part of this that ever mattered.

| | saturates all 40 threads at |
|---|---|
| before — email fallback on the request path (20 s) | **2 buzzes/sec** |
| before — a slow push vendor (8 s) | **5 buzzes/sec** |
| now — push capped at 2 s | 20 buzzes/sec |
| now — healthy push (~0.25 s) | 160 buzzes/sec |

Two buzzes a second is inside the peak figure for a MODEST userbase. That was a real fault in
Claude's build, found by David asking the right question, and it is fixed:

- **`BUZZ_PUSH_TIMEOUT = 2`** — a buzz may hold a worker thread for two seconds, not eight. The
  intro-reminder lane keeps the old 8 s default, because it is a background job and does not care;
  the timeout became a parameter rather than a global change.
- **The email fallback is off the request entirely** — queued with `BackgroundTasks`. The sender is
  told immediately that it is going by email; the request never waits on a mail provider.

## The only part that grows without a ceiling

`buzz_log`. At 500 000 pairs it is **23 GB a year on an 80 GB disk**, sharing that disk with the
database. It is operational data — rate limiting and did-it-arrive — never a conversation, so
ageing it out costs nothing: **`BUZZ_LOG_KEEP_DAYS = 90`**, pruned lazily on roughly one send in
five hundred, the same pattern the wishlist signals already use instead of a cron.

## Triggers, so this is watched rather than assumed

- **Sustained above ~10 buzzes/sec** (roughly 350 000 active pairs): move the push off the request
  path too, exactly as the email now is. Cheap when it is needed, unnecessary before.
- **`buzz_log` above ~2 GB**: shorten the retention, not the feature.
- **SQLite:** WAL with one writer is fine at these rates (tens of writes/sec against thousands
  possible). Worth knowing that `database.py` sets no `busy_timeout`, so contention surfaces as an
  immediate "database is locked" rather than a short wait — pre-existing and app-wide, not caused by
  Buzz, but Buzz adds writes and it is a one-line hardening whenever that file is next touched.
