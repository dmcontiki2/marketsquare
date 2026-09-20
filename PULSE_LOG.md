# PULSE LOG — trustsquare.co (one line per heartbeat)
2026-07-12 🟢 up · full app served · SSL 74d · BEA v1.3.1 (first logged pulse — load-time instrumentation from next scheduled run)
2026-07-15 🟢 trustsquare.co up · 1.1s · SSL 71d · /health ok · /payment/test ok
2026-07-15 (daytime) 🟢 trustsquare.co up · 0.6s · SSL 71d · /health ok (v1.3.1) · /payment/test ok (paystack connected)
2026-07-16 🟢 trustsquare.co up · 1.0s · /health ok · /payment/test ok · SSL 70d
2026-07-16 🟢 trustsquare.co up · 2.8s · /health ok · /payment/test ok · SSL 70d
2026-07-17 🟢 trustsquare.co up · 0.8s · SSL 68d · /health ok (v1.3.1) · /payment/test ok
2026-07-17 🟢 trustsquare.co up · 1.2s · SSL 69d (daytime)
2026-07-18 11:03 UTC 🟢 trustsquare.co up · 0.8s · SSL 68d · /health ok · /payment/test ok
2026-07-18 17:03 UTC 🟢 trustsquare.co up · 0.6s · SSL 67d · /health ok · /payment/test ok (daytime pulse)
2026-07-19 (daytime) 🟢 trustsquare.co up · 2.8s · SSL 67d · /health ok v1.3.1 · /payment/test ok (paystack connected)
2026-07-20 🟢 trustsquare.co up · 0.8s · /health ok · /payment/test ok (paystack connected) · SSL 66d
2026-07-20 🟢 trustsquare.co up · 0.9s · /health ok · /payment/test ok · SSL 66d
2026-07-20 🟢 trustsquare.co up · 0.7s · SSL 66d
2026-07-22 · 🟢 trustsquare.co up · 0.9s · SSL 64d · /health ok · /payment/test ok (paystack connected)
2026-07-22 (daytime) 🟢 trustsquare.co up · 0.6s · SSL 64d · /health ok · /payment/test ok
2026-07-22 (daytime) 🟡 trustsquare.co up but SLOW · 3.4s (retries 2.3/4.1/4.7s) · SSL 64d · /health ok v1.3.1 · /payment/test ok (paystack connected)
2026-07-22 (follow-up) 🟢 amber resolved — edge caching enabled; homepage 0.2–0.3s (cf-cache HIT), purge-on-deploy fixed (stale CF_ZONE_ID was root cause)
2026-07-23 🟢 trustsquare.co up · 1.3s · SSL 63d · /health ok · /payment/test ok
2026-07-23 19:03 🟢 trustsquare.co up · 1.5s · SSL 62d · /health ok · /payment/test ok
🟢 trustsquare.co up · 1.2s · SSL 62d · /health ok · /payment/test ok  (2026-07-24)
2026-07-24 14:00 🟢 trustsquare.co up · 2.4s · SSL 61d · /health ok · /payment/test ok
2026-07-25 🟢 trustsquare.co up · 1.3s · SSL 61d
2026-07-25 🟢 trustsquare.co up · 1.2s · SSL 60d · /health ok · /payment/test ok
2026-07-26 🟢 trustsquare.co up · 1.3s · SSL 60d · /health ok · /payment/test ok (scheduled daytime pulse)
2026-07-26 🟢 trustsquare.co up · /health 0.4s /payment/test 2.2s root 1.2s · SSL 59d
🟢 trustsquare.co up · 2.0s · SSL 59d · /health ok · /payment/test ok · 2026-07-26
2026-07-27 (daytime) 🟢 trustsquare.co up · 1.2s · /health ok (v1.3.1) · /payment/test ok (paystack connected) · SSL 58d
2026-07-27 (daytime) 🟢 trustsquare.co up · 0.8s · SSL 58d · /health ok · /payment/test ok
2026-07-28 🟢 trustsquare.co up · 0.9s · /health ok · /payment/test ok (paystack_connected) · SSL 58d
2026-07-28 (daytime) 🟢 trustsquare.co up · 1.4s · SSL 57d · /health ok (v1.3.1) · /payment/test ok (paystack_connected)
2026-07-29 11:16 UTC 🟢 trustsquare.co up · 1.1s · SSL 57d · /health ok · /payment/test ok
2026-07-29 🟢 trustsquare.co up · 1.3s · SSL 57d · /health ok (v1.3.1) · /payment/test ok (paystack_connected)
2026-07-30 (daytime) 🟢 trustsquare.co up · 0.4s · SSL 55d · /health ok · /payment/test ok
2026-07-31 🟢 trustsquare.co up · 0.9s · SSL 55d (health ok, payment/test ok, paystack connected)
2026-07-31 (daytime) 🟢 trustsquare.co up · 0.7s · SSL 54d · /health ok (v1.3.1) · /payment/test ok (paystack connected)
🟢 2026-08-01 trustsquare.co up · 1.3s · SSL 54d · /health ok · /payment/test ok
🟢 2026-08-01 (daytime) trustsquare.co up · 1.2s · SSL 53d · /health ok · /payment/test ok
2026-08-02 (daytime) 🟢 trustsquare.co up · 1.0s · SSL 53d · /health ok v1.3.1 · /payment/test ok (paystack connected)
2026-09-18 02:20 UTC 🟢 trustsquare.co up · 1.0s · /health ok (v1.3.1, db integrity ok, primary present) · homepage 200 (421 KB) · /quick/ 200 · BIT board 8/8 PASS · ledger 0 REGRESSED. SSL omitted — /health exposes no ssl_days and a sandbox TLS probe only sees the egress-proxy certificate (never the site's). *First entry since 2026-08-02: every run between was cloud-only with no write path, so 47 days of pulses were run and not logged — an unlogged pulse is an unrun pulse.*
2026-09-18 02:25 UTC (scoped run) 🟢 trustsquare.co up · 0.33s · /health ok (v1.3.1, db integrity ok, primary present) · homepage 200. SSL omitted — /health exposes no ssl_days. Second probe of the day; the 02:20 stand-up line above is the run of record.
2026-09-18 03:28 UTC 🟢 post-deploy re-check (release 8ad84a9) · trustsquare.co up · 0.97s · /health ok (v1.3.1, integrity ok) · BIT 8/8 PASS, 0 failing · /privacy 26,719 bytes serving Supplements A–D (UK · US · AU · EU), breach clause now 72h for UK GDPR, zero legal@ routes · /terms EULA v1.17. Deploy verified by probing the live pages, not by reading the deploy log.
2026-09-18 19:0xZ (stand-up) 🟢 trustsquare.co up · 0.41s homepage (420,987 B, HTTP 200) · /health ok (v1.3.1, db integrity ok, primary present, 3,481,600 B) · BIT board 8/8 PASS, failing:[] · ledger 392 entries · 374 LOCKED · 18 OPEN · **0 REGRESSED** · maintenance heartbeat 17:20:41Z (~1.7h old, inside the 12h bar) mode:LIVE armed:true brain_state:GREEN, 7d spend $0.000257/17 calls against a $0.50/day budget. SSL omitted — /health exposes no ssl_days and a TLS probe from here only sees the egress-proxy certificate, never the site's. Two live defects found and shipped this run: the EULA published v1.17 in its header and v1.16 in its footer (fixed at source, synced by the one writer); and ms.js called an agent "vetted" on a listing surface, which RG-0238 bans by name (removed, 0 remaining).
2026-09-19 19:0xZ (stand-up) 🟢 trustsquare.co up · 0.43s homepage (420,925 B, HTTP 200) · /health ok (v1.3.1, db integrity ok, primary present, 3,604,480 B — up 122,880 B on yesterday) · /quick/ 200 · BIT board 8/8 PASS, failing:[] · ledger 404 entries · 381 LOCKED · 23 OPEN · **0 REGRESSED** · maintenance heartbeat 17:22:01Z (~1.8h old, inside the 12h bar) mode:LIVE armed:true brain_state:GREEN (gpt-5.6-luna, probe 200), 7d spend $0.000276/20 calls against a $0.50/day budget. SSL omitted — /health exposes no ssl_days and a TLS probe from here only sees the egress-proxy certificate, never the site's. **The 18:49Z board printed 1 REGRESSED (RG-0163) and that conviction was FALSE:** its only fail was `ProbeOffline('gate credential rate-limited (429 at /review/l` — the gate 429'd, the payload was never read, and a re-judge this run returns HOLDING with the endpoint live. RG-0401 (LOCKED, 18 Sep) says an edge refusal is BLIND, never REGRESSED; `_judge()` only honoured that when the WHOLE machine was offline. Fixed at source (EDGE-BLIND-2) with a test that fails on the old code. Also fixed this run: ms.js called agents 'Vetted' in the zero-results empty state, which RG-0238 bans by name — 0 banned adjectives remain on either listing surface.
2026-09-20 17:2xZ 🟢 post-deploy re-check (release a55f885) · trustsquare.co up · 0.55s homepage (272,433 B, HTTP 200) · /health ok (v1.3.1, integrity ok, primary 3,866,624 B) · BIT 8/8 PASS, failing:[]. EULA-FORK-2 shipped: the seller acceptance box carries no EULA text of its own (626 B shell, no version marker) and ms.js serves it _EULA_HTML at **v1.18** — the version the site publishes. It had been stuck on a hand-kept v1.10 from 23 July. Verified by probing the live page and the live ms.js, not by reading the deploy log.
