## 2026-09-02 — WAVE-MONITOR-1: hand-fired 19:03 wave watched live; two class fixes; RG-0244 locked

**Wave:** David fired `launch_day_wave.bat` at 19:03 SAST (first wave under MIN-GAP-1 / STOP-LOSS-FLOOR-1). Claude monitored the log live. **90 sent, 0 failed** — Cape Town 12, Durban 12, Bloemfontein 12, East London 12, Port Elizabeth 10, Polokwane 24, Sydney 8; PMB/NY/London gated by min gap (sent earlier today), Pretoria stop-loss 5/59, Nelspruit/Kimberley/JHB pools empty. Server synced. CTA links `/?magic=1…` (PROBED earlier via Resend dashboard for every wave since 29 Aug — the 29–30 Aug and 1 Sep 04:xx waves carried `/admin.html`; 31 Aug and everything after the 20:24 SAST 1 Sep fix carried `/`).

**Two faults the run exposed, fixed the same evening (RG-0247, LOCKED):**
- **RAMP-FLOOR-1** — Polokwane sent 24 against a 12 cap: RAMP-1 read its 2-email wave #1 as "clean" and doubled. A wave now counts toward the streak only if ≥ `ramp.min_wave_for_streak` (default = base batch); a dirty wave of any size still breaks it.
- **ONE-PER-ORG-1** — the Polokwane teachers_trainers batch carried six University of Limpopo departments and four Mopani TVET offices. `get_prospects` now collapses to one mailbox per normalised organisation and holds siblings of orgs already emailed in the city; `sendable_by_category` counts organisations the same way (PLAN-TRUTH-1). Targeted `--email` sends bypass.

**RG-0244 LOCKED:** `deploy_citylauncher.bat` rode; `POST /launch-api/prospects/reconcile` answers 401 (was 404). The onboarded/published counters now have a live writer.

Backups: `emailer.py.bak-oneperorg-20260902-191135`, `wave_runner.py.bak-rampfloor-20260902-191135`.
