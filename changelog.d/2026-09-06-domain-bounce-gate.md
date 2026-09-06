## 2026-09-06 — DOMAIN-BOUNCE-1 (the email stop-loss now watches the sending domain)

**Found during the viability review David asked for, by probing rather than reading.** Every day since
the soft launch, the outreach lane exceeded its own 5% hard-bounce limit and nothing stopped it:
29 Aug 5.6% · 1 Sep 7.2% · 2 Sep 8.5% · 3 Sep 15.3% · 5 Sep 7.8% — **86 bounces on 981 sends (8.8%)**.

**Why no gate fired.** `gate_check`'s stop-loss judges ONE CITY'S LAST WAVE. A wave is ~12 sends and
the floor is 3 bounces, so a city needs 25% in a batch to trip. Reputation, however, is scored on the
SENDING DOMAIN. This is the identical dimension error `DAILY-CAP-1` corrected for VOLUME on 5 Sep —
its own comment says reputation "depends on TOTAL volume from our domain per day, not on how it is
split between cities" — left uncorrected for BOUNCES one day later.

**Fixed.** New `domain_bounce_state()` in `emailer/wave_runner.py` reads a rolling all-cities window;
`gate_check` blocks on it against the same `bounce_stop_pct`. New defaults in `waves_policy.json`:
`domain_bounce_window_days` (3) and `domain_bounce_min_sample` (50, so a tiny sample cannot latch).
The city-scoped stop-loss is untouched — this is an additional gate, not a replacement.

**A second fault found while verifying it.** The first cut read 0.0% because it counted `email_events`
bounce rows, and **the sending machine's copy of `prospects.db` holds 11 of those against the server's
86** — while the per-prospect `bounced_at` flag had synced 66. Sends sync cleanly (981 both sides);
bounce EVENTS do not. The gate now counts off `bounced_at`, which is also what `wave_history` trusts.
Asserted, so an event-log count cannot creep back in.

**VERIFIED:** `wave_runner.py --plan` blocks every armed city —
`DOMAIN-BOUNCE-1: domain hard-bounce 5.47% over last 3d (24/439) > 5.0% -- clean the pool before
sending again`. Sending stays held until the pool is cleaned. **RG-0312 LOCKED.**
